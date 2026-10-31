"""Le occasioni della zona grigia hanno una forma riconoscibile?

Se si concentrano su certe garanzie, c'e' un piano: configurare quelle.
Se sono sparse a caso, e' solo fortuna di chi passava di li', e non si
puo' costruire niente.

Tutto contato per ATTORE (creatore), non per contratto.
"""
import json, collections, datetime
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
CRE=json.load(open("data/liquidazioni/creatori.json"))
FAB={"0x4e59b44847b379578588920ca78fbf26c0b4956c",
     "0x0000000000ffe8b47b3e2130213b802212439497",
     "0x7a0d94f55792c434d74a40883c6ed8545e406d12"}
EUR=1/1.08
NOMI={"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"WETH",
 "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":"USDC",
 "0xdac17f958d2ee523a2206206994597c13d831ec7":"USDT",
 "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"WBTC",
 "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"wstETH",
 "0xae78736cd615f374d3085123a210448e74fc6393":"rETH",
 "0x9d39a5de30e57443bff2a8307a4256c8797a3497":"sUSDe",
 "0xa1290d69c65a6fe4df752f95823fae25cb99e5a7":"rsETH",
 "0x6b175474e89094c44da98b954eedeac495271d0f":"DAI",
 "0x514910771af9ca656af840dff83e8264ecf986ca":"LINK",
 "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9":"AAVE"}
def attore(a):
    c=CRE.get(a,{}).get("creatore")
    return c if (c and c not in FAB) else a
def valore(a,q):
    v=PR.get(a)
    return None if not v else q/10**v["decimali"]*v["prezzo_usd"]*EUR
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
fatte=len(json.load(open("data/liquidazioni/finestre_fatte_v2.json")))
giorni=60*fatte/88
occ=collections.defaultdict(lambda:{"prem":0.0,"liq":None,"gar":None,"ign":0})
for e in ev:
    d=e["dati"][2:]
    if len(d)<64*3: continue
    o=occ[e["tx"]]; o["liq"]="0x"+d[64*2+24:64*3]; o["gar"]=e["gar"]
    vg=valore(e["gar"], int(d[64:128],16)); vd=valore(e["deb"], int(d[0:64],16))
    if vg is None or vd is None: o["ign"]+=1
    else: o["prem"]+=vg-vd
val=[o for o in occ.values() if o["ign"]==0 and o["prem"]>0]
c=collections.Counter(attore(o["liq"]) for o in val)
pro={a for a,n in c.items() if n>=3}
print(f"   {giorni:.0f} giorni | {len(val)} occasioni | {len(c)} attori "
      f"({len(pro)} ricorrenti)\n")
g=collections.defaultdict(lambda:[0,0,0.0,0.0])
for o in val:
    k=NOMI.get(o["gar"], o["gar"][:10]+"..")
    g[k][0]+=1; g[k][2]+=o["prem"]
    if attore(o["liq"]) in pro: g[k][1]+=1; g[k][3]+=o["prem"]
print(f"   {'garanzia':<13}{'occ.':>6}{'% ai ricorrenti':>17}"
      f"{'valore tot':>13}{'valore NON presidiato':>23}")
for k,(n,p,v,vp) in sorted(g.items(), key=lambda x:-(x[1][2]-x[1][3])):
    print(f"   {k:<13}{n:>6}{p/n*100:>15.0f}%{v:>13,.0f}{v-vp:>23,.0f}")
tot_ng=sum(v-vp for _,(n,p,v,vp) in g.items())
print(f"\n   valore NON presidiato dai ricorrenti: {tot_ng:,.0f} EUR "
      f"= {tot_ng/giorni:,.0f} EUR/giorno")
print(f"   di cui sulle prime 3 garanzie: ", end="")
top=sorted(g.items(), key=lambda x:-(x[1][2]-x[1][3]))[:3]
print(f"{sum(v-vp for _,(n,p,v,vp) in top):,.0f} EUR "
      f"({sum(v-vp for _,(n,p,v,vp) in top)/max(tot_ng,1)*100:.0f}%)")
