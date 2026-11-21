"""Lo storico dei tassi di finanziamento da Hyperliquid: informazione che NON
e' il prezzo, pubblica, senza chiave, una lettura all'ora su decine di mercati.

Il tasso di finanziamento dice chi sta pagando chi: se e' molto positivo, i
lunghi pagano i corti, cioe' la folla e' da una parte sola. E' posizionamento,
non storia dei prezzi — quindi non e' chiuso dal risultato sui pattern.
"""
import json, urllib.request, os, time
os.makedirs("data/finanziamento", exist_ok=True)
def post(corpo, tent=3):
    for _ in range(tent):
        try:
            r=urllib.request.Request("https://api.hyperliquid.xyz/info",
                json.dumps(corpo).encode(), {"content-type":"application/json","user-agent":"Mozilla/5.0"})
            with urllib.request.urlopen(r,timeout=40) as f: return json.load(f)
        except Exception: time.sleep(2)
    return None
meta=post({"type":"meta"})
if not meta: print("universo non raggiungibile"); raise SystemExit
nomi=[u["name"] for u in meta["universe"] if not u.get("isDelisted")]
print(f"mercati vivi su Hyperliquid: {len(nomi)}")
INIZIO=1759276800000   # 1 ottobre 2025
fatti=0; righe=0
for c in nomi[:120]:
    f=f"data/finanziamento/{c}.json"
    if os.path.exists(f): fatti+=1; continue
    tutto=[]; t=INIZIO
    for _ in range(14):                      # la finestra per chiamata e' limitata
        d=post({"type":"fundingHistory","coin":c,"startTime":t})
        if not d: break
        nuovi=[x for x in d if x["time"]>t]
        if not nuovi: break
        tutto+=nuovi; t=nuovi[-1]["time"]
        if len(d)<500: break
        time.sleep(0.12)
    if len(tutto)>500:
        json.dump(tutto, open(f,"w")); fatti+=1; righe+=len(tutto)
    time.sleep(0.12)
print(f"scaricati: {fatti} mercati, {righe:,} letture orarie")
