"""La prova registrata: oro e rame sui dati GIORNALIERI, mai usati.

I candidati vengono dalle candele orarie, dove la ricerca su 126 regole ha
bruciato la cassaforte. Questa serie e' diversa per fonte e per frequenza.
Confronto contro IL CASO sullo stesso mercato, non contro zero.
"""
import json, statistics as st, random
random.seed(11); COSTO=0.0005
def carica(f):
    D=json.load(open(f))
    c=[x for x in D["c"] if x]; h=[x for x in D["h"] if x]; l=[x for x in D["l"] if x]
    n=min(len(c),len(h),len(l)); return c[:n],h[:n],l[:n],n
PROVE=[("oro","data/mercati/GC_F_1d.json","rottura max 24",
        lambda c,h,l,i: c[i]>max(h[i-24:i]), [6,24]),
       ("rame","data/mercati/HG_F_1d.json","rottura min 24",
        lambda c,h,l,i: c[i]<min(l[i-24:i]), [6,24,72])]
print("   mercato  regola            oriz    regola      il CASO    DIFFERENZA        esito")
for nome,f,et,fn,oriz in PROVE:
    c,h,l,n=carica(f)
    for o in oriz:
        idx=[i for i in range(100,n-o-1) if fn(c,h,l,i)]
        v=[(c[i+o]/c[i]-1)-COSTO for i in idx]
        if len(v)<30:
            print(f"   {nome:<8} {et:<17} {o:>3}   troppo pochi casi ({len(v)})"); continue
        casi=[(c[i+o]/c[i]-1)-COSTO for i in random.sample(range(100,n-o-1), min(2000,n-105-o))]
        d=st.mean(v)-st.mean(casi)
        e=1.96*((st.stdev(v)**2/len(v))+(st.stdev(casi)**2/len(casi)))**0.5
        esito = "SOPRA IL CASO" if d-e>0 else ("sotto" if d+e<0 else "non dimostrato")
        print(f"   {nome:<8} {et:<17} {o:>3}  {st.mean(v)*100:+7.3f}%  {st.mean(casi)*100:+7.3f}%  "
              f"{d*100:+7.3f}% +/-{e*100:5.3f}  {esito}  n={len(v)}")
