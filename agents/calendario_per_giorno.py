"""Il calendario, con l'unita' indipendente GIUSTA.

Errore trovato e corretto il 27/10 sera: 347 mercati nello stesso giovedi'
non sono 347 osservazioni, sono UNA. I mercati si muovono insieme. L'unita'
indipendente e' la DATA: si fa prima la media fra i mercati dentro ogni
giorno, poi la statistica fra i giorni.

In due anni i giovedi' sono circa cento, non ventiseimila.
"""
import json, glob, os, statistics as st, math, datetime, collections
COSTO=0.0010
P=[]
for d in ["data/binance","data/binance_piccoli","data/binance_f150",
          "data/binance_f450","data/binance_f600"]:
    for f in glob.glob(d+"/*.json"):
        try: dd=json.load(open(f))
        except Exception: continue
        if not isinstance(dd,list) or len(dd)<3000: continue
        k="t" if "t" in dd[0] else ("T" if "T" in dd[0] else None)
        if not k: continue
        P.append({int(x[k]): x["c"] for x in dd})
print(f"   {len(P)} mercati")
# rendimento di ogni mercato in ogni giorno (00:00 -> 00:00 UTC)
pergiorno=collections.defaultdict(list)
for pr in P:
    for t,p in pr.items():
        dt=datetime.datetime.fromtimestamp(t/1000, datetime.UTC)
        if dt.hour!=0: continue
        t1=t+24*3600000
        if t1 in pr and p>0:
            pergiorno[dt.date()].append(pr[t1]/p-1-COSTO)
giorni={g:(st.mean(v), len(v)) for g,v in pergiorno.items() if len(v)>=30}
print(f"   {len(giorni)} giorni con almeno 30 mercati\n")
nomi=["lun","mar","mer","gio","ven","sab","dom"]
print(f"   {'giorno':<8}{'giorni':>8}{'media del giorno':>20}{'':>16}")
tutti=[v[0] for v in giorni.values()]
mt=st.mean(tutti)*100
for i,n in enumerate(nomi):
    v=[x[0] for g,x in giorni.items() if g.weekday()==i]
    if len(v)<10: continue
    m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
    diff=m-mt
    print(f"   {n:<8}{len(v):>8}{m:>+15.4f}% +/-{e:.4f}"
          f"   contro media {diff:+.4f}%  {'FUORI' if abs(diff)>e else 'nel rumore'}")
print(f"\n   media di tutti i giorni: {mt:+.4f}%")
print(f"   (ogni riga e' la media fra i mercati DENTRO il giorno; l'unita'")
print(f"    indipendente e' il giorno, non il mercato-giorno)")
