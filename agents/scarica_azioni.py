"""Cento azioni dalla stessa fonte gratuita, per dare potenza alla prova
fra-mercati. Con 18 materie prime l'intervallo era +/-4,9%: non puo' decidere.
Si scelgono titoli GRANDI e noti, perche' sono quelli tradabili su trade.xyz
(98 mercati azionari) e perche' una lista scelta da me fra i vincenti sarebbe
una selezione a posteriori."""
import json, urllib.request, os, time
os.makedirs("data/azioni", exist_ok=True)
TITOLI = """AAPL MSFT NVDA AMZN GOOGL META TSLA BRK-B LLY AVGO JPM XOM UNH V MA PG JNJ HD
COST ABBV MRK WMT NFLX AMD PEP KO ADBE CRM TMO CSCO ACN MCD ABT LIN DHR INTC VZ TXN
NKE PM WFC DIS INTU AMGN CAT IBM QCOM GE NOW BA HON SPGI UNP LOW RTX BKNG SBUX GS
ISRG BLK MDT ELV ADP DE LMT SYK AXP MDLZ GILD TJX VRTX MMC CI ADI PLD REGN CB SCHW
MO ZTS SO BSX DUK PGR EOG CME ITW SLB APD CL AON MU NOC WM FDX ORLY MCK HUM PSA
PYPL""".split()
fatti=0; falliti=[]
for s in TITOLI:
    f=f"data/azioni/{s}.json"
    if os.path.exists(f): fatti+=1; continue
    try:
        r=urllib.request.Request(
          f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?interval=1d&range=10y",
          headers={"user-agent":"Mozilla/5.0"})
        with urllib.request.urlopen(r,timeout=30) as fh: j=json.load(fh)
        res=j["chart"]["result"][0]
        json.dump({"t":res["timestamp"],"c":res["indicators"]["quote"][0]["close"]}, open(f,"w"))
        fatti+=1
    except Exception as e:
        falliti.append(s)
    time.sleep(0.15)
print(f"azioni scaricate: {fatti}/{len(TITOLI)}")
if falliti: print(f"   non riuscite ({len(falliti)}): {' '.join(falliti[:12])}")
