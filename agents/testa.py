"""LA TESTA: collega la sentinella al braccio. In modalita' SILENZIOSA.

Fa tutto fino all'ultimo passo e, invece di mandare, scrive cosa avrebbe
mandato. Cosi' si vede se la decisione era giusta senza rischiare nulla.

Catena, quando una posizione cade:
  1. quale garanzia e quale debito ha        (gia' calcolato prima)
  2. quanto debito si puo' ripagare          (il protocollo limita a meta',
                                              o tutto se la salute e' sotto 0,95)
  3. come si vende la garanzia               (aggregatore, ~1 secondo)
  4. compone la chiamata al contratto        (e NON la manda)

Il silenziatore si toglie con una riga, e sara' una decisione di Nicolo'.
"""
import json, os, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
SILENZIOSA = True        # <<< il silenziatore
U="https://ethereum-rpc.publicnode.com"
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
PDP="0x41393e5e337606dc3821075af65aee84d7688cbd"
# L'INDIRIZZO VIENE DA UN SOLO POSTO (4/11 sera). Era scritto a mano in
# dieci file, il sorgente e' cresciuto e il contratto in catena non e' mai
# stato ridistribuito: la calldata chiamava un selettore che il bytecode
# distribuito non aveva, e ~12.000 pacchetti sono morti al primo byte con
# revert vuoto. Vedi agents/indirizzi.py.
from indirizzi import contratto as _dove
CONTRATTO=_dove()
SEL_SALUTE=firma("getUserAccountData(address)")[2:10]
SEL_CONF=firma("getReserveConfigurationData(address)")[2:10]
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
# rsETH escluso: due prove dicono che non si vende
ESCLUSI={"0xa1290d69c65a6fe4df752f95823fae25cb99e5a7"}
REG="data/liquidazioni/decisioni.jsonl"
def rpc(m,p,giri=3,tout=15):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=tout))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.2*(g+1))
    return None
def salute(a):
    v=rpc("eth_call",[{"to":POOL,"data":"0x"+SEL_SALUTE+a[2:].zfill(64)},"latest"])
    if isinstance(v,str) and len(v)>=2+64*6:
        x=v[2:]
        return {"debito":int(x[64:128],16)/1e8,"salute":int(x[320:384],16)/1e18}
    return None
def premio_protocollo(asset):
    """Il bonus di liquidazione, LETTO dal protocollo e non assunto."""
    v=rpc("eth_call",[{"to":PDP,"data":"0x"+SEL_CONF+asset[2:].zfill(64)},"latest"])
    if isinstance(v,str) and len(v)>=2+64*5:
        b=int(v[2:][192:256],16)      # liquidationBonus, base 10000
        return (b-10000)/10000 if b>10000 else None
    return None
def percorso_vendita(src, dst, quanti, sd, dd):
    """Chiede all'aggregatore come vendere. Ritorna (chiamata, sconto, secondi)."""
    t0=time.time()
    try:
        r=urllib.request.Request(
            f"https://api.paraswap.io/prices?srcToken={src}&destToken={dst}"
            f"&amount={quanti}&srcDecimals={sd}&destDecimals={dd}&side=SELL&network=1",
            headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
        d=json.load(urllib.request.urlopen(r, timeout=20))
        pr=d["priceRoute"]
        se=float(pr.get("srcUSD",0)); de=float(pr.get("destUSD",0))
        rq=urllib.request.Request(
            "https://api.paraswap.io/transactions/1?ignoreChecks=true&ignoreGasEstimate=true",
            data=json.dumps({"srcToken":src,"destToken":dst,"srcAmount":str(quanti),
                "priceRoute":pr,"userAddress":CONTRATTO,"slippage":100}).encode(),
            headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
        tx=json.load(urllib.request.urlopen(rq, timeout=20))
        return tx, (1-de/se)*100 if se else None, time.time()-t0
    except Exception as e:
        return None, str(e)[:80], time.time()-t0
def decidi(utente, comp):
    """Tutta la catena, fino all'ultimo passo escluso."""
    t0=time.time()
    s=salute(utente)
    if not s or s["salute"]>=1.0:
        return {"esito":"non piu' liquidabile"}
    gar=comp["garanzia_principale"]; deb=comp["debito_principale"]
    if gar in ESCLUSI:
        return {"esito":"garanzia esclusa (non si vende)","garanzia":gar}
    pg=PR.get(gar); pd=PR.get(deb)
    if not pg or not pd:
        return {"esito":"prezzo mancante: non procedo"}
    # quanto si puo' chiudere: meta', o tutto se la salute e' sotto 0,95
    quota = 1.0 if s["salute"] < 0.95 else 0.5
    debito_usd = comp["debito_usd"] * quota
    quanti_debito = int(debito_usd / pd["prezzo_usd"] * 10**pd["decimali"])
    bonus = premio_protocollo(gar)
    garanzia_usd = debito_usd * (1 + (bonus or 0.05))
    quanti_gar = int(garanzia_usd / pg["prezzo_usd"] * 10**pg["decimali"])
    tx, sconto, dt_agg = percorso_vendita(gar, deb, quanti_gar,
                                          pg["decimali"], pd["decimali"])
    premio_lordo = garanzia_usd - debito_usd
    costo_vendita = garanzia_usd * (sconto/100) if isinstance(sconto,float) else None
    return {"esito":"PRONTA" if tx else "vendita non ottenuta",
            "utente":utente, "salute":s["salute"],
            "garanzia":gar, "debito":deb,
            "quota_chiusa":quota,
            "debito_ripagato_usd":round(debito_usd,2),
            "bonus_protocollo":bonus,
            "garanzia_incassata_usd":round(garanzia_usd,2),
            "premio_lordo_usd":round(premio_lordo,2),
            "sconto_vendita_pct":sconto if isinstance(sconto,float) else None,
            "costo_vendita_usd":round(costo_vendita,2) if costo_vendita else None,
            "netto_stimato_usd":round(premio_lordo-(costo_vendita or 0),2),
            "chiamata_a": tx.get("to") if tx else None,
            "secondi_totali": round(time.time()-t0,2),
            "secondi_aggregatore": round(dt_agg,2)}
if __name__=="__main__":
    try: comp=json.load(open("data/liquidazioni/composizione.json"))
    except Exception: comp={}
    print(f"   {len(comp)} posizioni con composizione nota")
    print(f"   modalita': {'SILENZIOSA (non manda nulla)' if SILENZIOSA else 'ARMATA'}\n")
    # prova a secco sulla posizione piu' vicina, come se fosse caduta
    if comp:
        u=min(comp, key=lambda k: comp[k]["salute"])
        c=comp[u]
        print(f"   prova a secco su {u[:14]} (salute {c['salute']:.4f})")
        print(f"      garanzia {c['garanzia_principale'][:12]}.. ${c['garanzia_usd']:,.0f}")
        print(f"      debito   {c['debito_principale'][:12]}.. ${c['debito_usd']:,.0f}")
        b=premio_protocollo(c["garanzia_principale"])
        print(f"      bonus di liquidazione letto dal protocollo: "
              f"{b*100:.2f}%" if b else "      bonus non letto")
        gar=c["garanzia_principale"]; deb=c["debito_principale"]
        pg=PR.get(gar); pd=PR.get(deb)
        if pg and pd:
            dus=c["debito_usd"]*0.5
            qg=int(dus*(1+(b or 0.05))/pg["prezzo_usd"]*10**pg["decimali"])
            tx,sc,dt=percorso_vendita(gar,deb,qg,pg["decimali"],pd["decimali"])
            print(f"      vendita di ${dus*(1+(b or 0.05)):,.0f} di garanzia:")
            print(f"         {'ottenuta' if tx else 'NON ottenuta'}  "
                  f"sconto {sc:.3f}%" if isinstance(sc,float) else f"         {sc}")
            print(f"         tempo aggregatore: {dt:.2f}s")
            if tx and isinstance(sc,float):
                prem=dus*(b or 0.05)
                print(f"      PREMIO LORDO stimato: ${prem:,.2f}")
                print(f"      costo vendita:        ${dus*(1+(b or 0.05))*sc/100:,.2f}")
                print(f"      NETTO stimato:        ${prem - dus*(1+(b or 0.05))*sc/100:,.2f}")
