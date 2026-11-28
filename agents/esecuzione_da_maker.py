"""Le esecuzioni da fornitore di liquidita': quante volte si viene presi, e
cosa succede quando si viene presi rispetto a quando no.

Tutto il margine del candidato dipende da questo, e finora l'avevo assunto.
Prova: all'ora k metto un ordine di ACQUISTO al prezzo di chiusura di k.
  - vengo eseguito se il MINIMO dell'ora k+1 scende fino a quel prezzo
  - poi guardo il rendimento nelle 12 ore successive
Se il rendimento di chi viene eseguito e' PEGGIORE di quello di chi compra
subito al prezzo di mercato, quella differenza e' la selezione avversa, e va
tolta dal risparmio di commissione (0,06% per gamba).
"""
import json, glob, os, statistics as st, math
D=[]
for f in sorted(glob.glob("data/binance_hl/*.json")):
    d=json.load(open(f))
    if len(d)>3000: D.append((os.path.basename(f)[:-5], d))
print(f"{len(D)} mercati | {sum(len(x[1]) for x in D):,} ore\n")
ORIZ=12
presi=[]; nonpresi=[]; subito=[]
for nome,d in D:
    for k in range(1, len(d)-ORIZ-2, 7):          # un campione ogni 7 ore: niente sovrapposizioni
        p=d[k]["c"]
        if d[k+1]["l"] <= p:                       # l'ordine di acquisto viene toccato
            presi.append(d[k+1+ORIZ]["c"]/p-1)
        else:
            nonpresi.append(d[k+1+ORIZ]["c"]/p-1)
        subito.append(d[k+ORIZ]["c"]/d[k]["c"]-1)  # chi compra subito al mercato
tot=len(presi)+len(nonpresi)
print(f"   ordini eseguiti: {len(presi):,} su {tot:,}  ({len(presi)/tot:.1%})")
def riga(et,v):
    m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
    print(f"   {et:<34} {m:+7.4f}% +/-{e:6.4f}  n={len(v):,}")
riga("chi viene ESEGUITO (12h dopo)", presi)
riga("chi NON viene eseguito (12h dopo)", nonpresi)
riga("chi compra subito al mercato", subito)
sa=(st.mean(presi)-st.mean(subito))*100
print(f"\n   selezione avversa = eseguito meno mercato = {sa:+.4f}%")
print(f"   risparmio di commissione mettendo l'ordine:        +0.0600%")
print(f"   NETTO del mettere l'ordine invece di prenderlo:    {0.06+sa:+.4f}%")
print("   -> " + ("conviene mettere l'ordine" if 0.06+sa>0 else
      "NON conviene: la selezione avversa supera il risparmio"))
