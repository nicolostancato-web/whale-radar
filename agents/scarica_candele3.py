"""Scaricatore CORRETTO: cammina all'indietro.

L'errore scoperto il 25/10: l'API di Hyperliquid IGNORA lo startTime e rispetta
solo l'endTime, restituendo ~601 candele per chiamata. Il mio scaricatore
camminava in avanti, quindi riceveva quello che decideva l'API e non quello che
chiedevo: i dati potevano avere buchi senza che nulla lo segnalasse.
Qui si parte da adesso e si va indietro, usando come nuova fine la candela piu'
vecchia ricevuta. Si DICHIARA quante ore si sono prese e da quando.
"""
import json, urllib.request, os, time, glob
os.makedirs("data/candele3", exist_ok=True)
GIRI=int(os.environ.get("GIRI","22"))
def post(c, tent=3):
    for _ in range(tent):
        try:
            r=urllib.request.Request("https://api.hyperliquid.xyz/info", json.dumps(c).encode(),
                {"content-type":"application/json","user-agent":"Mozilla/5.0"})
            with urllib.request.urlopen(r,timeout=40) as f: return json.load(f)
        except Exception: time.sleep(1.5)
    return None
nomi=[os.path.basename(f).replace(".json","") for f in sorted(glob.glob("data/finanziamento/*.json"))]
print(f"{len(nomi)} mercati, {GIRI} giri ciascuno (~{GIRI*601/24/30:.0f} mesi)")
fatti=0; righe=0; vuoti=0
for c in nomi:
    f=f"data/candele3/{c}.json"
    if os.path.exists(f): fatti+=1; continue
    fine=int(time.time()*1000); tutto=[]
    for _ in range(GIRI):
        d=post({"type":"candleSnapshot","req":{"coin":c,"interval":"1h",
                "startTime":fine-601*3600*1000,"endTime":fine}})
        if not d: break
        tutto = d + tutto
        fine = d[0]["t"] - 3600000
        time.sleep(0.1)
    if len(tutto)<400: vuoti+=1; continue
    vis=set(); pul=[]
    for x in tutto:
        if x["t"] in vis: continue
        vis.add(x["t"]); pul.append({"t":x["t"],"c":float(x["c"]),
                                     "v":float(x.get("v",0)),"n":int(x.get("n",0))})
    pul.sort(key=lambda x:x["t"])
    json.dump(pul, open(f,"w")); fatti+=1; righe+=len(pul)
print(f"fatti {fatti}, vuoti {vuoti}, {righe:,} ore nuove")
