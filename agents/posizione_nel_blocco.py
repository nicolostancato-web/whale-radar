"""Le liquidazioni sono vinte al millisecondo, o c'e' spazio per chi arriva dopo?

Un bundle di professionisti finisce in CIMA al blocco (posizione 0-2), perche'
e' cosi' che si vince la corsa. Se invece le liquidazioni sono sparse nel
blocco, sono transazioni normali e la gara non e' di latenza pura.

E' la domanda che decide se possiamo starci: con nodi pubblici che perdono
meta' delle richieste, una corsa al millisecondo non si vince.
"""
import json, time, urllib.request, sys, os, statistics as st
sys.path.insert(0,"agents")
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
F="data/liquidazioni/eventi.jsonl"
ev=[json.loads(x) for x in open(F)] if os.path.exists(F) else []
# piu' le 6 trovate prima, recuperate dai log gia' misurati
noti=["0x78e0f2cad5f0","0xa9592aeb8b1c","0x090811cf7607",
      "0xb09d12ee1ef7","0xecd28001e250","0x38ca2a076cbb"]
print(f"   {len(ev)} liquidazioni dall'accumulatore\n")
pos=[]
for e in ev:
    r=chiama("eth_getTransactionReceipt",[e["tx"]])
    if not r: continue
    idx=int(r["transactionIndex"],16)
    bl=chiama("eth_getBlockByNumber",[r["blockNumber"], False])
    n=len(bl.get("transactions",[])) if bl else None
    pz=int(r.get("effectiveGasPrice","0x0"),16)/1e9
    pos.append((e["prot"], idx, n, pz))
    print(f"   {e['prot']:<10} posizione {idx:>3} su {n:>3} transazioni  "
          f"gas {pz:.3f} gwei  {'IN CIMA' if idx<=2 else ''}")
if pos:
    cima=sum(1 for _,i,_,_ in pos if i<=2)
    print(f"\n   in cima al blocco: {cima}/{len(pos)}")
    rel=[i/n*100 for _,i,n,_ in pos if n]
    if rel:
        print(f"   posizione relativa mediana: {st.median(rel):.0f}% del blocco")
    print(f"   -> {'gara di latenza chiusa' if cima/len(pos)>0.6 else 'NON e una gara di sola latenza'}")
else:
    print("   nessuna ricevuta ottenuta")
