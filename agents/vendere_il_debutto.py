"""Vendere allo scoperto una moneta appena quotata: la coda destra uccide?

La perdita di chi e' corto e' illimitata. Media e mediana vicine a 72h non
bastano: serve vedere i casi peggiori, perche' basta una moneta che fa +300%
per cancellare venti vincenti.
"""
import json, glob, os, statistics as st, math, collections
COSTO=0.0010
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
pri=collections.Counter(v[0][0] for v in viste.values())
bordi={t for t,n in pri.items() if n>=3}
deb={s:v for s,v in viste.items() if v[0][0] not in bordi}
for ORE in (24,72):
    r=[]
    for s,v in deb.items():
        if len(v)<ORE+2: continue
        t0,p0=v[1]
        if v[1+ORE][0]-t0 != ORE*3600000: continue
        r.append((s, -(v[1+ORE][1]/p0-1)-COSTO))     # CORTO
    r.sort(key=lambda x:x[1])
    v=[x[1] for x in r]
    m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
    print(f"\n   CORTO per {ORE} ore | {len(v)} debutti")
    print(f"      media {m:+.2f}% +/-{e:.2f}   mediana {st.median(v)*100:+.2f}%")
    print(f"      vincenti {sum(1 for x in v if x>0)/len(v)*100:.0f}%")
    for q,nome in [(0.01,"1%"),(0.05,"5%"),(0.25,"25%"),(0.75,"75%"),(0.95,"95%"),(0.99,"99%")]:
        print(f"         percentile {nome:>3}: {v[int(q*(len(v)-1))]*100:+8.2f}%")
    print(f"      5 peggiori: " + ", ".join(f"{s} {x*100:+.0f}%" for s,x in r[:5]))
    # quanto pesano i 3 casi peggiori sul totale
    senza=st.mean(v[3:])*100
    print(f"      togliendo i 3 peggiori la media diventa {senza:+.2f}%"
          f"  (era {m:+.2f}%)")
    # perdita massima su una singola posizione
    print(f"      perdita peggiore su una posizione: {min(v)*100:+.1f}%")
