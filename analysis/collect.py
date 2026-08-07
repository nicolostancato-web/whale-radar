#!/usr/bin/env python3
"""
collect.py — raccoglie il dataset grande della chain Robinhood (una volta, salvato su disco).
Per ogni pool: nome, liquidità (reserve_usd), volume, OHLCV orario storico. Salva incrementale.
Gentile coi rate-limit (GeckoTerminal free ~30/min). Se muore, riprende ciò che ha già salvato.
"""
import urllib.request, json, time, os
GT = "https://api.geckoterminal.com/api/v2"
OUT = "data/dataset.json"
def get(url):
    last=None
    for a in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}), timeout=35))
        except Exception as e:
            last=e; time.sleep(3.0*(a+1))   # backoff su 429
    raise last

os.makedirs("data", exist_ok=True)
data = json.load(open(OUT)) if os.path.exists(OUT) else {}
print(f"gia' salvati: {len(data)} pool")

# 1) lista pool: piu' pagine possibili (dedup)
pool_meta = {}
for pg in range(1, 11):
    try:
        d = get(f"{GT}/networks/robinhood/pools?page={pg}")
        rows = d.get("data", [])
        if not rows: break
        for p in rows:
            a = p.get("attributes", {})
            addr = a.get("address")
            if addr:
                pool_meta[addr] = {
                    "name": a.get("name"),
                    "liq": float(a.get("reserve_in_usd") or 0),
                    "vol24": float((a.get("volume_usd") or {}).get("h24") or 0),
                }
        print(f"  pagina {pg}: {len(rows)} pool (tot unici {len(pool_meta)})")
        time.sleep(2.6)
    except Exception as e:
        print(f"  pagina {pg} stop: {str(e)[:50]}"); break

print(f"pool totali da scaricare: {len(pool_meta)}")

# 2) OHLCV per ogni pool non ancora salvato
n=0
for addr, meta in pool_meta.items():
    if addr in data:  # gia' fatto
        continue
    try:
        d = get(f"{GT}/networks/robinhood/pools/{addr}/ohlcv/hour?aggregate=1&limit=1000")
        oh = d.get("data", {}).get("attributes", {}).get("ohlcv_list", [])
        data[addr] = {**meta, "ohlcv": sorted(oh)}
        n += 1
        if n % 10 == 0:
            json.dump(data, open(OUT, "w"))
            print(f"  ...{n} scaricati/salvati (tot {len(data)})")
        time.sleep(2.6)
    except Exception as e:
        print(f"  {meta.get('name','?')[:16]} err {str(e)[:40]}"); time.sleep(1)
json.dump(data, open(OUT, "w"))
print(f"\n✅ DATASET pronto: {len(data)} pool salvati in {OUT}")
tot_candles = sum(len(v.get("ohlcv", [])) for v in data.values())
print(f"   candele orarie totali: {tot_candles:,}")
