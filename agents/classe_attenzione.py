"""La CLASSE dell'attenzione, non il singolo candidato.

Stessa prova della classe dei pattern: si generano sistematicamente le regole
basate su volume e numero di operazioni, e ognuna si confronta con gli STESSI
segnali a tempi rimescolati. Se il centro coincide, la famiglia e' vuota e il
candidato di oggi era un estremo della coda, non una scoperta.
Senza costo: la statistica deve misurare il segnale.
"""
import json, glob, statistics as st, random, math
from collections import deque
random.seed(37)
dati=[]
for f in sorted(glob.glob("data/binance/*.json"))[:30]:
    d=json.load(open(f))
    if len(d)<3000: continue
    c=[x["c"] for x in d]; n=len(d)
    pre={}
    for campo in ("v","n"):
        s=[x[campo] for x in d]
        for L in (200,500):
            # percentile mobile approssimato: si usa la finestra ordinata ogni 50 passi
            sog={}
            for q in (0.80,0.90,0.95,0.99):
                v=[0.0]*n; ultimo=None
                for i in range(n):
                    if i<L: v[i]=float("inf"); continue
                    if ultimo is None or i%50==0:
                        fin=sorted(s[i-L:i]); ultimo=fin
                    v[i]=ultimo[int(q*len(ultimo))-1]
                sog[q]=v
            pre[(campo,L)]=sog
    dati.append((c,[x["v"] for x in d],[x["n"] for x in d],pre,n))
print(f"{len(dati)} mercati | {sum(x[4] for x in dati):,} ore")
REG=[]
for campo in ("v","n"):
    for L in (200,500):
        for q in (0.80,0.90,0.95,0.99):
            REG.append((f"{campo} q{int(q*100)} L{L}", campo, L, q))
print(f"{len(REG)} regole x 2 versi x 3 orizzonti = {len(REG)*6} prove\n")
def esegui(campo,L,q,verso,oriz,mescola):
    v=[]
    for c,vol,num,pre,n in dati:
        s = vol if campo=="v" else num
        sog=pre[(campo,L)][q]
        idx=[k for k in range(L+5,n-oriz) if s[k]>=sog[k]]
        if len(idx)<20: continue
        if mescola: idx=random.sample(range(L+5,n-oriz), min(len(idx), n-L-10-oriz))
        lib=0
        for k in idx:
            if k<lib: continue
            dire = 1 if c[k]>c[k-1] else -1
            seg = -dire if verso=="contrasta" else dire
            v.append(seg*(c[k+oriz]/c[k]-1)); lib=k+oriz
    if len(v)<200: return None
    return st.mean(v)/(st.stdev(v)/math.sqrt(len(v)))
veri=[]; casi=[]
for nome,campo,L,q in REG:
    for verso in ("contrasta","segui"):
        for oriz in (2,4,12):
            a=esegui(campo,L,q,verso,oriz,False); b=esegui(campo,L,q,verso,oriz,True)
            if a is not None and b is not None: veri.append(a); casi.append(b)
def riass(et,x):
    x=sorted(x)
    print(f"   {et:<24} n={len(x):<4} mediana {st.median(x):+6.2f}  "
          f"5%={x[max(0,len(x)//20)]:+6.2f}  95%={x[min(len(x)-1,19*len(x)//20)]:+6.2f}  "
          f"estremi |t|>2: {sum(1 for v in x if abs(v)>2)}")
riass("REGOLE VERE", veri); riass("segnali rimescolati", casi)
