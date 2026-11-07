"""I simboli Binance mai scaricati: il campione tenuto da parte per la
prova pre-registrata di 'vendere il debutto'. Gratis, endpoint pubblico.
Per ogni simbolo bastano le prime 200 ore dal debutto piu' il finanziamento.
"""
import json, glob, os, time, urllib.request
def get(u):
    r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r, timeout=30))
info=get("https://fapi.binance.com/fapi/v1/exchangeInfo")
tutti=[x["symbol"] for x in info["symbols"]
       if x["symbol"].endswith("USDT") and x["contractType"]=="PERPETUAL"]
visti=set()
for d in ["data/binance","data/binance_piccoli","data/binance_f150","data/binance_f450","data/binance_f600"]:
    visti |= {os.path.basename(f).replace(".json","") for f in glob.glob(d+"/*.json")}
resto=[s for s in tutti if s not in visti]
print(f"{len(tutti)} perpetui | {len(visti)} gia' visti | {len(resto)} da scaricare")
os.makedirs("data/finanziamento_resto", exist_ok=True)
n=0
for s in resto:
    o1=f"data/binance_resto/{s}.json"; o2=f"data/finanziamento_resto/{s}.json"
    if os.path.exists(o1) and os.path.exists(o2): n+=1; continue
    try:
        k=get(f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval=1h&limit=300&startTime=0")
        if not k: continue
        t0=int(k[0][0])
        f=get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={s}"
              f"&startTime={t0}&endTime={t0+30*86400000}&limit=1000")
    except Exception as e:
        print(f"   {s}: {e}"); time.sleep(1); continue
    json.dump([{"t":int(x[0]),"c":float(x[4]),"v":float(x[5])} for x in k], open(o1,"w"))
    json.dump([{"t":int(x["fundingTime"]),"r":float(x["fundingRate"])} for x in f], open(o2,"w"))
    n+=1
    if n%40==0: print(f"   {n}/{len(resto)}")
    time.sleep(0.2)
print(f"fatti {n}/{len(resto)}")
