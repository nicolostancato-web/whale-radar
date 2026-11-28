"""Il gradiente: il segnale cresce scendendo nella classifica dei volumi?

Confermato fra due fasce (grandi -0,027%, 300-380 +0,041%). Se e' un gradiente
vero deve essere ordinato su piu' fasce, non un salto fra due.
Stessa regola registrata, stesso costo (2 gambe x 0,05% = 0,10%), taratura sui
due versi in ogni fascia.
"""
import json, glob, os, statistics as st, math
COSTO=2*0.0005
FASCE=[("1-80 (i piu' grandi)","data/binance/*.json"),
       ("150-230","data/binance_f150/*.json"),
       ("300-380","data/binance_piccoli/*.json"),
       ("450-530","data/binance_f450/*.json"),
       ("600-680","data/binance_f600/*.json")]
def resa(M,verso,oriz=4):
    v=[]
    for d in M:
        storia=[]; lib=0
        for k in range(len(d)):
            storia.append(d[k]["v"])
            if k<500 or k>=len(d)-oriz or k<lib: continue
            fin=sorted(storia[-500:])
            if d[k]["v"] < fin[int(0.95*len(fin))]: continue
            dire=1 if d[k]["c"]>d[k-1]["c"] else -1
            seg=-dire if verso=="contrasta" else dire
            v.append(seg*(d[k+oriz]["c"]/d[k]["c"]-1)-COSTO); lib=k+oriz
    if len(v)<300: return None
    return st.mean(v)*100, 1.96*st.stdev(v)/math.sqrt(len(v))*100, len(v)
print("   fascia                merc.   lordo      netto contrastando    taratura")
for et,patt in FASCE:
    M=[json.load(open(f)) for f in sorted(glob.glob(patt))]
    M=[d for d in M if len(d)>3000]
    if len(M)<20: print(f"   {et:<20} solo {len(M)} mercati: salto"); continue
    a=resa(M,"contrasta"); b=resa(M,"segui")
    if not a or not b: continue
    lordo=(a[0]-b[0])/2; tar=(a[0]+b[0])/2
    seg="SOPRA ZERO" if a[0]-a[1]>0 else ("non dim." if a[0]+a[1]>0 else "sotto zero")
    print(f"   {et:<20} {len(M):>4}  {lordo:+7.4f}%   {a[0]:+7.4f}% +/-{a[1]:5.4f} {seg:<11} {tar:+.4f}%")
