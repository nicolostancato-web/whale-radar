"""Lungo su una piazza, corto sull'altra: si incassa la DIFFERENZA di
finanziamento, senza rischio di prezzo (i due prezzi stanno entro 0,045%).

Tre ingredienti, nessuno dei tre va dimenticato:
  + finanziamento incassato (tasso della piazza dove sono CORTO
    meno tasso della piazza dove sono LUNGO)
  + variazione dello scarto di prezzo mentre tengo (NON e' zero: ha varianza,
    e si realizza alla chiusura)
  - 0,19% di quattro gambe, una volta sola, spalmato sulla tenuta

Lezione 27/10: la direzione si sceglie sulla differenza OSSERVATA PRIMA,
mai su quella che sto incassando, altrimenti e' sguardo in avanti.
Binance paga ogni 8 ore, Hyperliquid ogni ora: si sommano 8 ore.
"""
import json, glob, os, statistics as st, math
COSTO=0.0019
def car(f):
    try: return json.load(open(f))
    except Exception: return None
def prezzi(f):
    d=car(f)
    if not isinstance(d,list) or not d: return {}
    k="t" if "t" in d[0] else ("T" if "T" in d[0] else None)
    return {int(x[k]): x["c"] for x in d} if k else {}
monete=sorted(os.path.basename(f).replace(".json","")
              for f in glob.glob("data/finanziamento_binance/*.json"))
def prova(tenuta):          # tenuta in finestre da 8 ore
    gua=[]; solo_fin=[]
    for s in monete:
        fb=car(f"data/finanziamento_binance/{s}.json")
        fh=car(f"data/finanziamento/{s}.json")
        pb=prezzi(f"data/binance/{s}USDT.json"); ph=prezzi(f"data/candele3/{s}.json")
        if not fb or not fh or not pb or not ph: continue
        oraria={int(x["time"])//3600000*3600000: float(x["fundingRate"]) for x in fh}
        B=sorted((int(x["t"]), x["r"]) for x in fb)
        # somma delle 8 ore di Hyperliquid che precedono ogni pagamento Binance
        hl8={}
        for t,_ in B:
            ore=[t-i*3600000 for i in range(8)]
            v=[oraria[o] for o in ore if o in oraria]
            if len(v)==8: hl8[t]=sum(v)
        ts=[t for t,_ in B if t in hl8]
        tassi={t:r for t,r in B}
        lib=0
        for i in range(1, len(ts)-tenuta):
            if i<lib: continue
            t0=ts[i]; t1=ts[i+tenuta]
            prec = tassi[ts[i-1]] - hl8[ts[i-1]]      # osservata PRIMA
            if abs(prec) < 1e-9: continue
            verso = 1 if prec>0 else -1   # +1: corto Binance, lungo Hyperliquid
            inc = sum(verso*(tassi[ts[j]] - hl8[ts[j]]) for j in range(i, i+tenuta))
            # scarto di prezzo: se sono lungo HL e corto Binance guadagno
            # quando HL sale rispetto a Binance
            if t0 not in pb or t0 not in ph or t1 not in pb or t1 not in ph:
                sc=None
            else:
                d0=ph[t0]/pb[t0]-1; d1=ph[t1]/pb[t1]-1
                sc = verso*(d1-d0)
            solo_fin.append(inc-COSTO)
            if sc is not None: gua.append(inc+sc-COSTO)
            lib=i+tenuta
    def r(v,nome):
        if len(v)<150: return f"      {nome}: solo {len(v)} casi"
        m=st.mean(v)*100; e=1.96*st.stdev(v)/math.sqrt(len(v))*100
        return (f"      {nome:<28}{len(v):>6} casi  netto {m:+.4f}% +/-{e:.4f}  "
                f"{'SOPRA ZERO' if m-e>0 else 'non dim.'}")
    print(f"   tenuta {tenuta*8} ore")
    print(r(solo_fin,"solo finanziamento"))
    print(r(gua,"finanziamento + scarto"))
for t in (1,3,9,21):
    prova(t)
