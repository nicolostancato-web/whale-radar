#!/usr/bin/env python3
"""
MULTICHAIN_COLLECTOR — espande l'accumulo alle chain GROSSE via GeckoTerminal (1 sola API, tutte le chain).
Risolve il collo di bottiglia dati: Robinhood dava ~3 tradeabili/giorno (anni per imparare); Solana/BSC/Base
ne lanciano migliaia. Scopre memecoin pool + scarica candele orarie, per chain, in data/multichain/<chain>/.
Stesso metodo/loop/learner: gli diamo solo 100x piu' dati. Resumable, immutabile, compresso, budget-tempo. €0.
"""
import urllib.request, urllib.error, json, gzip, os, time

CHAINS = ["solana", "bsc", "base", "robinhood"]
GT = "https://api.geckoterminal.com/api/v2"
MONEY = {"weth", "eth", "usdg", "usdc", "usdt", "dai", "usdb", "weth9", "sol", "wsol", "wbnb", "bnb", "busd", "usd1"}
MAX_SECONDS = 560          # budget tempo per run (poi committa e riprende al prossimo)
NEW_PAGES = 8              # pagine di new_pools per chain (20/pagina)
CANDLE_BATCH = 120         # quante candele scaricare per chain per run
now0 = time.time()


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "wr"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(8 * (i + 1))
            else: time.sleep(2)
        except Exception: time.sleep(2)
    return None


def is_meme(name):
    p = [x.strip().split(" ")[0].lower() for x in (name or "").split("/")]
    return len(p) == 2 and not (p[0] in MONEY and p[1] in MONEY)


def main():
    os.makedirs("data/multichain", exist_ok=True)
    envc = os.environ.get("CHAIN", "").strip().lower()
    if envc in CHAINS:
        chain = envc   # matrix: una chain DEDICATA per job → 4 chain in parallelo (4x throughput, IP diversi)
    else:
        # fallback manuale: round-robin una chain per run
        rf = "data/multichain/rotation.json"
        rot = json.load(open(rf)) if os.path.exists(rf) else {"i": 0}
        chain = CHAINS[rot["i"] % len(CHAINS)]
        rot["i"] = (rot["i"] + 1) % len(CHAINS); json.dump(rot, open(rf, "w"))

    total_new = total_cand = 0
    for chain in [chain]:
        if time.time() - now0 > MAX_SECONDS: break
        base = f"data/multichain/{chain}"
        os.makedirs(f"{base}/candles", exist_ok=True)
        poolf = f"{base}/pools.json"
        pools = json.load(open(poolf)) if os.path.exists(poolf) else {}
        ckf = f"{base}/ckpt.json"
        ck = json.load(open(ckf)) if os.path.exists(ckf) else {}
        ck.setdefault("last_fetch", {})   # addr -> epoch dell'ultimo scarico

        # --- 1. SCOPERTA: nuovi pool + trending (memecoin) ---
        for kind in ("new_pools", "trending_pools"):
            for pg in range(1, NEW_PAGES + 1):
                if time.time() - now0 > MAX_SECONDS: break
                d = get(f"{GT}/networks/{chain}/{kind}?page={pg}")
                time.sleep(2.2)
                if not d or not d.get("data"): break
                for p in d["data"]:
                    a = p["attributes"]; addr = a.get("address"); nm = a.get("name")
                    if addr and is_meme(nm) and addr not in pools:
                        pools[addr] = {"name": nm, "created": a.get("pool_created_at"), "seen": int(now0)}
                        total_new += 1
        json.dump(pools, open(poolf, "w"))

        # --- 2. CANDELE: priorita ai MAI scaricati, poi RI-scarica i GIOVANI (accumulano storia invecchiando) ---
        lf = ck["last_fetch"]; nowi = int(now0)
        never = [a for a in pools if a not in lf]
        stale = [a for a in pools if a in lf and nowi - lf[a] > 20 * 3600
                 and nowi - pools[a].get("seen", nowi) < 8 * 86400]   # giovane <8gg: la storia 168h non e' ancora piena
        todo = (never + stale)[:CANDLE_BATCH]
        for addr in todo:
            if time.time() - now0 > MAX_SECONDS: break
            d = get(f"{GT}/networks/{chain}/pools/{addr}/ohlcv/hour?aggregate=1&limit=168")
            time.sleep(2.2)
            lf[addr] = nowi
            if not d: continue
            lst = d.get("data", {}).get("attributes", {}).get("ohlcv_list", [])
            if not lst: continue
            with gzip.open(f"{base}/candles/{addr}.jsonl.gz", "wt") as fo:  # sovrascrive con la storia piu' piena
                for row in lst:  # [ts, o, h, l, c, vol]
                    fo.write(json.dumps({"ts": row[0], "op": row[1], "hi": row[2], "lo": row[3],
                                         "cl": row[4], "vol": row[5]}) + "\n")
            total_cand += 1
        json.dump(ck, open(ckf, "w"))
        print(f"  {chain}: {len(pools)} pool | +{total_cand} candele (mai {len(never)}, giovani-stantii {len(stale)})", flush=True)

    print(f"MULTICHAIN | +{total_new} pool nuovi | +{total_cand} candele scaricate", flush=True)


if __name__ == "__main__":
    main()
