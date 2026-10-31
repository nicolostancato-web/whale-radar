"""Dove NON stanno guardando i professionisti?

Non si vince una gara di velocita' contro venti bot con nodi dedicati. Ma
«non si vince dove tutti corrono» non e' «non si vince»: si cerca una fetta
dove i ricorrenti sono assenti.

Si classifica il vincitore di ogni occasione: RICORRENTE (3+ occasioni) o
OCCASIONALE. Poi si incrocia con asset, protocollo e ora del giorno.
Dove vincono gli occasionali, i mestieranti non ci sono.
"""
import json, collections, datetime, statistics as st
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
EUR=1/1.08
def valore(a,q):
    v=PR.get(a)
    return None if not v else q/10**v["decimali"]*v["prezzo_usd"]*EUR
NOMI={"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"WETH",
 "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":"USDC",
 "0xdac17f958d2ee523a2206206994597c13d831ec7":"USDT",
 "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"WBTC",
 "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"wstETH",
 "0xae78736cd615f374d3085123a210448e74fc6393":"rETH",
 "0x6b175474e89094c44da98b954eedeac495271d0f":"DAI",
 "0x83f20f44975d03b1b09e64809b757c47f942beea":"sDAI",
 "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"cbBTC",
 "0x514910771af9ca656af840dff83e8264ecf986ca":"LINK",
 "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9":"AAVE"}
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
occ=collections.defaultdict(lambda:{"prem":0.0,"liq":None,"gar":None,
                                    "prot":None,"ora":0,"ign":0})
for e in ev:
    d=e["dati"][2:]
    if len(d)<64*3: continue
    o=occ[e["tx"]]
    o["liq"]="0x"+d[64*2+24:64*3]; o["gar"]=e["gar"]; o["prot"]=e["prot"]
    o["ora"]=e["ora"]
    vg=valore(e["gar"], int(d[64:128],16)); vd=valore(e["deb"], int(d[0:64],16))
    if vg is None or vd is None: o["ign"]+=1
    else: o["prem"]+=vg-vd
c=collections.Counter(o["liq"] for o in occ.values() if o["liq"])
pro={a for a,n in c.items() if n>=3}
print(f"   {len(c)} liquidatori: {len(pro)} ricorrenti (3+), "
      f"{len(c)-len(pro)} occasionali\n")
val=[o for o in occ.values() if o["ign"]==0 and o["prem"]>=100]
print(f"   {len(val)} occasioni sopra 100 EUR\n")
def tab(chiave, nome, estrai):
    print(f"   per {nome}:")
    g=collections.defaultdict(lambda:[0,0,0.0])
    for o in val:
        k=estrai(o)
        g[k][0]+=1
        if o["liq"] in pro: g[k][1]+=1
        g[k][2]+=o["prem"]
    print(f"      {'fetta':<14}{'occasioni':>10}{'vinte da pro':>14}{'valore EUR':>14}")
    for k,(n,p,v) in sorted(g.items(), key=lambda x:-x[1][2]):
        print(f"      {str(k):<14}{n:>10}{p:>9} ({p/n*100:>3.0f}%){v:>14,.0f}")
    print()
tab(None,"garanzia", lambda o: NOMI.get(o["gar"], o["gar"][:10]+".."))
tab(None,"protocollo", lambda o: o["prot"])
tab(None,"ora UTC (fascia)",
    lambda o: f"{datetime.datetime.fromtimestamp(o['ora'],datetime.UTC).hour//6*6:02d}-"
              f"{datetime.datetime.fromtimestamp(o['ora'],datetime.UTC).hour//6*6+5:02d}")
