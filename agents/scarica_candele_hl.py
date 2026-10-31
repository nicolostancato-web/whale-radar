"""Le candele orarie degli stessi mercati, dalla stessa fonte pubblica.
Serve il prezzo DOPO il segnale, e deve venire dalla stessa piazza dove si
opererebbe: usare i prezzi di un'altra borsa introdurrebbe uno scarto che non
e' nostro.
"""
import json, urllib.request, os, glob, time
os.makedirs("data/candele_hl", exist_ok=True)
def post(corpo, tent=3):
    for _ in range(tent):
        try:
            r=urllib.request.Request("https://api.hyperliquid.xyz/info",
                json.dumps(corpo).encode(), {"content-type":"application/json","user-agent":"Mozilla/5.0"})
            with urllib.request.urlopen(r,timeout=40) as f: return json.load(f)
        except Exception: time.sleep(2)
    return None
nomi=[os.path.basename(f).replace(".json","") for f in sorted(glob.glob("data/finanziamento/*.json"))]
print(f"{len(nomi)} mercati da coprire")
fatti=0; righe=0
for c in nomi:
    f=f"data/candele_hl/{c}.json"
    if os.path.exists(f): fatti+=1; continue
    tutto=[]; t=1759276800000
    for _ in range(14):
        d=post({"type":"candleSnapshot","req":{"coin":c,"interval":"1h","startTime":t,
                                               "endTime":t+5000*3600*1000}})
        if not d: break
        nuovi=[x for x in d if x["t"]>t]
        if not nuovi: break
        tutto+=nuovi; t=nuovi[-1]["t"]
        time.sleep(0.12)
    if len(tutto)>300:
        json.dump([{"t":x["t"],"c":float(x["c"])} for x in tutto], open(f,"w"))
        fatti+=1; righe+=len(tutto)
    time.sleep(0.12)
print(f"candele: {fatti} mercati, {righe:,} righe nuove")
