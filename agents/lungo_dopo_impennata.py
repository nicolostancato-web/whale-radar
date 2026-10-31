"""Comprare dopo un'impennata di volume, SENZA guardare la direzione dell'ora.

Emerso dalla prova a un verso solo, che il disegno vecchio non poteva vedere.
Qui si misura in EURO, non in unita' statistiche, e su piu' piazze.
Costo: una posizione sola = 2 gambe. Binance 2x0,05%=0,10%; Hyperliquid
2x0,045%=0,09%. Il confronto e' sempre contro entrate lunghe a caso sullo
stesso mercato, che e' cio' che toglie la marea.
"""
import json, glob, os, statistics as st, random, math
random.seed(71)
def carica(patt, campo_v="v"):
    out=[]
    for f in sorted(glob.glob(patt)):
        d=json.load(open(f))
        if isinstance(d, dict): continue
        if len(d)<3000: continue
        if campo_v not in d[0]: continue
        out.append(([x["c"] for x in d],[x[campo_v] for x in d]))
    return out
def misura(dati, costo, q=0.95, L=500, oriz=(4,12,24)):
    for o in oriz:
        veri=[]; casi=[]
        for c,v in dati:
            lib=0
            for k in range(L, len(c)-o):
                if k<lib: continue
                fin=sorted(v[k-L:k])
                if v[k] < fin[int(q*len(fin))-1]: continue
                veri.append(c[k+o]/c[k]-1-costo); lib=k+o
            n=len([1 for _ in range(0)])
        # entrate a caso, stesso numero per mercato
        for c,v in dati:
            lib=0; quante=0
            for k in range(L, len(c)-o):
                if k<lib: continue
                fin=sorted(v[k-L:k])
                if v[k] >= fin[int(q*len(fin))-1]: quante+=1; lib=k+o
            if quante<5: continue
            ks=sorted(random.sample(range(L,len(c)-o), min(quante, len(c)-L-o-1)))
            lib=0
            for k in ks:
                if k<lib: continue
                casi.append(c[k+o]/c[k]-1-costo); lib=k+o
        if len(veri)<200 or len(casi)<200: continue
        mv=st.mean(veri)*100; ev=1.96*st.stdev(veri)/math.sqrt(len(veri))*100
        mc=st.mean(casi)*100; ec=1.96*st.stdev(casi)/math.sqrt(len(casi))*100
        d=mv-mc; ed=1.96*math.sqrt((st.stdev(veri)**2/len(veri))+(st.stdev(casi)**2/len(casi)))*100
        print(f"      {o:>3}h  regola {mv:+7.4f}% +/-{ev:5.4f}   caso {mc:+7.4f}%   "
              f"differenza {d:+7.4f}% +/-{ed:5.4f}  {'SOPRA ZERO' if d-ed>0 else 'non dim.'}")
print("   BINANCE grandi (costo 0,10%)")
misura(carica("data/binance/*.json"), 0.0010)
print("\n   BINANCE piccoli, fascia 300-380 (costo 0,10%)")
misura(carica("data/binance_piccoli/*.json"), 0.0010)
print("\n   HYPERLIQUID (costo 0,09%)")
misura(carica("data/candele3/*.json"), 0.0009)
