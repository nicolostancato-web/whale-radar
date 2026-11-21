"""Quanto rende se mi posiziono SOLO quando la differenza e' grande?

La media su tutte le finestre dava ~4%/anno. Il tetto di questa architettura
sta nella coda: selezionare le differenze grandi alza il tasso e abbassa la
frequenza. Serve a sapere a quale CAPITALE smette di essere spiccioli.

Soglia sempre sulla differenza OSSERVATA PRIMA. Tenuta 7 giorni (21 finestre),
dove il lordo era dimostrato. Costo 0,19% una volta.
"""
import json, glob, os, statistics as st, math
COSTO=0.0019; TEN=21
def car(f):
    try: return json.load(open(f))
    except Exception: return None
def prezzi(f):
    d=car(f)
    if not isinstance(d,list) or not d: return {}
    k="t" if "t" in d[0] else ("T" if "T" in d[0] else None)
    return {int(x[k]): x["c"] for x in d} if k else {}
dati=[]
for f in sorted(glob.glob("data/finanziamento_binance/*.json")):
    s=os.path.basename(f).replace(".json","")
    fb=car(f); fh=car(f"data/finanziamento/{s}.json")
    pb=prezzi(f"data/binance/{s}USDT.json"); ph=prezzi(f"data/candele3/{s}.json")
    if not fb or not fh or not pb or not ph: continue
    oraria={int(x["time"])//3600000*3600000: float(x["fundingRate"]) for x in fh}
    B=sorted((int(x["t"]), x["r"]) for x in fb); tassi=dict(B)
    hl8={}
    for t,_ in B:
        v=[oraria[t-i*3600000] for i in range(8) if t-i*3600000 in oraria]
        if len(v)==8: hl8[t]=sum(v)
    ts=[t for t,_ in B if t in hl8]
    dati.append((s,ts,tassi,hl8,pb,ph))
print(f"   {len(dati)} monete\n")
def prova(soglia):
    g=[]
    for s,ts,tassi,hl8,pb,ph in dati:
        lib=0
        for i in range(1,len(ts)-TEN):
            if i<lib: continue
            prec=tassi[ts[i-1]]-hl8[ts[i-1]]
            if abs(prec)<soglia: continue
            v=1 if prec>0 else -1
            inc=sum(v*(tassi[ts[j]]-hl8[ts[j]]) for j in range(i,i+TEN))
            t0,t1=ts[i],ts[i+TEN]
            if not all(t in pb and t in ph for t in (t0,t1)): continue
            sc=v*((ph[t1]/pb[t1]-1)-(ph[t0]/pb[t0]-1))
            g.append(inc+sc-COSTO); lib=i+TEN
    if len(g)<60: return None
    m=st.mean(g)*100; e=1.96*st.stdev(g)/math.sqrt(len(g))*100
    return len(g), m, e, (m/7*365)
print(f"   {'soglia 8h':>11}{'posizioni':>11}{'netto 7gg':>14}{'all anno':>12}")
for soglia in (0.0, 0.0002, 0.0005, 0.001, 0.002, 0.004):
    r=prova(soglia)
    if not r: print(f"   {soglia*100:>10.2f}%   troppo poche"); continue
    n,m,e,an=r
    print(f"   {soglia*100:>10.2f}%{n:>11}  {m:+.4f}% +/-{e:.4f}  {an:>+8.1f}%  "
          f"{'' if m-e>0 else '(non dim.)'}")
