"""La FAMIGLIA, non sei regole: la distribuzione di cento regole contro il caso.

Obiezione di Nicolò: «avete chiuso i pattern provandone sei». Giusta. Qui si
prova la classe: si generano sistematicamente decine di regole meccaniche e si
confronta la DISTRIBUZIONE dei loro risultati con quella che darebbe il caso.
Non si cerca la vincente — cercarla produce solo falsi positivi. Si guarda se
la nuvola intera e' spostata.

Il caso si costruisce rimescolando QUANDO scattano i segnali, mantenendo quanti
ne scattano: cosi' il confronto e' a parita' di numero e di mercato.
"""
import json, glob, os, statistics as st, random
random.seed(31); COSTO=0.0010
M=[]
for f in sorted(glob.glob("data/binance/*.json"))[:40]:
    d=json.load(open(f))
    if len(d)>3000: M.append(d)
print(f"{len(M)} mercati | {sum(len(d) for d in M):,} ore\n")
def costruisci():
    R=[]
    for L in (6,12,24,72,168):
        R.append((f"rottura max {L}", lambda d,k,L=L: d[k]["c"]>max(x["c"] for x in d[k-L:k])))
        R.append((f"rottura min {L}", lambda d,k,L=L: d[k]["c"]<min(x["c"] for x in d[k-L:k])))
        R.append((f"sopra media {L}", lambda d,k,L=L: d[k]["c"]>st.mean([x["c"] for x in d[k-L:k]])))
        R.append((f"sotto media {L}", lambda d,k,L=L: d[k]["c"]<st.mean([x["c"] for x in d[k-L:k]])))
    for n in (2,3,4,5):
        R.append((f"{n} salite", lambda d,k,n=n: all(d[k-i]["c"]>d[k-i-1]["c"] for i in range(n))))
        R.append((f"{n} cali",   lambda d,k,n=n: all(d[k-i]["c"]<d[k-i-1]["c"] for i in range(n))))
    return R
REG=costruisci()
print(f"regole generate: {len(REG)} x 2 versi x 2 orizzonti = {len(REG)*4} prove\n")
def esegui(fn, verso, oriz, rimescola=False):
    v=[]
    for d in M:
        idx=[k for k in range(200,len(d)-oriz) if fn(d,k)]
        if rimescola and idx:
            idx=random.sample(range(200,len(d)-oriz), len(idx))
        libero=0
        for k in idx:
            if k<libero: continue
            s = 1 if verso=="lungo" else -1
            v.append(s*(d[k+oriz]["c"]/d[k]["c"]-1)-COSTO); libero=k+oriz
    if len(v)<200: return None
    return st.mean(v), st.stdev(v)/len(v)**0.5, len(v)
veri=[]; casuali=[]
for nome,fn in REG:
    for verso in ("lungo","corto"):
        for oriz in (4,24):
            r=esegui(fn,verso,oriz)
            if r: veri.append(r[0]/r[1])             # quante volte l'errore
            r=esegui(fn,verso,oriz,rimescola=True)
            if r: casuali.append(r[0]/r[1])
def riassunto(et, x):
    x=sorted(x)
    print(f"   {et:<22} n={len(x):<4} mediana {st.median(x):+6.2f}  "
          f"5%={x[len(x)//20]:+6.2f}  95%={x[19*len(x)//20]:+6.2f}  "
          f"|sopra +2|={sum(1 for v in x if v>2)}  |sotto -2|={sum(1 for v in x if v<-2)}")
riassunto("REGOLE VERE", veri)
riassunto("segnali rimescolati", casuali)
print(f"\n   se la famiglia non ha vantaggio, le due righe coincidono.")
