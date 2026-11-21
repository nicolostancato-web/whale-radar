"""Il centro e' spostato: ma quanto vale in euro?

Prima famiglia in cui la mediana si sposta (+0,47 contro 0,00 del caso) invece
di allargarsi soltanto. Un valore statistico pero' non si incassa: qui si
misura la RESA per ciclo, con e senza i costi, su tutte le 435 coppie messe
insieme — non scegliendone una, che sarebbe selezione.
Costo: 0,10% a giro (due gambe, chi prende il prezzo) e 0,089% (da maker, col
vantaggio misurato di 0,011%).
"""
import json, glob, os, statistics as st, math, itertools
S={}
for f in sorted(glob.glob("data/binance_hl/*.json")):
    d=json.load(open(f))
    if len(d)>3000: S[os.path.basename(f)[:-5]]={x["t"]:x["c"] for x in d}
ore=sorted(set.intersection(*[set(v) for v in S.values()]))
nomi=sorted(S); P={n:[S[n][t] for t in ore] for n in nomi}
coppie=list(itertools.combinations(nomi,2))
ORIZ=12; FIN=120
tutte=[]; per_coppia=[]
for a,b in coppie:
    ra=P[a]; rb=P[b]
    r=[ra[i]/rb[i] for i in range(len(ore))]
    v=[]; lib=0
    for k in range(FIN, len(r)-ORIZ):
        if k<lib: continue
        fin=r[k-FIN:k]; m=st.mean(fin); sd=st.stdev(fin)
        if sd<=0: continue
        z=(r[k]-m)/sd
        if abs(z)<2: continue
        seg=-1 if z>0 else 1
        v.append(seg*((ra[k+ORIZ]/ra[k]-1)-(rb[k+ORIZ]/rb[k]-1))); lib=k+ORIZ
    if len(v)>=25:
        tutte+=v; per_coppia.append(st.mean(v))
n=len(tutte); m=st.mean(tutte); e=1.96*st.stdev(tutte)/math.sqrt(n)
print(f"   {len(per_coppia)} coppie | {n:,} operazioni non sovrapposte\n")
print(f"   LORDO per operazione:            {m*100:+7.4f}% +/-{e*100:6.4f}")
for costo,et in ((0.0010,"prendendo il prezzo (0,100%)"),(0.00089,"mettendo l'ordine (0,089%)")):
    net=m-costo
    esito="SOPRA ZERO" if net-e>0 else ("positivo" if net>0 else "negativo")
    print(f"   netto {et:<30} {net*100:+7.4f}%   {esito}")
print(f"\n   coppie con media positiva: {sum(1 for x in per_coppia if x>0)}/{len(per_coppia)}")
print(f"   resa mediana fra le coppie: {st.median(per_coppia)*100:+.4f}%")
print(f"\n   NB: le 435 coppie NON sono indipendenti (30 mercati, ognuno in 29 coppie):")
print( "       l'intervallo qui sopra e' piu' stretto del vero.")
