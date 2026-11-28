"""Il confronto giusto non e' contro zero: e' contro IL CASO sullo stesso
mercato e nello stesso periodo.

Allarme che ha imposto la correzione: sull'argento a 72h erano positive quattro
regole che dicono cose opposte (rottura di massimo E tre cali di fila). Regole
contrarie non possono avere ragione insieme: vuol dire che in quel periodo
l'argento saliva, e tutte le regole comprano-e-tengono, quindi ereditano la
marea. Misuravo la deriva del mercato, non un vantaggio.

Quindi per ogni mercato e orizzonte si calcola la resa di 2.000 entrate A CASO
e si riporta la DIFFERENZA. Quella e' il vantaggio, se c'e'.
"""
import json, glob, statistics as st, random, os
# 2 gambe x 0,05% = 0,10%. Prima: una gamba sola.
COSTO=2*0.0005; random.seed(7)
REGOLE={
 "rottura max 24h":  lambda c,h,l,i: c[i] > max(h[i-24:i]),
 "rottura min 24h":  lambda c,h,l,i: c[i] < min(l[i-24:i]),
 "rottura max 72h":  lambda c,h,l,i: c[i] > max(h[i-72:i]),
 "3 cali di fila":   lambda c,h,l,i: c[i]<c[i-1]<c[i-2]<c[i-3],
 "3 salite di fila": lambda c,h,l,i: c[i]>c[i-1]>c[i-2]>c[i-3],
 "espansione vol":   lambda c,h,l,i: (h[i]-l[i]) > 2*st.mean([h[j]-l[j] for j in range(i-24,i)]),
}
ORIZZONTI=[6,24,72]
NOMI={"EURUSD_X":"EUR/USD","HG_F":"rame","CL_F":"petrolio","GC_F":"oro",
      "NG_F":"gas","SI_F":"argento","ZW_F":"grano"}
prove=0; sopra=[]
print("   mercato    regola              oriz    regola      il CASO     DIFFERENZA")
for f in sorted(glob.glob("data/mercati/*_1h.json")):
    base=os.path.basename(f).replace("_1h.json","")
    D=json.load(open(f))
    c=[x for x in D["c"] if x]; h=[x for x in D["h"] if x]; l=[x for x in D["l"] if x]
    n=min(len(c),len(h),len(l)); c,h,l=c[:n],h[:n],l[:n]
    if n<2000: continue
    meta=n//2+100
    for o in ORIZZONTI:
        casi=[(c[i+o]/c[i]-1)-COSTO for i in random.sample(range(meta,n-o-1), min(2000,n-meta-o-2))]
        base_m=st.mean(casi); base_sd=st.stdev(casi)
        for nome,fn in REGOLE.items():
            prove+=1
            idx=[i for i in range(meta,n) if fn(c,h,l,i)]
            v=[(c[i+o]/c[i]-1)-COSTO for i in idx if i+o<n]
            if len(v)<40: continue
            d=st.mean(v)-base_m
            # errore della differenza fra due medie indipendenti
            e=1.96*((st.stdev(v)**2/len(v))+(base_sd**2/len(casi)))**0.5
            if d-e>0:
                sopra.append((NOMI.get(base,base),nome,o,d*100,e*100,len(v)))
                print(f"   {NOMI.get(base,base):<10} {nome:<19} {o:>3}h  {st.mean(v)*100:+7.3f}%  "
                      f"{base_m*100:+7.3f}%   {d*100:+7.3f}% +/-{e*100:5.3f}  <-- sopra il caso")
print(f"\n   prove: {prove} | attesi per caso: ~{prove*0.025:.0f} | trovati sopra il caso: {len(sopra)}")
if not sopra:
    print("   -> NESSUNA regola batte le entrate a caso. I positivi di prima erano la marea.")
