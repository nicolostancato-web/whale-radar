#!/usr/bin/env python3
"""
FIRST_BUYERS — cattura i PRIMI acquisti di ogni token DAL LISTING, SENZA soglia di size (qualsiasi importo).
Serve a vedere i PICCOLI INSIDER che la soglia $3k di whale_backfill taglia fuori (uno che SA entra con $500).
Per ogni pool: dal blocco di creazione, scansiona gli Swap e tiene i primi ~40 BUY (con wallet=tx.from, USD dal
lato quote, timing dal listing, posizione in sequenza). File immutabili, dedup, resumable, budget. RPC gratis. NO live.
"""
import urllib.request, json, time, os, gzip, glob, sys, calendar

GT = "https://api.geckoterminal.com/api/v2"
RPC = "https://rpc.mainnet.chain.robinhood.com"
PAUSE = 2.6; RPC_PAUSE = 0.45
FIRST_N = int(os.environ.get("FIRST_N", 40))      # primi N buy per token
WIN = 30000                                        # finestra blocchi (il listing e' denso -> piccola)
SWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
TEST = "--test" in sys.argv
BATCH = 3 if TEST else int(os.environ.get("FB_BATCH", 12))
MAX_SECONDS = int(os.environ.get("FB_SEC", 850))
MONEY = {"weth", "eth", "usdg", "usdc", "usdt", "dai", "usdb", "weth9"}
CK = "data/first_buyers_checkpoint.json"; POOLS = "data/pools.json"


def gt(url, tries=5, pause=3.0):
    last = None
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}), timeout=30))
        except Exception as e:
            last = e; time.sleep(pause * (a + 1))
    return None


def rpc(method, params, tries=4):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    for a in range(tries):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, method="POST"), timeout=30))
            if "result" in r: return r["result"]
            time.sleep(0.8 * (a + 1))
        except urllib.error.HTTPError as e:
            time.sleep((6.0 if e.code == 429 else 1.0) * (a + 1))
        except Exception:
            time.sleep(1.0 * (a + 1))
    return None


def to_int(w):
    v = int(w, 16); return v - (1 << 256) if v >= (1 << 255) else v


def block_model():
    lh = rpc("eth_blockNumber", [])
    if not lh: return None
    latest = int(lh, 16); b0 = max(1, latest - 500000)
    def bt(bn):
        blk = rpc("eth_getBlockByNumber", [hex(bn), False]); time.sleep(RPC_PAUSE)
        return int(blk["timestamp"], 16) if blk and blk.get("timestamp") else None
    t1 = bt(latest); t0 = bt(b0)
    if t1 is None or t0 is None or latest == b0: return None
    return {"latest": latest, "b0": b0, "t0": t0, "spb": (t1 - t0) / (latest - b0)}


def pool_meta(addr):
    d = gt(f"{GT}/networks/robinhood/pools/{addr}?include=base_token,quote_token", tries=2, pause=2.0)
    if not d or "data" not in d: return None
    a = d["data"]["attributes"]; rel = d["data"]["relationships"]
    base = rel["base_token"]["data"]["id"]; quote = rel["quote_token"]["data"]["id"]
    dec = {inc["id"]: int(inc["attributes"].get("decimals") or 18) for inc in d.get("included", [])}
    ba = base.split("_")[-1].lower(); qa = quote.split("_")[-1].lower()
    t0, _ = sorted([ba, qa])
    return {"name": a.get("name"), "quote_dec": dec.get(quote, 18), "quote_price": float(a.get("quote_token_price_usd") or 0),
            "quote_is_t0": (qa == t0), "created": a.get("pool_created_at"), "base": ba, "quote": qa}


def detect(addr, latest):
    for span in (2000, 20000, 120000):
        lo = max(1, latest - span)
        for tag, topic in (("v3", SWAP_V3), ("v2", SWAP_V2)):
            res = rpc("eth_getLogs", [{"address": addr, "fromBlock": hex(lo), "toBlock": hex(latest), "topics": [topic]}]); time.sleep(RPC_PAUSE)
            if isinstance(res, list) and len(res) > 0: return tag, topic
    return None, None


def decode(log, tag, meta):
    data = log.get("data", "")[2:]
    if tag == "v3":
        if len(data) < 128: return None
        a0 = to_int(data[0:64]); a1 = to_int(data[64:128]); q = a0 if meta["quote_is_t0"] else a1
        if q == 0: return None
        usd = abs(q) / 10 ** meta["quote_dec"] * meta["quote_price"]; is_buy = q > 0
    else:
        if len(data) < 256: return None
        a0i = int(data[0:64], 16); a1i = int(data[64:128], 16); a0o = int(data[128:192], 16); a1o = int(data[192:256], 16)
        qin = a0i if meta["quote_is_t0"] else a1i; qout = a0o if meta["quote_is_t0"] else a1o
        q = qin if qin > 0 else qout
        if q == 0: return None
        usd = q / 10 ** meta["quote_dec"] * meta["quote_price"]; is_buy = qin > 0
    return usd, is_buy


def main():
    os.makedirs("data/raw/firstbuyers", exist_ok=True)
    reg = json.load(open(POOLS)) if os.path.exists(POOLS) else {"pools": {}}
    ck = json.load(open(CK)) if os.path.exists(CK) else {}
    m = block_model()
    if not m: print("❌ RPC ko"); sys.exit(1)
    latest = m["latest"]
    def blk_ts(bn): return int(m["t0"] + (bn - m["b0"]) * m["spb"])

    pools = [(a, v.get("name")) for a, v in reg["pools"].items() if len(a) == 42]
    # solo memecoin (salta coppie money/money) e non ancora fatti, i piu' vecchi (arretrati) prima
    def is_meme(name):
        parts = [x.strip().split(" ")[0].lower() for x in (name or "").split("/")]
        return not (len(parts) == 2 and parts[0] in MONEY and parts[1] in MONEY)
    todo = [(a, n) for a, n in pools if is_meme(n) and not ck.get(a, {}).get("done")]
    todo = sorted(todo, key=lambda an: ck.get(an[0], {}).get("ts", 0))[:BATCH]

    txfrom = {}
    def wallet_of(tx):
        if tx in txfrom: return txfrom[tx]
        d = rpc("eth_getTransactionByHash", [tx]); time.sleep(RPC_PAUSE)
        w = d.get("from") if isinstance(d, dict) else None; txfrom[tx] = w; return w

    now = int(time.time()); out = f"data/raw/firstbuyers/fb_{now}.jsonl.gz"; fo = gzip.open(out, "wt"); total = 0
    START = time.time()
    for addr, name in todo:
        if time.time() - START > MAX_SECONDS: break
        meta = pool_meta(addr); time.sleep(PAUSE)
        if not meta or meta["quote_price"] <= 0: ck[addr] = {"done": True, "ts": now}; continue
        tag, topic = detect(addr, latest)
        if not tag: ck[addr] = {"done": True, "ts": now}; continue
        # blocco di creazione
        try:
            ep = calendar.timegm(time.strptime(meta["created"].split(".")[0].replace("Z", ""), "%Y-%m-%dT%H:%M:%S"))
            start = min(latest, max(1, int(m["b0"] + (ep - m["t0"]) / m["spb"])))
        except Exception:
            start = max(1, latest - 500000)
        b = start; buys = []; first_ts = None; scanned = 0
        while b < latest and len(buys) < FIRST_N and scanned < 3_000_000 and time.time() - START < MAX_SECONDS:
            to = min(b + WIN, latest)
            res = rpc("eth_getLogs", [{"address": addr, "fromBlock": hex(b), "toBlock": hex(to), "topics": [topic]}]); time.sleep(RPC_PAUSE)
            if not isinstance(res, list):
                b = to + 1; scanned += WIN; continue
            for lg in sorted(res, key=lambda l: (int(l.get("blockNumber", "0x0"), 16), int(l.get("logIndex", "0x0"), 16))):
                d = decode(lg, tag, meta)
                if not d: continue
                usd, is_buy = d
                bn = int(lg.get("blockNumber", "0x0"), 16)
                if first_ts is None: first_ts = blk_ts(bn)
                if not is_buy: continue
                tx = lg.get("transactionHash")
                buys.append({"pool": addr, "name": meta["name"], "wallet": wallet_of(tx), "usd": round(usd, 2),
                             "blk": bn, "ts": blk_ts(bn), "sec_da_listing": blk_ts(bn) - first_ts, "seq": len(buys) + 1,
                             "tx": tx, "li": lg.get("logIndex")})
                if len(buys) >= FIRST_N: break
            b = to + 1; scanned += WIN
        for r in buys:
            fo.write(json.dumps(r) + "\n"); total += 1
        ck[addr] = {"done": True, "ts": now, "n": len(buys)}
        print(f"  {meta['name'][:16]:16} [{tag}] primi {len(buys)} buy (size min ${min([r['usd'] for r in buys], default=0):.0f})", flush=True)
    fo.close()
    if total == 0: os.remove(out)
    json.dump(ck, open(CK, "w"))
    done = sum(1 for v in ck.values() if isinstance(v, dict) and v.get("done"))
    rem = sum(1 for a, n in pools if is_meme(n) and not ck.get(a, {}).get("done"))
    print(f"\n✅ first_buyers: +{total} early-buy | pool fatti {done} | REMAINING={rem}", flush=True)


if __name__ == "__main__":
    main()
