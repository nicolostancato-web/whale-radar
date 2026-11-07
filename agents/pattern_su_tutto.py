"""Gli stessi pattern su piu' mercati. 108 prove: la meta' mai vista e' la difesa.

Cercando fra centinaia di configurazioni se ne trovano sempre alcune positive
per caso. Quindi: si CONTANO le prove, si guarda SOLO la seconda meta', e si
promuove un candidato solo se li' il suo intervallo sta sopra lo zero.
Costo di giro 0,05% (misurato su gTrade; su trade.xyz sarebbe 0,018%).
"""
import json, glob, statistics as st, random, os
# 2 gambe (apri + chiudi) x 0,05% per gamba su futures Binance = 0,10%
# PRIMA era 0,0005: una gamba sola. Verdetti invariati (erano gia' negativi).
COSTO=2*0.0005
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
prove=0; promossi=[]
print("   mercato    regola              oriz   SECONDA META' (mai vista)")
for f in sorted(glob.glob("data/mercati/*_1h.json")):
    base=os.path.basename(f).replace("_1h.json","")
    D=json.load(open(f))
    c=[x for x in D["c"] if x]; h=[x for x in D["h"] if x]; l=[x for x in D["l"] if x]
    n=min(len(c),len(h),len(l)); c,h,l=c[:n],h[:n],l[:n]
    if n<2000: continue
    for nome,fn in REGOLE.items():
        for o in ORIZZONTI:
            prove+=1
            idx=[i for i in range(n//2+100,n) if fn(c,h,l,i)]
            v=[(c[i+o]/c[i]-1)-COSTO for i in idx if i+o<n]
            if len(v)<40: continue
            m=st.mean(v)*100; e=1.96*st.stdev(v)/len(v)**0.5*100
            segna = "  <-- sopra zero" if m-e>0 else ""
            if m-e>0: promossi.append((NOMI.get(base,base),nome,o,m,e,len(v)))
            if m-e>0 or abs(m)>0.15:
                print(f"   {NOMI.get(base,base):<10} {nome:<19} {o:>3}h  {m:+7.4f}% +/-{e:5.4f} n={len(v):<5}{segna}")
print(f"\n   prove totali: {prove}")
print(f"   candidati col margine sopra zero sulla meta' mai vista: {len(promossi)}")
print(f"   attesi per puro caso a questo numero di prove: ~{prove*0.025:.0f}")
for p in promossi: print(f"      {p[0]} / {p[1]} / {p[2]}h : {p[3]:+.4f}% +/- {p[4]:.4f}")
