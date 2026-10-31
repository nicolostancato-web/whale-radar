"""Il ritardo dall'oracolo GIUSTO: ogni garanzia ha il suo prezzo.

La misura precedente usava ETH/USD per tutte le liquidazioni: se la garanzia
era WBTC o un dollaro sintetico, misuravo il ritardo da un prezzo che non
c'entrava. Qui si chiede ad Aave quale fonte usa per ciascun asset, e si
misura contro quella.
"""
import json, time, urllib.request, sys, collections, statistics as st
sys.path.insert(0,"agents")
from keccak import firma
ORACOLO="0x54586be62e3c3580375ae3723c145253060ca0c2"   # AaveOracle v3
U="https://ethereum-rpc.publicnode.com"
def call(to, dato, giri=4):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
                  "params":[{"to":to,"data":dato},"latest"]}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=25))
            if "result" in d and d["result"] not in (None,"0x"): return d["result"]
        except Exception: pass
        time.sleep(0.4*(g+1))
    return None
def logs(ind, topic, da, a, giri=4):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[
        {"fromBlock":hex(da),"toBlock":hex(a),"address":ind,"topics":[topic]}]}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=35))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.5*(g+1))
    return None
SRC=firma("getSourceOfAsset(address)")[2:10]
AGGR=firma("aggregator()")[2:10]
AU=firma("AnswerUpdated(int256,uint256,uint256)")
# i log storici non sono serviti dai nodi pubblici oltre pochi giorni:
# si usano le liquidazioni RECENTI raccolte in avanti, che stanno dentro
# la finestra di ritenzione.
import os
ev=[]
for f in ("data/liquidazioni/eventi.jsonl","data/liquidazioni/storia_v2.jsonl"):
    if os.path.exists(f): ev+=[json.loads(x) for x in open(f)]
# serve la moneta della garanzia: i record vecchi non ce l'hanno
ev=[e for e in ev if e.get("gar")]
# prendo le liquidazioni piu' recenti (gli altri log non sono piu' serviti)
ev=[e for e in ev if e.get("gar")]
ev.sort(key=lambda e:-e["blocco"])
# solo blocchi dentro la ritenzione (ultimi ~2 giorni)
ultimo=max(e["blocco"] for e in ev)
recenti=[e for e in ev if e["blocco"] > ultimo-14400][:14]
print(f"   {len(recenti)} liquidazioni recenti da esaminare\n")
feed={}
for a in {e["gar"] for e in recenti}:
    s=call(ORACOLO, "0x"+SRC+a[2:].zfill(64))
    if not s or len(s)<42: print(f"   {a[:12]}: fonte non letta"); continue
    pr="0x"+s[-40:]
    ag=call(pr, "0x"+AGGR)
    feed[a]=("0x"+ag[-40:]) if ag and len(ag)>=42 else pr
    print(f"   garanzia {a[:12]}...  fonte {feed[a][:12]}...")
    time.sleep(0.2)
print()
rit=[]
for e in recenti:
    f=feed.get(e["gar"])
    if not f: continue
    bn=e["blocco"]
    L=logs(f, AU, bn-600, bn)
    if L is None: print(f"   blocco {bn}: log non ottenuti"); continue
    bl=[int(x["blockNumber"],16) for x in L]
    if not bl: print(f"   blocco {bn}: nessun aggiornamento nelle 600 precedenti"); continue
    d=bn-max(bl)
    rit.append(d)
    print(f"   blocco {bn}  ritardo dal prezzo della SUA garanzia: {d} blocchi"
          f"  ({d*12/60:.1f} min){'  STESSO BLOCCO' if d==0 else ''}")
    time.sleep(0.3)
if rit:
    rit.sort()
    print(f"\n   {len(rit)} misure | ritardo mediano {st.median(rit):.0f} blocchi "
          f"({st.median(rit)*12/60:.1f} minuti)")
    print(f"   entro 1 blocco: {sum(1 for x in rit if x<=1)}/{len(rit)}")
    print(f"   -> {'CORSA: si vince al blocco' if st.median(rit)<=1 else 'non si vince al blocco: c e una finestra'}")
