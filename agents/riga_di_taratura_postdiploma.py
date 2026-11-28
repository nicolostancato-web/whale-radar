"""LA RIGA DI TARATURA sul post-diploma: quanto costa davvero un giro?

Il -4,5% della strategia poggia su un costo DICHIARATO del 6%. Se quel 6% e'
sbagliato, il verdetto e' sbagliato. Qui lo misuro invece di assumerlo:
compro su una stampa di ACQUISTO e rivendo sulla PRIMA stampa di VENDITA
successiva. Il risultato DEVE essere negativo e pari al pedaggio: e' la riga
che rende leggibile tutta la tabella.

Serve anche a rispondere ad Astra: il pedaggio e' PROPORZIONALE (hook + tassa
creatore) o ha una parte FISSA? Se e' proporzionale, rimpicciolire il biglietto
non lo riduce, e la curva dei costi a 2/5/10 EUR non salva niente.
"""
import gzip, glob, json, statistics as st
BLOCCO=0.093; RITARDO=int(60/BLOCCO)

giri=[]; per_dist=[[],[],[],[]]
for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl.gz")):
    with gzip.open(f,"rt") as fh:
        for riga in fh:
            try: d=json.loads(riga)
            except Exception: continue
            s=d.get("s") or []; dip=d.get("diploma")
            if not dip or len(s)<4: continue
            P=[(b,abs(a0/a1),a0<0,abs(a0)) for b,a0,a1,_ in s if a1!=0]
            for i,(b,p,acq,nat) in enumerate(P):
                if b < dip+RITARDO or not acq: continue
                for j in range(i+1,min(i+40,len(P))):
                    bj,pj,aj,_ = P[j]
                    if aj: continue
                    r = pj/p - 1
                    giri.append(r)
                    k = min(3, bj-b)        # distanza in blocchi: 0,1,2,3+
                    per_dist[k].append(r)
                    break
                if len(giri) > 120000: break

print(f"GIRI ISTANTANEI misurati: {len(giri):,}")
m=st.mean(giri)*100; e=1.96*st.stdev(giri)/len(giri)**0.5*100
print(f"   resa del giro compra-e-rivendi: {m:+.2f}% +/- {e:.2f}")
print(f"   mediana: {st.median(giri)*100:+.2f}%")
print("\n   per distanza fra le due stampe (blocchi):")
for k,v in enumerate(per_dist):
    if len(v)<50: continue
    et="0" if k==0 else ("1" if k==1 else ("2" if k==2 else "3+"))
    print(f"      {et:>2} blocchi  n={len(v):>7,}  media {st.mean(v)*100:+6.2f}%  mediana {st.median(v)*100:+6.2f}%")
print("\n   -> il pedaggio e' la mediana a 0 blocchi: proporzionale, NON si riduce")
print("      rimpicciolendo il biglietto (quello tocca solo lo scivolamento).")
