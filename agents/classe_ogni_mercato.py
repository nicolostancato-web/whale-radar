"""La prova della classe su OGNI mercato tradizionale, singolarmente.

Fatta per l'EUR/USD su richiesta; qui si estende agli altri 18 per non lasciare
chiusure superficiali in giro. Per ciascuno: ~88 prove appaiate con gli stessi
segnali a tempi rimescolati, candele orarie.
Si guarda se il centro si sposta (vantaggio) o se solo le code si allargano
(macchina di falsi positivi) o se nulla si muove (mercato piatto).
"""
import json, glob, os, statistics as st, random, math
from collections import deque
random.seed(59)
FIN=(6,12,24,72)
NOMI={"GC":"oro","HG":"rame","SI":"argento","PL":"platino","PA":"palladio",
      "ALI":"alluminio","CL":"petrolio","NG":"gas","HO":"gasolio","RB":"benzina",
      "ZW":"grano","ZC":"mais","ZS":"soia","CT":"cotone","SB":"zucchero",
      "KC":"caffe","CC":"cacao","LE":"bovini","EURUSD":"EUR/USD"}
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
print("   mercato      prove   REGOLE VERE (med, code, estremi)   RIMESCOLATE")
for f in sorted(glob.glob("data/mercati/*_1h.json")):
    sig=os.path.basename(f).replace("_1h.json","").replace("_X","").replace("_F","")
    c=[x for x in json.load(open(f))["c"] if x]
    if len(c)<3000: continue
    P=pre(c); veri=[]; casi=[]
    for fn in R:
        for s in (1,-1):
            for o in (4,24):
                def es(mesc):
                    idx=[k for k in range(200,len(c)-o) if fn(c,P,k)]
                    if not idx: return None
                    if mesc: idx=sorted(random.sample(range(200,len(c)-o), min(len(idx),len(c)-205-o)))
                    v=[]; lib=0
                    for k in idx:
                        if k<lib: continue
                        v.append(s*(c[k+o]/c[k]-1)); lib=k+o
                    if len(v)<150: return None
                    sd=st.stdev(v)
                    return st.mean(v)/(sd/math.sqrt(len(v))) if sd>0 else None
                a=es(False); b=es(True)
                if a is not None and b is not None: veri.append(a); casi.append(b)
    if len(veri)<20: continue
    veri.sort(); casi.sort()
    ev=sum(1 for x in veri if abs(x)>2); ec=sum(1 for x in casi if abs(x)>2)
    print(f"   {NOMI.get(sig,sig):<12} {len(veri):>4}   {st.median(veri):+5.2f}  "
          f"[{veri[len(veri)//20]:+5.2f},{veri[19*len(veri)//20]:+5.2f}]  {ev:>3}      "
          f"{st.median(casi):+5.2f}  [{casi[len(casi)//20]:+5.2f},{casi[19*len(casi)//20]:+5.2f}]  {ec}")
