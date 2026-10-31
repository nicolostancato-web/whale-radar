"""Lo stesso ritorno fra mercati, su Hyperliquid: altra piazza, altri mercati.

E' la prova che ha ucciso il candidato precedente. Parametri identici:
guarda 72 ore, tieni 12, lungo il quintile basso e corto quello alto.
Costo: 0,03% per ciclo da fornitore di liquidita' su Hyperliquid (1,5 punti
base per gamba), e 0,09% da chi prende il prezzo. Si stampano entrambi.
"""
import json, glob, statistics as st, math, os
S={}
for f in sorted(glob.glob("data/candele3/*.json")):
    d=json.load(open(f))
    if len(d)<3000: continue
    S[os.path.basename(f)[:-5]]={x["t"]:x["c"] for x in d}
if len(S)<20: print(f"solo {len(S)} mercati: troppo pochi"); raise SystemExit
ore=sorted(set.intersection(*[set(v) for v in S.values()]))
tutti=sorted(S)
print(f"Hyperliquid: {len(tutti)} mercati | {len(ore):,} ore in comune\n")
P={n:[S[n][t] for t in ore] for n in tutti}
A=[n for i,n in enumerate(tutti) if i%2==0]; B=[n for i,n in enumerate(tutti) if i%2==1]
def prova(nomi,guardo,tengo,costo,da=0.0,a=1.0):
    i0=int(da*len(ore)); i1=int(a*len(ore)); res=[]
    for k in range(i0+guardo, i1-tengo, tengo):
        r=sorted([(P[n][k]/P[n][k-guardo]-1, n) for n in nomi])
        q=max(2,len(r)//5)
        rb=st.mean([P[n][k+tengo]/P[n][k]-1 for n in r[:q] for n in [n[1]]]) if False else \
           st.mean([P[n][k+tengo]/P[n][k]-1 for _,n in r[:q]])
        ra=st.mean([P[n][k+tengo]/P[n][k]-1 for _,n in r[-q:]])
        res.append((rb-ra)-costo)
    if len(res)<60: return None
    m=st.mean(res); e=1.96*st.stdev(res)/math.sqrt(len(res))
    return m*100, e*100, len(res)
for costo,et in ((0.0003,"mette l'ordine (0,03%)"),(0.0009,"prende il prezzo (0,09%)")):
    print(f"   --- {et} ---")
    for nome,nomi,da,a in (("tutti",tutti,0.0,1.0),("mercati A",A,0.0,1.0),("mercati B",B,0.0,1.0),
                           ("prima meta'",tutti,0.0,0.5),("seconda meta'",tutti,0.5,1.0)):
        r=prova(nomi,72,12,costo,da,a)
        if not r: print(f"   {nome:<14} cicli insufficienti"); continue
        m,e,n=r
        esito="SOPRA ZERO" if m-e>0 else ("positivo" if m>0 else "negativo")
        print(f"   {nome:<14} {m:+7.4f}% +/-{e:6.4f} n={n:<5} {esito}")
    print()
