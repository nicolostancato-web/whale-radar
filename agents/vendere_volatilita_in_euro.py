"""Il premio di volatilita' convertito in EURO, con la coda.

Chi vende volatilita' incassa la differenza fra implicita e realizzata, ma
la incassa in modo NON lineare: il guadagno e' limitato al premio, la
perdita cresce col quadrato del movimento. E' la forma che ieri mi ha
ingannato sui debutti (vince spesso, perde tutto).

Approssimazione dichiarata: una posizione di varianza pura rende
  (IV^2 - RV^2) x nozionale / (2 x IV)   in percentuale del nozionale
che e' la resa standard di uno swap di varianza coperto. Non e' esatta per
uno straddle, ma e' la grandezza giusta e non lusinga: la non linearita'
c'e' tutta.
"""
import json, math, statistics as st
GIORNI=30; ORE=GIORNI*24
def realizzata(pr, ore, i, n):
    r=[]
    for j in range(i, i+n):
        a,b=ore[j], ore[j+1]
        if b-a != 3600000 or pr[a]<=0: return None
        r.append(math.log(pr[b]/pr[a]))
    if len(r)<n*0.9: return None
    return st.stdev(r)*math.sqrt(24*365)*100
for m in ("BTC","ETH"):
    iv={int(x["t"])//3600000*3600000: x["iv"] for x in json.load(open(f"data/volatilita/dvol_{m}.json"))}
    pr={int(x["t"]): x["c"] for x in json.load(open(f"data/volatilita/prezzo_{m}.json"))}
    ore=sorted(set(iv)&set(pr))
    res=[]; i=0
    while i+ORE+1 < len(ore):
        rv=realizzata(pr, ore, i, ORE)
        if rv is None: i+=1; continue
        im=iv[ore[i]]
        # resa in % del nozionale, per 30 giorni
        g=(im**2-rv**2)/(2*im)/100 * (GIORNI/365)
        res.append(g*100)
        i+=ORE
    res_ord=sorted(res)
    mm=st.mean(res); e=1.96*st.stdev(res)/math.sqrt(len(res))
    print(f"\n   {m}: {len(res)} finestre da 30 giorni")
    print(f"      resa media per finestra  {mm:+7.3f}% del nozionale  +/-{e:.3f}"
          f"   {'SOPRA ZERO' if mm-e>0 else 'non dimostrato'}")
    print(f"      mediana                  {st.median(res):+7.3f}%")
    print(f"      all'anno (12 finestre)   {mm*12:+7.2f}%")
    print(f"      vincenti {sum(1 for x in res if x>0)}/{len(res)}")
    for q,n in [(0.02,"2%"),(0.10,"10%"),(0.90,"90%"),(0.98,"98%")]:
        print(f"         percentile {n:>3}: {res_ord[int(q*(len(res_ord)-1))]:+8.3f}%")
    print(f"      PEGGIORE singola finestra: {min(res):+.3f}%")
    senza=st.mean(res_ord[1:])
    print(f"      togliendo la peggiore la media diventa {senza:+.3f}% "
          f"(era {mm:+.3f}%)")
    q=sum(1 for x in res if x<0)
    print(f"      quante finestre in perdita: {q}/{len(res)}")
