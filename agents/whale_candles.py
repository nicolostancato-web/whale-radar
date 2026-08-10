#!/usr/bin/env python3
"""
WHALE_CANDLES — candele (orarie+daily) su TUTTO l'universo memecoin, non solo sui pool con whale.
Serve a misurare l'esito (72h/168h) su MOLTI token diversi -> senza diversita' ogni numero e' un aneddoto.
Legge il registro pool, salta le coppie di arbitraggio, e a batch (per arretrato) scarica le candele di
ogni memecoin. Su piu' run copre tutti i ~185. File immutabili, dedup, resumable. Gratis (GeckoTerminal). NO live.
"""
import urllib.request, json, time, os, gzip, glob

GT = "https://api.geckoterminal.com/api/v2"; PAUSE = 2.6; LIMIT = 1000
BATCH = int(os.environ.get("CANDLE_BATCH", 45))     # pool per run (45*2 chiamate ~ 8-9 min, margine sul timeout 20min)
MONEY = {"weth", "eth", "usdg", "usdc", "usdt", "dai", "usdb"}
POOLS = "data/pools.json"; CK = "data/whale_candles_checkpoint.json"


def get(url, tries=4, pause=2.5):
    last = None
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}), timeout=30))
        except Exception as e:
            last = e; time.sleep(pause * (a + 1))
    return None


def is_meme(name):
    parts = [x.strip().split(" ")[0].lower() for x in (name or "").split("/")]
    return not (len(parts) == 2 and parts[0] in MONEY and parts[1] in MONEY)


def main():
    os.makedirs("data/raw/candles", exist_ok=True)
    now = int(time.time())
    reg = json.load(open(POOLS)) if os.path.exists(POOLS) else {"pools": {}}
    ck = json.load(open(CK)) if os.path.exists(CK) else {}
    # UNIVERSO = registro (include i morti, catturati alla nascita) UNITO alla lista fresca GeckoTerminal (i vivi).
    universe = {a: v.get("name") for a, v in reg["pools"].items() if len(a) == 42}
    for pg in range(1, 11):                            # tutte le pagine GT (fino a ~200 pool vivi)
        d = get(f"{GT}/networks/robinhood/pools?page={pg}")
        rows = d.get("data", []) if d else []
        if not rows: break
        for p in rows:
            a = p.get("attributes", {})
            if a.get("address"): universe[a["address"]] = a.get("name")
        time.sleep(PAUSE)
    pools = [(a, n) for a, n in universe.items() if len(a) == 42 and is_meme(n)]
    pools.sort(key=lambda kv: ck.get(kv[0], 0))       # i meno recentemente aggiornati prima
    todo = pools[:BATCH]
    print(f"memecoin nel registro: {len(pools)} | copro in questo run: {len(todo)}", flush=True)

    seen = set()
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                if l.strip():
                    try:
                        d = json.loads(l); seen.add(f"{d['pool']}_{d['ts']}_{d['tf']}")
                    except: pass
        except EOFError: pass

    cf = f"data/raw/candles/meme_{now}.jsonl.gz"; fc = gzip.open(cf, "wt"); nc = 0
    for i, (addr, name) in enumerate(todo):
        for tf in ("hour", "day"):
            d = get(f"{GT}/networks/robinhood/pools/{addr}/ohlcv/{tf}?aggregate=1&limit={LIMIT}")
            time.sleep(PAUSE)
            if not d: continue
            for x in d.get("data", {}).get("attributes", {}).get("ohlcv_list", []):
                sid = f"{addr}_{int(x[0])}_{tf}"
                if sid in seen: continue
                seen.add(sid); nc += 1
                fc.write(json.dumps({"pool": addr, "tf": tf, "ts": int(x[0]), "o": x[1], "h": x[2], "l": x[3], "cl": x[4], "v": round(x[5])}) + "\n")
        ck[addr] = now
        if (i + 1) % 20 == 0:
            print(f"  ...{i+1}/{len(todo)} pool, +{nc} candele", flush=True)
    fc.close()
    if nc == 0:
        os.remove(cf)
    json.dump(ck, open(CK, "w"))
    done = sum(1 for a, _ in pools if ck.get(a, 0) > now - 12 * 3600)
    print(f"✅ whale_candles: +{nc} candele | memecoin aggiornati nelle ultime 12h: {done}/{len(pools)} | archivio: {len(seen):,}", flush=True)


if __name__ == "__main__":
    main()
