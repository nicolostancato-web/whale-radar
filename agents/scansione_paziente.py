"""Scansione paziente della storia delle liquidazioni.

Il tentativo veloce (finestre da 10.000) e' fallito al 98%: la prova singola
passava, l'uso continuato no. Qui si va piano e si SALVA A OGNI FINESTRA,
cosi' il lavoro non si perde se cade a meta' e i giri successivi riprendono
da dove si e' arrivati.

Mai .gz in append e mai riscrivere il file intero: una riga per finestra.
"""
import json, os, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
RPC=["https://ethereum-rpc.publicnode.com","https://eth.llamarpc.com",
     "https://rpc.payload.de","https://eth.drpc.org","https://1rpc.io/eth"]
def chiama(m,p=None,giri=4):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        for u in RPC:
            try:
                r=urllib.request.Request(u,data=c,headers={
                  "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=45))
                if "result" in d and d["result"] is not None: return d["result"]
            except Exception: pass
            time.sleep(0.25)
        time.sleep(1.2*(g+1))
    return None
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
POOL={"aave_v3":"0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
      "spark":"0xc13e21b648a5ee794902342038ff3adab66be987"}
D="data/liquidazioni"; os.makedirs(D,exist_ok=True)
STATO=f"{D}/scansione.json"; FUORI=f"{D}/storia.jsonl"
ult=int(chiama("eth_blockNumber"),16)
st_=json.load(open(STATO)) if os.path.exists(STATO) else {}
INDIETRO=60*7200
inizio = st_.get("prossimo", ult-INDIETRO)
fine_tot = st_.get("fino_a", ult)
print(f"   dal blocco {inizio} verso {fine_tot}  "
      f"({(fine_tot-inizio)/7200:.1f} giorni rimasti)")
b=inizio; letti=0; falliti=0; trovati=0; t0=time.time()
while b < fine_tot and time.time()-t0 < 540:     # si ferma da sola, riprende dopo
    f=min(b+1999, fine_tot)
    ok=True
    for nome,ind in POOL.items():
        r=chiama("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(f),
                                 "address":ind,"topics":[LIQ]}])
        if r is None: ok=False; continue
        if r:
            with open(FUORI,"a") as g:
                for x in r:
                    g.write(json.dumps({"prot":nome,"blocco":int(x["blockNumber"],16),
                        "tx":x["transactionHash"],"gar":"0x"+x["topics"][1][-40:],
                        "dati":x["data"]})+"\n")
            trovati+=len(r)
    if ok: letti += f-b+1
    else: falliti += f-b+1
    b=f+1
    json.dump({"prossimo":b,"fino_a":fine_tot}, open(STATO,"w"))
    time.sleep(0.3)
tot=letti+falliti
print(f"   in questo giro: {letti:,} blocchi letti, {falliti:,} falliti "
      f"({falliti/max(tot,1)*100:.0f}%) | {trovati} eventi nuovi")
print(f"   arrivato a {b}, mancano {(fine_tot-b)/7200:.1f} giorni")
n=sum(1 for _ in open(FUORI)) if os.path.exists(FUORI) else 0
print(f"   storia accumulata: {n} eventi")
