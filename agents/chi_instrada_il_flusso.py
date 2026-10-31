"""Chi instrada il flusso oggi su questa chain?

Per sapere cosa serve a prendersi lo 0,2% del flusso, prima bisogna sapere di
chi e'. Nello Swap v4 il campo `sender` e' il contratto che ha chiamato il
gestore: di solito il router di un'applicazione, non il portafoglio umano.
Se tre contratti fanno il 95%, entrare vuol dire toglierlo a loro. Se la coda
e' lunga, esiste una nicchia.
Si misura ANCHE il volume per router, non solo il numero di scambi: dieci
scambi da mille euro contano piu' di mille da dieci.
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents")
from keccak import firma
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"; NAT="0x"+"0"*40
SWAP=firma("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)")
INIT=firma("Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)")
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def s256(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ETH=3030.0
ult=int(rpc("eth_blockNumber",[]),16); ORA=int(3600/0.093); PASSO=2000
lato={}
for b in range(ult-ORA*8, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        c0="0x"+L["topics"][2][-40:]; c1="0x"+L["topics"][3][-40:]
        if c0==NAT: lato[L["topics"][1]]=0
        elif c1==NAT: lato[L["topics"][1]]=1
n=collections.Counter(); vol=collections.Counter(); tot=0.0
for b in range(ult-ORA, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        k=L["topics"][1]
        if k not in lato: continue
        mitt="0x"+L["topics"][2][-40:]
        d=L["data"][2:]; w=d[0:64] if lato[k]==0 else d[64:128]
        v=abs(s256(w))/1e18*ETH
        n[mitt]+=1; vol[mitt]+=v; tot+=v
print(f"un'ora | {sum(n.values()):,} scambi su pool con un lato in ether | volume {tot:,.0f} EUR\n")
print(f"   contratti che instradano: {len(n)}")
print("   contratto                   scambi      volume(EUR)   quota   e' un contratto?")
for a,v in vol.most_common(8):
    code=rpc("eth_getCode",[a,"latest"])
    c = "si" if code and len(code)>4 else "NO (portafoglio)"
    print(f"   {a[:22]}…  {n[a]:>7}  {v:>14,.0f}  {v/tot:>6.1%}   {c}")
q3=sum(v for _,v in vol.most_common(3))/max(tot,1)
print(f"\n   quota dei primi 3: {q3:.1%}")
print(f"   quanti ne servono per fare il 90% del volume: ", end="")
acc=0; k=0
for _a,v in vol.most_common():
    acc+=v; k+=1
    if acc/tot>=0.9: break
print(k)
print("   -> " + ("pochi padroni: entrare vuol dire togliere a loro" if q3>0.8 else
      "coda lunga: una nicchia esiste"))
