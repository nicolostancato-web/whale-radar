"""La prova della CLASSE sul solo EUR/USD, su tre frequenze.

Il 25/10 l'avevo chiuso con SEI regole, e la prova della classe l'avevo poi
fatta sulle crypto estendendone la conclusione senza rifarla qui. Rimedio.

Ogni regola si confronta con gli STESSI segnali a tempi rimescolati. Nessun
costo nella statistica: deve misurare il segnale, non quante volte un costo
fisso sta dentro l'errore.
"""
import json, statistics as st, random, math
from collections import deque
random.seed(53)
def serie(f, campo="c"):
    D=json.load(open(f)); return [x for x in D[campo] if x]
def pre(c, fin):
    n=len(c); P={}
    for L in fin:
        mx=[0.0]*n; mn=[0.0]*n; md=[0.0]*n; s=0.0
        A=deque(); B=deque()
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
FIN=(6,12,24,72)
def regole():
    R=[]
    for L in FIN:
        R.append((f"rottura max {L}", lambda c,P,k,L=L: c[k]>P[L][0][k-1]))
        R.append((f"rottura min {L}", lambda c,P,k,L=L: c[k]<P[L][1][k-1]))
        R.append((f"sopra media {L}", lambda c,P,k,L=L: c[k]>P[L][2][k-1]))
        R.append((f"sotto media {L}", lambda c,P,k,L=L: c[k]<P[L][2][k-1]))
    for q in (2,3,4):
        R.append((f"{q} salite", lambda c,P,k,q=q: all(c[k-i]>c[k-i-1] for i in range(q))))
        R.append((f"{q} cali",   lambda c,P,k,q=q: all(c[k-i]<c[k-i-1] for i in range(q))))
    return R
def giro(et, f, oriz):
    c=serie(f)
    if len(c)<2000: print(f"   {et}: solo {len(c)} candele"); return
    P=pre(c,FIN); veri=[]; casi=[]
    for nome,fn in regole():
        for verso in ("lungo","corto"):
            for o in oriz:
                def esegui(mesc):
                    v=[]; lib=0
                    idx=[k for k in range(200,len(c)-o) if fn(c,P,k)]
                    if not idx: return None
                    if mesc: idx=sorted(random.sample(range(200,len(c)-o), min(len(idx),len(c)-205-o)))
                    s=1 if verso=="lungo" else -1
                    for k in idx:
                        if k<lib: continue
                        v.append(s*(c[k+o]/c[k]-1)); lib=k+o
                    if len(v)<150: return None
                    sd=st.stdev(v)
                    return st.mean(v)/(sd/math.sqrt(len(v))) if sd>0 else None
                a=esegui(False); b=esegui(True)
                if a is not None and b is not None: veri.append(a); casi.append(b)
    print(f"\n   {et} — {len(c):,} candele, {len(veri)} prove appaiate")
    for nm,x in (("REGOLE VERE",veri),("rimescolate",casi)):
        if not x: print(f"      {nm}: nessuna prova valida"); continue
        x=sorted(x)
        print(f"      {nm:<14} mediana {st.median(x):+6.2f}  5%={x[max(0,len(x)//20)]:+6.2f}  "
              f"95%={x[min(len(x)-1,19*len(x)//20)]:+6.2f}  estremi |t|>2: {sum(1 for v in x if abs(v)>2)}")
giro("ORARIE (2 anni)", "data/mercati/EURUSD_X_1h.json", (4,24))
giro("5 MINUTI (2 mesi)", "data/mercati/EURUSD_X_5m.json", (3,12))
giro("GIORNALIERE (10 anni)", "data/mercati/EURUSD_X_1d.json", (2,10))
