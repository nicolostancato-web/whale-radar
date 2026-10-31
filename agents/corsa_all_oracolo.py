"""Quanti blocchi passano fra l'aggiornamento del prezzo e la liquidazione?

E' la misura che sostituisce quella ritirata (la posizione nel blocco, senza
forza perche' i blocchi sono pieni al 41%).

Se la liquidazione arriva nello STESSO blocco dell'aggiornamento, o in
quello dopo, e' un robot che corre l'oracolo: con nodi pubblici non si
compete. Se invece il ritardo e' sparso dentro l'intervallo fra due
aggiornamenti, nessuno sta correndo e c'e' spazio per chi se ne accorge.
"""
import json, time, urllib.request, sys, os, statistics as st
sys.path.insert(0,"agents")
from keccak import firma
RPC=["https://eth.llamarpc.com","https://ethereum-rpc.publicnode.com",
     "https://rpc.ankr.com/eth","https://cloudflare-eth.com"]
def chiama(m,p=None,giri=6):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        for u in RPC:
            try:
                r=urllib.request.Request(u,data=c,headers={
                  "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=30))
                if "result" in d and d["result"] is not None: return d["result"]
            except Exception: pass
        time.sleep(0.4*(g+1))
    return None
PROXY="0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419"     # ETH/USD Chainlink
agg=chiama("eth_call",[{"to":PROXY,"data":"0x"+firma("aggregator()")[2:10]},"latest"])
if not agg or len(agg)<42:
    print("   non riesco a leggere l'aggregatore"); sys.exit(1)
AGG="0x"+agg[-40:]
print(f"   aggregatore ETH/USD: {AGG}")
AU=firma("AnswerUpdated(int256,uint256,uint256)")
ev=[json.loads(x) for x in open("data/liquidazioni/eventi.jsonl")] \
   if os.path.exists("data/liquidazioni/eventi.jsonl") else []
print(f"   {len(ev)} liquidazioni accumulate\n")
# prima: ogni quanto si aggiorna l'oracolo (serve per sapere cosa e' «a caso»)
ult=int(chiama("eth_blockNumber"),16)
agg_bl=[]
b=ult-3000
while b<ult:
    f=min(b+499,ult)
    r=chiama("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(f),
                             "address":AGG,"topics":[AU]}])
    if r: agg_bl += [int(x["blockNumber"],16) for x in r]
    b=f+1; time.sleep(0.1)
agg_bl=sorted(set(agg_bl))
if len(agg_bl)>1:
    gap=[agg_bl[i+1]-agg_bl[i] for i in range(len(agg_bl)-1)]
    print(f"   l'oracolo si aggiorna ogni {st.median(gap):.0f} blocchi "
          f"(mediana su {len(gap)} intervalli)")
    atteso=st.median(gap)/2
    print(f"   se nessuno corresse, il ritardo medio sarebbe ~{atteso:.0f} blocchi\n")
else:
    print("   pochi aggiornamenti letti\n"); atteso=None
rit=[]
for e in ev:
    bn=e["blocco"]
    prec=[x for x in agg_bl if x<=bn]
    if not prec:
        r=chiama("eth_getLogs",[{"fromBlock":hex(bn-300),"toBlock":hex(bn),
                                 "address":AGG,"topics":[AU]}])
        prec=[int(x["blockNumber"],16) for x in (r or [])]
    if not prec: print(f"   {e['prot']} blocco {bn}: nessun aggiornamento trovato"); continue
    d=bn-max(prec)
    rit.append(d)
    print(f"   {e['prot']:<10} blocco {bn}  ritardo dall'ultimo prezzo: {d} blocchi"
          f"  {'(STESSO BLOCCO: corsa)' if d==0 else ''}")
if rit:
    print(f"\n   ritardo mediano {st.median(rit):.0f} blocchi su {len(rit)} liquidazioni")
    if atteso:
        print(f"   atteso se nessuno corresse: ~{atteso:.0f}")
        print(f"   -> {'CORSA ALL ORACOLO' if st.median(rit)<=1 else 'nessuna corsa evidente'}")
