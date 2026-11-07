"""Quanto vale, al giorno, la parte NON presidiata dai professionisti?

E' il tetto di cio' che un nuovo entrante sistematico potrebbe contendere:
non il mercato intero (quello e' dei bot veloci), ma la parte che oggi se
la prendono indirizzi che appaiono una o due volte.

Un occasionale che vince una volta non sta presidiando niente: quella e'
proprio la parte dove basterebbe esserci sempre.
"""
import json, collections, statistics as st
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
EUR=1/1.08
def valore(a,q):
    v=PR.get(a)
    return None if not v else q/10**v["decimali"]*v["prezzo_usd"]*EUR
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
fatte=len(json.load(open("data/liquidazioni/finestre_fatte_v2.json")))
giorni=60*fatte/88
occ=collections.defaultdict(lambda:{"prem":0.0,"liq":None,"ign":0})
for e in ev:
    d=e["dati"][2:]
    if len(d)<64*3: continue
    o=occ[e["tx"]]; o["liq"]="0x"+d[64*2+24:64*3]
    vg=valore(e["gar"], int(d[64:128],16)); vd=valore(e["deb"], int(d[0:64],16))
    if vg is None or vd is None: o["ign"]+=1
    else: o["prem"]+=vg-vd
c=collections.Counter(o["liq"] for o in occ.values() if o["liq"])
val=[o for o in occ.values() if o["ign"]==0 and o["prem"]>0]
print(f"   copertura {fatte}/88 = {giorni:.1f} giorni | {len(val)} occasioni positive\n")
for soglia in (2,3,5):
    pro={a for a,n in c.items() if n>=soglia}
    vp=sum(o["prem"] for o in val if o["liq"] in pro)
    vo=sum(o["prem"] for o in val if o["liq"] not in pro)
    no=len([o for o in val if o["liq"] not in pro])
    print(f"   «professionista» = {soglia}+ occasioni  ({len(pro)} indirizzi)")
    print(f"      valore ai professionisti  {vp:>11,.0f} EUR  "
          f"({vp/(vp+vo)*100:>4.0f}%)  = {vp/giorni:>8,.0f} EUR/giorno")
    print(f"      valore agli occasionali   {vo:>11,.0f} EUR  "
          f"({vo/(vp+vo)*100:>4.0f}%)  = {vo/giorni:>8,.0f} EUR/giorno")
    print(f"      occasioni prese da occasionali: {no}, "
          f"{no/giorni:.2f} al giorno\n")
occ_sole=[o for o in val if c[o["liq"]]==1]
print(f"   vinte da chi appare UNA SOLA VOLTA: {len(occ_sole)} occasioni, "
      f"{sum(o['prem'] for o in occ_sole):,.0f} EUR "
      f"({sum(o['prem'] for o in occ_sole)/giorni:,.0f} EUR/giorno)")
g=sorted((o["prem"] for o in occ_sole), reverse=True)[:6]
print(f"   le maggiori fra queste: " + ", ".join(f"{x:,.0f}" for x in g))
