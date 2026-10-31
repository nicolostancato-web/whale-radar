"""Il ritorno fra mercati, con i COSTI dentro e diviso in due meta' di mercati.

Correzione di metodo: nelle prove della classe includevo entrambi i versi sulle
stesse entrate, che sono esatti opposti — quindi la mediana zero era
un'IDENTITA', non una prova. Il vantaggio si vede nell'asimmetria, e qui c'e':
le cinque combinazioni piu' forti sono tutte nel verso del ritorno.

Qui: costo 0,10% per ciclo (due gambe), e mercati divisi in pari/dispari, che
e' l'unico asse davvero indipendente.
"""
import json, glob, statistics as st, math
COSTO=0.0010
S={}
for f in sorted(glob.glob("data/binance/*.json"))[:60]:
    d=json.load(open(f))
    if len(d)<6000: continue
    S[f.split("/")[-1][:-5]]={x["t"]:x["c"] for x in d}
ore=sorted(set.intersection(*[set(v) for v in S.values()]))
tutti=sorted(S)
A=[n for i,n in enumerate(tutti) if i%2==0]
B=[n for i,n in enumerate(tutti) if i%2==1]
P={n:[S[n][t] for t in ore] for n in tutti}
def prova(nomi, guardo, tengo, da=0.0, a=1.0):
    i0=int(da*len(ore)); i1=int(a*len(ore)); res=[]
    for k in range(i0+guardo, i1-tengo, tengo):
        r=sorted([(P[n][k]/P[n][k-guardo]-1, n) for n in nomi])
        q=max(2,len(r)//5)
        bassi=[n for _,n in r[:q]]; alti=[n for _,n in r[-q:]]
        rb=st.mean([P[n][k+tengo]/P[n][k]-1 for n in bassi])
        ra=st.mean([P[n][k+tengo]/P[n][k]-1 for n in alti])
        res.append((rb-ra)-COSTO)        # ritorno: lungo i bassi, corto gli alti
    if len(res)<100: return None
    m=st.mean(res); e=1.96*st.stdev(res)/math.sqrt(len(res))
    return m*100, e*100, len(res)
print("   combinazione        insieme         resa NETTA per ciclo      esito")
for guardo,tengo in ((72,4),(12,4),(72,12),(24,4),(168,12)):
    for et,nomi,da,a in (("tutti",tutti,0.0,1.0),("mercati A",A,0.0,1.0),("mercati B",B,0.0,1.0),
                         ("prima meta'",tutti,0.0,0.5),("seconda meta'",tutti,0.5,1.0)):
        r=prova(nomi,guardo,tengo,da,a)
        if not r: continue
        m,e,n=r
        esito="SOPRA ZERO" if m-e>0 else ("positivo" if m>0 else "negativo")
        print(f"   guardo{guardo:>4}h tengo{tengo:>3}h  {et:<14} {m:+7.4f}% +/-{e:6.4f} n={n:<5} {esito}")
    print()
