"""La prova registrata, su una piazza mai vista: i futures Binance.

Parametri IDENTICI alla registrazione del 25/10, nessun ritocco:
  soglia 95esimo percentile delle ultime 500 ore di quel mercato,
  si contrasta il movimento dell'ora, si esce dopo 4 ore,
  osservazioni non sovrapposte, confronto col verso opposto (taratura).
Costo 0,10% a giro (commissione Binance leggermente piu' alta di Hyperliquid).
"""
import json, glob, os, statistics as st
COSTO=0.0010
M=[]
for f in sorted(glob.glob("data/binance/*.json")):
    d=json.load(open(f))
    if len(d)>3000: M.append((os.path.basename(f)[:-5], d))
print(f"{len(M)} mercati | {sum(len(x[1]) for x in M):,} ore\n")
def resa(mercati, campo, verso, oriz=4, da=None, a=None):
    v=[]
    for c,d in mercati:
        i0 = 0 if da is None else int(da*len(d))
        i1 = len(d) if a is None else int(a*len(d))
        storia=[x[campo] for x in d[:i0]]; libero=0
        for k in range(i0,i1):
            storia.append(d[k][campo])
            if k<500 or k>=i1-oriz or k<libero: continue
            fin=sorted(storia[-500:])
            if d[k][campo] < fin[int(0.95*len(fin))]: continue
            dire = 1 if d[k]["c"]>d[k-1]["c"] else -1
            seg = -dire if verso=="contrasta" else dire
            v.append(seg*(d[k+oriz]["c"]/d[k]["c"]-1)-COSTO)
            libero=k+oriz
    if len(v)<300: return None
    return st.mean(v)*100, 1.96*st.stdev(v)/len(v)**0.5*100, len(v)
print("   misura        verso        resa netta             esito")
for campo,et in (("n","operazioni"),("v","volume")):
    for verso in ("contrasta","segui"):
        r=resa(M,campo,verso)
        if not r: continue
        m,e,n=r
        esito="SOPRA ZERO" if m-e>0 else ("sotto zero" if m+e<0 else "non dimostrato")
        print(f"   {et:<12} {verso:<11} {m:+7.4f}% +/-{e:6.4f} n={n:<7} {esito}")
print(f"\n   taratura: i due versi devono mediarsi a -{COSTO*100:.2f}%")
print("\n   e diviso in due periodi (contrasta):")
for campo,et in (("n","operazioni"),("v","volume")):
    for nome,da,a in (("prima meta'",0,0.5),("seconda meta'",0.5,1.0)):
        r=resa(M,campo,"contrasta",4,da,a)
        if not r: continue
        m,e,n=r
        print(f"   {et:<12} {nome:<14} {m:+7.4f}% +/-{e:6.4f} n={n:<7} "
              f"{'SOPRA ZERO' if m-e>0 else ('positivo' if m>0 else 'NEGATIVO')}")
