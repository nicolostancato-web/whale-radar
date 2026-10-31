"""La stessa prova fra-mercati, su 99 azioni invece di 18 materie prime.

Perche': con 18 mercati l'intervallo era +/-4,9% e non poteva decidere nulla.
Con 99 titoli la classifica e' molto piu' stabile e il quintile e' di 20 nomi.
Nessuna regola nuova: stessa classifica (rendimento passato), stessi due versi,
stessi costi. Cambia solo la potenza.
Lungo-corto, quindi il movimento comune del mercato azionario e' gia' tolto.
"""
import json, glob, os, statistics as st
# lungo-corto = 4 gambe; il codice moltiplica per 2 -> 2 per lato = 4 totali
COSTO_GAMBA=2*0.0005
serie={}
for f in sorted(glob.glob("data/azioni/*.json")):
    s=os.path.basename(f).replace(".json","")
    D=json.load(open(f))
    d={tt:cc for tt,cc in zip(D["t"],D["c"]) if cc}
    if len(d)>2000: serie[s]=d
giorni=sorted(set.intersection(*[set(v) for v in serie.values()]))
print(f"{len(serie)} azioni, {len(giorni)} giorni in comune\n")
def prova(guardo,tengo,verso,frazione=5):
    res=[]
    for k in range(guardo, len(giorni)-tengo, tengo):
        d0,d1,d2 = giorni[k-guardo], giorni[k], giorni[k+tengo]
        cls=sorted(serie, key=lambda s: serie[s][d1]/serie[s][d0]-1, reverse=(verso=="continuazione"))
        q=max(2,len(cls)//frazione)
        rl=st.mean([serie[s][d2]/serie[s][d1]-1 for s in cls[:q]])
        rc=st.mean([serie[s][d2]/serie[s][d1]-1 for s in cls[-q:]])
        res.append((rl-rc) - 2*COSTO_GAMBA)
    if len(res)<20: return None
    return st.mean(res)*100, 1.96*st.stdev(res)/len(res)**0.5*100, len(res)
print("   verso          guardo  tengo    resa per ciclo        esito")
for verso in ("continuazione","ritorno"):
    for guardo,tengo in ((20,20),(60,20),(120,20),(250,20),(60,60),(250,60)):
        r=prova(guardo,tengo,verso)
        if not r: continue
        m,e,n=r
        esito="SOPRA ZERO" if m-e>0 else ("sotto zero" if m+e<0 else "non dimostrato")
        print(f"   {verso:<14} {guardo:>5}g {tengo:>5}g   {m:+7.3f}% +/-{e:5.3f} n={n:<4} {esito}")
print("\n   12 prove, e i due versi sono speculari: le prove indipendenti sono 6.")
