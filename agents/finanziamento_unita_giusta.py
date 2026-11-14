"""La differenza di finanziamento, con l'unita' indipendente corretta.

Propagazione della lezione del calendario (27/10 sera): mettere insieme 39
monete nella stessa finestra temporale non fa 39 osservazioni. Le monete si
muovono insieme. L'unita' indipendente e' la FINESTRA, non moneta-finestra.

Prima si fa la media fra le monete dentro ogni data di apertura, poi la
statistica fra le date.
"""
import json, glob, os, statistics as st, math, collections
COSTO=0.0019; TEN=21     # 21 finestre da 8 ore = 7 giorni
def car(f):
    try: return json.load(open(f))
    except Exception: return None
def prezzi(f):
    d=car(f)
    if not isinstance(d,list) or not d: return {}
    k="t" if "t" in d[0] else ("T" if "T" in d[0] else None)
    return {int(x[k]): x["c"] for x in d} if k else {}
per_data=collections.defaultdict(list)
n_monete=0
for f in sorted(glob.glob("data/finanziamento_binance/*.json")):
    s=os.path.basename(f).replace(".json","")
    fb=car(f); fh=car(f"data/finanziamento/{s}.json")
    pb=prezzi(f"data/binance/{s}USDT.json"); ph=prezzi(f"data/candele3/{s}.json")
    if not fb or not fh or not pb or not ph: continue
    n_monete+=1
    oraria={int(x["time"])//3600000*3600000: float(x["fundingRate"]) for x in fh}
    B=sorted((int(x["t"]), x["r"]) for x in fb); tassi=dict(B)
    hl8={}
    for t,_ in B:
        v=[oraria[t-i*3600000] for i in range(8) if t-i*3600000 in oraria]
        if len(v)==8: hl8[t]=sum(v)
    ts=[t for t,_ in B if t in hl8]
    lib=0
    for i in range(1,len(ts)-TEN):
        if i<lib: continue
        prec=tassi[ts[i-1]]-hl8[ts[i-1]]
        if abs(prec)<1e-9: continue
        v=1 if prec>0 else -1
        inc=sum(v*(tassi[ts[j]]-hl8[ts[j]]) for j in range(i,i+TEN))
        t0,t1=ts[i],ts[i+TEN]
        if not all(t in pb and t in ph for t in (t0,t1)): continue
        sc=v*((ph[t1]/pb[t1]-1)-(ph[t0]/pb[t0]-1))
        per_data[t0].append(inc+sc-COSTO)
        lib=i+TEN
print(f"   {n_monete} monete | {len(per_data)} date di apertura distinte\n")
tutte=[x for v in per_data.values() for x in v]
med=[st.mean(v) for v in per_data.values() if len(v)>=3]
def riga(nome, v, n):
    m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
    print(f"   {nome:<34}{n:>6} osservazioni  {m:>+8.4f}% +/-{e:.4f}  "
          f"{'SOPRA ZERO' if m-e>0 else 'non dimostrato'}")
riga("come l'avevo contato (moneta-data)", tutte, len(tutte))
riga("con l'unita' giusta (la data)", med, len(med))
print(f"\n   lordo = netto + 0,19% di pedaggio")
m=st.mean(med)*100; e=1.96*st.stdev(med)/math.sqrt(len(med))*100
print(f"   lordo con l'unita' giusta: {m+0.19:+.4f}% +/-{e:.4f} su 7 giorni"
      f"  ->  {(m+0.19)/7*365:+.1f}% l'anno")
print(f"   {'resta dimostrato' if m+0.19-e>0 else 'NON PIU DIMOSTRATO'}")
