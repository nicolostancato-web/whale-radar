"""Classifica di carry: comprare le monete che PAGANO il finanziamento e
vendere quelle che lo COSTANO, dentro la stessa piazza.

Diverso dalle prove gia' chiuse: non e' «quando entrare su X» ma una
classifica fra monete, quindi la marea comune si cancella. Usa i 7 anni di
storia Binance appena scaricati — nessun vincolo dall'altra piazza.

Unita' indipendente: LA DATA (lezione di stasera). Prima la media fra le
monete dentro la data, poi la statistica fra le date.
Costo 0,20% (quattro gambe) per ciclo. Si incassa il finanziamento sui
due lati piu' la differenza di prezzo fra i due panieri.
"""
import json, glob, os, statistics as st, math, collections
COSTO=0.0020
F={}; P={}
for f in sorted(glob.glob("data/finanziamento_profondo/*.json")):
    s=os.path.basename(f).replace(".json","")
    d=json.load(open(f))
    F[s]={int(x["t"])//3600000*3600000: x["r"] for x in d}
    pf=f"data/binance/{s}USDT.json"
    if not os.path.exists(pf): continue
    dd=json.load(open(pf)); k="t" if "t" in dd[0] else "T"
    P[s]={int(x[k]): x["c"] for x in dd}
com=[s for s in F if s in P]
print(f"   {len(com)} monete con finanziamento profondo e prezzi")
inst=collections.Counter()
for s in com:
    for t in F[s]: inst[t]+=1
date=sorted(t for t,n in inst.items() if n>=20)
print(f"   {len(date)} istanti con almeno 20 monete\n")
def prova(TEN):
    per_data=collections.defaultdict(list)
    i=1
    while i+TEN < len(date):
        t0=date[i]; tp=date[i-1]; t1=date[i+TEN]
        cand=[]
        for s in com:
            if tp in F[s] and t0 in P[s] and t1 in P[s] and P[s][t0]>0:
                inc=sum(F[s].get(date[j],0) for j in range(i,i+TEN))
                cand.append((F[s][tp], inc, P[s][t1]/P[s][t0]-1))
        if len(cand)<20: i+=1; continue
        cand.sort(key=lambda x:x[0])
        k=max(3,len(cand)//4)
        # chi PAGA di piu' (tasso piu' negativo = paga chi e' lungo? no:
        # tasso positivo -> paga il lungo. Quindi si compra dove il tasso e'
        # piu' NEGATIVO (incassa il lungo) e si vende dove e' piu' positivo.
        lungo=cand[:k]          # tasso piu' negativo
        corto=cand[-k:]         # tasso piu' positivo
        inc = -st.mean(x[1] for x in lungo) + st.mean(x[1] for x in corto)
        pre = st.mean(x[2] for x in lungo) - st.mean(x[2] for x in corto)
        per_data[t0].append(inc+pre-COSTO)
        i+=TEN
    v=[st.mean(x) for x in per_data.values()]
    if len(v)<30: return None
    m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
    return len(v), m, e
print(f"   {'tenuta':>10}{'cicli':>8}{'netto':>13}{'intervallo':>12}")
for TEN in (1,3,9,21,63):
    r=prova(TEN)
    if not r: continue
    n,m,e=r
    eti="SOPRA ZERO" if m-e>0 else ("SOTTO ZERO" if m+e<0 else "")
    print(f"   {TEN*8:>8}h{n:>8}  {m:>+10.4f}%  +/-{e:>7.4f}  {eti}")
