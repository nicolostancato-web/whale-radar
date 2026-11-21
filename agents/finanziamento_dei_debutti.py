"""Il finanziamento che paga chi e' CORTO su una moneta appena quotata.
Gratis, endpoint pubblico. Scarica i primi pagamenti dal debutto.
"""
import json, glob, os, time, urllib.request, collections
def serie(f):
    try: d=json.load(open(f))
    except Exception: return None
    if not isinstance(d,list) or len(d)<200: return None
    k="t" if "t" in d[0] else ("T" if "T" in d[0] else None)
    return sorted((int(x[k]), x["c"]) for x in d) if k else None
viste={}
for d in ["data/binance","data/binance_piccoli","data/binance_f150","data/binance_f450","data/binance_f600"]:
    for f in glob.glob(d+"/*.json"):
        s=os.path.basename(f).replace("USDT.json","")
        if s not in viste:
            v=serie(f)
            if v: viste[s]=v
pri=collections.Counter(v[0][0] for v in viste.values())
bordi={t for t,n in pri.items() if n>=3}
deb={s:v for s,v in viste.items() if v[0][0] not in bordi}
os.makedirs("data/finanziamento_debutti", exist_ok=True)
def get(u):
    r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r, timeout=30))
n=0
for s,v in sorted(deb.items()):
    out=f"data/finanziamento_debutti/{s}.json"
    if os.path.exists(out): n+=1; continue
    t0=v[0][0]
    try:
        d=get(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={s}USDT"
              f"&startTime={t0}&endTime={t0+30*86400000}&limit=1000")
    except Exception as e:
        print(f"   {s}: {e}"); continue
    json.dump([{"t":int(x["fundingTime"]),"r":float(x["fundingRate"])} for x in d], open(out,"w"))
    n+=1; time.sleep(0.2)
print(f"scaricati {n}/{len(deb)}")
