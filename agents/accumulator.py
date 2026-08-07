#!/usr/bin/env python3
"""
tracker.py — PAPER TEST LIVE (out-of-sample), versione EFFICIENTE (~5 chiamate/giro, rate-limit safe).
Usa SOLO la lista-pool GeckoTerminal (prezzo + volume h1/h24 + liquidità in 1 call per ~20 pool).
Segnale = volume dell'ultima ora >> media oraria del giorno + prezzo in salita (forte acquisto).
Apre posizioni paper $100, scale-out, chiude a 72h. NIENTE soldi reali. Stato in data/paper_state.json.
"""
import urllib.request, json, time, os, statistics as st
GT = "https://api.geckoterminal.com/api/v2"
STATE = "data/paper_state.json"
NOTIONAL = 100.0
SPIKE_RATIO = 4.0      # vol ultima ora > 4x la media oraria del giorno
MIN_H1_VOL = 10000     # e almeno $10k assoluto (compra vera, non rumore)
MIN_PC_H1 = 1.0        # e prezzo su >= +1% nell'ora (forte acquisto)
FEE_RT = 0.02
LADDER = [(0.30,0.25),(0.80,0.25),(1.80,0.25)]  # scale-out: 25% a +30/+80/+180%
WINDOW_H = 72
COOLDOWN = 24*3600     # stesso pool: max 1 segnale/giorno
NOW = int(time.time())
PAGES = 6              # ~120 pool

def get(url):
    last=None
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}), timeout=30))
        except Exception as e: last=e; time.sleep(2.5*(a+1))
    raise last

os.makedirs("data", exist_ok=True)
S = json.load(open(STATE)) if os.path.exists(STATE) else {"open":[], "closed":[], "last_sig":{}, "runs":0, "started":NOW}
S.setdefault("last_sig", {})

# 1) lista pool (poche chiamate): prezzo + volumi + liquidità di ~120 pool
mkt={}
for pg in range(1, PAGES+1):
    try:
        d=get(f"{GT}/networks/robinhood/pools?page={pg}")
        for p in d.get("data",[]):
            a=p.get("attributes",{}); addr=a.get("address")
            if not addr: continue
            vol=a.get("volume_usd",{}) or {}; pc=a.get("price_change_percentage",{}) or {}
            try: price=float(a.get("base_token_price_usd") or 0)
            except: price=0
            mkt[addr]={"name":a.get("name"),"price":price,"liq":float(a.get("reserve_in_usd") or 0),
                       "vh1":float(vol.get("h1") or 0),"vh24":float(vol.get("h24") or 0),
                       "pc1":float(pc.get("h1") or 0)}
        time.sleep(2.5)
    except Exception as e:
        print("pool pg", pg, "err", str(e)[:50]); break

# 1.5) ACCUMULATORE ARCHIVIO: fotografa TUTTA la chain ogni ora (cresce all'infinito, gratis).
# Registriamo i token MENTRE sono vivi -> quando muoiono abbiamo ancora i dati -> aggiusta survivorship.
# File COMPRESSO IMMUTABILE per ora (poco spazio, niente gonfiore git: scritto 1 volta, mai riscritto).
if mkt:
    import gzip
    day = time.strftime("%Y-%m-%d", time.gmtime(NOW))
    hm = time.strftime("%H%M", time.gmtime(NOW))
    os.makedirs(f"data/snapshots/{day}", exist_ok=True)
    with gzip.open(f"data/snapshots/{day}/{hm}.jsonl.gz", "wt") as f:
        for addr, m in mkt.items():
            f.write(json.dumps({"ts": NOW, "a": addr, "n": m["name"], "p": m["price"],
                                "liq": round(m["liq"]), "v1": round(m["vh1"]), "v24": round(m["vh24"]),
                                "pc1": m["pc1"]}) + "\n")

# 2) rileva NUOVI segnali
new_sig=0
for addr,m in mkt.items():
    if m["price"]<=0 or m["vh24"]<=0: continue
    hourly_avg = m["vh24"]/24
    if hourly_avg<=0: continue
    ratio = m["vh1"]/hourly_avg
    last = S["last_sig"].get(addr, 0)
    if ratio>=SPIKE_RATIO and m["vh1"]>=MIN_H1_VOL and m["pc1"]>=MIN_PC_H1 and (NOW-last)>COOLDOWN:
        S["last_sig"][addr]=NOW; new_sig+=1
        S["open"].append({"pool":addr,"name":m["name"],"entry_ts":NOW,"entry":m["price"],
                          "liq":m["liq"],"max_px":m["price"],"last_px":m["price"],
                          "sold":0.0,"realized":0.0})

# 3) aggiorna posizioni aperte (dalla stessa lista, 0 chiamate extra)
still=[]
for pos in S["open"]:
    m=mkt.get(pos["pool"])
    cur = m["price"] if (m and m["price"]>0) else pos.get("last_px", pos["entry"])
    pos["last_px"]=cur
    pos["max_px"]=max(pos.get("max_px",pos["entry"]), cur)
    liq=max(pos["liq"],1)
    for thr,frac in LADDER:
        key=f"h{thr}"
        if pos.get(key): continue
        if pos["max_px"]>=pos["entry"]*(1+thr):
            exit_imp=(NOTIONAL*frac)/(liq*0.7)
            pos["realized"]+=frac*((1+thr)*(1-exit_imp)); pos["sold"]+=frac; pos[key]=True
    if NOW-pos["entry_ts"]>=WINDOW_H*3600:
        rem=1.0-pos["sold"]; end_ret=cur/pos["entry"]
        exit_imp=(NOTIONAL*rem)/(liq*0.7)
        pos["realized"]+=rem*(end_ret*(1-exit_imp))
        pos["net_ret"]=pos["realized"]*(1-FEE_RT)*(1-NOTIONAL/liq)-1
        pos["closed_ts"]=NOW; S["closed"].append(pos)
    else:
        still.append(pos)
S["open"]=still

# 4) stats
S["runs"]+=1; S["last_run"]=NOW
S["last_sig"]={k:v for k,v in S["last_sig"].items() if NOW-v < 7*24*3600}  # pota vecchi
closed=S["closed"]
if closed:
    rets=[c["net_ret"] for c in closed]
    S["stats"]={"n_closed":len(closed),"n_open":len(S["open"]),
                "mean_ret":sum(rets)/len(rets),"median_ret":st.median(rets),
                "win_rate":sum(1 for x in rets if x>0)/len(rets),
                "paper_pnl_usd":sum(NOTIONAL*r for r in rets)}
json.dump(S, open(STATE,"w"))
print(f"✅ run #{S['runs']} | pool visti: {len(mkt)} | nuovi segnali: {new_sig} | aperte: {len(S['open'])} | chiuse: {len(closed)}")
if closed:
    s=S["stats"]; print(f"   PAPER: {s['n_closed']} chiusi | media {s['mean_ret']*100:+.1f}% | mediana {s['median_ret']*100:+.1f}% | win {s['win_rate']*100:.0f}% | P&L ${s['paper_pnl_usd']:+.2f}")
