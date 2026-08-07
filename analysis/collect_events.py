#!/usr/bin/env python3
"""
collect_events.py — FASE 1: dataset EVENTO + GRAFICO-PRIMA + ESITO-DOPO (tutti i pool, compresso).
Per ogni 'grande acquisto' salva: il setup del grafico prima + cosa succede dopo. Migliaia di eventi.
Serve a capire QUALI setup funzionano e COME entrare. Gratis (GeckoTerminal), gzip (poco spazio), resumable.
"""
import urllib.request, json, time, os, gzip, statistics as st
GT = "https://api.geckoterminal.com/api/v2"
OUT = "data/events.jsonl.gz"
SPIKE = 4.0
def get(url):
    last=None
    for a in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}), timeout=35))
        except Exception as e: last=e; time.sleep(3.0*(a+1))
    raise last

os.makedirs("data", exist_ok=True)
done_pools=set()
if os.path.exists(OUT):
    for l in gzip.open(OUT,"rt"):
        try: done_pools.add(json.loads(l)["pool"])
        except: pass
print(f"pool gia' fatti: {len(done_pools)}")

# 1) TUTTI i pool (paginazione fino a esaurimento / rate-limit)
pools={}
for pg in range(1, 26):
    try:
        d=get(f"{GT}/networks/robinhood/pools?page={pg}")
        rows=d.get("data",[])
        if not rows: break
        for p in rows:
            a=p.get("attributes",{}); addr=a.get("address")
            if addr: pools[addr]={"name":a.get("name"),"liq":float(a.get("reserve_in_usd") or 0)}
        print(f"  pag {pg}: {len(rows)} (tot {len(pools)})"); time.sleep(3.2)
    except Exception as e:
        print(f"  pag {pg} stop: {str(e)[:40]}"); break
print(f"pool totali trovati: {len(pools)}")

def features(c, k):
    """c=OHLCV ordinato, k=indice evento. Ritorna setup-prima + esito-dopo."""
    ts,o,hi,lo,cl,v = c[k]
    pre = c[max(0,k-24):k]        # 24h prima
    post = [c[k+j] for j in range(1,73) if k+j < len(c)]  # 72h dopo
    if len(pre)<6 or len(post)<6: return None
    pre_cl=[x[4] for x in pre if x[4]>0]; pre_v=[x[5] for x in pre]
    postp=[x[4] for x in post if x[4]>0]
    if not pre_cl or not postp or cl<=0: return None
    flat = (max(pre_cl)/min(pre_cl)-1) if min(pre_cl)>0 else 9  # range 24h prima (piccolo=piatto)
    prior_ret = cl/pre_cl[0]-1                                   # quanto gia' salito in 24h
    peak = max(postp)/cl-1
    trough = min(postp)/cl-1
    tpk = next((j for j,x in enumerate(post,1) if x[4]>=max(postp)),0)
    return {
        "flat_24h": round(flat,3), "prior_ret_24h": round(prior_ret,3),
        "vol_ratio": round(v/(st.median(pre_v) or 1),1), "vol_usd": round(v),
        "r6": round(post[5][4]/cl-1,3) if len(post)>5 else None,
        "r24": round(post[23][4]/cl-1,3) if len(post)>23 else None,
        "r72": round(postp[-1]/cl-1,3),
        "peak72": round(peak,3), "drawdown72": round(trough,3), "hours_to_peak": tpk,
    }

# 2) per ogni pool: OHLCV -> eventi con features
new=0
fout=gzip.open(OUT,"at")
for i,(addr,meta) in enumerate(pools.items()):
    if addr in done_pools: continue
    try:
        d=get(f"{GT}/networks/robinhood/pools/{addr}/ohlcv/hour?aggregate=1&limit=1000")
        c=sorted(d.get("data",{}).get("attributes",{}).get("ohlcv_list",[]))
        time.sleep(3.2)
    except Exception as e:
        print(f"  {meta['name'][:14]} err {str(e)[:30]}"); continue
    if len(c)<40: continue
    vols=[x[5] for x in c if x[5]>0]; medv=st.median(vols) if vols else 0
    if medv<=0: continue
    for k in range(24, len(c)-6):
        ts,o,hi,lo,cl,v=c[k]
        if v>SPIKE*medv and cl>o and cl>0:
            f=features(c,k)
            if f:
                f.update({"pool":addr,"name":meta["name"],"liq":round(meta["liq"]),"ts":ts,"entry":cl})
                fout.write(json.dumps(f)+"\n"); new+=1
    if (i+1)%15==0: fout.flush(); print(f"  ...{i+1} pool, {new} eventi nuovi")
fout.close()
# conteggio finale
tot=sum(1 for _ in gzip.open(OUT,"rt"))
size=os.path.getsize(OUT)/1024
print(f"\n✅ DATASET EVENTI: +{new} nuovi | TOTALE {tot} eventi | file {size:.0f} KB (compresso)")
