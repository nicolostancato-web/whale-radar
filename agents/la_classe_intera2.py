"""La classe intera, versione veloce: le finestre si precalcolano una volta.

La prima versione ricalcolava massimi e medie a ogni passo: 224 esecuzioni x
640.000 ore = troppo. Qui massimi, minimi e medie mobili si calcolano una sola
volta per mercato, poi le regole leggono valori gia' pronti.
"""
import json, glob, statistics as st, random, math
random.seed(31); COSTO=0.0   # SENZA costo: la statistica deve misurare il SEGNALE,
# non quante volte un costo fisso sta dentro l'errore (errore del primo tentativo)
FIN=(6,12,24,72,168)
dati=[]
for f in sorted(glob.glob("data/binance/*.json"))[:30]:
    d=json.load(open(f))
    if len(d)<3000: continue
    c=[x["c"] for x in d]; n=len(c)
    pre={}
    for L in FIN:
        mx=[0.0]*n; mn=[0.0]*n; md=[0.0]*n; s=0.0
        from collections import deque
        dq_max=deque(); dq_min=deque()
        for i in range(n):
            s+=c[i]
            if i>=L: s-=c[i-L]
            md[i]=s/min(i+1,L)
            while dq_max and c[dq_max[-1]]<=c[i]: dq_max.pop()
            dq_max.append(i)
            while dq_max[0]<=i-L: dq_max.popleft()
            mx[i]=c[dq_max[0]]
            while dq_min and c[dq_min[-1]]>=c[i]: dq_min.pop()
            dq_min.append(i)
            while dq_min[0]<=i-L: dq_min.popleft()
            mn[i]=c[dq_min[0]]
        pre[L]=(mx,mn,md)
    dati.append((c,pre,n))
print(f"{len(dati)} mercati | {sum(x[2] for x in dati):,} ore")
REG=[]
for L in FIN:
    REG.append((f"max{L}", lambda c,p,k,L=L: c[k]>p[L][0][k-1]))
    REG.append((f"min{L}", lambda c,p,k,L=L: c[k]<p[L][1][k-1]))
    REG.append((f"sopra media{L}", lambda c,p,k,L=L: c[k]>p[L][2][k-1]))
    REG.append((f"sotto media{L}", lambda c,p,k,L=L: c[k]<p[L][2][k-1]))
for q in (2,3,4,5):
    REG.append((f"{q} salite", lambda c,p,k,q=q: all(c[k-i]>c[k-i-1] for i in range(q))))
    REG.append((f"{q} cali",   lambda c,p,k,q=q: all(c[k-i]<c[k-i-1] for i in range(q))))
print(f"{len(REG)} regole x 2 versi x 2 orizzonti = {len(REG)*4} prove\n")
def esegui(fn, verso, oriz, mescola):
    v=[]
    for c,p,n in dati:
        idx=[k for k in range(200,n-oriz) if fn(c,p,k)]
        if not idx: continue
        if mescola: idx=random.sample(range(200,n-oriz), min(len(idx),n-205-oriz))
        lib=0; s=1 if verso=="lungo" else -1
        for k in idx:
            if k<lib: continue
            v.append(s*(c[k+oriz]/c[k]-1)-COSTO); lib=k+oriz
    if len(v)<200: return None
    sd=st.stdev(v)
    return st.mean(v)/(sd/math.sqrt(len(v)))
# si tengono solo le prove che sopravvivono in ENTRAMBI i casi: confrontare
# 112 vere con 73 rimescolate non e' un confronto.
veri=[]; casi=[]
for nome,fn in REG:
    for verso in ("lungo","corto"):
        for oriz in (4,24):
            a=esegui(fn,verso,oriz,False); b=esegui(fn,verso,oriz,True)
            if a is not None and b is not None:
                veri.append(a); casi.append(b)
def riass(et,x):
    x=sorted(x)
    print(f"   {et:<24} n={len(x):<4} mediana {st.median(x):+6.2f}  "
          f"5%={x[len(x)//20]:+6.2f}  95%={x[19*len(x)//20]:+6.2f}  "
          f"sopra+2: {sum(1 for v in x if v>2)}  sotto-2: {sum(1 for v in x if v<-2)}")
riass("REGOLE VERE", veri); riass("segnali rimescolati", casi)
print("\n   se la famiglia non ha vantaggio le due righe coincidono.")
