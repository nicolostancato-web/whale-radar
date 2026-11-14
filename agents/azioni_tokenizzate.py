"""DECIMA STRADA: le azioni tokenizzate a borsa chiusa.

Perche' questa e' diversa dalle nove precedenti: non poggia su un pattern che
puo' svanire, poggia su un OROLOGIO. La borsa americana chiude alle 16:00 ET;
il token continua a scambiare tutta la notte. Chi compra NVDA alle 3 di notte
paga uno spread largo perche' il sottostante e' fermo e nessuno puo' coprirsi.

Primo passo, puramente descrittivo: quali azioni esistono qui, quanto
scambiano, con che commissione, e quanto sono profonde. Senza numeri su questo
non ha senso parlare di strategia.
"""
import json, urllib.request, collections, statistics as st, datetime
RPC="https://rpc.mainnet.chain.robinhood.com"; GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def call(to,dato): return rpc("eth_call",[{"to":to,"data":dato},"latest"])
def testo(h):
    if not h or len(h)<130: return None
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return None
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v

ora=datetime.datetime.now(datetime.UTC)
print(f"adesso {ora:%H:%M} UTC — la borsa USA e' aperta 13:30-20:00 UTC: "
      f"{'APERTA' if 13.5 <= ora.hour+ora.minute/60 < 20 and ora.weekday()<5 else 'CHIUSA'}\n")
ult=int(rpc("eth_blockNumber",[]),16); FIN=100000; PASSO=1000
pool={}
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        d=L["data"][2:]
        pool[L["topics"][1]]=("0x"+L["topics"][2][-40:], "0x"+L["topics"][3][-40:],
                              int(d[0:64],16), "0x"+d[128+24:192])
scambi=collections.Counter(); vol=collections.Counter()
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        k=L["topics"][1]; scambi[k]+=1
        vol[k]+=abs(sg(L["data"][2:][0:64]))/1e18
nomi={}
for pid,(c0,c1,fee,hook) in pool.items():
    for c in (c0,c1):
        if c not in nomi and c!="0x"+"0"*40:
            nomi[c]=testo(call(c,"0x95d89b41")) or "?"
print(f"pool esaminati: {len(pool)} in ~{FIN*0.093/3600:.1f} ore")
AZ={"NVDA","TSLA","AAPL","MSFT","AMZN","META","GOOGL","SPY","QQQ","COIN","HOOD","AMD","SPCX","MSTR","PLTR"}
tro=[(pid,p) for pid,p in pool.items() if (nomi.get(p[0],"") in AZ or nomi.get(p[1],"") in AZ)]
print(f"pool su AZIONI tokenizzate: {len(tro)}\n")
print("   coppia                 fee     scambi   volume(ETH)")
for pid,(c0,c1,fee,hook) in sorted(tro, key=lambda x:-scambi.get(x[0],0))[:12]:
    n0="ETH" if c0=="0x"+"0"*40 else nomi.get(c0,"?"); n1=nomi.get(c1,"?")
    et="dinamica" if fee==0x800000 else f"{fee/10000:.2f}%"
    print(f"   {n0:>8}/{n1:<10} {et:>9}  {scambi.get(pid,0):>7}  {vol.get(pid,0):>10.3f}")
if not tro:
    print("   nessuna in questa finestra. Simboli visti piu' spesso:")
    for s,n in collections.Counter(nomi.values()).most_common(12): print(f"      {s}  {n}")
