"""Prova IN AVANTI del premio di volatilita' e della sua scelta temporale.

Perche' in avanti: l'indice di volatilita' esiste solo per BTC ed ETH, che
sono il campione in cui la regola e' nata. Non esiste un campione tenuto da
parte, e inventarne uno storto sarebbe peggio di non averlo.

Ogni esecuzione: se e' passata una finestra da 30 giorni dall'ultima riga
aperta, la chiude calcolando la realizzata, e ne apre una nuova.
Le righe aperte registrano la PREVISIONE prima di sapere l'esito.
"""
import json, os, math, statistics as st, datetime, urllib.request, time
FUORI="data/volatilita/prova_in_avanti.jsonl"
GIORNI=30; ORE=GIORNI*24
def get(u):
    r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
    d=json.load(urllib.request.urlopen(r, timeout=40))
    return d.get("result", d) if isinstance(d,dict) else d
def realizzata_da(m, t0, t1):
    ore={}
    fine=t1
    for _ in range(4):
        k=get(f"https://fapi.binance.com/fapi/v1/klines?symbol={m}USDT"
              f"&interval=1h&limit=1500&endTime={fine}")
        if not k: break
        for x in k: ore[int(x[0])]=float(x[4])
        fine=int(k[0][0])-1
        if min(ore) <= t0: break
        time.sleep(0.2)
    ts=sorted(t for t in ore if t0<=t<=t1)
    if len(ts)<ORE*0.8: return None
    r=[math.log(ore[ts[i+1]]/ore[ts[i]]) for i in range(len(ts)-1)
       if ts[i+1]-ts[i]==3600000]
    return st.stdev(r)*math.sqrt(24*365)*100
righe=[json.loads(x) for x in open(FUORI)] if os.path.exists(FUORI) else []
ora=int(time.time()*1000)
# 1) chiudere le righe mature
cambi=0
for r in righe:
    if r.get("rv") is not None: continue
    if ora < r["t"]+ORE*3600000: continue
    rv=realizzata_da(r["m"], r["t"], r["t"]+ORE*3600000)
    if rv is None: continue
    r["rv"]=rv
    r["resa"]=(r["iv"]**2-rv**2)/(2*r["iv"])/100*(GIORNI/365)*100
    cambi+=1
# 2) aprire una riga nuova se non ce n'e' una aperta
for m in ("BTC","ETH"):
    if any(x["m"]==m and x.get("rv") is None for x in righe): continue
    st_=get(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?"
            f"currency={m}&start_timestamp={ora-900*3600*1000}&end_timestamp={ora}&resolution=3600")
    d=st_.get("data") if isinstance(st_,dict) else None
    if not d: continue
    iv=float(d[-1][4])
    storia=[float(x["iv"]) for x in json.load(open(f"data/volatilita/dvol_{m}.json"))]
    med=st.median(storia)
    righe.append({"m":m,"t":int(d[-1][0]),"iv":iv,"mediana_storica":med,
                  "sopra_mediana": iv>med,
                  "previsione":"vendere" if iv>med else "stare fermi",
                  "aperta": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M"),
                  "rv":None})
    cambi+=1
with open(FUORI,"w") as f:
    for r in righe: f.write(json.dumps(r)+"\n")
print(f"   righe totali {len(righe)} | modifiche in questo giro {cambi}\n")
for r in righe:
    if r.get("rv") is None:
        print(f"   APERTA  {r['m']}  {r['aperta']}  implicita {r['iv']:.1f} "
              f"(mediana {r['mediana_storica']:.1f}) -> {r['previsione']}")
    else:
        print(f"   chiusa  {r['m']}  implicita {r['iv']:.1f} realizzata {r['rv']:.1f} "
              f"resa {r['resa']:+.3f}%  ({r['previsione']})")
ch=[r for r in righe if r.get("rv") is not None]
if len(ch)>=6:
    v=[r["resa"] for r in ch]
    print(f"\n   {len(ch)} finestre chiuse: media {st.mean(v):+.3f}%")
else:
    print(f"\n   servono almeno 6 finestre chiuse prima di leggere "
          f"(ora {len(ch)}) — circa 3 mesi")
