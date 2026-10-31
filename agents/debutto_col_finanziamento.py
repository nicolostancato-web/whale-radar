"""Vendere il debutto, CON il finanziamento che paga chi e' corto.

Chi e' corto RICEVE il finanziamento quando il tasso e' positivo e lo PAGA
quando e' negativo. Sui debutti caldi il tasso puo' essere molto negativo:
e' l'ingrediente che puo' cancellare tutto il guadagno da solo.
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
        if s not in viste:
            v=serie(f)
            if v: viste[s]=v
pri=collections.Counter(v[0][0] for v in viste.values())
bordi={t for t,n in pri.items() if n>=3}
deb={s:v for s,v in viste.items() if v[0][0] not in bordi}
for ORE in (24,72,168):
    pz=[]; fz=[]; tot=[]
    for s,v in deb.items():
        if len(v)<ORE+2: continue
        t0,p0=v[1]
        if v[1+ORE][0]-t0 != ORE*3600000: continue
        f=f"data/finanziamento_debutti/{s}.json"
        if not os.path.exists(f): continue
        fin=json.load(open(f))
        inc=sum(x["r"] for x in fin if t0 <= x["t"] <= t0+ORE*3600000)  # corto RICEVE il tasso positivo
        prezzo=-(v[1+ORE][1]/p0-1)
        pz.append(prezzo); fz.append(inc); tot.append(prezzo+inc-COSTO)
    if len(tot)<20: continue
    def rr(v):
        m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
        return f"{m:+7.2f}% +/-{e:5.2f}"
    print(f"\n   CORTO {ORE}h | {len(tot)} debutti")
    print(f"      solo prezzo        {rr(pz)}")
    print(f"      solo finanziamento {rr(fz)}   mediana {st.median(fz)*100:+.2f}%"
          f"   peggiore {min(fz)*100:+.1f}%")
    print(f"      TOTALE netto       {rr(tot)}   mediana {st.median(tot)*100:+.2f}%"
          f"   vincenti {sum(1 for x in tot if x>0)/len(tot)*100:.0f}%")
    m=st.mean(tot)*100; e=1.96*st.stdev(tot)/math.sqrt(len(tot))*100
    print(f"      -> {'SOPRA ZERO' if m-e>0 else 'NON DIMOSTRATO'}")
