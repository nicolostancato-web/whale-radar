"""Stessa regola, mercati piccoli contro mercati grandi.

Ipotesi: la commissione e' identica ovunque (0,05% per gamba), ma la
concorrenza no. Se l'inefficienza sopravvive dove nessuno guarda, deve vedersi
confrontando le due fasce con la STESSA regola.
Regola registrata il 25/10: impennata di volume oltre il 95esimo percentile
delle ultime 500 ore, si contrasta il movimento dell'ora, si esce dopo 4 ore.
Costo: 2 gambe x 0,05% = 0,10% (una posizione sola, non una coppia).
I due versi devono mediarsi a -0,10%: taratura.
"""
import json, glob, os, statistics as st, math
COSTO=2*0.0005
def carica(d):
    M=[]
    for f in sorted(glob.glob(d)):
        x=json.load(open(f))
        if len(x)>3000: M.append((os.path.basename(f)[:-5], x))
    return M
def resa(M, verso, campo="v", oriz=4):
    v=[]
    for c,d in M:
        storia=[]; lib=0
        for k in range(len(d)):
            storia.append(d[k][campo])
            if k<500 or k>=len(d)-oriz or k<lib: continue
            fin=sorted(storia[-500:])
            if d[k][campo] < fin[int(0.95*len(fin))]: continue
            dire = 1 if d[k]["c"]>d[k-1]["c"] else -1
            seg = -dire if verso=="contrasta" else dire
            v.append(seg*(d[k+oriz]["c"]/d[k]["c"]-1)-COSTO); lib=k+oriz
    if len(v)<300: return None
    return st.mean(v)*100, 1.96*st.stdev(v)/math.sqrt(len(v))*100, len(v)
for et,patt in (("GRANDI (primi 80)","data/binance/*.json"),
                ("PICCOLI (300-380)","data/binance_piccoli/*.json")):
    M=carica(patt)
    print(f"\n   {et}: {len(M)} mercati, {sum(len(x[1]) for x in M):,} ore")
    val={}
    for verso in ("contrasta","segui"):
        r=resa(M,verso)
        if not r: continue
        val[verso]=r[0]
        esito="SOPRA ZERO" if r[0]-r[1]>0 else ("sotto zero" if r[0]+r[1]<0 else "non dimostrato")
        print(f"      {verso:<10} {r[0]:+7.4f}% +/-{r[1]:6.4f} n={r[2]:<6} {esito}")
    if len(val)==2:
        media=(val["contrasta"]+val["segui"])/2
        lordo=(val["contrasta"]-val["segui"])/2
        print(f"      taratura: media dei due versi {media:+.4f}% (deve valere -{COSTO*100:.2f}%)")
        print(f"      SEGNALE LORDO: {lordo:+.4f}%  (il costo e' {COSTO*100:.2f}%)")
