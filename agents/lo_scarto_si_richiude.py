"""La divergenza fra due piazze si RICHIUDE, o e' uno scarto stabile?

1) Controllo di allineamento: se spostando di +/-1 ora la divergenza cala,
   gli archivi erano sfasati e tutto il resto e' un mio artefatto.
2) Ogni moneta ha il suo scarto tipico (base): si scommette sul ritorno a
   QUELLA, non a zero.
3) Guadagno = quanto si richiude lo scostamento, meno 0,19% di 4 gambe.
   Osservazioni non sovrapposte.
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
    if len(ore)<1000: continue
    serie[s]=(ore,b,h)
print(f"   {len(serie)} monete\n\n   1) ALLINEAMENTO (mediana di |divergenza|)")
for sp in (-2,-1,0,1,2):
    v=[]
    for s,(ore,b,h) in serie.items():
        for t in ore:
            t2=t+sp*3600000
            if t2 in h: v.append(abs(h[t2]/b[t]-1))
    print(f"      sfasamento {sp:+d}h: {st.median(v)*100:.4f}%  ({len(v)} ore)")
print("\n   2) LO SCARTO SI RICHIUDE? (scostamento dalla base della moneta)")
for soglia in (0.002,0.003,0.005):
    for oriz in (1,2,4):
        gua=[]
        for s,(ore,b,h) in serie.items():
            d={t: h[t]/b[t]-1 for t in ore}
            base=st.median(d.values())
            lib=0
            for i,t in enumerate(ore[:-oriz]):
                if i<lib: continue
                if ore[i+oriz]-t != oriz*3600000: continue
                x=d[t]-base
                if abs(x)<soglia: continue
                y=d[ore[i+oriz]]-base
                gua.append((abs(x)-abs(y))*(1 if abs(x)>abs(y) or True else 1)-COSTO)
                # quanto si e' richiuso, meno il pedaggio: se y ha superato
                # dall'altra parte, abs(x)-abs(y) puo' restare positivo ma il
                # guadagno vero e' x-y nel verso giusto:
                gua[-1]=(x-y)*(1 if x>0 else -1)-COSTO
                lib=i+oriz
        if len(gua)<200: continue
        m=st.mean(gua)*100; e=1.96*st.stdev(gua)/math.sqrt(len(gua))*100
        print(f"      soglia {soglia*100:.1f}%  {oriz}h  {len(gua):>6} casi  "
              f"netto {m:+.4f}% +/-{e:.4f}  {'SOPRA ZERO' if m-e>0 else 'non dim.'}")
