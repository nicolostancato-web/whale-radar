"""Quanto si puo' davvero muovere su un perpetuo prima che lo scivolamento
mangi il guadagno? Finora nella frontiera avevo MESSO IO 1.000 EUR senza
misurarlo: e' una costante inventata, lo stesso errore della commissione
allo 0,30%.

Si legge il libro degli ordini vero (endpoint pubblico, gratis) e si calcola
quanto costa in percentuale comprare N euro di nozionale.
"""
import json, urllib.request, statistics as st
def get(u):
    r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r, timeout=30))
EUR=1/1.08
def costo(sym, eur):
    d=get(f"https://fapi.binance.com/fapi/v1/depth?symbol={sym}&limit=500")
    ask=[(float(p),float(q)) for p,q in d["asks"]]
    if not ask: return None
    mid=(float(d["bids"][0][0])+ask[0][0])/2
    resta=eur/EUR; speso=0.0; preso=0.0
    for p,q in ask:
        v=min(resta, p*q)
        speso+=v; preso+=v/p; resta-=v
        if resta<=0: break
    if resta>0: return None          # il libro non basta
    return (speso/preso)/mid-1
MERC=["BTCUSDT","ETHUSDT","SOLUSDT","ADAUSDT","DOGEUSDT","LINKUSDT",
      "AVAXUSDT","CRVUSDT","RSRUSDT","GALAUSDT"]
TAGLIE=[52, 1000, 10000, 100000, 1000000]
print(f"   scivolamento di SOLA ANDATA, in percentuale\n")
print(f"   {'mercato':<11}" + "".join(f"{t:>11,}" for t in TAGLIE))
agg={t:[] for t in TAGLIE}
for s in MERC:
    riga=f"   {s.replace('USDT',''):<11}"
    for t in TAGLIE:
        try: c=costo(s,t)
        except Exception: c=None
        if c is None: riga+=f"{'libro ko':>11}"
        else: riga+=f"{c*100:>10.4f}%"; agg[t].append(c)
    print(riga)
print(f"\n   {'mediana':<11}" + "".join(
    f"{st.median(agg[t])*100:>10.4f}%" if agg[t] else f"{'-':>11}" for t in TAGLIE))
print("\n   Un'operazione completa sono DUE gambe: raddoppiare questi numeri.")
print("   La capienza utile e' la taglia alla quale 2x scivolamento resta")
print("   sotto il lordo della strada.")
