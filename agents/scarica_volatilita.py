"""Indice di volatilita' implicita (DVOL) da Deribit + prezzi orari, gratis.

DVOL e' la volatilita' a 30 giorni che il mercato delle opzioni sta PREZZANDO.
Confrontarlo con quella poi REALIZZATA misura quanto si fa pagare
l'incertezza rispetto a quanta ne arriva.
"""
import json, os, time, urllib.request, datetime
def get(u):
    r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
    d=json.load(urllib.request.urlopen(r, timeout=40))
    # Deribit risponde {"result": ...}, Binance risponde direttamente una
    # lista: il lettore deve reggere entrambe le forme.
    return d.get("result", d) if isinstance(d, dict) else d
for m in ("BTC","ETH"):
    out=f"data/volatilita/dvol_{m}.json"
    if not os.path.exists(out):
        righe=[]; fine=int(time.time()*1000)
        for _ in range(40):
            u=(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?"
               f"currency={m}&start_timestamp={fine-900*3600*1000}&end_timestamp={fine}&resolution=3600")
            try: r=get(u)
            except Exception as e: print(f"   {m}: {e}"); break
            d=r.get("data") if isinstance(r,dict) else None
            if not d: break
            righe = d + righe
            fine = int(d[0][0]) - 1
            time.sleep(0.25)
        if righe:
            vis={int(x[0]): float(x[4]) for x in righe}   # chiusura dell'indice
            json.dump([{"t":t,"iv":vis[t]} for t in sorted(vis)], open(out,"w"))
            g=(max(vis)-min(vis))/86400000
            print(f"   DVOL {m}: {len(vis)} ore, {g:.0f} giorni")
    # prezzi orari dello stesso periodo
    po=f"data/volatilita/prezzo_{m}.json"
    if not os.path.exists(po):
        tutti={}; fine=int(time.time()*1000)
        for _ in range(30):
            try:
                k=get(f"https://fapi.binance.com/fapi/v1/klines?symbol={m}USDT"
                      f"&interval=1h&limit=1500&endTime={fine}")
            except Exception as e: print(e); break
            if not k: break
            for x in k: tutti[int(x[0])]=float(x[4])
            fine=int(k[0][0])-1
            if len(k)<1500: break
            time.sleep(0.2)
        json.dump([{"t":t,"c":tutti[t]} for t in sorted(tutti)], open(po,"w"))
        print(f"   prezzi {m}: {len(tutti)} ore")
