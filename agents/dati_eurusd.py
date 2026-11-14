"""La macchina dati GENERICA: accetta qualunque simbolo, non solo EUR/USD.

Prima regola della nuova fase: la fonte deve essere gratis e verificabile, e si
DICHIARA quante candele si sono prese e da quando. Niente «circa un anno».
Si provano piu' fonti pubbliche in ordine e si tiene la prima che risponde.
"""
import json, urllib.request, sys, os
os.makedirs("data/mercati", exist_ok=True)
def prendi(url, nome):
    try:
        r=urllib.request.Request(url, headers={"user-agent":"Mozilla/5.0"})
        with urllib.request.urlopen(r, timeout=45) as f:
            return json.load(f)
    except Exception as e:
        print(f"   {nome}: no ({str(e)[:60]})"); return None
SIM = sys.argv[1] if len(sys.argv)>1 else "EURUSD=X"
print(f"cerco i dati per {SIM}\n")
fonti = [
 ("Yahoo 1h / 2 anni",
  f"https://query1.finance.yahoo.com/v8/finance/chart/{SIM}?interval=1h&range=730d"),
 ("Yahoo 1d / 10 anni",
  f"https://query1.finance.yahoo.com/v8/finance/chart/{SIM}?interval=1d&range=10y"),
 ("Yahoo 5m / 60 giorni",
  f"https://query1.finance.yahoo.com/v8/finance/chart/{SIM}?interval=5m&range=60d"),
]
for nome,url in fonti:
    j=prendi(url,nome)
    if not j: continue
    try:
        res=j["chart"]["result"][0]
        t=res["timestamp"]; q=res["indicators"]["quote"][0]
        n=len(t)
        import datetime as dt
        da=dt.datetime.fromtimestamp(t[0],dt.UTC); a=dt.datetime.fromtimestamp(t[-1],dt.UTC)
        print(f"   {nome}: {n:,} candele, da {da:%Y-%m-%d} a {a:%Y-%m-%d}")
        f=f"data/mercati/{SIM.replace('=','_')}_{nome.split()[1].replace('/','')}.json"
        json.dump({"simbolo":SIM,"intervallo":nome,"t":t,
                   "o":q.get("open"),"h":q.get("high"),"l":q.get("low"),
                   "c":q.get("close"),"v":q.get("volume")}, open(f,"w"))
        print(f"      salvato in {f}")
    except Exception as e:
        print(f"   {nome}: risposta non interpretabile ({str(e)[:50]})")
