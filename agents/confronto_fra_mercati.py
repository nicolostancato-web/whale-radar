"""IDEA NUOVA: non «questo mercato sale?» ma «quali fra diciannove battono gli altri?»

Difetto di tutto cio' che ho provato finora: ogni regola compra e tiene, quindi
eredita la marea del mercato (la trappola dell'argento). Questa forma non puo'
averlo: si compra la meta' alta di una classifica e si vende allo scoperto la
meta' bassa, quindi il movimento comune si cancella per costruzione.

Si prova una classifica sola, dichiarata prima: il rendimento passato su N
giorni. Due versi possibili, e si guardano ENTRAMBI senza sceglierne uno dopo:
  - continuazione: compra chi e' salito, vende chi e' sceso
  - ritorno: il contrario
Costo: 0,05% per gamba, quindi 0,1% per ogni ribilanciamento (due gambe).
"""
import json, glob, os, statistics as st
# lungo-corto = 4 gambe: apri il lungo, apri il corto, chiudili entrambi.
# Il codice piu' sotto fa 2*COSTO_GAMBA, quindi qui si mette il costo per LATO
# (2 gambe x 0,05%), cosi' il totale e' 4 x 0,05% = 0,20%.
COSTO_GAMBA=2*0.0005
NOMI={"GC_F":"oro","HG_F":"rame","SI_F":"argento","PL_F":"platino","PA_F":"palladio",
      "ALI_F":"alluminio","CL_F":"petrolio","NG_F":"gas","HO_F":"gasolio","RB_F":"benzina",
      "ZW_F":"grano","ZC_F":"mais","ZS_F":"soia","CT_F":"cotone","SB_F":"zucchero",
      "KC_F":"caffe","CC_F":"cacao","LE_F":"bovini"}
serie={}
for f in sorted(glob.glob("data/mercati/*_1d.json")):
    base=os.path.basename(f).replace("_1d.json","")
    if base not in NOMI: continue      # solo materie prime: l'EUR/USD non sta in classifica
    D=json.load(open(f)); t=D["t"]; c=D["c"]
    serie[base]={tt:cc for tt,cc in zip(t,c) if cc}
giorni=sorted(set.intersection(*[set(v) for v in serie.values()]))
print(f"{len(serie)} mercati, {len(giorni)} giorni in comune "
      f"(solo le date presenti in TUTTI: altrimenti si confrontano insiemi diversi)\n")
def prova(guardo, tengo, verso):
    res=[]
    for k in range(guardo, len(giorni)-tengo, tengo):
        d0,d1,d2 = giorni[k-guardo], giorni[k], giorni[k+tengo]
        cls=sorted(serie, key=lambda s: serie[s][d1]/serie[s][d0]-1, reverse=(verso=="continuazione"))
        q=max(1,len(cls)//3)
        lunghi, corti = cls[:q], cls[-q:]
        rl=st.mean([serie[s][d2]/serie[s][d1]-1 for s in lunghi])
        rc=st.mean([serie[s][d2]/serie[s][d1]-1 for s in corti])
        res.append((rl-rc) - 2*COSTO_GAMBA)
    if len(res)<20: return None
    m=st.mean(res)*100; e=1.96*st.stdev(res)/len(res)**0.5*100
    return m,e,len(res)
print("   verso          guardo  tengo    resa per ciclo        esito")
for verso in ("continuazione","ritorno"):
    for guardo,tengo in ((20,20),(60,20),(120,20),(60,60),(120,60),(250,60)):
        r=prova(guardo,tengo,verso)
        if not r: continue
        m,e,n=r
        esito = "SOPRA ZERO" if m-e>0 else ("sotto zero" if m+e<0 else "non dimostrato")
        print(f"   {verso:<14} {guardo:>5}g {tengo:>5}g   {m:+7.3f}% +/-{e:5.3f} n={n:<4} {esito}")
print("\n   NB: lungo-corto, quindi il movimento comune delle materie prime e' gia' tolto.")
print("       12 prove: attesi ~0,3 falsi positivi.")
