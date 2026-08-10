#!/usr/bin/env python3
"""
WHALE_BACKFILL — cattura le whale STORICHE dagli eventi Swap on-chain via RPC pubblico Robinhood.
Sblocca il pezzo debole: da ~9 whale a MIGLIAIA. Fonte: rpc.mainnet.chain.robinhood.com (gratis, tollerante).
Per ogni pool: metadati da GeckoTerminal (base/quote, decimals, prezzo quote), rileva V2/V3, scarica gli Swap
a finestre di ~2000 blocchi (limite del RPC), decodifica amount0/amount1, calcola l'USD dal lato quote
(WETH/stable), tiene i BUY >= $10k con WALLET (recipient). Timestamp via modello lineare blocco->tempo.
File IMMUTABILI per run (no corruzione), dedup per tx+logIndex, resumable per-pool via checkpoint. NO live.

Uso:
  python3 agents/whale_backfill.py --test        # 3 pool, poche finestre, stampa esempi
  BATCH=8 python3 agents/whale_backfill.py        # batch resumable (adatto a GitHub Actions)
"""
import urllib.request, json, time, os, gzip, glob, sys, calendar

GT = "https://api.geckoterminal.com/api/v2"
RPC = "https://rpc.mainnet.chain.robinhood.com"
PAUSE = 2.6            # GeckoTerminal gentile
RPC_PAUSE = 0.45      # ~2 req/s sul RPC (testato tollerante)
WHALE = int(os.environ.get("WHALE", 3000))   # soglia cattura: $3k (accumula anche le whale memecoin piu' piccole; si filtra dopo in analisi)
MONEY = {"weth", "eth", "usdg", "usdc", "usdt", "dai", "usdb", "weth9"}  # token "denaro": una coppia con ENTRAMBI = arbitraggio, non memecoin
WIN0 = 40000          # finestra iniziale; si adatta: dimezza se il RPC va in errore (troppi log), cresce se scarsa
WIN_MIN = 1000
WIN_MAX = 120000
MAX_BLOCKS = 300000 if "--test" in sys.argv else int(os.environ.get("MAX_BLOCKS", 5000000))  # budget blocchi/pool/run
SWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
TEST = "--test" in sys.argv
BATCH = 3 if TEST else int(os.environ.get("BATCH", 12))
MAX_CALLS = 40 if TEST else int(os.environ.get("MAX_CALLS", 350))   # budget getLogs per run: bound wall-clock (run GHA ~3-5min)
CK = "data/whale_backfill_checkpoint.json"
POOLS = "data/pools.json"


def gt(url, tries=5, pause=3.0):
    last = None
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}), timeout=30))
        except Exception as e:
            last = e; time.sleep(pause * (a + 1))
    return None


def rpc(method, params, tries=4):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    last = None
    for a in range(tries):
        try:
            r = json.load(urllib.request.urlopen(
                urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, method="POST"), timeout=30))
            if "result" in r:
                return r["result"]
            last = r.get("error"); time.sleep(0.8 * (a + 1))       # errori interni: piccola pausa
        except urllib.error.HTTPError as e:
            last = e; time.sleep((6.0 if e.code == 429 else 1.0) * (a + 1))
        except Exception as e:
            last = e; time.sleep(1.0 * (a + 1))
    return None


def to_int(word):
    v = int(word, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def block_time_model():
    """Ritorna (b0, t0, sec_per_block) campionando 2 blocchi lontani. Per stimare il ts di ogni blocco."""
    latest_hex = rpc("eth_blockNumber", [])
    if not latest_hex:
        return None
    latest = int(latest_hex, 16)
    b_lo = max(1, latest - 500000)
    def bt(bn):
        blk = rpc("eth_getBlockByNumber", [hex(bn), False])
        return int(blk["timestamp"], 16) if blk and blk.get("timestamp") else None
    t_hi = bt(latest); time.sleep(RPC_PAUSE); t_lo = bt(b_lo); time.sleep(RPC_PAUSE)
    if t_hi is None or t_lo is None or latest == b_lo:
        return None
    spb = (t_hi - t_lo) / (latest - b_lo)
    return {"latest": latest, "b0": b_lo, "t0": t_lo, "spb": spb}


def pool_meta(addr):
    d = gt(f"{GT}/networks/robinhood/pools/{addr}?include=base_token,quote_token")
    if not d or "data" not in d:
        return None
    a = d["data"]["attributes"]; rel = d["data"]["relationships"]
    base_id = rel["base_token"]["data"]["id"]; quote_id = rel["quote_token"]["data"]["id"]
    dec = {inc["id"]: int(inc["attributes"].get("decimals") or 18) for inc in d.get("included", [])}
    base_addr = base_id.split("_")[-1].lower(); quote_addr = quote_id.split("_")[-1].lower()
    quote_price = float(a.get("quote_token_price_usd") or 0)
    t0, _ = sorted([base_addr, quote_addr])
    return {"name": a.get("name"), "quote_dec": dec.get(quote_id, 18), "quote_price": quote_price,
            "quote_is_t0": (quote_addr == t0), "created": a.get("pool_created_at")}


def detect_version(addr, latest):
    """Rileva V2/V3 su finestre RECENTI (attivita' garantita), piccole-prima per evitare il cap di risultati."""
    for span in (2000, 20000, 120000):
        lo = max(1, latest - span)
        for tag, topic in (("v3", SWAP_V3), ("v2", SWAP_V2)):
            res = rpc("eth_getLogs", [{"address": addr, "fromBlock": hex(lo), "toBlock": hex(latest), "topics": [topic]}])
            time.sleep(RPC_PAUSE)
            if isinstance(res, list) and len(res) > 0:
                return tag, topic
    return None, None


def decode(log, tag, meta):
    """Ritorna (usd, is_buy, wallet) o None. USD dal lato quote."""
    data = log.get("data", "")[2:]
    if tag == "v3":
        if len(data) < 128: return None
        a0 = to_int(data[0:64]); a1 = to_int(data[64:128])
        q = a0 if meta["quote_is_t0"] else a1
        if q == 0: return None
        usd = abs(q) / (10 ** meta["quote_dec"]) * meta["quote_price"]
        is_buy = q > 0                      # quote entra nel pool = compra il memecoin
    else:  # v2: amount0In, amount1In, amount0Out, amount1Out
        if len(data) < 256: return None
        a0i = int(data[0:64], 16); a1i = int(data[64:128], 16); a0o = int(data[128:192], 16); a1o = int(data[192:256], 16)
        q_in = a0i if meta["quote_is_t0"] else a1i
        q_out = a0o if meta["quote_is_t0"] else a1o
        q = q_in if q_in > 0 else q_out
        if q == 0: return None
        usd = q / (10 ** meta["quote_dec"]) * meta["quote_price"]
        is_buy = q_in > 0
    topics = log.get("topics", [])
    router = ("0x" + topics[-1][-40:]) if len(topics) >= 2 else None    # recipient = spesso il ROUTER, non la whale
    return usd, is_buy, router


def main():
    os.makedirs("data/raw/whales", exist_ok=True)
    reg = json.load(open(POOLS)) if os.path.exists(POOLS) else {"pools": {}}
    ck = json.load(open(CK)) if os.path.exists(CK) else {}
    now = int(time.time())
    m = block_time_model()
    if not m:
        print("❌ RPC non risponde (block model)"); sys.exit(1)
    latest = m["latest"]
    print(f"ultimo blocco: {latest} | ~{m['spb']:.2f} sec/blocco", flush=True)

    seen = set()
    for f in glob.glob("data/raw/whales/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                try:
                    d = json.loads(l)
                    if d.get("tx"): seen.add(f"{d['tx']}_{d.get('li','')}")
                except: pass
        except EOFError: pass

    pools = [kv for kv in reg["pools"].items() if len(kv[0]) == 42]
    pools.sort(key=lambda kv: kv[1].get("vol", 0), reverse=True)
    # cattura CONTINUA: prendi i pool non ancora completati OPPURE completati ma "stantii" (>REFRESH):
    # un pool 'done' viene riaperto dall'ultimo blocco al nuovo latest per catturare i BUY NUOVI.
    REFRESH = int(os.environ.get("REFRESH_SEC", 4 * 3600))
    cand_pools = [p for p in pools if (not ck.get(p[0], {}).get("done")) or (now - ck.get(p[0], {}).get("ts", 0) > REFRESH)]
    todo = sorted(cand_pools, key=lambda kv: ck.get(kv[0], {}).get("ts", 0))[:BATCH]

    out = f"data/raw/whales/backfill_{now}.jsonl.gz"
    fw = gzip.open(out, "wt"); total = 0
    def blk_ts(bn): return int(m["t0"] + (bn - m["b0"]) * m["spb"])
    txfrom = {}
    def real_wallet(tx):
        """EOA vero = tx.from (il recipient nei log e' spesso il router). Cache per tx."""
        if tx in txfrom: return txfrom[tx]
        d = rpc("eth_getTransactionByHash", [tx]); time.sleep(RPC_PAUSE)
        w = d.get("from") if isinstance(d, dict) else None
        txfrom[tx] = w; return w

    calls = 0
    for addr, info in todo:
        if calls >= MAX_CALLS:
            print(f"  (budget {MAX_CALLS} chiamate esaurito, i restanti pool al prossimo run)", flush=True); break
        st = ck.get(addr, {})
        meta = pool_meta(addr); time.sleep(PAUSE)
        if not meta:
            print(f"  retry-later {addr[:10]} (meta ko, transitorio)", flush=True); continue   # non marcare done: riprova prossimo run
        if meta["quote_price"] <= 0:
            print(f"  skip {addr[:10]} (quote senza prezzo USD)", flush=True); ck[addr] = {"done": True, "ts": now}; continue
        # salta le coppie di puro arbitraggio (es. USDG/WETH): entrambi i lati sono token "denaro", non memecoin
        parts = [p.strip().split(" ")[0].lower() for p in (meta["name"] or "").split("/")]
        if len(parts) == 2 and parts[0] in MONEY and parts[1] in MONEY:
            print(f"  skip {meta['name'][:20]} (coppia arbitraggio, non memecoin)", flush=True); ck[addr] = {"done": True, "ts": now}; continue
        # blocco di partenza: dove eravamo rimasti, oppure la creazione del pool
        if st.get("blk"):
            start = st["blk"]
        else:
            try:
                ep = calendar.timegm(time.strptime(meta["created"].split(".")[0].replace("Z", ""), "%Y-%m-%dT%H:%M:%S"))
                # BUG-FIX: NON clampare a b0 (recente) -> per i token vecchi si partiva dal presente perdendo tutto lo storico.
                # Ora si parte dal blocco di CREAZIONE vero (min 1), cosi' catturiamo le whale vecchie con 72h/168h gia' pronti.
                start = min(latest, max(1, int(m["b0"] + (ep - m["t0"]) / m["spb"])))
            except Exception:
                start = max(1, latest - 300000)
        tag = st.get("tag")
        if not tag:
            tag, topic = detect_version(addr, latest)
            if not tag:
                print(f"  {meta['name'][:16]:16} nessuno Swap log", flush=True); ck[addr] = {"done": True, "ts": now}; continue
        else:
            topic = SWAP_V3 if tag == "v3" else SWAP_V2
        b = start; new = 0; found = 0; win = WIN0; scanned = 0
        while b < latest and scanned < MAX_BLOCKS and calls < MAX_CALLS:
            to = min(b + win, latest)
            res = rpc("eth_getLogs", [{"address": addr, "fromBlock": hex(b), "toBlock": hex(to), "topics": [topic]}])
            time.sleep(RPC_PAUSE); calls += 1
            if not isinstance(res, list):                 # errore = troppi log: restringi e riprova la stessa zona
                if win > WIN_MIN:
                    win = max(WIN_MIN, win // 2); continue
                b = to + 1; scanned += (to - b); continue  # al minimo e ancora errore: salta
            for lg in res:
                d = decode(lg, tag, meta)
                if not d: continue
                usd, is_buy, router = d
                if is_buy and usd >= WHALE:
                    found += 1
                    tx = lg.get("transactionHash")
                    k = f"{tx}_{lg.get('logIndex')}"
                    if k in seen: continue
                    seen.add(k)
                    bn = int(lg.get("blockNumber", "0x0"), 16)
                    fw.write(json.dumps({"tx": tx, "li": lg.get("logIndex"),
                                         "ts": blk_ts(bn), "blk": bn, "pool": addr, "name": meta["name"],
                                         "wallet": real_wallet(tx), "router": router, "usd": round(usd)}) + "\n")
                    new += 1; total += 1
            scanned += (to - b); b = to + 1
            if len(res) < 400 and win < WIN_MAX:          # zona rada: allarga per andare piu' veloce
                win = min(WIN_MAX, int(win * 1.8))
            elif len(res) >= 900 and win > WIN_MIN:       # zona densa: restringi per non sforare
                win = max(WIN_MIN, win // 2)
        done = b >= latest
        ck[addr] = {"blk": b, "tag": tag, "done": done, "ts": now}
        print(f"  {meta['name'][:16]:16} [{tag}] +{new} whale (viste {found}) blk->{b}{' ✓done' if done else ' …resume'}", flush=True)
        if TEST and new:
            for line in [json.loads(x) for x in gzip.open(out, "rt")][-3:]:
                print(f"     es: ${line['usd']:,} wallet {line['wallet']} tx {line['tx'][:18]} ts {line['ts']}", flush=True)
    fw.close()
    if total == 0:
        os.remove(out)
    json.dump(ck, open(CK, "w"))
    ndone = sum(1 for v in ck.values() if v.get("done"))
    print(f"\n✅ backfill batch {len(todo)} pool | +{total} whale nuove | pool completati {ndone}/{len(pools)} | archivio: {len(seen):,} chiavi", flush=True)


if __name__ == "__main__":
    main()
