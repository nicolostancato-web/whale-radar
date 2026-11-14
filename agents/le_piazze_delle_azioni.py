"""Le piazze VERE delle azioni tokenizzate: azione contro dollaro o contro ether.

Le azioni qui sono vere (emesse da Robinhood: NVDA, SPCX=SpaceX, ...), ma i
pool che le accoppiano a una monetina sono morti. Se il mestiere esiste, sta
nei pool azione/USDG o azione/ETH. Si misura: quanti sono, quanto scambiano,
con che commissione, e quanto e' profonda la liquidita'.
"""
import json, urllib.request, collections, statistics as st, datetime
RPC="https://rpc.mainnet.chain.robinhood.com"; GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
USDG="0x5fc5360d0400a0fd4f2af552add042d716f1d168"; NAT="0x"+"0"*40
WETH="0x0bd7d308f8e1639fab988df18a8011f41eacad73"
CONTRO={USDG:("USDG",6), NAT:("ETH",18), WETH:("WETH",18)}
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def call(to,d): return rpc("eth_call",[{"to":to,"data":d},"latest"])
def testo(h):
    if not h or len(h)<130: return "?"
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v

ult=int(rpc("eth_blockNumber",[]),16); FIN=400000; PASSO=2000   # ~10 ore
print(f"finestra ~{FIN*0.093/3600:.1f} ore\n")
pool={}
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        c0="0x"+L["topics"][2][-40:]; c1="0x"+L["topics"][3][-40:]
        if c0 in CONTRO or c1 in CONTRO:
            d=L["data"][2:]
            pool[L["topics"][1]]=(c0,c1,int(d[0:64],16))
sc=collections.Counter(); vol=collections.Counter()
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        k=L["topics"][1]
        if k in pool: sc[k]+=1; vol[k]+=abs(sg(L["data"][2:][0:64]))
nomi={}
righe=[]
for pid,(c0,c1,fee) in pool.items():
    if sc.get(pid,0) < 3: continue
    for c in (c0,c1):
        if c not in nomi: nomi[c]= "ETH" if c==NAT else (testo(call(c,"0x95d89b41")) or "?")
    base = c1 if c0 in CONTRO else c0
    nm = testo(call(base,"0x06fdde03")) if base not in CONTRO else ""
    azione = "Robinhood Token" in (nm or "")
    righe.append((sc[pid], nomi[c0], nomi[c1], fee, azione, pid))
righe.sort(reverse=True)
print(f"pool contro USDG/ETH con almeno 3 scambi: {len(righe)}")
print(f"   di cui su AZIONI vere: {sum(1 for r in righe if r[4])}\n")
print("   scambi  coppia                 fee       azione vera?")
for n,n0,n1,fee,az,pid in righe[:14]:
    et="dinamica" if fee==0x800000 else f"{fee/10000:.2f}%"
    print(f"   {n:>6}  {n0:>8}/{n1:<12} {et:>9}   {'SI' if az else 'no'}")
