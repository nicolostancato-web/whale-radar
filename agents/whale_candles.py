#!/usr/bin/env python3
"""
WHALE_CANDLES — accumulo FOCALIZZATO di candele sui pool DOVE CI SONO LE WHALE.
Il collector generico si spalma su tutti i pool e lascia buchi (es. BLINK: 174 whale, 0 candele).
Qui: leggo i pool con whale dai file backfill, e ad OGNI run scarico le loro candele orarie (1000 = ~41gg)
+ daily, per TUTTI (sono ~25 -> ci stanno in un run). Cosi' la finestra 72h/168h dopo ogni buy si riempie
e si aggiorna in continuo -> sblocca la verifica della tesi (tieni-e-5x nei giorni dopo). File immutabili,
dedup, gratis (GeckoTerminal). NO live, NO trading.
"""
import urllib.request, json, time, os, gzip, glob

GT = "https://api.geckoterminal.com/api/v2"; PAUSE = 2.6
LIMIT_HOURS = 1000


def get(url, tries=4, pause=2.5):
    last = None
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}), timeout=30))
        except Exception as e:
            last = e; time.sleep(pause * (a + 1))
    return None


def main():
    os.makedirs("data/raw/candles", exist_ok=True)
    now = int(time.time())

    # pool con whale (dai backfill): sono quelli che contano davvero
    wp = {}
    for f in glob.glob("data/raw/whales/backfill_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                try:
                    d = json.loads(l)
                    if d.get("usd") and d.get("pool") and len(d["pool"]) == 42:
                        wp[d["pool"]] = d.get("name", "?")
                except: pass
        except EOFError: pass
    pools = list(wp.items())
    print(f"pool-whale da coprire: {len(pools)}", flush=True)
    if not pools:
        print("nessun pool-whale ancora; esco."); return

    # dedup dagli immutabili
    seen = set()
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                if l.strip():
                    try:
                        d = json.loads(l); seen.add(f"{d['pool']}_{d['ts']}_{d['tf']}")
                    except: pass
        except EOFError: pass

    cf = f"data/raw/candles/whalepools_{now}.jsonl.gz"
    fc = gzip.open(cf, "wt"); nc = 0
    for i, (addr, name) in enumerate(pools):
        for tf in ("hour", "day"):
            d = get(f"{GT}/networks/robinhood/pools/{addr}/ohlcv/{tf}?aggregate=1&limit={LIMIT_HOURS}")
            time.sleep(PAUSE)
            if not d: continue
            for x in d.get("data", {}).get("attributes", {}).get("ohlcv_list", []):
                sid = f"{addr}_{int(x[0])}_{tf}"
                if sid in seen: continue
                seen.add(sid); nc += 1
                fc.write(json.dumps({"pool": addr, "tf": tf, "ts": int(x[0]), "o": x[1], "h": x[2], "l": x[3], "cl": x[4], "v": round(x[5])}) + "\n")
        if (i + 1) % 10 == 0:
            print(f"  ...{i+1}/{len(pools)} pool, +{nc} candele", flush=True)
    fc.close()
    if nc == 0:
        os.remove(cf)
    print(f"✅ whale_candles: {len(pools)} pool-whale | +{nc} candele nuove | archivio: {len(seen):,} candele", flush=True)


if __name__ == "__main__":
    main()
