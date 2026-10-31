"""Quanto paga UNA liquidazione, in euro.

Si valutano solo le liquidazioni la cui garanzia e' in una moneta di cui
conosco decimali e prezzo (WETH, USDC, USDT, DAI, WBTC, cbBTC). Le altre
si contano a parte come non valutabili: mai sommate come zero.
Il premio di Aave e' una percentuale della garanzia presa: qui si riporta
la garanzia, e il premio tipico dichiarato (5-10%) come intervallo.
"""
import sys, json, time, urllib.request, collections
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
RPC=["https://eth.llamarpc.com","https://ethereum-rpc.publicnode.com",
     "https://rpc.ankr.com/eth","https://cloudflare-eth.com"]
def chiama(m,p=None,giri=8):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        for u in RPC:
            try:
                r=urllib.request.Request(u,data=c,headers={
                  "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=30))
                if "result" in d: return d["result"]
            except Exception: pass
        time.sleep(0.5*(g+1))
    return None
# prezzi: solo monete note. ETH e BTC dal prezzo spot pubblico, gratis.
def spot(s):
    try:
        r=urllib.request.Request(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}",
                                 headers={"user-agent":"Mozilla/5.0"})
        return float(json.load(urllib.request.urlopen(r,timeout=20))["price"])
    except Exception: return None
eth=spot("ETHUSDT"); btc=spot("BTCUSDT")
if not eth or not btc: print("   manca un prezzo: non procedo"); sys.exit(1)
EUR=1/1.08
NOTE={
 "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": ("WETH",18,eth),
 "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": ("USDC",6,1.0),
 "0xdac17f958d2ee523a2206206994597c13d831ec7": ("USDT",6,1.0),
 "0x6b175474e89094c44da98b954eedeac495271d0f": ("DAI",18,1.0),
 "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": ("WBTC",8,btc),
 "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf": ("cbBTC",8,btc),
}
ult=int(chiama("eth_blockNumber"),16)
ev=[]; fal=0; fin=0
b=ult-7200*3
while b<ult:
    f=min(b+199,ult)
    r=chiama("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(f),
                             "address":POOL,"topics":[LIQ]}])
    fin+=1
    if r is None: fal+=1
    else: ev+=r
    b=f+1; time.sleep(0.12)
print(f"   finestre {fin}, fallite {fal} ({fal/fin*100:.0f}%)")
print(f"   liquidazioni lette: {len(ev)}\n")
val=[]; nonval=collections.Counter()
for x in ev:
    gar="0x"+x["topics"][1][-40:]
    d=x["data"][2:]
    if len(d)<64*2: continue
    q=int(d[64:128],16)
    if gar in NOTE:
        n,dec,pz=NOTE[gar]
        val.append((n, q/10**dec*pz*EUR))
    else:
        nonval[gar]+=1
if val:
    val.sort(key=lambda x:-x[1])
    tot=sum(v for _,v in val)
    print(f"   {len(val)} valutabili, {sum(nonval.values())} no")
    for n,v in val[:8]:
        print(f"      garanzia presa {n:<6}{v:>12,.0f} EUR")
    print(f"\n   totale garanzia presa in 3 giorni: {tot:,.0f} EUR")
    print(f"   premio del liquidatore al 5-10%: "
          f"{tot*0.05:,.0f} - {tot*0.10:,.0f} EUR in 3 giorni")
    print(f"   AL GIORNO, per TUTTI i liquidatori del mondo: "
          f"{tot*0.05/3:,.0f} - {tot*0.10/3:,.0f} EUR")
else:
    print("   nessuna liquidazione valutabile in questa finestra")
    print(f"   non valutabili: {dict(nonval)}")
