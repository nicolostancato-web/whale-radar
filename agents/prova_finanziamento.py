"""Il posizionamento della folla, letto dal tasso di finanziamento.

Ipotesi, dichiarata prima: quando il tasso e' molto positivo i lunghi pagano i
corti, cioe' la folla e' da una parte sola. Mettersi dall'altra parte da' DUE
pezzi di guadagno: l'eventuale movimento del prezzo E il finanziamento
incassato mentre si aspetta. Si contano entrambi.

Regole fissate prima:
  - segnale: tasso oltre il 90esimo (o sotto il 10esimo) percentile delle
    ultime 500 ore DI QUEL MERCATO — soglia relativa, nota prima di entrare
  - verso contrario: tasso alto -> corto; tasso basso -> lungo
  - orizzonti 8, 24, 72 ore; osservazioni NON sovrapposte
  - costo 0,094% a giro (4,7 punti base per gamba, misura pubblica su Hyperliquid)
  - confronto contro entrate a caso sullo stesso mercato
  - si stampa anche il verso OPPOSTO: i due devono mediarsi a -costo se non
    c'e' segnale. E' la riga di taratura.
"""
import json, glob, os, statistics as st, random
random.seed(29); COSTO=0.00094
mercati=[]
for f in sorted(glob.glob("data/finanziamento/*.json")):
    c=os.path.basename(f).replace(".json","")
    p=f"data/candele_hl/{c}.json"
    if not os.path.exists(p): continue
    fnd={x["time"]//3600000: float(x["fundingRate"]) for x in json.load(open(f))}
    prz={x["t"]//3600000: x["c"] for x in json.load(open(p))}
    ore=sorted(set(fnd)&set(prz))
    if len(ore)>1500: mercati.append((c,fnd,prz,ore))
print(f"{len(mercati)} mercati con tasso E prezzo allineati "
      f"({sum(len(m[3]) for m in mercati):,} ore in comune)\n")
def prova(verso, oriz):
    v=[]
    for c,fnd,prz,ore in mercati:
        storia=[]; libero=0
        for k,o in enumerate(ore):
            storia.append(fnd[o])
            if k<500 or k>=len(ore)-oriz or k<libero: continue
            fin=sorted(storia[-500:])
            alto, basso = fin[int(0.9*len(fin))], fin[int(0.1*len(fin))]
            t=fnd[o]
            if t>=alto: seg=-1
            elif t<=basso: seg=+1
            else: continue
            if verso=="con la folla": seg=-seg
            o2=ore[k+oriz]
            mov=seg*(prz[o2]/prz[o]-1)
            # il finanziamento: chi e' corto INCASSA quando il tasso e' positivo
            flusso=sum(-seg*fnd[x] for x in ore[k:k+oriz] if x in fnd)*-1
            v.append(mov+flusso-COSTO)
            libero=k+oriz
    if len(v)<200: return None
    return st.mean(v)*100, 1.96*st.stdev(v)/len(v)**0.5*100, len(v)
print("   verso            oriz     resa media            esito")
for verso in ("contro la folla","con la folla"):
    for oriz in (8,24,72):
        r=prova(verso,oriz)
        if not r: continue
        m,e,n=r
        esito="SOPRA ZERO" if m-e>0 else ("sotto zero" if m+e<0 else "non dimostrato")
        print(f"   {verso:<16} {oriz:>3}h   {m:+7.4f}% +/-{e:6.4f} n={n:<6} {esito}")
print("\n   i due versi devono mediarsi a -0,094% se non c'e' segnale: e' la taratura.")
