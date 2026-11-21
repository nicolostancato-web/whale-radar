"""Candele orarie dai futures Binance: pubblico, senza chiave, storia dal 2021.

Serve a decidere il candidato dell'attenzione su un campione che la ricerca non
ha mai visto: su Hyperliquid c'erano 7 mesi, qui ce ne sono anni.
Si tengono prezzo, volume e NUMERO DI OPERAZIONI (campo 8), che sono le due
grandezze che non sono il prezzo.
Si cammina in AVANTI, qui lo startTime viene rispettato (verificato).
"""
import json, urllib.request, os, time
os.makedirs("data/binance", exist_ok=True)
DA=int(os.environ.get("DA","1735689600000"))      # 1 gennaio 2025
QUANTI=int(os.environ.get("QUANTI","80"))
def get(u, tent=3):
    for _ in range(tent):
        try:
            r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
            with urllib.request.urlopen(r,timeout=35) as f: return json.load(f)
        except Exception: time.sleep(1.5)
    return None
e=get("https://fapi.binance.com/fapi/v1/exchangeInfo")
if not e: print("elenco mercati non raggiungibile"); raise SystemExit
sim=[s["symbol"] for s in e["symbols"]
     if s.get("status")=="TRADING" and s["symbol"].endswith("USDT")]
print(f"mercati in USDT attivi: {len(sim)} | ne scarico {QUANTI}")
fatti=0; righe=0
for s in sim[:QUANTI]:
    f=f"data/binance/{s}.json"
    if os.path.exists(f): fatti+=1; continue
    tutto=[]; t=DA
    for _ in range(30):
        d=get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&limit=1500&startTime={t}")
        if not d: break
        tutto+=d
        if len(d)<1500: break
        t=d[-1][0]+3600000
        time.sleep(0.12)
    if len(tutto)<2000: continue
    json.dump([{"t":x[0],"c":float(x[4]),"v":float(x[5]),"n":int(x[8])} for x in tutto], open(f,"w"))
    fatti+=1; righe+=len(tutto)
    time.sleep(0.1)
print(f"scaricati {fatti} mercati, {righe:,} ore")
