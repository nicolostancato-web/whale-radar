"""Scende indietro DAVVERO nella storia del finanziamento Binance.

Il primo scaricatore si fermava a 500 pagamenti (166 giorni) per un uscita
anticipata dal ciclo. Qui si cammina all'indietro con endTime esplicito
finche' l'archivio finisce. Piu' SETTIMANE distinte = piu' osservazioni
indipendenti sull'unica cosa viva (le monete nella stessa settimana non
sono osservazioni nuove).
"""
import json, os, time, glob, urllib.request
def get(u):
    r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r, timeout=30))
mon=[os.path.basename(f).replace(".json","")
     for f in sorted(glob.glob("data/finanziamento_binance/*.json"))]
os.makedirs("data/finanziamento_profondo", exist_ok=True)
print(f"{len(mon)} monete")
for s in mon:
    out=f"data/finanziamento_profondo/{s}.json"
    if os.path.exists(out): continue
    vis={}; fine=int(time.time()*1000)
    for giro in range(30):
        try:
            d=get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={s}USDT"
                  f"&endTime={fine}&limit=1000")
        except Exception as e:
            print(f"   {s}: {e}"); break
        if not d: break
        prima=len(vis)
        for x in d: vis[int(x["fundingTime"])]=float(x["fundingRate"])
        if len(vis)==prima: break           # non arrivano piu' dati nuovi
        fine=min(int(x["fundingTime"]) for x in d)-1
        time.sleep(0.15)
    if vis:
        json.dump([{"t":t,"r":vis[t]} for t in sorted(vis)], open(out,"w"))
        g=(max(vis)-min(vis))/86400000
        print(f"   {s}: {len(vis)} pagamenti, {g:.0f} giorni")
