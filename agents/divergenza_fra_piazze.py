"""Triage: lo stesso asset su due piazze diverge oltre il pedaggio?

Una posizione di arbitraggio sono 4 gambe (apri lungo + apri corto, chiudi
entrambe) = 0,19% fra Binance (0,05%/gamba) e Hyperliquid (0,045%/gamba).
Alle chiusure ORARIE la divergenza e' un LIMITE SUPERIORE grossolano: il
vero arbitraggio vive al secondo. Ma se nemmeno all'ora si vede nulla, la
strada e' chiusa senza comprare dati al secondo.

Attenzione (lezione 27/10): i due archivi devono essere allineati
sull'ISTANTE, non sull'indice. Si abbina per timestamp.
"""
import json, glob, os, statistics as st
COSTO = 0.0019
def leggi(f):
    try: d=json.load(open(f))
    except Exception: return None
    if not isinstance(d,list) or len(d)<500: return None
    k = "t" if "t" in d[0] else ("T" if "T" in d[0] else None)
    if k is None: return None
    return {int(x[k]): x["c"] for x in d}
B={os.path.basename(f).replace("USDT.json",""): f for f in glob.glob("data/binance/*.json")}
H={os.path.basename(f).replace(".json",""): f for f in glob.glob("data/candele3/*.json")}
com=sorted(set(B)&set(H))
print(f"   monete su entrambe le piazze: {len(com)}  {com[:12]}")
tot=[]; righe=[]
for s in com:
    b=leggi(B[s]); h=leggi(H[s])
    if not b or not h: continue
    ore=sorted(set(b)&set(h))
    if len(ore)<300: continue
    d=[abs(h[t]/b[t]-1) for t in ore]
    d=[x for x in d if x<0.5]          # scarta disallineamenti grossolani
    if len(d)<300: continue
    sopra=sum(1 for x in d if x>COSTO)/len(d)
    righe.append((s,len(d),st.median(d)*100,sorted(d)[int(0.99*len(d))]*100,sopra*100))
    tot+=d
righe.sort(key=lambda r:-r[4])
print(f"   {'moneta':<10}{'ore':>7}{'mediana':>10}{'99esimo':>10}{'% oltre pedaggio':>19}")
for s,n,me,p99,so in righe[:15]:
    print(f"   {s:<10}{n:>7}{me:>9.3f}%{p99:>9.3f}%{so:>18.2f}%")
if tot:
    print(f"\n   TOTALE {len(tot)} ore abbinate | mediana {st.median(tot)*100:.3f}% | "
          f"99esimo {sorted(tot)[int(0.99*len(tot))]*100:.3f}%")
    print(f"   ore con divergenza oltre il pedaggio di {COSTO*100:.2f}%: "
          f"{sum(1 for x in tot if x>COSTO)/len(tot)*100:.2f}%")
