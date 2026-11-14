"""Il calendario: ore del giorno, giorni della settimana, finestre del
finanziamento. Niente da indovinare — l'orario si sa in anticipo.

Prova di CLASSE: 24 ore + 7 giorni + 3 finestre = 34 regole, ognuna
appaiata con lo stesso numero di entrate lunghe a orari a caso.
Un verso solo, osservazioni non sovrapposte, costo 0,10% (due gambe).
Si legge contro il pavimento tarato oggi: sotto 2,2 e' rumore.
"""
import json, glob, os, statistics as st, math, random, datetime, collections
random.seed(4242)
COSTO=0.0010
P=[]
for d in ["data/binance","data/binance_piccoli","data/binance_f150",
          "data/binance_f450","data/binance_f600"]:
    for f in glob.glob(d+"/*.json"):
        try: dd=json.load(open(f))
        except Exception: continue
        if not isinstance(dd,list) or len(dd)<3000: continue
        k="t" if "t" in dd[0] else ("T" if "T" in dd[0] else None)
        if not k: continue
        P.append(sorted((int(x[k]), x["c"]) for x in dd))
print(f"   {len(P)} mercati | {sum(len(x) for x in P):,} ore\n")
# CORREZIONE 27/10 sera: il pavimento tarato a 2,2 e' in unita' statistiche,
# che crescono come la radice del numero di casi. Quella prova aveva migliaia
# di osservazioni, questa ne ha 185.000 per regola: lo stesso effetto
# economico produce un valore molto piu' grande. Il metro NON si trasporta
# fra disegni con n diverso. Si misura in PERCENTUALE per operazione, che e'
# l'unica cosa confrontabile e l'unica che si incassa.
def mis(v):
    if len(v)<150: return None
    return st.mean(v)*100, 1.96*st.stdev(v)/math.sqrt(len(v))*100
def prova(scelta, oriz):
    veri=[]; casi=[]
    for ser in P:
        n=0; lib=0
        for i in range(len(ser)-oriz):
            if i<lib: continue
            t,p=ser[i]
            if ser[i+oriz][0]-t != oriz*3600000: continue
            if not scelta(datetime.datetime.fromtimestamp(t/1000, datetime.UTC)): continue
            veri.append(ser[i+oriz][1]/p-1-COSTO); lib=i+oriz; n+=1
        if n<2: continue
        ks=sorted(random.sample(range(len(ser)-oriz), min(n, len(ser)-oriz-1)))
        lib=0
        for i in ks:
            if i<lib: continue
            if ser[i+oriz][0]-ser[i][0] != oriz*3600000: continue
            casi.append(ser[i+oriz][1]/ser[i][1]-1-COSTO); lib=i+oriz
    a=mis(veri); b=mis(casi)
    if a is None or b is None: return None
    err=math.sqrt(a[1]**2+b[1]**2)
    return len(veri), a[0], b[0], err
R=[]
for h in range(24):
    r=prova(lambda d,h=h: d.hour==h, 4)
    if r: R.append((f"ora {h:02d} UTC", *r))
for g,nome in enumerate(["lun","mar","mer","gio","ven","sab","dom"]):
    r=prova(lambda d,g=g: d.weekday()==g, 24)
    if r: R.append((f"{nome}", *r))
for h in (0,8,16):
    r=prova(lambda d,h=h: d.hour==h, 8)
    if r: R.append((f"finanziamento {h:02d}", *r))
print(f"   {len(R)} prove appaiate\n")
R2=sorted(R, key=lambda x: -abs(x[2]-x[3]))
print(f"   {'regola':<18}{'casi':>8}{'netto vero':>12}{'caso':>10}{'differenza':>22}")
for nome,n,a,b,e in R2[:8]:
    d=a-b
    seg = "SOPRA ZERO" if abs(d)>e else "nel rumore"
    print(f"   {nome:<18}{n:>8}{a:>+11.4f}%{b:>+9.4f}%{d:>+12.4f}% +/-{e:.4f} {seg}")
dd=[x[2]-x[3] for x in R]
print(f"\n   differenza mediana {st.median(dd):+.4f}%  |  massima in valore "
      f"assoluto {max(dd,key=abs):+.4f}%")
print(f"   costo di una operazione (due gambe): 0,10%")
sopra=[x for x in R if abs(x[2]-x[3])>max(x[4],0.10)]
print(f"   regole con differenza oltre sia il rumore sia il costo: {len(sopra)}/{len(R)}")
for nome,n,a,b,e in sopra:
    print(f"      {nome:<18}{a-b:+.4f}% +/-{e:.4f}")
