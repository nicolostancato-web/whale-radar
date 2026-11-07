"""Finanziamento di Binance per le monete presenti anche su Hyperliquid.
Endpoint pubblico e gratuito, nessuna chiave. Binance paga ogni 8 ore,
Hyperliquid ogni ora: il confronto si fa sommando 8 ore di Hyperliquid.
"""
import json, glob, os, time, urllib.request
HL={os.path.basename(f).replace(".json","") for f in glob.glob("data/finanziamento/*.json")}
BIN={os.path.basename(f).replace("USDT.json","") for f in glob.glob("data/binance/*.json")}
com=sorted(HL & BIN)
print(f"{len(com)} monete in comune")
def get(u):
    r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r, timeout=30))
fatti=0
for s in com:
    out=f"data/finanziamento_binance/{s}.json"
    if os.path.exists(out): fatti+=1; continue
    righe=[]; fine=int(time.time()*1000)
    for _ in range(12):
        try:
            d=get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={s}USDT&limit=1000&endTime={fine}")
        except Exception as e:
            print(f"   {s}: {e}"); break
        if not d: break
        righe = d + righe
        fine = int(d[0]["fundingTime"]) - 1
        if len(d) < 1000: break
        time.sleep(0.25)
    if righe:
        vis={}
        for x in righe: vis[int(x["fundingTime"])]=float(x["fundingRate"])
        json.dump([{"t":t,"r":vis[t]} for t in sorted(vis)], open(out,"w"))
        fatti+=1
        print(f"   {s}: {len(vis)} pagamenti")
print(f"fatti {fatti}/{len(com)}")
