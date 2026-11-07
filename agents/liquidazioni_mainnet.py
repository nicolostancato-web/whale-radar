"""Le liquidazioni dove accadono davvero: Ethereum, non la chain comoda.

Lezione gia' pagata tre volte: scegliere il posto perche' avevo il
collegamento la' significa misurare me stesso. Aave v3 su Ethereum e'
l'archivio piu' grande del mestiere.
Si contano i FALLIMENTI delle finestre: zeri silenziosi hanno gia' fatto
sembrare morto Kleros.
"""
import sys, json, time, urllib.request, collections
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
RPC=["https://eth.llamarpc.com","https://ethereum-rpc.publicnode.com",
     "https://rpc.ankr.com/eth","https://cloudflare-eth.com"]
def chiama(metodo, par=None, giri=8):
    corpo=json.dumps({"jsonrpc":"2.0","id":1,"method":metodo,"params":par or []}).encode()
    for g in range(giri):
        for u in RPC:
            try:
                r=urllib.request.Request(u, data=corpo, headers={
                    "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r, timeout=30))
                if "result" in d: return d["result"]
            except Exception: pass
        time.sleep(0.5*(g+1))      # attesa crescente: i pubblici limitano
    return None
ult=chiama("eth_blockNumber")
if not ult: print("   nessun RPC risponde"); sys.exit(1)
ult=int(ult,16)
GIORNI=2; BL=GIORNI*7200
print(f"   Ethereum, blocco {ult} | finestra {BL} blocchi (~{GIORNI} giorni)")
tutti=[]; falliti=0; fin=0
b=ult-BL
while b < ult:
    fine=min(b+199, ult)       # finestre piu' corte: meno rifiuti
    r=chiama("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(fine),
                             "address":POOL,"topics":[LIQ]}])
    fin+=1
    if r is None: falliti+=1
    else: tutti+=r
    b=fine+1
    time.sleep(0.15)
print(f"   finestre {fin}, fallite {falliti} "
      f"({falliti/fin*100:.0f}% — se alta il conto e' sottostimato)")
print(f"   liquidazioni in {GIORNI} giorni: {len(tutti)}"
      f"   ({len(tutti)/GIORNI:.1f} al giorno)\n")
if not tutti: sys.exit(0)
chi=collections.Counter()
for x in tutti:
    d=x["data"][2:]
    if len(d)>=64*3: chi["0x"+d[64*2+24:64*3]]+=1
tot=sum(chi.values())
print(f"   {len(chi)} liquidatori diversi su {tot} liquidazioni")
for a,n in chi.most_common(10):
    print(f"      {a[:42]:<44}{n:>4}  {n/tot*100:>5.1f}%")
p=chi.most_common(1)[0][1]/tot*100
tre=sum(n for _,n in chi.most_common(3))/tot*100
print(f"\n   quota del primo {p:.0f}%   dei primi tre {tre:.0f}%")
