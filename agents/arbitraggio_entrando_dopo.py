"""Lo stesso arbitraggio, ma entrando DOPO aver visto il segnale.

Lezione gia' pagata: l'esito si misura da dove si entra davvero. Il segnale
e' la chiusura dell'ora t; l'ordine si puo' mandare solo dopo, quindi
l'apertura e' la chiusura dell'ora t+1. Se il guadagno sparisce, lo scarto
visto a t era un ultimo prezzo FERMO su una delle due piazze: si richiude
da solo e non e' comprabile.
"""
import json, glob, os, statistics as st, math
COSTO=0.0019
def leggi(f):
    try: d=json.load(open(f))
    except Exception: return None
    if not isinstance(d,list) or len(d)<500: return None
    k="t" if "t" in d[0] else ("T" if "T" in d[0] else None)
    return {int(x[k]): x["c"] for x in d} if k else None
B={os.path.basename(f).replace("USDT.json",""):f for f in glob.glob("data/binance/*.json")}
H={os.path.basename(f).replace(".json",""):f for f in glob.glob("data/candele3/*.json")}
serie={}
for s in sorted(set(B)&set(H)):
    b=leggi(B[s]); h=leggi(H[s])
    if not b or not h: continue
    ore=sorted(set(b)&set(h))
    if len(ore)>=1000: serie[s]=(ore,b,h)
def prova(rit, soglia, oriz):
    gua=[]
    for s,(ore,b,h) in serie.items():
        d={t: h[t]/b[t]-1 for t in ore}
        base=st.median(d.values())
        lib=0
        for i in range(len(ore)-rit-oriz):
            if i<lib: continue
            t=ore[i]; ta=ore[i+rit]; tc=ore[i+rit+oriz]
            if ta-t!=rit*3600000 or tc-ta!=oriz*3600000: continue
            seg=d[t]-base
            if abs(seg)<soglia: continue
            x=d[ta]-base            # scostamento al momento in cui APRO
            y=d[tc]-base            # scostamento al momento in cui CHIUDO
            gua.append((x-y)*(1 if seg>0 else -1)-COSTO)
            lib=i+rit+oriz
    if len(gua)<150: return None
    m=st.mean(gua)*100; e=1.96*st.stdev(gua)/math.sqrt(len(gua))*100
    return len(gua), m, e
print("   ritardo 0 = entro alla chiusura che fa da segnale (irrealistico)")
print("   ritardo 1 = entro all'ora dopo (realistico)\n")
for soglia in (0.002,0.003,0.005):
    for rit in (0,1):
        for oriz in (1,4):
            r=prova(rit,soglia,oriz)
            if not r: continue
            n,m,e=r
            print(f"   soglia {soglia*100:.1f}%  ritardo {rit}h  tenuta {oriz}h  "
                  f"{n:>5} casi  netto {m:+.4f}% +/-{e:.4f}  "
                  f"{'SOPRA ZERO' if m-e>0 else 'non dim.'}")
    print()
