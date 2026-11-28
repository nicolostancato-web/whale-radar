"""Un VERSO SOLO: l'unico modo di vedere un vantaggio direzionale.

Limite del disegno precedente (segnalato da Astra e confermato): includendo
lungo e corto sulle stesse entrate, ogni valore positivo ha il gemello negativo
per costruzione. La mediana esce +0,00 su tutti i mercati perche' e'
un'identita', non un risultato — e l'asimmetria viene cancellata prima di
guardarla.

Qui si prende il solo verso LUNGO e lo si confronta con lo stesso numero di
entrate lunghe a tempi rimescolati. Se la nuvola vera e' spostata rispetto a
quella finta, c'e' un vantaggio direzionale.
"""
import json, glob, os, statistics as st, random, math
from collections import deque
random.seed(61)
FIN=(6,12,24,72)
NOMI={"GC":"oro","HG":"rame","SI":"argento","PL":"platino","PA":"palladio","ALI":"alluminio",
      "CL":"petrolio","NG":"gas","HO":"gasolio","RB":"benzina","ZW":"grano","ZC":"mais",
      "ZS":"soia","CT":"cotone","SB":"zucchero","KC":"caffe","CC":"cacao","LE":"bovini",
      "EURUSD":"EUR/USD"}
def pre(c):
    n=len(c); P={}
    for L in FIN:
        mx=[0.0]*n; mn=[0.0]*n; md=[0.0]*n; s=0.0; A=deque(); B=deque()
        for i in range(n):
            s+=c[i]
            if i>=L: s-=c[i-L]
            md[i]=s/min(i+1,L)
            while A and c[A[-1]]<=c[i]: A.pop()
            A.append(i)
            while A[0]<=i-L: A.popleft()
            mx[i]=c[A[0]]
            while B and c[B[-1]]>=c[i]: B.pop()
            B.append(i)
            while B[0]<=i-L: B.popleft()
            mn[i]=c[B[0]]
        P[L]=(mx,mn,md)
    return P
R=[]
for L in FIN:
    R.append(lambda c,P,k,L=L: c[k]>P[L][0][k-1]); R.append(lambda c,P,k,L=L: c[k]<P[L][1][k-1])
    R.append(lambda c,P,k,L=L: c[k]>P[L][2][k-1]); R.append(lambda c,P,k,L=L: c[k]<P[L][2][k-1])
for q in (2,3,4):
    R.append(lambda c,P,k,q=q: all(c[k-i]>c[k-i-1] for i in range(q)))
    R.append(lambda c,P,k,q=q: all(c[k-i]<c[k-i-1] for i in range(q)))
print("   mercato      prove   VERE (mediana)   RIMESCOLATE   differenza")
tot_v=[]; tot_c=[]
for f in sorted(glob.glob("data/mercati/*_1h.json")):
    sig=os.path.basename(f).replace("_1h.json","").replace("_X","").replace("_F","")
    c=[x for x in json.load(open(f))["c"] if x]
    if len(c)<3000: continue
    P=pre(c); veri=[]; casi=[]
    for fn in R:
        for o in (4,24):
            def es(mesc):
                idx=[k for k in range(200,len(c)-o) if fn(c,P,k)]
                if not idx: return None
                if mesc: idx=sorted(random.sample(range(200,len(c)-o), min(len(idx),len(c)-205-o)))
                v=[]; lib=0
                for k in idx:
                    if k<lib: continue
                    v.append(c[k+o]/c[k]-1); lib=k+o      # SOLO LUNGO
                if len(v)<150: return None
                sd=st.stdev(v)
                return st.mean(v)/(sd/math.sqrt(len(v))) if sd>0 else None
            a=es(False); b=es(True)
            if a is not None and b is not None: veri.append(a); casi.append(b)
    if len(veri)<10: continue
    tot_v+=veri; tot_c+=casi
    print(f"   {NOMI.get(sig,sig):<12} {len(veri):>4}   {st.median(veri):+8.2f}     "
          f"{st.median(casi):+8.2f}     {st.median(veri)-st.median(casi):+8.2f}")
if tot_v:
    print(f"\n   TUTTI I MERCATI INSIEME ({len(tot_v)} prove):")
    print(f"      vere        mediana {st.median(tot_v):+.3f}")
    print(f"      rimescolate mediana {st.median(tot_c):+.3f}")
    print(f"      differenza  {st.median(tot_v)-st.median(tot_c):+.3f}")
