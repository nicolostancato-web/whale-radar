"""La selezione avversa, misurata su orizzonti ALLINEATI.

Difetto del primo tentativo: confrontavo chi viene eseguito (finestra che parte
a k+1) con chi compra al mercato (finestra che parte a k). Due orizzonti
diversi: la differenza mescolava la selezione avversa con uno sfasamento.

Qui entrambi finiscono allo STESSO istante k+1+ORIZ, e si confronta il prezzo
di ingresso: chi mette l'ordine entra a p (prezzo di chiusura di k) se viene
toccato; chi prende il prezzo entra alla chiusura di k+1. Stessa uscita.
"""
import json, glob, os, statistics as st, math
D=[]
for f in sorted(glob.glob("data/binance_hl/*.json")):
    d=json.load(open(f))
    if len(d)>3000: D.append((os.path.basename(f)[:-5], d))
ORIZ=12
mk=[]; tk=[]; persi=[]
for nome,d in D:
    for k in range(1, len(d)-ORIZ-3, 7):
        p=d[k]["c"]; uscita=d[k+1+ORIZ]["c"]
        tk.append(uscita/d[k+1]["c"]-1)              # prende il prezzo: entra a k+1
        if d[k+1]["l"] <= p: mk.append(uscita/p-1)   # mette l'ordine: entra a p
        else: persi.append(uscita/d[k+1]["c"]-1)     # non eseguito: resta fuori
print(f"   {len(D)} mercati | uscita comune a k+1+{ORIZ}\n")
def riga(et,v):
    if not v: print(f"   {et:<36} nessun caso"); return None
    m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
    print(f"   {et:<36} {m:+7.4f}% +/-{e:6.4f}  n={len(v):,}")
    return m
a=riga("mette l'ordine ed e' eseguito", mk)
b=riga("prende il prezzo (stessa uscita)", tk)
riga("i casi NON eseguiti", persi)
print(f"\n   quota eseguita: {len(mk)/(len(mk)+len(persi)):.1%}")
print(f"   differenza di prezzo d'ingresso (eseguito - mercato): {a-b:+.4f}%")
print(f"   risparmio di commissione per gamba:                   +0.0300%")
print(f"   NETTO per gamba:                                      {0.03+(a-b):+.4f}%")
print("\n   NB: si assume di essere in coda al prezzo di chiusura. In un libro")
print("       vero si sta dietro ad altri ordini, quindi la quota eseguita e'")
print("       un LIMITE SUPERIORE.")
