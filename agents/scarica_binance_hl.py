"""Candele con MASSIMO e MINIMO: servono per sapere se un ordine messo a un
certo prezzo sarebbe stato eseguito.

Tutto il margine del candidato superstite dipende dal pagare 0,04% invece di
0,10%, cioe' dal mettere l'ordine invece di prenderlo. Finora l'ho ASSUNTO.
Con massimi e minimi si misura: l'ordine viene toccato? e cosa succede dopo,
quando viene toccato rispetto a quando no (selezione avversa)?
"""
import json, urllib.request, os, time
os.makedirs("data/binance_hl", exist_ok=True)
DA=1735689600000
def get(u, tent=3):
    for _ in range(tent):
        try:
            r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
            with urllib.request.urlopen(r,timeout=35) as f: return json.load(f)
        except Exception: time.sleep(1.5)
    return None
e=get("https://fapi.binance.com/fapi/v1/exchangeInfo")
sim=[s["symbol"] for s in e["symbols"] if s.get("status")=="TRADING" and s["symbol"].endswith("USDT")][:30]
print(f"{len(sim)} mercati")
fatti=0; righe=0
for s in sim:
    f=f"data/binance_hl/{s}.json"
    if os.path.exists(f): fatti+=1; continue
    tutto=[]; t=DA
    for _ in range(20):
        d=get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&limit=1500&startTime={t}")
        if not d: break
        tutto+=d
        if len(d)<1500: break
        t=d[-1][0]+3600000
        time.sleep(0.1)
    if len(tutto)<2000: continue
    json.dump([{"t":x[0],"o":float(x[1]),"h":float(x[2]),"l":float(x[3]),"c":float(x[4])}
               for x in tutto], open(f,"w"))
    fatti+=1; righe+=len(tutto)
print(f"scaricati {fatti}, {righe:,} ore")
