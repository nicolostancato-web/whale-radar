"""Le STESSE due regole registrate, su mercati che non hanno mai visto.

Nessuna regola nuova: cambiano solo i mercati. Se l'effetto e' vero, mettendo
insieme tanti mercati la media resta positiva e l'intervallo si stringe; se e'
rumore, si annulla. Il confronto resta contro IL CASO sullo stesso mercato.
"""
import json, glob, os, statistics as st, random
random.seed(13); COSTO=0.0005
NOMI={"GC_F":"oro","HG_F":"rame","SI_F":"argento","PL_F":"platino","PA_F":"palladio",
      "ALI_F":"alluminio","CL_F":"petrolio","NG_F":"gas","HO_F":"gasolio","RB_F":"benzina",
      "ZW_F":"grano","ZC_F":"mais","ZS_F":"soia","CT_F":"cotone","SB_F":"zucchero",
      "KC_F":"caffe","CC_F":"cacao","LE_F":"bovini","EURUSD_X":"EUR/USD"}
REGOLE=[("rottura max 24", lambda c,h,l,i: c[i]>max(h[i-24:i])),
        ("rottura min 24", lambda c,h,l,i: c[i]<min(l[i-24:i]))]
ORIZ=[6,24]
def diff(c,h,l,n,fn,o):
    idx=[i for i in range(100,n-o-1) if fn(c,h,l,i)]
    v=[(c[i+o]/c[i]-1)-COSTO for i in idx]
    if len(v)<30: return None
    casi=[(c[i+o]/c[i]-1)-COSTO for i in random.sample(range(100,n-o-1), min(3000,n-105-o))]
    d=st.mean(v)-st.mean(casi)
    e=1.96*((st.stdev(v)**2/len(v))+(st.stdev(casi)**2/len(casi)))**0.5
    return d,e,len(v)
for et,fn in REGOLE:
    for o in ORIZ:
        righe=[]
        for f in sorted(glob.glob("data/mercati/*_1d.json")):
            base=os.path.basename(f).replace("_1d.json","")
            D=json.load(open(f))
            c=[x for x in D["c"] if x]; h=[x for x in D["h"] if x]; l=[x for x in D["l"] if x]
            n=min(len(c),len(h),len(l)); c,h,l=c[:n],h[:n],l[:n]
            if n<800: continue
            r=diff(c,h,l,n,fn,o)
            if r: righe.append((NOMI.get(base,base), r[0]*100, r[1]*100, r[2]))
        if not righe: continue
        ds=[x[1] for x in righe]
        pos=sum(1 for x in ds if x>0)
        m=st.mean(ds); e=1.96*st.stdev(ds)/len(ds)**0.5
        print(f"\n   {et}, orizzonte {o}  —  {len(righe)} mercati")
        print(f"      positivi: {pos}/{len(righe)}")
        print(f"      differenza media fra i mercati: {m:+.3f}% +/- {e:.3f}")
        print(f"      -> {'SOPRA IL CASO su un insieme di mercati' if m-e>0 else 'non dimostrato'}")
        righe.sort(key=lambda x:-x[1])
        print("      migliori: " + ", ".join(f"{x[0]} {x[1]:+.2f}%" for x in righe[:4]))
        print("      peggiori: " + ", ".join(f"{x[0]} {x[1]:+.2f}%" for x in righe[-3:]))
