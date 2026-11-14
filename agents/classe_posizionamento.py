"""Prova di CLASSE sul posizionamento: non una regola, ma una famiglia intera,
ognuna confrontata con se stessa a orari rimescolati.

Disegno (lezioni gia' pagate):
  - UN VERSO SOLO (lungo): il doppio verso azzera la mediana per identita'
    e non puo' mai mostrare un vantaggio direzionale;
  - osservazioni NON sovrapposte;
  - entrata un'ora DOPO il segnale, perche' il dato orario si conosce alla
    fine dell'ora e l'ordine parte dopo;
  - controllo appaiato: stesso numero di entrate lunghe, a orari a caso.

Variabili: interesse aperto (oi), rapporto conti lunghi/corti (ls),
quota di volume aggressivo in acquisto (tk). In livello (percentile su
finestra mobile) e in variazione (su 6 e 24 ore).
"""
import json, glob, os, statistics as st, math, random
random.seed(913)
def serie(f):
    d=json.load(open(f))
    pr={int(x["t"]): x["c"] for x in d["c"]}
    out={}
    for k,campo in [("oi","sumOpenInterestValue"),("ls","longShortRatio"),("tk","buySellRatio")]:
        out[k]={int(x["timestamp"])//3600000*3600000: float(x[campo]) for x in d[k]}
    ore=sorted(set(pr) & set(out["oi"]) & set(out["ls"]) & set(out["tk"]))
    if len(ore)<300: return None
    return ore, pr, out
D=[]
for f in sorted(glob.glob("data/posizionamento/*.json")):
    try: s=serie(f)
    except Exception: continue
    if s: D.append(s)
print(f"   {len(D)} mercati | {sum(len(x[0]) for x in D):,} ore\n")
L=120   # finestra per i percentili
def segnali(ore, v, tipo, q, dt):
    out=[]
    for i in range(L, len(ore)):
        if dt:
            if i-dt < 0: continue
            a=v.get(ore[i]); b=v.get(ore[i-dt])
            if a is None or b is None or b==0: continue
            x=a/b-1
            st_=[ (v[ore[j]]/v[ore[j-dt]]-1) for j in range(i-L,i)
                  if v.get(ore[j]) and v.get(ore[j-dt]) ]
        else:
            x=v.get(ore[i])
            st_=[v[ore[j]] for j in range(i-L,i) if ore[j] in v]
        if x is None or len(st_)<L//2: continue
        st_=sorted(st_); s=st_[int(q*(len(st_)-1))]
        if (x>=s if tipo=="alto" else x<=s): out.append(i)
    return out
def valuta(idx_f, oriz):
    veri=[]; casi=[]
    for ore, pr, v in D:
        idx=idx_f(ore, v)
        lib=0; n=0
        for i in idx:
            if i<lib or i+1+oriz>=len(ore): continue
            a,b=ore[i+1], ore[i+1+oriz]
            if b-a != oriz*3600000: continue
            veri.append(pr[b]/pr[a]-1); lib=i+1+oriz; n+=1
        if n<3: continue
        ks=sorted(random.sample(range(L, len(ore)-oriz-2), min(n, len(ore)-L-oriz-3)))
        lib=0
        for i in ks:
            if i<lib: continue
            a,b=ore[i+1], ore[i+1+oriz]
            if b-a != oriz*3600000: continue
            casi.append(pr[b]/pr[a]-1); lib=i+1+oriz
    if len(veri)<150 or len(casi)<150: return None
    def t(v): 
        s=st.stdev(v); return st.mean(v)/(s/math.sqrt(len(v))) if s>0 else 0
    return len(veri), t(veri), t(casi)
RISU=[]
for var in ("oi","ls","tk"):
    for dt in (0,6,24):
        for q,tipo in ((0.90,"alto"),(0.95,"alto"),(0.10,"basso"),(0.05,"basso")):
            for oriz in (4,12,24):
                r=valuta(lambda ore,v,var=var,tipo=tipo,q=q,dt=dt:
                         segnali(ore, v[var], tipo, q, dt), oriz)
                if r: RISU.append((var,dt,tipo,q,oriz)+r)
print(f"   {len(RISU)} prove appaiate\n")
for var in ("oi","ls","tk"):
    sub=[x for x in RISU if x[0]==var]
    if not sub: continue
    tv=sorted(x[6] for x in sub); tc=sorted(x[7] for x in sub)
    print(f"   {var}  ({len(sub)} prove)")
    print(f"      vere        mediana {st.median(tv):+6.3f}  "
          f"[{tv[int(.05*len(tv))]:+6.2f},{tv[int(.95*len(tv))]:+6.2f}]")
    print(f"      rimescolate mediana {st.median(tc):+6.3f}")
    print(f"      DIFFERENZA  {st.median(tv)-st.median(tc):+6.3f}")
