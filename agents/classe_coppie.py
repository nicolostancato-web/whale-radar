"""La CLASSE delle coppie, non dieci coppie scelte a mano.

La famiglia era chiusa provandone dieci su dati sottili. Con 30 mercati le
coppie sono 435: si provano tutte e si confronta la DISTRIBUZIONE con quella
degli stessi segnali a tempi rimescolati.
Senza costo nella statistica (misura il segnale); osservazioni non
sovrapposte; soglia relativa alla coppia.
"""
import json, glob, os, statistics as st, math, random, itertools
random.seed(43)
S={}
for f in sorted(glob.glob("data/binance_hl/*.json")):
    d=json.load(open(f))
    if len(d)>3000: S[os.path.basename(f)[:-5]]={x["t"]:x["c"] for x in d}
ore=sorted(set.intersection(*[set(v) for v in S.values()]))
nomi=sorted(S); P={n:[S[n][t] for t in ore] for n in nomi}
coppie=list(itertools.combinations(nomi,2))
print(f"{len(nomi)} mercati | {len(ore):,} ore | {len(coppie)} coppie\n")
ORIZ=12; FIN=120
def prova(a,b,mescola):
    ra=P[a]; rb=P[b]
    r=[ra[i]/rb[i] for i in range(len(ore))]
    v=[]; lib=0
    cand=[]
    for k in range(FIN, len(r)-ORIZ):
        fin=r[k-FIN:k]
        m=st.mean(fin); sd=st.stdev(fin)
        if sd<=0: continue
        z=(r[k]-m)/sd
        if abs(z)<2: continue
        cand.append((k, -1 if z>0 else 1))
    if len(cand)<30: return None
    if mescola:
        ks=random.sample(range(FIN,len(r)-ORIZ), len(cand))
        cand=[(k, random.choice((-1,1))) for k in sorted(ks)]
    for k,seg in cand:
        if k<lib: continue
        v.append(seg*((ra[k+ORIZ]/ra[k]-1)-(rb[k+ORIZ]/rb[k]-1))); lib=k+ORIZ
    if len(v)<25: return None
    sd=st.stdev(v)
    if sd<=0: return None
    return st.mean(v)/(sd/math.sqrt(len(v)))
veri=[]; casi=[]
for a,b in coppie:
    x=prova(a,b,False); y=prova(a,b,True)
    if x is not None and y is not None: veri.append(x); casi.append(y)
def riass(et,x):
    x=sorted(x)
    print(f"   {et:<24} n={len(x):<4} mediana {st.median(x):+6.2f}  "
          f"5%={x[max(0,len(x)//20)]:+6.2f}  95%={x[min(len(x)-1,19*len(x)//20)]:+6.2f}  "
          f"estremi |t|>2: {sum(1 for v in x if abs(v)>2)}")
riass("COPPIE VERE", veri); riass("segnali rimescolati", casi)
if veri:
    print(f"\n   positive: {sum(1 for v in veri if v>0)}/{len(veri)}   "
          f"(il caso ne darebbe circa {len(veri)//2})")
