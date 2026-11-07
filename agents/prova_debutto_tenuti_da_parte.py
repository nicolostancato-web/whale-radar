"""PROVA PRE-REGISTRATA (PREREGISTRAZIONE_VENDERE_IL_DEBUTTO_27OTT.md).

Corto alla chiusura della prima ora intera, uscita a 72 ore, costo 0,10%
piu' il finanziamento dalla parte del corto. 372 simboli mai toccati.

Asticella fissata PRIMA, tutte e tre:
  1) netto a 72h sopra zero con l'intervallo che non tocca lo zero
  2) vincenti sopra il 55%
  3) togliendo i 3 migliori la media resta positiva
"""
import json, glob, os, statistics as st, math, collections
COSTO=0.0010; ORE=72
agg={}
for f in glob.glob("data/binance_resto/*.json"):
    s=os.path.basename(f).replace(".json","")
    try: d=json.load(open(f))
    except Exception: continue
    if not isinstance(d,list) or len(d)<ORE+2: continue
    agg[s]=sorted((int(x["t"]), x["c"]) for x in d)
pri=collections.Counter(v[0][0] for v in agg.values())
bordi={t for t,n in pri.items() if n>=3}
if bordi: print(f"   escluse {sum(pri[t] for t in bordi)} su data condivisa")
r=[]
for s,v in agg.items():
    if v[0][0] in bordi: continue
    t0,p0=v[1]
    if v[1+ORE][0]-t0 != ORE*3600000: continue
    ff=f"data/finanziamento_resto/{s}.json"
    if not os.path.exists(ff): continue
    fin=json.load(open(ff))
    inc=sum(x["r"] for x in fin if t0 <= x["t"] <= t0+ORE*3600000)
    r.append((s, -(v[1+ORE][1]/p0-1) + inc - COSTO))
v=sorted(x[1] for x in r)
print(f"\n   {len(v)} debutti mai visti\n")
m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
vinc=sum(1 for x in v if x>0)/len(v)*100
senza=st.mean(v[:-3])*100
print(f"   netto medio   {m:+.2f}% +/-{e:.2f}   mediana {st.median(v)*100:+.2f}%")
print(f"   vincenti      {vinc:.0f}%")
print(f"   senza i 3 migliori {senza:+.2f}%")
print(f"   peggiore {min(v)*100:+.1f}%   migliore {max(v)*100:+.1f}%")
print()
c1 = m-e>0; c2 = vinc>55; c3 = senza>0
print(f"   1) sopra zero con intervallo      {'PASSA' if c1 else 'NO'}")
print(f"   2) vincenti sopra 55%             {'PASSA' if c2 else 'NO'}")
print(f"   3) non trascinato dalla coda      {'PASSA' if c3 else 'NO'}")
print(f"\n   ESITO: {'PASSA' if (c1 and c2 and c3) else 'BOCCIATA'}")
