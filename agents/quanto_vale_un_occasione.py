"""Quanto vale UNA occasione, in euro, contando per transazione.

Una transazione puo' liquidare piu' posizioni: il guadagno e' la somma delle
garanzie prese in QUELLA transazione, non di una sola posizione.
Si valutano solo le monete di cui conosco decimali e prezzo; le altre si
contano a parte, mai come zero.
"""
import json, time, urllib.request, sys, os, collections, statistics as st
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
def spot(s):
    r=urllib.request.Request(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}",
                             headers={"user-agent":"Mozilla/5.0"})
    return float(json.load(urllib.request.urlopen(r,timeout=20))["price"])
eth=spot("ETHUSDT"); btc=spot("BTCUSDT"); EUR=1/1.08
NOTE={"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":("WETH",18,eth),
      "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":("USDC",6,1.0),
      "0xdac17f958d2ee523a2206206994597c13d831ec7":("USDT",6,1.0),
      "0x6b175474e89094c44da98b954eedeac495271d0f":("DAI",18,1.0),
      "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":("WBTC",8,btc),
      "0x83f20f44975d03b1b09e64809b757c47f942beea":("sDAI",18,1.0),
      "0xae78736cd615f374d3085123a210448e74fc6393":("rETH",18,eth),
      "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":("wstETH",18,eth)}
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
ev=[json.loads(x) for x in open("data/liquidazioni/eventi.jsonl")]
pertx=collections.defaultdict(list)
for e in ev: pertx[e["tx"]].append(e)
print(f"   {len(ev)} eventi in {len(pertx)} occasioni\n")
valori=[]; ign=collections.Counter()
for tx, lista in pertx.items():
    bn=lista[0]["blocco"]
    r=chiama("eth_getTransactionReceipt",[tx])
    if not r: print(f"   {tx[:14]}: ricevuta non ottenuta"); continue
    tot=0.0; pezzi=[]
    for L in r.get("logs",[]):
        if not L.get("topics") or L["topics"][0]!=LIQ: continue
        gar="0x"+L["topics"][1][-40:]
        d=L["data"][2:]
        if len(d)<128: continue
        q=int(d[64:128],16)
        if gar in NOTE:
            n,dec,pz=NOTE[gar]; v=q/10**dec*pz*EUR; tot+=v; pezzi.append((n,v))
        else: ign[gar]+=1
    gas=int(r["gasUsed"],16)*int(r.get("effectiveGasPrice","0x0"),16)/1e18*eth*EUR
    if tot>0:
        valori.append((tx, tot, tot*0.05-gas, len(pezzi)))
        print(f"   {tx[:14]}  {len(pezzi)} posizioni  garanzia {tot:>11,.0f} EUR")
        print(f"      premio 5% {tot*0.05:>9,.2f}  gas {gas:>6,.2f}  "
              f"NETTO {tot*0.05-gas:>+10,.2f} EUR")
if valori:
    v=sorted(x[2] for x in valori)
    print(f"\n   {len(valori)} occasioni valutabili"
          f"{', ' + str(sum(ign.values())) + ' posizioni in monete ignote' if ign else ''}")
    print(f"   netto per occasione: mediana {st.median(v):,.2f} EUR   "
          f"massimo {max(v):,.2f}   minimo {min(v):,.2f}")
    print(f"   somma {sum(v):,.2f} EUR su {len(valori)} occasioni")
