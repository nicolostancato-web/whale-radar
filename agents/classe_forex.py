"""La prova della CLASSE sui mercati tradizionali — quella che avevo fatto solo
sulle crypto estendendone la conclusione senza rifarla qui.

19 mercati (EUR/USD + 18 fra valute e materie prime), candele orarie e da 5
minuti. Si generano sistematicamente decine di regole e ognuna si confronta con
gli STESSI segnali a tempi rimescolati. Niente costo nella statistica: deve
misurare il segnale.
Se il centro coincide e le code si allargano, e' la stessa macchina di falsi
positivi vista sulle crypto. Se il centro si sposta, il forex e' diverso.
"""
import json, glob, os, statistics as st, random, math
from collections import deque
random.seed(47)
def carica(patt):
    out=[]
    for f in sorted(glob.glob(patt)):
        D=json.load(open(f))
        c=[x for x in D["c"] if x]
        if len(c)>3000: out.append((os.path.basename(f).split("_")[0], c))
    return out
def precalcola(c, fin):
    n=len(c); pre={}
    for L in fin:
        mx=[0.0]*n; mn=[0.0]*n; md=[0.0]*n; s=0.0
        dmax=deque(); dmin=deque()
        for i in range(n):
            s+=c[i]
            if i>=L: s-=c[i-L]
            md[i]=s/min(i+1,L)
            while dmax and c[dmax[-1]]<=c[i]: dmax.pop()
            dmax.append(i)
            while dmax[0]<=i-L: dmax.popleft()
            mx[i]=c[dmax[0]]
            while dmin and c[dmin[-1]]>=c[i]: dmin.pop()
            dmin.append(i)
            while dmin[0]<=i-L: dmin.popleft()
            mn[i]=c[dmin[0]]
        pre[L]=(mx,mn,md)
    return pre
FIN=(6,12,24,72)
REG=[]
for L in FIN:
    REG.append((f"max{L}", lambda c,p,k,L=L: c[k]>p[L][0][k-1]))
    REG.append((f"min{L}", lambda c,p,k,L=L: c[k]<p[L][1][k-1]))
    REG.append((f"sopra media{L}", lambda c,p,k,L=L: c[k]>p[L][2][k-1]))
    REG.append((f"sotto media{L}", lambda c,p,k,L=L: c[k]<p[L][2][k-1]))
for q in (2,3,4):
    REG.append((f"{q} salite", lambda c,p,k,q=q: all(c[k-i]>c[k-i-1] for i in range(q))))
    REG.append((f"{q} cali",   lambda c,p,k,q=q: all(c[k-i]<c[k-i-1] for i in range(q))))
def giro(nome, patt, oriz):
    M=[(n,c,precalcola(c,FIN)) for n,c in carica(patt)]
    if not M: print(f"   {nome}: nessun dato"); return
    veri=[]; casi=[]
    for et,fn in REG:
        for verso in ("lungo","corto"):
            for o in oriz:
                def esegui(mescola):
                    v=[]
                    for n,c,p in M:
                        idx=[k for k in range(200,len(c)-o) if fn(c,p,k)]
                        if not idx: continue
                        if mescola: idx=random.sample(range(200,len(c)-o), min(len(idx),len(c)-205-o))
                        lib=0; s=1 if verso=="lungo" else -1
                        for k in idx:
                            if k<lib: continue
                            v.append(s*(c[k+o]/c[k]-1)); lib=k+o
                    if len(v)<200: return None
                    sd=st.stdev(v)
                    return st.mean(v)/(sd/math.sqrt(len(v))) if sd>0 else None
                a=esegui(False); b=esegui(True)
                if a is not None and b is not None: veri.append(a); casi.append(b)
    def ri(et,x):
        x=sorted(x)
        print(f"      {et:<22} n={len(x):<4} mediana {st.median(x):+6.2f}  "
              f"5%={x[max(0,len(x)//20)]:+6.2f}  95%={x[min(len(x)-1,19*len(x)//20)]:+6.2f}  "
              f"estremi |t|>2: {sum(1 for v in x if abs(v)>2)}")
    print(f"\n   {nome} — {len(M)} mercati, {sum(len(c) for _,c,_ in M):,} candele")
    ri("REGOLE VERE", veri); ri("rimescolate", casi)
giro("CANDELE ORARIE", "data/mercati/*_1h.json", (4,24))
giro("CANDELE DA 5 MINUTI", "data/mercati/*_5m.json", (3,12))
