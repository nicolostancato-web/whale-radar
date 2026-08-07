#!/usr/bin/env python3
"""
tracker.py — PAPER TEST LIVE (out-of-sample) della strategia whale/momentum su Robinhood chain.
Ogni run (orario): 1) trova NUOVI segnali (spike volume+verde) 2) apre posizioni paper ($100 notional)
3) aggiorna le aperte con prezzo attuale + scale-out 4) chiude dopo 72h 5) aggiorna P&L. Tutto GRATIS.
NIENTE soldi reali. Stato in data/paper_state.json. Se il segnale regge in avanti -> allora soldi veri piccoli.
"""
import urllib.request, json, time, os, statistics as st
GT = "https://api.geckoterminal.com/api/v2"
STATE = "data/paper_state.json"
NOTIONAL = 100.0          # $ paper per segnale
SPIKE = 5.0               # volume candela > 5x mediana
FEE_RT = 0.02             # fee round-trip
LADDER = [(0.30,0.25),(0.80,0.25),(1.80,0.25)]  # scale-out
WINDOW_H = 72
NOW = int(time.time())

def get(url):
    last=None
    for a in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}), timeout=35))
        except Exception as e: last=e; time.sleep(3.0*(a+1))
    raise last

os.makedirs("data", exist_ok=True)
S = json.load(open(STATE)) if os.path.exists(STATE) else {"open":[], "closed":[], "seen":[], "runs":0, "started":NOW}
seen = set(S["seen"])

# 1) pool attivi (top ~50 per volume)
pools=[]
try:
    d=get(f"{GT}/networks/robinhood/pools?page=1")
    for p in d.get("data",[]):
        a=p.get("attributes",{})
        pools.append({"addr":a.get("address"),"name":a.get("name"),"liq":float(a.get("reserve_in_usd") or 0)})
    time.sleep(2.6)
    d=get(f"{GT}/networks/robinhood/pools?page=2")
    for p in d.get("data",[]):
        a=p.get("attributes",{})
        pools.append({"addr":a.get("address"),"name":a.get("name"),"liq":float(a.get("reserve_in_usd") or 0)})
except Exception as e: print("pool err", str(e)[:60])
pools=[p for p in pools if p["addr"]][:50]

# 2) rileva NUOVI segnali (spike nelle ultime ~3 candele)
new_sig=0
for p in pools:
    try:
        d=get(f"{GT}/networks/robinhood/pools/{p['addr']}/ohlcv/hour?aggregate=1&limit=200")
        c=sorted(d.get("data",{}).get("attributes",{}).get("ohlcv_list",[]))
        time.sleep(2.6)
    except: continue
    if len(c)<40: continue
    vols=[x[5] for x in c if x[5]>0]; medv=st.median(vols) if vols else 0
    if medv<=0: continue
    for x in c[-3:]:  # ultime 3 candele orarie
        ts,o,hi,lo,cl,v=x
        sid=f"{p['addr']}_{ts}"
        if sid in seen: continue
        if v>SPIKE*medv and cl>o and cl>0 and NOW-ts < 4*3600:  # spike fresco (<4h)
            seen.add(sid); new_sig+=1
            S["open"].append({"sid":sid,"pool":p["addr"],"name":p["name"],"entry_ts":ts,"entry":cl,"liq":p["liq"],"sold":0.0,"realized":0.0})

# 3) aggiorna posizioni aperte
still_open=[]
for pos in S["open"]:
    try:
        d=get(f"{GT}/networks/robinhood/pools/{pos['pool']}/ohlcv/hour?aggregate=1&limit=100")
        c=sorted(d.get("data",{}).get("attributes",{}).get("ohlcv_list",[]))
        time.sleep(1.5)
    except: still_open.append(pos); continue
    path=[x[4] for x in c if x[0]>pos["entry_ts"] and x[4]>0]
    if not path: still_open.append(pos); continue
    liq=max(pos["liq"],1)
    # scale-out: vendi tranche quando il path tocca le soglie (una volta)
    for thr,frac in LADDER:
        key=f"h{thr}"
        if pos.get(key): continue
        if any(px>=pos["entry"]*(1+thr) for px in path):
            exit_imp=(NOTIONAL*frac)/(liq*0.7)
            pos["realized"]+=frac*((1+thr)*(1-exit_imp))
            pos["sold"]+=frac; pos[key]=True
    age=NOW-pos["entry_ts"]
    if age>=WINDOW_H*3600:  # chiudi il resto a mercato
        rem=1.0-pos["sold"]
        end_ret=path[-1]/pos["entry"]
        exit_imp=(NOTIONAL*rem)/(liq*0.7)
        pos["realized"]+=rem*(end_ret*(1-exit_imp))
        entry_imp=NOTIONAL/liq
        pos["net_ret"]=pos["realized"]*(1-FEE_RT)*(1-entry_imp)-1
        pos["closed_ts"]=NOW
        S["closed"].append(pos)
    else:
        still_open.append(pos)
S["open"]=still_open

# 4) stats
S["seen"]=list(seen)[-5000:]; S["runs"]+=1; S["last_run"]=NOW
closed=S["closed"]
if closed:
    rets=[c["net_ret"] for c in closed]
    S["stats"]={"n_closed":len(closed),"n_open":len(S["open"]),
                "mean_ret":sum(rets)/len(rets),"median_ret":st.median(rets),
                "win_rate":sum(1 for x in rets if x>0)/len(rets),
                "paper_pnl_usd":sum(NOTIONAL*r for r in rets)}
json.dump(S, open(STATE,"w"))
print(f"✅ run #{S['runs']} | nuovi segnali: {new_sig} | aperte: {len(S['open'])} | chiuse: {len(closed)}")
if closed:
    s=S["stats"]
    print(f"   PAPER: {s['n_closed']} trade chiusi | media {s['mean_ret']*100:+.1f}% | mediana {s['median_ret']*100:+.1f}% | win {s['win_rate']*100:.0f}% | P&L ${s['paper_pnl_usd']:+.2f}")
