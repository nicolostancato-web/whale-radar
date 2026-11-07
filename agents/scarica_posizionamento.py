"""Dati di POSIZIONAMENTO dai perpetui Binance: chi e' dentro e da che parte.
Tre serie, tutte pubbliche e gratuite, risoluzione oraria, 30 giorni:
  - openInterestHist          quanto nozionale e' aperto
  - topLongShortAccountRatio  rapporto fra conti lunghi e corti (i grandi)
  - takerlongshortRatio       quota di volume aggressivo in acquisto
Piu' le candele dello stesso periodo, per misurare l'esito.
"""
import json, os, time, urllib.request
def get(u):
    r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r, timeout=30))
info=get("https://fapi.binance.com/fapi/v1/exchangeInfo")
sym=[x["symbol"] for x in info["symbols"]
     if x["symbol"].endswith("USDT") and x["contractType"]=="PERPETUAL"
     and x["status"]=="TRADING"]
print(f"{len(sym)} perpetui attivi")
os.makedirs("data/posizionamento", exist_ok=True)
SERIE=[("openInterestHist","oi"),("topLongShortAccountRatio","ls"),
       ("takerlongshortRatio","tk")]
n=0
for s in sym:
    out=f"data/posizionamento/{s}.json"
    if os.path.exists(out): n+=1; continue
    d={}
    ok=True
    for ep,k in SERIE:
        try:
            r=get(f"https://fapi.binance.com/futures/data/{ep}?symbol={s}&period=1h&limit=500")
        except Exception:
            ok=False; break
        if not r: ok=False; break
        d[k]=r
        time.sleep(0.12)
    if not ok: continue
    try:
        kl=get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&limit=600")
    except Exception:
        continue
    d["c"]=[{"t":int(x[0]),"c":float(x[4])} for x in kl]
    json.dump(d, open(out,"w"))
    n+=1
    if n%50==0: print(f"   {n}/{len(sym)}")
    time.sleep(0.12)
print(f"fatti {n}/{len(sym)}")
