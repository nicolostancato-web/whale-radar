"""Solo le quotazioni VERE: quelle che iniziano dopo l'inizio dell'archivio.

Lezione ripetuta oggi: la prima candela di un archivio troncato e' l'inizio
della MIA raccolta, non un evento del mondo. Dieci monete con la stessa data
sono il bordo del file, non dieci quotazioni.
"""
import json, glob, os, datetime, collections, statistics as st, math
def serie(f):
    try: d=json.load(open(f))
    except Exception: return None
    if not isinstance(d,list) or not d: return None
    k="t" if "t" in d[0] else ("T" if "T" in d[0] else None)
    if not k: return None
    return sorted((int(x[k]), x["c"]) for x in d)
HL={}
for f in glob.glob("data/candele3/*.json"):
    s=serie(f)
    if s: HL[os.path.basename(f).replace(".json","")]=s
bordo=min(v[0][0] for v in HL.values())
c=collections.Counter(v[0][0] for v in HL.values())
print(f"   bordo archivio: {datetime.datetime.fromtimestamp(bordo/1000,datetime.UTC):%Y-%m-%d}")
print(f"   monete che iniziano esattamente al bordo: {c[bordo]} su {len(HL)}")
soglia = bordo + 3*86400000
veri = {s:v for s,v in HL.items() if v[0][0] > soglia}
print(f"   quotazioni VERE (iniziate dopo il bordo): {len(veri)}\n")
BN={}
for d in ["data/binance","data/binance_piccoli","data/binance_f150","data/binance_f450","data/binance_f600"]:
    for f in glob.glob(d+"/*.json"):
        s=os.path.basename(f).replace("USDT.json","")
        v=serie(f)
        if v and (s not in BN or v[0][0]<BN[s][0][0]): BN[s]=v
ev=[]
for s,v in veri.items():
    if s not in BN: continue
    t0=v[0][0]
    pb=dict(BN[s])
    if BN[s][0][0] > t0 - 14*86400000: continue   # serve storia prima
    ev.append((s,t0,pb))
print(f"   di cui gia' scambiate su Binance con 14+ giorni di storia: {len(ev)}")
if len(ev)<9:
    print("\n   POTENZA INSUFFICIENTE: con meno di 9 eventi non si vede")
    print("   nemmeno un effetto dell'1%. Il test non si fa.")
else:
    print(f"\n   {'ore dalla quotazione':>22}{'resa media':>14}{'intervallo':>14}")
    for a,b in [(-48,-1),(-24,-1),(-6,-1),(0,6),(0,24),(0,72),(0,168)]:
        r=[]
        for s,t0,pb in ev:
            ta=t0+a*3600000; tb=t0+b*3600000
            if ta in pb and tb in pb: r.append(pb[tb]/pb[ta]-1)
        if len(r)<5: continue
        m=st.mean(r)*100; e=1.96*st.stdev(r)/math.sqrt(len(r))*100 if len(r)>1 else 0
        print(f"   {a:>8} -> {b:<8}{len(r):>4} ev {m:>+9.2f}%  +/-{e:.2f}  "
              f"{'SOPRA ZERO' if m-e>0 else ''}")
