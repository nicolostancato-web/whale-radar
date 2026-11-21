"""Comprare una moneta appena quotata sui futures Binance e tenerla.

Perche' qui la data e' vera: questi archivi sono stati scaricati IN AVANTI
dall'inizio, quindi la prima candela e' il debutto. Si tengono solo i simboli
la cui storia e' piu' corta del limite dello scaricatore (18.000 ore): se un
archivio e' al limite, il suo inizio e' il mio troncamento, non un evento.

Costo: 2 gambe = 0,10%. L'entrata e' la chiusura della PRIMA ora intera,
non l'apertura: al primo istante il prezzo non e' ottenibile.
"""
import json, glob, os, statistics as st, math, datetime, collections
LIM=17000; COSTO=0.0010
def serie(f):
    try: d=json.load(open(f))
    except Exception: return None
    if not isinstance(d,list) or len(d)<200: return None
    k="t" if "t" in d[0] else ("T" if "T" in d[0] else None)
    return sorted((int(x[k]), x["c"]) for x in d) if k else None
viste={}
for d in ["data/binance","data/binance_piccoli","data/binance_f150","data/binance_f450","data/binance_f600"]:
    for f in glob.glob(d+"/*.json"):
        s=os.path.basename(f).replace("USDT.json","")
        if s in viste: continue
        v=serie(f)
        if v: viste[s]=v
# IL RILEVATORE (sbagliato due volte oggi): un archivio troncato si
# riconosce perche' CONDIVIDE la data d'inizio con molti altri. 169 simboli
# iniziavano tutti il 2025-01-01: quello e' un pavimento messo da me nello
# scaricatore, non una quotazione. Si escludono tutte le coorti numerose.
import collections as _c
_pri=_c.Counter(v[0][0] for v in viste.values())
_bordi={t for t,n in _pri.items() if n>=3}
tronc=[s for s,v in viste.items() if v[0][0] in _bordi]
deb={s:v for s,v in viste.items() if v[0][0] not in _bordi}
print(f"   {len(viste)} simboli | {len(tronc)} su una data condivisa (esclusi) | {len(deb)} debutti veri")
anni=collections.Counter(datetime.datetime.fromtimestamp(v[0][0]/1000,datetime.UTC).year
                         for v in deb.values())
print(f"   per anno: {dict(sorted(anni.items()))}\n")
print(f"   {'tenuta':>10}{'eventi':>8}{'resa netta':>14}{'intervallo':>12}")
for ore in (1,4,24,72,168,720):
    r=[]
    for s,v in deb.items():
        if len(v)<ore+2: continue
        t0,p0=v[1]                      # chiusura della prima ora intera
        if v[1+ore][0]-t0 != ore*3600000: continue
        r.append(v[1+ore][1]/p0-1-COSTO)
    if len(r)<20: continue
    m=st.mean(r)*100; e=1.96*st.stdev(r)/math.sqrt(len(r))*100
    me=st.median(r)*100
    print(f"   {ore:>7}h{len(r):>8}  {m:>+9.2f}%  +/-{e:>6.2f}  mediana {me:+.2f}%  "
          f"{'SOPRA ZERO' if m-e>0 else ''}")
