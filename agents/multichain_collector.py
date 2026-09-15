#!/usr/bin/env python3
"""
MULTICHAIN_COLLECTOR — espande l'accumulo alle chain GROSSE via GeckoTerminal (1 sola API, tutte le chain).
Risolve il collo di bottiglia dati: Robinhood dava ~3 tradeabili/giorno (anni per imparare); Solana/BSC/Base
ne lanciano migliaia. Scopre memecoin pool + scarica candele orarie, per chain, in data/multichain/<chain>/.
Stesso metodo/loop/learner: gli diamo solo 100x piu' dati. Resumable, immutabile, compresso, budget-tempo. €0.
"""
import urllib.request, urllib.error, json, gzip, os, time, datetime

CHAINS = ["solana", "bsc", "base", "robinhood"]
GT = "https://api.geckoterminal.com/api/v2"
MONEY = {"weth", "eth", "usdg", "usdc", "usdt", "dai", "usdb", "weth9", "sol", "wsol", "wbnb", "bnb", "busd", "usd1"}
MAX_SECONDS = int(os.environ.get("BUDGET_SEC", 560))   # budget tempo run (l'engine passa 110: il suo timeout e' 130)
NEW_PAGES = 4              # pagine di new_pools per chain (20/pagina): le prime sono le fresche, le altre
                           # erano gia' viste e ci mangiavano meta' budget in chiamate inutili
CANDLE_BATCH = 120         # quante candele scaricare per chain per run
FRESH_MIN_H = 3            # sotto le 3h di vita non ha abbastanza candele per entry+2h
FRESH_MAX_H = 96           # entro 4 giorni = ancora utile al forward (demo-live)
FRESH_QUOTA = 0.70         # 70% del batch ai GIOVANI (sbloccano il forward), 30% al backlog storico
now0 = time.time()


# THROTTLE ADATTIVO: GeckoTerminal free ~30 chiamate/min. Prima, a ogni 429, get() dormiva 8+16+24s = 24s
# BRUCIATI su un budget di 110s (bastavano 4 rate-limit per finire il run senza scaricare niente).
# Ora: una pausa comune fra le chiamate che si allunga se prendiamo 429 e si accorcia se va liscio, e UN solo
# retry breve. Stesse chiamate/minuto verso l'API, ma il tempo lo spendiamo a scaricare invece che a dormire.
_pace = {"gap": 2.2, "last": 0.0}


def get(url, tries=2):
    for i in range(tries):
        wait = _pace["gap"] - (time.time() - _pace["last"])
        if wait > 0: time.sleep(wait)
        _pace["last"] = time.time()
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "wr"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read())
            _pace["gap"] = max(1.6, _pace["gap"] * 0.9)          # va liscio: stringi un po'
            return d
        except urllib.error.HTTPError as e:
            if e.code == 429: _pace["gap"] = min(8.0, _pace["gap"] * 1.6)   # rate limit: rallenta il ritmo
        except Exception: pass
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
        # QUANDO L'ARRETRATO E' ENORME, SCOPRIRE E' CONTROPRODUCENTE (04/09).
        # Su BSC: 17.661 pool conosciuti, 1.206 con le candele. Scoprivamo pool piu' in fretta di
        # quanto riuscissimo a scaricarne i prezzi, quindi ogni giro allungava una coda che non
        # smaltiremo mai — e intanto rubava chiamate proprio a chi doveva smaltirla.
        # Un pool di cui non sapremo mai il prezzo non e' un dato: e' una riga in piu' in un elenco.
        # Sopra questa soglia si scopre solo il minimo (i nuovissimi, che sbloccano il forward) e
        # tutto il resto del budget va alle candele.
        mai_scaricati = sum(1 for a in pools if a not in ck["last_fetch"])
        pagine = 1 if mai_scaricati > 3000 else NEW_PAGES
        if pagine < NEW_PAGES:
            print(f"  {chain}: arretrato {mai_scaricati}, riduco la scoperta e scarico prezzi", flush=True)
        for kind in (("new_pools",) if pagine < NEW_PAGES else ("new_pools", "trending_pools")):
            for pg in range(1, pagine + 1):
                if time.time() - now0 > MAX_SECONDS: break
                d = get(f"{GT}/networks/{chain}/{kind}?page={pg}")
                if not d or not d.get("data"): break
                for p in d["data"]:
                    a = p["attributes"]; addr = a.get("address"); nm = a.get("name")
                    if addr and is_meme(nm) and addr not in pools:
                        pools[addr] = {"name": nm, "created": a.get("pool_created_at"), "seen": int(now0)}
                        total_new += 1
        json.dump(pools, open(poolf, "w"))

        # --- 2. CANDELE: priorita ai GIOVANI (LIFO), poi backlog storico ---
        # Perche': i pool nascono ~1400/giorno e ne scarichiamo ~300 → la coda "mai scaricati" in ordine di
        # scoperta (FIFO) cresce piu' veloce di quanto la smaltiamo, quindi i token FRESCHI non arrivavano MAI
        # (3914 pool Base nati dopo il 27/08 = 0 candele → demo_live_base fermo a 0 trade). Ora i giovani passano avanti.
        lf = ck["last_fetch"]; nowi = int(now0)

        def age_h(a):
            c = pools[a].get("created")
            if c:
                try:
                    return (nowi - datetime.datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ")
                            .replace(tzinfo=datetime.timezone.utc).timestamp()) / 3600
                except Exception: pass
            return (nowi - pools[a].get("seen", nowi)) / 3600

        fresh = [a for a in pools if FRESH_MIN_H <= age_h(a) <= FRESH_MAX_H and nowi - lf.get(a, 0) > 6 * 3600]
        fresh.sort(key=age_h)                                          # i piu' giovani per primi
        stale = [a for a in pools if a in lf and nowi - lf[a] > 20 * 3600
                 and nowi - pools[a].get("seen", nowi) < 8 * 86400]    # giovane <8gg: la storia 168h non e' ancora piena
        never = [a for a in pools if a not in lf and age_h(a) > FRESH_MAX_H]
        never.sort(key=age_h)                                          # backlog: dal piu' recente al piu' vecchio
        nfresh = int(CANDLE_BATCH * FRESH_QUOTA)
        todo = fresh[:nfresh]
        todo += [a for a in (stale + never) if a not in set(todo)][:CANDLE_BATCH - len(todo)]
        for i, addr in enumerate(todo):
            if time.time() - now0 > MAX_SECONDS: break
            if i and i % 20 == 0: json.dump(ck, open(ckf, "w"))        # ckpt incrementale: se ci killano non perdiamo il lavoro
            lim = 36 if age_h(addr) <= FRESH_MAX_H else 168   # un token giovane NON ha 168 ore di storia: non chiederle
            d = get(f"{GT}/networks/{chain}/pools/{addr}/ohlcv/hour?aggregate=1&limit={lim}")
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
        print(f"  {chain}: {len(pools)} pool | +{total_cand} candele "
              f"(freschi {len(fresh)}, stantii {len(stale)}, backlog {len(never)})", flush=True)

    print(f"MULTICHAIN | +{total_new} pool nuovi | +{total_cand} candele scaricate", flush=True)


if __name__ == "__main__":
    main()
