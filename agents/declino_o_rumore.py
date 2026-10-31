"""Lo zero recente e' un DECLINO o un trimestre tranquillo?

Se l'effetto si consuma perche' qualcuno lo sfrutta, la discesa e' ordinata e
non torna. Se e' rumore, i trimestri saltano senza direzione.
Due meta' non lo distinguono; sette trimestri si'.
"""
import json, glob, statistics as st, math, datetime as dt, os
COSTO=0.0004     # da fornitore di liquidita', due gambe
S={}
for f in sorted(glob.glob("data/binance/*.json"))[:60]:
    d=json.load(open(f))
    if len(d)<6000: continue
    S[os.path.basename(f)[:-5]]={x["t"]:x["c"] for x in d}
ore=sorted(set.intersection(*[set(v) for v in S.values()]))
nomi=sorted(S); P={n:[S[n][t] for t in ore] for n in nomi}
print(f"{len(nomi)} mercati | {len(ore):,} ore\n")
G,T=72,12
blocchi={}
for k in range(G, len(ore)-T, T):
    r=sorted([(P[n][k]/P[n][k-G]-1, n) for n in nomi])
    q=max(2,len(r)//5)
    rb=st.mean([P[n][k+T]/P[n][k]-1 for _,n in r[:q]])
    ra=st.mean([P[n][k+T]/P[n][k]-1 for _,n in r[-q:]])
    d=dt.datetime.fromtimestamp(ore[k]/1000, dt.UTC)
    tri=f"{d.year}-T{(d.month-1)//3+1}"
    blocchi.setdefault(tri,[]).append((rb-ra)-COSTO)
print("   trimestre   cicli    resa netta per ciclo")
medie=[]
for tri in sorted(blocchi):
    v=blocchi[tri]
    if len(v)<40: print(f"   {tri}      {len(v):>4}   (pochi cicli, non riportato)"); continue
    m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
    medie.append((tri,m))
    barra = "#"*max(0,int(m*40)) if m>0 else "-"*max(0,int(-m*40))
    print(f"   {tri}      {len(v):>4}   {m:+7.4f}% +/-{e:5.4f}  {barra}")
if len(medie)>=4:
    x=list(range(len(medie))); y=[m for _,m in medie]
    mx=st.mean(x); my=st.mean(y)
    b=sum((a-mx)*(c-my) for a,c in zip(x,y))/sum((a-mx)**2 for a in x)
    print(f"\n   pendenza fra i trimestri: {b:+.4f}% per trimestre")
    print(f"   positivi: {sum(1 for _,m in medie if m>0)}/{len(medie)}")
    print("   -> " + ("DECLINO ordinato: l'effetto si sta consumando" if b<-0.02
          else ("nessuna direzione: e' rumore fra trimestri" if abs(b)<=0.02 else "in crescita")))
