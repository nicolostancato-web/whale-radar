"""IL PRENOTATORE: compone il pacchetto per stare nello STESSO blocco.

Non si vince correndo, si vince prenotando. Il pacchetto dice al
costruttore del blocco: «subito dopo quella transazione di prezzo, esegui
la mia liquidazione». Si consegna PRIMA che il blocco esista.

Modalita' SILENZIOSA: compone, firma, e invece di consegnare scrive.

Un pacchetto sbagliato non viene incluso e non costa nulla: quindi si puo'
prenotare anche a vuoto, su tutte le posizioni vicine, senza sapere in
anticipo quale cadra' davvero.
"""
import json, os, subprocess, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
SILENZIOSO = True
FOUNDRY=os.path.expanduser("~/.foundry/bin")
CONTRATTO="0xE30b58692FB7a1a417d3e0F1F5585a8Bc4D51212"
OPERATIVO="0x4355962379C779009F833d81bd8D2912773749A0"
U="https://ethereum-rpc.publicnode.com"
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
REG="data/liquidazioni/prenotazioni.jsonl"
def cast(*a):
    r=subprocess.run([f"{FOUNDRY}/cast",*a], capture_output=True, text=True)
    return r.stdout.strip()
def rpc(m,p,giri=3):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=15))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.2*(g+1))
    return None
def vendita(src,dst,quanti,sd,dd):
    """Chiamata di vendita pronta, dall'aggregatore."""
    try:
        r=urllib.request.Request(
            f"https://api.paraswap.io/prices?srcToken={src}&destToken={dst}"
            f"&amount={quanti}&srcDecimals={sd}&destDecimals={dd}&side=SELL&network=1",
            headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
        pr=json.load(urllib.request.urlopen(r,timeout=15))["priceRoute"]
        rq=urllib.request.Request(
            "https://api.paraswap.io/transactions/1?ignoreChecks=true&ignoreGasEstimate=true",
            data=json.dumps({"srcToken":src,"destToken":dst,"srcAmount":str(quanti),
                "priceRoute":pr,"userAddress":CONTRATTO,"slippage":100}).encode(),
            headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
        tx=json.load(urllib.request.urlopen(rq,timeout=15))
        return tx.get("to"), tx.get("data")
    except Exception as e:
        return None, str(e)[:70]
def componi(utente, comp, debito_quota=0.5):
    """La transazione di liquidazione, pronta e firmata (non mandata)."""
    t0=time.time()
    gar=comp["garanzia_principale"]; deb=comp["debito_principale"]
    pg=PR.get(gar); pd=PR.get(deb)
    if not pg or not pd: return None,"prezzo mancante",0
    dus=comp["debito_usd"]*debito_quota
    qdeb=int(dus/pd["prezzo_usd"]*10**pd["decimali"])
    qgar=int(dus*1.07/pg["prezzo_usd"]*10**pg["decimali"])
    sede, dati = vendita(gar, deb, qgar, pg["decimali"], pd["decimali"])
    if not sede: return None, f"vendita non ottenuta: {dati}", time.time()-t0
    # la quantita' vera la scrive il contratto: con l'aggregatore la
    # posizione varia, quindi si lascia 0 e si accetta la quantita' fissata
    piano = (gar, utente, [(gar, sede, dati, 0)], 1)
    chiamata = cast("calldata",
        "esegui(address,uint256,(address,address,(address,address,bytes,uint256)[],uint256))",
        deb, str(qdeb),
        f"({gar},{utente},[({gar},{sede},{dati},0)],1)")
    return chiamata, None, time.time()-t0
if __name__=="__main__":
    comp=json.load(open("data/liquidazioni/composizione.json"))
    u=min(comp, key=lambda k: comp[k]["salute"])
    c=comp[u]
    print(f"   prova di composizione su {u[:14]} (salute {c['salute']:.4f})")
    print(f"   modalita': {'SILENZIOSA' if SILENZIOSO else 'ARMATA'}\n")
    ch, err, dt = componi(u, c)
    if err:
        print(f"   NON composta: {err}  ({dt:.2f}s)")
    else:
        print(f"   chiamata composta: {len(ch)} caratteri  in {dt:.2f}s")
        print(f"   inizio: {ch[:74]}...")
        bl=int(rpc("eth_blockNumber",[]),16)
        pacchetto={"version":"v0.1",
          "inclusion":{"block":hex(bl+1),"maxBlock":hex(bl+2)},
          "body":[{"hash":"0x"+"00"*32},          # qui andra' l'indizio vero
                  {"tx":"<la nostra, firmata>","canRevert":False}]}
        print(f"\n   PACCHETTO pronto per il blocco {bl+1}:")
        print(f"      {json.dumps(pacchetto)[:150]}...")
        print(f"\n   {'NON consegnato (silenzioso)' if SILENZIOSO else 'CONSEGNATO'}")
