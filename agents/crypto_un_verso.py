"""Le due famiglie crypto, rifatte A UN VERSO SOLO.

Col disegno a due versi la mediana era zero per identita' e l'asimmetria —
cioe' il vantaggio direzionale — veniva cancellata prima di guardarla.
Qui: solo LUNGO, contro lo stesso numero di entrate lunghe a tempi rimescolati.
Se la nuvola vera e' spostata, c'e' qualcosa che prima non potevo vedere.
"""
import json, glob, statistics as st, random, math
from collections import deque
random.seed(67)
FIN=(6,12,24,72)
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
dati=[]
for f in sorted(glob.glob("data/binance/*.json"))[:30]:
    d=json.load(open(f))
    if len(d)<3000: continue
    c=[x["c"] for x in d]; v=[x["v"] for x in d]
    dati.append((c,v,pre(c)))
print(f"{len(dati)} mercati | {sum(len(x[0]) for x in dati):,} ore\n")
PREZZO=[]
for L in FIN:
    PREZZO.append(lambda c,v,P,k,L=L: c[k]>P[L][0][k-1]); PREZZO.append(lambda c,v,P,k,L=L: c[k]<P[L][1][k-1])
    PREZZO.append(lambda c,v,P,k,L=L: c[k]>P[L][2][k-1]); PREZZO.append(lambda c,v,P,k,L=L: c[k]<P[L][2][k-1])
for q in (2,3,4):
    PREZZO.append(lambda c,v,P,k,q=q: all(c[k-i]>c[k-i-1] for i in range(q)))
    PREZZO.append(lambda c,v,P,k,q=q: all(c[k-i]<c[k-i-1] for i in range(q)))
def sogliafn(q,L):
    def f(c,v,P,k):
        if k<L: return False
        fin=sorted(v[k-L:k]); return v[k]>=fin[int(q*len(fin))-1]
    return f
ATTENZIONE=[sogliafn(q,L) for q in (0.80,0.90,0.95) for L in (200,500)]
def prova(regole, et):
    veri=[]; casi=[]
    for fn in regole:
        for o in (4,24):
            def es(mesc):
                tot=[]
                for c,v,P in dati:
                    idx=[k for k in range(500,len(c)-o) if fn(c,v,P,k)]
                    if not idx: continue
                    if mesc: idx=sorted(random.sample(range(500,len(c)-o), min(len(idx),len(c)-505-o)))
                    lib=0
                    for k in idx:
                        if k<lib: continue
                        tot.append(c[k+o]/c[k]-1); lib=k+o
                if len(tot)<300: return None
                sd=st.stdev(tot)
                return st.mean(tot)/(sd/math.sqrt(len(tot))) if sd>0 else None
            a=es(False); b=es(True)
            if a is not None and b is not None: veri.append(a); casi.append(b)
    if not veri: print(f"   {et}: nessuna prova"); return
    print(f"   {et} ({len(veri)} prove appaiate, solo LUNGO)")
    print(f"      vere        mediana {st.median(veri):+6.3f}   "
          f"[{min(veri):+6.2f},{max(veri):+6.2f}]")
    print(f"      rimescolate mediana {st.median(casi):+6.3f}   "
          f"[{min(casi):+6.2f},{max(casi):+6.2f}]")
    print(f"      DIFFERENZA  {st.median(veri)-st.median(casi):+6.3f}\n")
prova(PREZZO, "PATTERN DI PREZZO")
prova(ATTENZIONE, "ATTENZIONE (volume)")
