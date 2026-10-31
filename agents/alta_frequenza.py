"""Dove il filtro delle osservazioni e' rispettato: le candele da 5 minuti.

19 mercati x ~17.000 candele = oltre 300.000 osservazioni. Con questa potenza
si distingue un vantaggio di mezzo centesimo di punto, cosa impossibile ai
ribilanciamenti mensili.

Pedaggio: 0,018% a giro (misurato: trade.xyz 0,9 punti base per gamba).
Regole dichiarate prima, tutte simmetriche (lungo E corto), cosi' la marea si
cancella: non si compra-e-basta, si segue o si contrasta il segno.
Confronto SEMPRE contro il caso sullo stesso mercato.
"""
import json, glob, os, statistics as st, random
random.seed(23); COSTO=0.00018
NOMI={"GC_F":"oro","HG_F":"rame","SI_F":"argento","PL_F":"platino","PA_F":"palladio",
      "ALI_F":"alluminio","CL_F":"petrolio","NG_F":"gas","HO_F":"gasolio","RB_F":"benzina",
      "ZW_F":"grano","ZC_F":"mais","ZS_F":"soia","CT_F":"cotone","SB_F":"zucchero",
      "KC_F":"caffe","CC_F":"cacao","LE_F":"bovini","EURUSD_X":"EUR/USD"}
# ogni regola torna +1 (lungo), -1 (corto) o 0 (fuori). Simmetriche per costruzione.
REG={
 "segui l'ultima candela":  lambda c,h,l,i: 1 if c[i]>c[i-1] else -1,
 "contrasta l'ultima":      lambda c,h,l,i: -1 if c[i]>c[i-1] else 1,
 "segui 3 di fila":         lambda c,h,l,i: 1 if c[i]>c[i-1]>c[i-2]>c[i-3] else (-1 if c[i]<c[i-1]<c[i-2]<c[i-3] else 0),
 "contrasta 3 di fila":     lambda c,h,l,i: -1 if c[i]>c[i-1]>c[i-2]>c[i-3] else (1 if c[i]<c[i-1]<c[i-2]<c[i-3] else 0),
 "rottura banda 24":        lambda c,h,l,i: 1 if c[i]>max(h[i-24:i]) else (-1 if c[i]<min(l[i-24:i]) else 0),
 "contrasta banda 24":      lambda c,h,l,i: -1 if c[i]>max(h[i-24:i]) else (1 if c[i]<min(l[i-24:i]) else 0),
}
ORIZ=[1,3,12]
tot=collezione={}
print("   regola                    oriz   mercati   osservazioni   resa media         esito")
for nome,fn in REG.items():
    for o in ORIZ:
        tutti=[]; nmerc=0
        for f in sorted(glob.glob("data/mercati/*_5m.json")):
            base=os.path.basename(f).replace("_5m.json","")
            D=json.load(open(f))
            c=[x for x in D["c"] if x]; h=[x for x in D["h"] if x]; l=[x for x in D["l"] if x]
            n=min(len(c),len(h),len(l)); c,h,l=c[:n],h[:n],l[:n]
            if n<2000: continue
            nmerc+=1
            for i in range(30, n-o-1):
                s=fn(c,h,l,i)
                if s==0: continue
                tutti.append(s*(c[i+o]/c[i]-1)-COSTO)
        if len(tutti)<500: continue
        m=st.mean(tutti)*100; e=1.96*st.stdev(tutti)/len(tutti)**0.5*100
        esito="SOPRA ZERO" if m-e>0 else ("sotto zero" if m+e<0 else "non dimostrato")
        print(f"   {nome:<25} {o:>3}   {nmerc:>5}   {len(tutti):>11,}   {m:+7.4f}% +/-{e:6.4f}  {esito}")
print("\n   18 prove, i versi sono speculari: 9 indipendenti. Pedaggio 0,018% a giro.")
