"""Comprare la cima della classifica e vendere il fondo: la marea si cancella.

Perche' e' diverso da tutto cio' che ho provato oggi: non chiede «quando
comprare X» ma «fra 300 mercati, quali». Il movimento comune a tutti sparisce
per costruzione, ed e' quello che ha annegato ogni prova (t a -5 e -10).

Disegno: a ogni istante si ordinano i mercati per il rendimento delle ultime
L ore; si compra il decile alto e si vende il decile basso; si tiene H ore;
osservazioni NON sovrapposte. Costo 0,20% (quattro gambe).
Controllo appaiato: le stesse date, ma con i mercati assegnati A CASO ai due
lati — cosi' il confronto isola la CLASSIFICA, non il periodo.
"""
import json, glob, os, statistics as st, math, random, collections
random.seed(2718)
COSTO=0.0020
P={}
for d in ["data/binance","data/binance_piccoli","data/binance_f150",
          "data/binance_f450","data/binance_f600"]:
    for f in glob.glob(d+"/*.json"):
        s=os.path.basename(f).replace(".json","")
        if s in P: continue
        try: dd=json.load(open(f))
        except Exception: continue
        if not isinstance(dd,list) or len(dd)<3000: continue
        k="t" if "t" in dd[0] else ("T" if "T" in dd[0] else None)
        if not k: continue
        P[s]={int(x[k]): x["c"] for x in dd}
print(f"   {len(P)} mercati")
ore=collections.Counter()
for v in P.values():
    for t in v: ore[t]+=1
comuni=sorted(t for t,n in ore.items() if n>=60)
print(f"   {len(comuni)} ore con almeno 60 mercati presenti\n")
idx={t:i for i,t in enumerate(comuni)}
def prova(L, H, mesc):
    v=[]; i=L
    while i+H < len(comuni):
        t0=comuni[i]; tp=comuni[i-L]; t1=comuni[i+H]
        if t0-tp != L*3600000 or t1-t0 != H*3600000: i+=1; continue
        cand=[]
        for s,pr in P.items():
            if t0 in pr and tp in pr and t1 in pr and pr[tp]>0 and pr[t0]>0:
                cand.append((pr[t0]/pr[tp]-1, pr[t1]/pr[t0]-1))
        if len(cand)<60: i+=1; continue
        if mesc: random.shuffle(cand)
        else: cand.sort(key=lambda x:x[0])
        k=max(5, len(cand)//10)
        alto=st.mean(x[1] for x in cand[-k:])
        basso=st.mean(x[1] for x in cand[:k])
        v.append(alto-basso-COSTO)
        i+=H
    return v
print(f"   {'L':>5}{'H':>5}{'cicli':>8}{'netto':>12}{'intervallo':>12}{'':>14}")
for L in (12,24,72,168):
    for H in (12,24,72):
        v=prova(L,H,False)
        if len(v)<40: continue
        m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
        c=prova(L,H,True); mc=st.mean(c)*100
        eti = "SOPRA ZERO" if m-e>0 else ("SOTTO ZERO" if m+e<0 else "")
        print(f"   {L:>5}{H:>5}{len(v):>8}  {m:>+9.4f}%  +/-{e:>7.4f}  "
              f"caso {mc:+.4f}%  {eti}")
