"""L'ATTENZIONE: volume e numero di operazioni. Non e' il prezzo.

Un'impennata del numero di operazioni dice che in quell'ora tanta gente sta
guardando quel mercato. E' una classe diversa dalle sei gia' chiuse, con le
stesse centinaia di migliaia di osservazioni.

Due ipotesi opposte, entrambe provate senza sceglierne una dopo:
  - l'attenzione precede il movimento: si entra nella direzione dell'ora stessa
  - l'attenzione e' l'apice: si entra contro
Soglia relativa al mercato (percentile sulle ultime 500 ore). Osservazioni NON
sovrapposte. Costo 0,094%. I due versi devono mediarsi a -costo: taratura.
"""
import json, glob, os, statistics as st
COSTO=0.00094
M=[]
for f in sorted(glob.glob("data/candele3/*.json")):
    c=os.path.basename(f).replace(".json","")
    d=json.load(open(f))
    if len(d)>1500: M.append((c,d))
print(f"{len(M)} mercati | {sum(len(x[1]) for x in M):,} ore\n")
def prova(verso, oriz, campo):
    v=[]
    for c,d in M:
        storia=[]; libero=0
        for k,x in enumerate(d):
            storia.append(x[campo])
            if k<500 or k>=len(d)-oriz or k<libero: continue
            fin=sorted(storia[-500:])
            if x[campo] < fin[int(0.95*len(fin))]: continue   # solo le impennate
            dire = 1 if d[k]["c"]>d[k-1]["c"] else -1          # direzione dell'ora stessa
            seg = dire if verso=="segui" else -dire
            v.append(seg*(d[k+oriz]["c"]/d[k]["c"]-1)-COSTO)
            libero=k+oriz
    if len(v)<300: return None
    return st.mean(v)*100, 1.96*st.stdev(v)/len(v)**0.5*100, len(v)
for campo,et in (("n","numero di operazioni"),("v","volume")):
    print(f"   --- impennata del {et} (oltre il 95esimo percentile) ---")
    for verso in ("segui","contrasta"):
        for oriz in (4,12,24):
            r=prova(verso,oriz,campo)
            if not r: continue
            m,e,n=r
            esito="SOPRA ZERO" if m-e>0 else ("sotto zero" if m+e<0 else "non dimostrato")
            print(f"   {verso:<10} {oriz:>3}h   {m:+7.4f}% +/-{e:6.4f} n={n:<6} {esito}")
    print()
