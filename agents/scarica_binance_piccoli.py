"""I mercati PICCOLI di Binance: stessa commissione, molta meno concorrenza.

Buco notato il 26/10: ho sempre misurato i primi 80 mercati su 747, cioe' i
piu' scambiati. La commissione pero' e' identica ovunque (0,05% per gamba).
Quindi la fascia bassa ha lo STESSO pedaggio e meno gente che la guarda.
Si prendono i mercati dal 300esimo in poi per volume.
"""
import json, urllib.request, os, time
import sys
FASCIA=int(sys.argv[1]) if len(sys.argv)>1 else 300
CART=f"data/binance_f{FASCIA}"
os.makedirs(CART, exist_ok=True)
def get(u, tent=3):
    for _ in range(tent):
        try:
            r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
            with urllib.request.urlopen(r,timeout=35) as f: return json.load(f)
        except Exception: time.sleep(1.5)
    return None
t=get("https://fapi.binance.com/fapi/v1/ticker/24hr")
if not t: print("classifica non raggiungibile"); raise SystemExit
u=[x for x in t if x["symbol"].endswith("USDT")]
u.sort(key=lambda x:-float(x.get("quoteVolume",0)))
print(f"{len(u)} mercati in USDT")
print(f"   il piu' grande: {u[0]['symbol']} {float(u[0]['quoteVolume'])/1e6:,.0f}M al giorno")
print(f"   il 300esimo:    {u[299]['symbol']} {float(u[299]['quoteVolume'])/1e6:,.1f}M")
print(f"   il 500esimo:    {u[499]['symbol']} {float(u[499]['quoteVolume'])/1e6:,.2f}M" if len(u)>500 else "")
scelti=[x["symbol"] for x in u[FASCIA:FASCIA+80]]
print(f"\nscarico i mercati dal {FASCIA} al {FASCIA+80} ({len(scelti)})")
fatti=0; righe=0
for s in scelti:
    f=f"{CART}/{s}.json"
    if os.path.exists(f): fatti+=1; continue
    tutto=[]; tt=1735689600000
    for _ in range(20):
        d=get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&limit=1500&startTime={tt}")
        if not d: break
        tutto+=d
        if len(d)<1500: break
        tt=d[-1][0]+3600000
        time.sleep(0.1)
    if len(tutto)<2000: continue
    json.dump([{"t":x[0],"c":float(x[4]),"v":float(x[5]),"n":int(x[8])} for x in tutto], open(f,"w"))
    fatti+=1; righe+=len(tutto)
print(f"scaricati {fatti}, {righe:,} ore")
