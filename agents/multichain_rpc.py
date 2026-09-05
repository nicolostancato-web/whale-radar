#!/usr/bin/env python3
"""
MULTICHAIN_RPC — cattura i trade dal GIORNO-0 (punto-zero) leggendo gli Swap ON-CHAIN via RPC, per le chain EVM
(BSC, Base). Risolve il buco che GeckoTerminal non copre: i primi trade dei token scrollano via oltre i 300, ma
on-chain non spariscono mai. Per ogni pool: stima il blocco del listing (dalla prima candela), legge gli Swap
nella finestra iniziale (listing -> +6h) via eth_getLogs, decodifica buy/sell + importo quote + wallet (recipient),
e li salva in data/multichain/<chain>/trades/<addr>.jsonl.gz (stesso formato di GeckoTerminal → il brain li usa).
Solana e' non-EVM → esclusa (serve altro). Resumable per-pool, budget chiamate, matrix per chain (env CHAIN). €0.
"""
import urllib.request, urllib.error, json, time, os, gzip, glob, sys

RPCS = {"base": "https://mainnet.base.org", "bsc": "https://bsc.rpc.blxrbdn.com"}
GT = "https://api.geckoterminal.com/api/v2"
SWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
SWAP_AERO = "0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b"  # Aerodrome/Velodrome (DEX dominante Base), layout dati = V2
RPC_PAUSE = 0.25
POOL_BATCH = 25            # pool per run
MAX_CALLS = 300           # budget getLogs per run
WIN_BLOCKS = 3000         # blocchi per finestra getLogs (per-pool = piccola, no "too large")
EARLY_HOURS = 6           # cattura i trade nelle prime 6h dal listing (copre l'entrata +1/3h)
now0 = time.time()


def rpc(url, method, params, tries=4):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    for a in range(tries):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(
                url, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, method="POST"), timeout=30))
            if "result" in r: return r["result"]
            time.sleep(0.6 * (a + 1))
        except urllib.error.HTTPError as e:
            time.sleep((5.0 if e.code == 429 else 1.0) * (a + 1))
        except Exception:
            time.sleep(1.0 * (a + 1))
    return None


def block_at_ts(url, target_ts, latest, cache):
    """Ricerca BINARIA del blocco al timestamp del listing. Parte da un range RECENTE (stima via spb locale) per non
    interrogare blocchi troppo vecchi che gli RPC non-full-archive non hanno. Salta i blocchi mancanti (no abort)."""
    key = target_ts // 600
    if key in cache: return cache[key]
    def bts(bn):
        blk = rpc(url, "eth_getBlockByNumber", [hex(bn), False]); time.sleep(0.03)
        return int(blk["timestamp"], 16) if blk and blk.get("timestamp") else None
    t_hi = bts(latest); t_lo = bts(max(1, latest - 200000))
    if t_hi and t_lo and t_hi > t_lo:
        spb = (t_hi - t_lo) / 200000
        lo = max(1, latest - int((t_hi - target_ts) / spb * 1.5))   # parti vicino al listing (non dal blocco 1)
    else:
        lo = max(1, latest - 9000000)
    hi = latest
    for _ in range(42):
        if lo >= hi: break
        mid = (lo + hi) // 2
        blk = rpc(url, "eth_getBlockByNumber", [hex(mid), False]); time.sleep(0.03)
        if not blk or not blk.get("timestamp"): lo = mid + 1; continue   # blocco mancante: salta avanti, non abortire
        if int(blk["timestamp"], 16) < target_ts: lo = mid + 1
        else: hi = mid
    fin = rpc(url, "eth_getBlockByNumber", [hex(lo), False])                  # validazione: blocco davvero al listing?
    if not fin or not fin.get("timestamp") or abs(int(fin["timestamp"], 16) - target_ts) > 3600:
        cache[key] = 0; return 0                                              # RPC non ha la storia: fallisci pulito
    cache[key] = lo
    return lo


def gt(url, tries=4):
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}), timeout=30))
        except Exception: time.sleep(2.5 * (a + 1))
    return None


def to_int(w):
    v = int(w, 16); return v - (1 << 256) if v >= (1 << 255) else v


def block_model(url):
    lh = rpc(url, "eth_blockNumber", [])
    if not lh: return None
    latest = int(lh, 16); b_lo = max(1, latest - 500000)
    def bt(bn):
        blk = rpc(url, "eth_getBlockByNumber", [hex(bn), False])
        return int(blk["timestamp"], 16) if blk and blk.get("timestamp") else None
    t_hi = bt(latest); time.sleep(RPC_PAUSE); t_lo = bt(b_lo); time.sleep(RPC_PAUSE)
    if t_hi is None or t_lo is None or latest == b_lo: return None
    return {"latest": latest, "b0": b_lo, "t0": t_lo, "spb": (t_hi - t_lo) / (latest - b_lo)}


def pool_meta(chain, addr):
    d = gt(f"{GT}/networks/{chain}/pools/{addr}?include=base_token,quote_token")
    if not d or "data" not in d: return None
    a = d["data"]["attributes"]; rel = d["data"]["relationships"]
    base_id = rel["base_token"]["data"]["id"]; quote_id = rel["quote_token"]["data"]["id"]
    dec = {inc["id"]: int(inc["attributes"].get("decimals") or 18) for inc in d.get("included", [])}
    base_addr = base_id.split("_")[-1].lower(); quote_addr = quote_id.split("_")[-1].lower()
    t0, _ = sorted([base_addr, quote_addr])
    return {"quote_dec": dec.get(quote_id, 18), "quote_price": float(a.get("quote_token_price_usd") or 0),
            "quote_is_t0": (quote_addr == t0)}


def decode(log, tag, meta):
    data = log.get("data", "")[2:]
    if tag == "v3":
        if len(data) < 128: return None
        a0 = to_int(data[0:64]); a1 = to_int(data[64:128]); q = a0 if meta["quote_is_t0"] else a1
        if q == 0: return None
        usd = abs(q) / (10 ** meta["quote_dec"]) * meta["quote_price"]; is_buy = q > 0
    else:
        if len(data) < 256: return None
        a0i = int(data[0:64], 16); a1i = int(data[64:128], 16); a0o = int(data[128:192], 16); a1o = int(data[192:256], 16)
        q_in = a0i if meta["quote_is_t0"] else a1i; q_out = a0o if meta["quote_is_t0"] else a1o
        q = q_in if q_in > 0 else q_out
        if q == 0: return None
        usd = q / (10 ** meta["quote_dec"]) * meta["quote_price"]; is_buy = q_in > 0
    topics = log.get("topics", [])
    w = ("0x" + topics[-1][-40:]) if len(topics) >= 2 else None   # recipient (proxy wallet)
    return usd, is_buy, w


def main():
    chain = os.environ.get("CHAIN", "base").strip().lower()
    SHARD = int(os.environ.get("SHARD", "-1")); NSHARDS = int(os.environ.get("NSHARDS", "1"))
    if chain not in RPCS:
        print(f"MULTICHAIN_RPC | {chain} non EVM/non gestita"); return
    url = RPCS[chain]; base = f"data/multichain/{chain}"
    if not os.path.exists(f"{base}/pools.json"):
        print(f"MULTICHAIN_RPC | {chain}: nessun pool"); return
    pools = json.load(open(f"{base}/pools.json"))
    os.makedirs(f"{base}/trades", exist_ok=True)
    ckf = f"{base}/rpc_ckpt_{SHARD}.json" if SHARD >= 0 else f"{base}/rpc_ckpt.json"
    ck = json.load(open(ckf)) if os.path.exists(ckf) else {}
    attempts = ck.setdefault("attempts", {})   # pool -> tentativi senza giorno-0 (cap 3)
    # prima candela per pool (= listing) → ci serve per la finestra iniziale
    firstts = {}
    for cf in glob.glob(f"{base}/candles/*.jsonl.gz"):
        addr = cf.split("/")[-1].replace(".jsonl.gz", "")
        try:
            ts = [int(json.loads(l)["ts"]) for l in gzip.open(cf, "rt") if json.loads(l).get("cl")]
            if ts: firstts[addr] = min(ts)
        except: pass
    m = block_model(url)
    if not m: print(f"MULTICHAIN_RPC | {chain}: RPC non risponde"); return
    bcache = {}

    def has_preentry(addr):
        tf = f"{base}/trades/{addr}.jsonl.gz"
        if not os.path.exists(tf): return False
        thr = firstts[addr] + 3600
        try:
            for l in gzip.open(tf, "rt"):
                if json.loads(l).get("ts", 1 << 62) <= thr: return True
        except: pass
        return False
    cand = [a for a in pools if a in firstts and (SHARD < 0 or sum(ord(c) for c in a) % NSHARDS == SHARD)]
    cand = [a for a in cand if attempts.get(a, 0) < 3 and not has_preentry(a)]   # solo i mancanti, cap 3 tentativi
    cand.sort(key=lambda a: -firstts.get(a, 0))    # PRIORITA ai pool giovani (nuovi memecoin = piu' vivi/catturabili)
    todo = cand[:POOL_BATCH]
    calls = 0; saved = 0
    for addr in todo:
        if calls >= MAX_CALLS or time.time() - now0 > 500: break
        meta = pool_meta(chain, addr); time.sleep(2.5)
        if meta is None: continue                              # GeckoTerminal down: NON bruciare il pool, ritenta al prossimo run
        if meta["quote_price"] <= 0: attempts[addr] = 99; continue  # pool legit senza prezzo quote: skip definitivo
        lt = firstts[addr]
        bs0 = block_at_ts(url, lt, m["latest"], bcache)
        if bs0 <= 1: attempts[addr] = 99; continue                            # RPC senza la storia di questo pool: skip definitivo
        b_start = bs0 - 50
        b_end = int(b_start + (EARLY_HOURS * 3600) / m["spb"])            # +6h
        trades = []; found = None
        b = max(1, b_start)
        while b < b_end and calls < MAX_CALLS:
            to = min(b + WIN_BLOCKS, b_end)
            for tg, topic in (([found] if found else [("v3", SWAP_V3), ("v2", SWAP_V2), ("v2", SWAP_AERO)])):
                res = rpc(url, "eth_getLogs", [{"address": addr, "fromBlock": hex(b), "toBlock": hex(to), "topics": [topic]}])
                calls += 1; time.sleep(RPC_PAUSE)
                if isinstance(res, list) and res:
                    found = (tg, topic)
                    for lg in res:
                        d = decode(lg, tg, meta)
                        if not d: continue
                        usd, is_buy, w = d
                        bn = int(lg.get("blockNumber", "0x0"), 16)
                        ts = int(m["t0"] + (bn - m["b0"]) * m["spb"])
                        trades.append({"tx": lg.get("transactionHash"), "ts": ts,
                                       "kind": "buy" if is_buy else "sell", "usd": round(usd, 2), "w": w})
                    break
            b = to + 1
        if trades:
            # merge con eventuali trade GeckoTerminal gia' presenti (dedup per tx)
            tf = f"{base}/trades/{addr}.jsonl.gz"; seen = set(); rows = []
            if os.path.exists(tf):
                try:
                    for l in gzip.open(tf, "rt"):
                        r = json.loads(l); seen.add(r.get("tx")); rows.append(r)
                except: pass
            for t in trades:
                if t["tx"] not in seen: seen.add(t["tx"]); rows.append(t)
            rows.sort(key=lambda r: r.get("ts", 0))
            with gzip.open(tf, "wt") as fo:
                for r in rows: fo.write(json.dumps(r) + "\n")
            saved += 1
        if not has_preentry(addr): attempts[addr] = attempts.get(addr, 0) + 1   # non ha (ancora) il giorno-0: conta il tentativo
    ck["attempts"] = attempts; json.dump(ck, open(ckf, "w"))
    print(f"MULTICHAIN_RPC | {chain}: {len(todo)} pool, {saved} con trade giorno-0, {calls} chiamate RPC", flush=True)


if __name__ == "__main__":
    main()
