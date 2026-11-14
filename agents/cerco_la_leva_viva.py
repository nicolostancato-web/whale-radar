"""Quale pool a leva scambia DAVVERO, a mercato americano aperto?

Il pool trovato stanotte dall'elenco delle nascite e' fermo anche adesso: era
un omonimo morto. Si parte dall'altro verso — dai pool ATTIVI ORA — e si
guarda quali contengono un gettone a leva o un'azione tokenizzata.
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents")
from keccak import firma, keccak256
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
SWAP=firma("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)")
INIT=firma("Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)")
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def sel(s): return "0x"+keccak256(s.encode()).hex()[:8]
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
ult=int(rpc("eth_blockNumber",[]),16)
att=collections.Counter()
for b in range(ult-20000, ult, 2000):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":hex(min(b+1999,ult))}]) or []:
        att[L["topics"][1]]+=1
print(f"{sum(att.values()):,} scambi su {len(att)} pool nell'ultima mezz'ora")
# mappa pool -> monete, dalle nascite su una finestra larga
mon={}
for b in range(ult-4000000, ult, 12000):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+11999,ult))}]) or []:
        if L["topics"][1] in att:
            mon[L["topics"][1]]=("0x"+L["topics"][2][-40:], "0x"+L["topics"][3][-40:])
print(f"   di questi, {len(mon)} hanno una nascita nella finestra guardata")
nomi={}; trovati=[]
for pid,(a,b_) in mon.items():
    et=[]
    for t in (a,b_):
        if t=="0x"+"0"*40: et.append("ETH"); continue
        if t not in nomi: nomi[t]=testo(rpc("eth_call",[{"to":t,"data":sel("symbol()")},"latest"]))
        et.append(nomi[t])
    s=" ".join(et).upper()
    if any(k in s for k in ("X3L","X3S","X2L","X2S","NVDA","AAPL","TSLA","SPCX","MSTR","HOOD")):
        trovati.append((att[pid], pid, et[0], et[1]))
trovati.sort(reverse=True)
print(f"\n   pool su azioni/leva ATTIVI adesso: {len(trovati)}")
for n,pid,a,b_ in trovati[:10]:
    print(f"      {pid[:16]}…  {a}/{b_:<12} {n:>6} scambi in 30 min")
if not trovati:
    print("      nessuno: a mercato aperto, le azioni tokenizzate non scambiano")
    print("      sull'AMM nemmeno ora. La strada si chiude definitivamente.")
