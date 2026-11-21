"""Un importo senza la sua moneta non e' un numero.

Terzo errore della stessa famiglia in due giorni: sommare amount0 di tutti i
pool trattandolo come ether, mentre amount0 e' la PRIMA moneta della coppia,
che spesso e' un gettone qualunque. Risultato: un miliardo di ether in un'ora.
Qui si sommano SOLO i pool in cui la prima moneta e' davvero il nativo, e il
lato nativo e' quello che si conta.
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents")
from keccak import firma
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
NAT="0x"+"0"*40
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
# mappa pool -> (la prima moneta e' il nativo?), su una finestra larga
lato={}
for b in range(ult-ORA*8, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        c0="0x"+L["topics"][2][-40:]; c1="0x"+L["topics"][3][-40:]
        if c0==NAT: lato[L["topics"][1]]=0
        elif c1==NAT: lato[L["topics"][1]]=1
print(f"pool con un lato in ether, nati nelle ultime ~8 ore: {len(lato):,}")
vol=0.0; n=0; fuori=0
for b in range(ult-ORA, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        k=L["topics"][1]
        if k not in lato: fuori+=1; continue
        d=L["data"][2:]
        w = d[0:64] if lato[k]==0 else d[64:128]
        vol+=abs(s256(w))/1e18; n+=1
print(f"   in un'ora: {n:,} scambi contati, {fuori:,} ignorati (pool piu' vecchi)")
print(f"   volume sul lato ETHER: {vol:,.3f} ETH = {vol*ETH:,.0f} EUR/ora  ->  {vol*ETH*24:,.0f} EUR/giorno")
print("\n   quanto incassa chi sta dal lato del pedaggio, su questo flusso:")
for q,et in ((0.01,"1,00% (un locale tipo Pons)"),(0.003,"0,30%"),
             (0.0015,"0,15% (un'app che instrada)"),(0.0005,"0,05%")):
    print(f"      {et:<32} {vol*ETH*24*q:>10,.0f} EUR/giorno")
print(f"\n   e questa e' solo la parte NUOVA della chain ({len(lato):,} pool recenti):")
print(f"   il flusso sui pool piu' vecchi non e' contato ({fuori:,} scambi ignorati su {n+fuori:,}).")
