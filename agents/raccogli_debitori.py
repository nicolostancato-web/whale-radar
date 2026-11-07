# -*- coding: utf-8 -*-
"""Chi ha un debito su Aave: l'elenco completo, dalla nascita del protocollo.

La copertura del laghetto e' l'unica leva ancora aperta: misurato il 31/10,
vediamo il 31% di chi cade. Chi ha preso in prestito due anni fa e non l'ha
piu' toccato e' esattamente il tipo che scivola verso la liquidazione -- e
compare SOLO nella finestra vecchia.

RISCRITTO l'1/11. Prima:
  - Blockscout, finestre da 10.000 blocchi, 5 per giro, 5s di pausa
  - copriva solo gli ULTIMI 120 GIORNI (GIORNI=120): il 10% della storia
  - rifiuti 429 continui, e a un certo punto «lista completa» a 12.952
    debitori, che sembrava finito ed era invece solo il recinto che ci
    eravamo messi noi. Un limite scritto in una costante non si annuncia
    quando lo raggiungi: dice «completo».
Ora:
  - le due fonti RPC che reggono 50.000 blocchi (provate l'1/11), alternate
  - dalla NASCITA di Aave v3 su Ethereum: blocco 16291127 (gennaio 2023)
  - 183 finestre invece di 913, e nessun 429

Nessuna chiave, nessun costo. Provata anche la strada del subgraph: richiede
una chiave, quindi scartata (regola CFO: default alla strada gratis).
RIPRENDIBILE: salva dopo ogni finestra.
"""
import json, os, sys, time, urllib.request, itertools
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
BORROW=firma("Borrow(address,address,address,uint256,uint8,uint256,uint16)")
# nascita di Aave v3 su Ethereum mainnet: prima di qui non c'e' niente da leggere
GENESI=16291127
PASSO=50_000
MAX_PER_GIRO=8
FONTI=["https://gateway.tenderly.co/public/mainnet","https://rpc.mevblocker.io"]
_g=itertools.cycle([0,1])
D="data/liquidazioni"; os.makedirs(D, exist_ok=True)
FUORI=f"{D}/debitori.json"; FATTE=f"{D}/finestre_debitori_v3.json"
def rpc(m,p):
    i=next(_g)
    for u in (FONTI[i],FONTI[1-i]):
        try:
            c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
            r=urllib.request.Request(u,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=60))
            if "result" in d: return d["result"]
        except Exception: pass
    return None
deb=set(json.load(open(FUORI))) if os.path.exists(FUORI) else set()
fatte=set(json.load(open(FATTE))) if os.path.exists(FATTE) else set()
t=rpc("eth_blockNumber",[])
if not t:
    print("   non raggiungo la chain: niente da fare questo giro"); sys.exit(0)
ult=int(t,16)
# si parte dalle finestre RECENTI e si va indietro: se il tempo finisce,
# meglio avere i debitori di ieri che quelli di due anni fa.
tutte=list(range(GENESI//PASSO*PASSO, ult, PASSO))[::-1]
# L'ULTIMA FINESTRA SI RILEGGE SEMPRE. Difetto trovato il 4/11 dal
# C-check risalendo dagli ingressi alla sorgente: una finestra veniva
# segnata come "fatta" anche quando conteneva la TESTA della catena, cioe'
# quando era stata letta solo fino a dove la catena era arrivata in quel
# momento (f = min(b+PASSO-1, ult)). Poi la catena avanza DENTRO la stessa
# finestra e quei blocchi non si rileggono mai: fino a 50.000 blocchi,
# circa una settimana di debitori nuovi che non esistono per noi.
# E i debitori nuovi con posizioni a leva sono proprio quelli piu' vicini
# alla liquidazione.
# Costa una finestra in piu' per giro, cioe' niente.
# LEZIONE: "fatta" non vuol dire "completa" quando il confine si muove.
finestra_della_testa = (ult // PASSO) * PASSO
if finestra_della_testa in fatte:
    fatte.discard(finestra_della_testa)
    print(f"   rileggo la finestra della testa ({finestra_della_testa:,}): "
          f"la catena ci e' avanzata dentro")
restano=[b for b in tutte if b not in fatte]
if finestra_della_testa not in restano and finestra_della_testa < ult:
    restano.insert(0, finestra_della_testa)
print(f"   {len(fatte)}/{len(tutte)} finestre ({100*len(fatte)/len(tutte):.0f}%) | "
      f"{len(deb)} debitori")
if not restano:
    print("   tutta la storia di Aave v3 e' stata letta"); sys.exit(0)
presi=nuovi=0
for b in restano[:MAX_PER_GIRO]:
    f=min(b+PASSO-1, ult)
    lg=rpc("eth_getLogs",[{"address":POOL,"topics":[BORROW],
        "fromBlock":hex(b),"toBlock":hex(f)}])
    if lg is None:
        print(f"   rifiuto su {b}: mi fermo e salvo"); break
    for x in lg:
        # topics: [firma, reserve, onBehalfOf, referral] -> il DEBITORE e'
        # onBehalfOf (topic 2), non 'user' che sta nei dati: chi ha chiesto
        # il prestito puo' essere un altro, il debito e' di onBehalfOf.
        if len(x.get("topics",[]))>2:
            a="0x"+x["topics"][2][-40:]
            if a not in deb: deb.add(a); nuovi+=1
    fatte.add(b); presi+=1
    json.dump(sorted(deb), open(FUORI,"w"))
    json.dump(sorted(fatte), open(FATTE,"w"))
    time.sleep(1.2)
print(f"   prese {presi} finestre, {nuovi} debitori nuovi | totale {len(deb)}")
print(f"   copertura {len(fatte)}/{len(tutte)} ({100*len(fatte)/len(tutte):.0f}%)")
