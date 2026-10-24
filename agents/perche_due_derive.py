"""Perche' due campioni quasi identici danno -1,35% e -0,63%?

Sospetto preciso: nella versione "posizioni" le monete senza una stampa di
VENDITA nella finestra valgono -100% (regola: le impiccate non si scartano);
nella versione "deriva" venivano ESCLUSE. Se sono l'1% del campione, da sole
spostano la media di un punto, che e' quasi tutto il divario.
Qui le due versioni si calcolano sullo STESSO insieme, cambiando solo quella
regola, cosi' il confronto isola una variabile sola.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO); DUE=int(120/BLOCCO)
tutte=[]; impiccate=0
for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
    with gzip.open(f,"rt") as fh:
        for riga in fh:
            try: d=json.loads(riga)
            except Exception: continue
            s=d.get("s") or []; dip=d.get("diploma")
            if not dip: continue
            P=[(b,abs(a0/a1),a0<0) for b,a0,a1,_ in s if a1 and a0]
            if len(P)<3: continue
            b_ent=dip+RITARDO
            ent=next((p for b,p,_v in P if b>=b_ent), None)
            if ent is None or ent<=0: continue
            usc=None
            for b,p,v in P:
                if b_ent<b<=b_ent+DUE and v: usc=p
            if usc is None: impiccate+=1; tutte.append(None)
            else: tutte.append(max((usc/ent)**0.5-1,-1.0))
n=len(tutte)
print(f"monete: {n:,} | senza una stampa di VENDITA nella finestra: {impiccate:,} ({impiccate/n:.2%})\n")
scartando=[x for x in tutte if x is not None]
contando=[(-1.0 if x is None else x) for x in tutte]
for nome,v in (("SCARTANDO le impiccate (sbagliato)",scartando),
               ("CONTANDOLE a -100% (la regola)",contando)):
    sd=st.stdev(v)
    print(f"   {nome:<36} n={len(v):>5}  media {st.mean(v)*100:+6.2f}%  +/- {1.96*sd/len(v)**0.5*100:.2f}")
d=(st.mean(contando)-st.mean(scartando))*100
print(f"\n   differenza dovuta SOLO a questa regola: {d:+.2f} punti")
print("   -> " + ("spiega il divario: la stima giusta e' quella piu' bassa"
      if abs(d)>0.4 else "non basta a spiegare il divario: cercare altrove"))
print(f"\n   NETTO con la stima corretta = +2,09 {st.mean(contando)*100:+.2f} = "
      f"{2.09+st.mean(contando)*100:+.2f}%   (intervallo "
      f"[{2.09-0.09+st.mean(contando)*100-1.96*st.stdev(contando)/len(contando)**0.5*100:+.2f} , "
      f"{2.09+0.09+st.mean(contando)*100+1.96*st.stdev(contando)/len(contando)**0.5*100:+.2f}])")
