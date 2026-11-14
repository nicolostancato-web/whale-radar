"""Prova PRE-REGISTRATA (PREREGISTRAZIONE_LUNGO_IMPENNATA_27OTT.md).

Regola fissata PRIMA: volume >= 95mo percentile delle 500 ore precedenti,
LUNGO, uscita a 12 ore, osservazioni non sovrapposte, costo 2 gambe = 0,10%.
Asticella fissata PRIMA: il netto ASSOLUTO deve essere sopra zero con
l'intervallo che non tocca lo zero. Battere il caso NON basta.

Mercati: le tre fasce f150/f450/f600, mai usate nella ricerca. I mercati
che compaiono anche fra i 30 gia' visti vengono ESCLUSI, altrimenti non e'
un campione tenuto da parte.
"""
import json, glob, os, statistics as st, random, math
random.seed(104)
Q, L, ORIZ, COSTO = 0.95, 500, 12, 0.0010
visti = {os.path.basename(f) for f in glob.glob("data/binance/*.json")} | \
        {os.path.basename(f) for f in glob.glob("data/binance_piccoli/*.json")}
def carica(d):
    out=[]
    for f in sorted(glob.glob(d+"/*.json")):
        if os.path.basename(f) in visti: continue
        try: dd=json.load(open(f))
        except Exception: continue
        if not isinstance(dd, list) or len(dd)<3000 or "v" not in dd[0]: continue
        out.append(([x["c"] for x in dd],[x["v"] for x in dd]))
    return out
def prova(nome, dati):
    if not dati: print(f"   {nome}: nessun mercato nuovo"); return
    veri=[]; casi=[]
    for c,v in dati:
        lib=0; q=0
        for k in range(L, len(c)-ORIZ):
            if k<lib: continue
            fin=sorted(v[k-L:k])
            if v[k] < fin[int(Q*len(fin))-1]: continue
            veri.append(c[k+ORIZ]/c[k]-1-COSTO); lib=k+ORIZ; q+=1
        if q<5: continue
        ks=sorted(random.sample(range(L,len(c)-ORIZ), min(q, len(c)-L-ORIZ-1)))
        lib=0
        for k in ks:
            if k<lib: continue
            casi.append(c[k+ORIZ]/c[k]-1-COSTO); lib=k+ORIZ
    if len(veri)<200: print(f"   {nome}: solo {len(veri)} operazioni"); return
    mv=st.mean(veri)*100; ev=1.96*st.stdev(veri)/math.sqrt(len(veri))*100
    mc=st.mean(casi)*100
    d=mv-mc; ed=1.96*math.sqrt(st.stdev(veri)**2/len(veri)+st.stdev(casi)**2/len(casi))*100
    print(f"   {nome:<14} {len(dati):>3} mercati  {len(veri):>5} operazioni")
    print(f"      NETTO ASSOLUTO  {mv:+7.4f}% +/-{ev:6.4f}   -> {'PASSA' if mv-ev>0 else 'NON PASSA'}")
    print(f"      vantaggio caso  {d:+7.4f}% +/-{ed:6.4f}   (caso {mc:+.4f}%)")
for t in ["data/binance_f150","data/binance_f450","data/binance_f600"]:
    prova(t.split("/")[-1], carica(t))
