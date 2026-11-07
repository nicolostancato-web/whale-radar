# -*- coding: utf-8 -*-
"""RILEGGE la composizione delle posizioni che contano, e la confronta.

Perche' esiste (4/11, trovato dal C-check guardando gli INGRESSI invece dei
passaggi). composizione_posizioni.py compone solo le posizioni NUOVE:
  gia = set(chi c'e' gia');  nuove = [c for c in tutte if c non in gia]
Quindi una posizione composta giorni fa tiene la sua coppia PER SEMPRE,
anche se il debitore nel frattempo ha cambiato garanzia o ripagato un
debito. L'ordine pronto sarebbe costruito sulla coppia sbagliata e si
annullerebbe al momento del colpo -- e nessuno lo controllava.

Non si rileggono tutte (sono 88.183): si rileggono quelle che CONTANO, cioe'
le piu' vicine alla caduta con un premio che vale qualcosa. Una posizione a
salute 3,0 puo' avere la composizione sbagliata senza che ci costi niente.
"""
from scrittura import atomico
import json, os, sys, time, urllib.request
sys.path.insert(0, "agents")
from keccak import firma
D = "data/liquidazioni"
U = "https://ethereum-rpc.publicnode.com"
FONTI = ["https://gateway.tenderly.co/public/mainnet", U, "https://rpc.mevblocker.io"]
POOL = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
PDP  = "0x41393e5e337606dc3821075af65aee84d7688cbd"
QUANTE = int(sys.argv[1]) if len(sys.argv) > 1 else 25
def rpc(dati, to):
    c = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
        "params":[{"to":to,"data":dati},"latest"]}).encode()
    for u in FONTI:
        try:
            r = urllib.request.Request(u, data=c, headers={
                "content-type":"application/json","user-agent":"Mozilla/5.0"})
            v = json.load(urllib.request.urlopen(r, timeout=20))
            if "result" in v: return v["result"]
        except Exception: pass
    return None
PR = json.load(open(f"{D}/prezzi_oracolo.json"))
S_LISTA = firma("getReservesList()")[2:10]
S_CONF  = firma("getUserConfiguration(address)")[2:10]
S_DATI  = firma("getUserReserveData(address,address)")[2:10]
v = rpc("0x"+S_LISTA, POOL)
if not v or len(v) < 200:
    print("   non riesco a leggere la lista delle riserve"); sys.exit(1)
x = v[2:]; n = int(x[64:128], 16)
riserve = ["0x"+x[128+i*64+24:128+(i+1)*64].lower() for i in range(n)]
def coppia_dalla_catena(u):
    """La garanzia e il debito PRINCIPALI, letti adesso."""
    c = rpc("0x"+S_CONF+u[2:].lower().zfill(64), POOL)
    if not c: return None
    mappa = int(c, 16)
    gar, deb = [], []
    for i, a in enumerate(riserve):
        usa_deb = (mappa >> (2*i)) & 1
        usa_gar = (mappa >> (2*i+1)) & 1
        if not (usa_deb or usa_gar): continue
        p = PR.get(a)
        if not p: continue
        d = rpc("0x"+S_DATI+a[2:].zfill(64)+u[2:].lower().zfill(64), PDP)
        if not d or len(d) < 200: continue
        y = d[2:]
        g_usd = int(y[0:64],16)/10**p["decimali"]*p["prezzo_usd"]
        d_usd = int(y[128:192],16)/10**p["decimali"]*p["prezzo_usd"]
        if usa_gar and g_usd > 0: gar.append((a, g_usd))
        if usa_deb and d_usd > 0: deb.append((a, d_usd))
    if not gar or not deb: return None
    gar.sort(key=lambda t:-t[1]); deb.sort(key=lambda t:-t[1])
    return {"garanzia_principale":gar[0][0], "garanzia_usd":round(gar[0][1],2),
            "debito_principale":deb[0][0], "debito_usd":round(deb[0][1],2)}
def main():
    s = json.load(open(f"{D}/salute_note.json"))
    co = json.load(open(f"{D}/composizione.json"))
    chiavi = {k.lower(): k for k in co}
    # quelle che CONTANO: vicine alla caduta e con un premio vero
    # SI RILEGGONO LE PIU' PREZIOSE, non solo le piu' vicine.
    #
    # DIFETTO PAGATO il 4/11 sera: la prova sulla copia della catena e'
    # fallita con l'errore di Aave "SpecifiedCurrencyNotBorrowedByUser" --
    # cioe' la moneta che credevamo in prestito NON lo era. La composizione
    # registrata era sbagliata, e quella posizione non era fra le 25 piu'
    # vicine, quindi non la rileggevamo mai.
    # Non e' un problema della prova: se SPARIAMO su una posizione di cui
    # sbagliamo il debito, la liquidazione si annulla e la presa e' persa.
    # Lo stesso errore, nel momento del colpo.
    # Quindi si rileggono quelle che il pescatore guarda a ogni blocco --
    # le piu' preziose -- e non solo le piu' vicine alla soglia. E' la
    # stessa correzione fatta oggi alla corsia e alla sentinella: il valore
    # decide, non solo la vicinanza.
    try:
        PREMI = {k.lower(): (x.get("premio") or 0) for k, x in
                 json.load(open(f"{D}/vendite_pronte.json")).items()}
    except Exception:
        PREMI = {}
    vive = [(PREMI.get(a, 0), d["salute"], a) for a, d in s.items()
            if a in chiavi and 1.0 <= d["salute"] < 1.25
            and d["debito"]*0.5*0.07 >= 200]
    # meta' del lavoro alle piu' preziose, meta' alle piu' vicine
    per_valore = sorted(vive, key=lambda t: -t[0])[:QUANTE//2]
    presi = {t[2] for t in per_valore}
    per_vicinanza = [t for t in sorted(vive, key=lambda t: t[1])
                     if t[2] not in presi][:QUANTE - len(per_valore)]
    cand = [(t[1], t[2]) for t in per_valore + per_vicinanza]
    print(f"   rileggo {len(cand)} posizioni fra le piu' vicine alla caduta")
    diversi, uguali, muti, dettagli = 0, 0, 0, []
    for h, a in cand:
        vero = coppia_dalla_catena(a)
        if not vero: muti += 1; continue
        vecchio = co[chiavi[a]]
        cambiata = (vero["garanzia_principale"].lower() != vecchio["garanzia_principale"].lower()
                    or vero["debito_principale"].lower() != vecchio["debito_principale"].lower())
        if cambiata:
            diversi += 1
            dettagli.append({"posizione":a, "salute":round(h,4),
                "prima":{"gar":vecchio["garanzia_principale"][:12],
                         "deb":vecchio["debito_principale"][:12]},
                "adesso":{"gar":vero["garanzia_principale"][:12],
                          "deb":vero["debito_principale"][:12]},
                "premio_in_gioco":round(vero["debito_usd"]*0.5*0.07,2)})
            print(f"   !!! {a[:12]} salute {h:.4f}: la coppia E' CAMBIATA")
            print(f"       prima  {vecchio['garanzia_principale'][:12]} / {vecchio['debito_principale'][:12]}")
            print(f"       adesso {vero['garanzia_principale'][:12]} / {vero['debito_principale'][:12]}")
            co[chiavi[a]].update(vero)      # si CORREGGE subito
            # E L'ORDINE PRONTO VA BUTTATO. Era costruito per vendere la
            # garanzia VECCHIA: al momento del colpo il contratto non
            # troverebbe quel gettone in casa e lo scambio si annullerebbe.
            # Correggere la composizione senza invalidare l'ordine avrebbe
            # lasciato il difetto esattamente dov'era.
            try:
                VP = json.load(open(f"{D}/vendite_pronte.json"))
                for k in (chiavi[a], a, a.lower()):
                    if k in VP:
                        VP[k]["quando"] = 0
                        VP[k].pop("chiamata", None)
                        VP[k]["invalidato"] = "coppia cambiata sulla catena"
                json.dump(VP, open(f"{D}/vendite_pronte.json","w"))
                print("       ordine pronto INVALIDATO: verra' rifatto")
            except Exception as e:
                print(f"       non riesco a invalidare l'ordine: {str(e)[:60]}")
        else:
            uguali += 1
            co[chiavi[a]]["debito_usd"] = vero["debito_usd"]
            co[chiavi[a]]["garanzia_usd"] = vero["garanzia_usd"]
    atomico(co, f"{D}/composizione.json", indent=1)
    json.dump({"quando":time.time(), "rilette":len(cand), "uguali":uguali,
               "cambiate":diversi, "mute":muti, "dettagli":dettagli},
              open(f"{D}/composizione_riletta.json","w"), indent=1)
    print(f"   {uguali} invariate, {diversi} CAMBIATE, {muti} non lette")
    return 0
if __name__ == "__main__":
    sys.exit(main())
