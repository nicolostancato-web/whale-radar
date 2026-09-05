#!/usr/bin/env python3
"""
SOLANA_HELIUS — cattura i PRIMI trade Solana dal GIORNO-0, a costo COSTANTE per qualsiasi token (gigante o no).
Metodo (v2): invece di paginare la storia dall'oggi all'indietro (impossibile sui token con milioni di trade),
SALTIAMO diretti al listing: 1) ricerca BINARIA sugli slot per lo slot del listing (dalla prima candela),
2) getBlock -> una signature "marcatore" al listing, 3) getSignaturesForAddress(before=marker) -> le firme dei
PRIMI trade, 4) parse batch (Helius Enhanced /v0/transactions, 100/chiamata) -> buy/sell + wallet + importo SOL.
~25 chiamate/pool indipendenti da eta'/volume. 8 shard su 2 key (HELIUS_KEY + HELIUS_KEY2). Auto-guidato sulla
coverage (has_preentry), cap 3 tentativi. Salva in data/multichain/solana/trades/<pool>.jsonl.gz. Resumable. €0.
KEY: os.environ['HELIUS_KEY'] / ['HELIUS_KEY2'] (mai hardcodate, mai committate).
"""
import urllib.request, urllib.error, json, gzip, os, time, glob

GT = "https://api.geckoterminal.com/api/v2"
SOL_USD = 180.0            # prezzo SOL approssimato (le feature usano rapporti: il valore esatto non conta)
POOL_BATCH = 20            # pool per run
PARSE_LIMIT = 150          # quanti dei primi trade parsare (first-buyers/insider: bastano i primi ~150)
EARLY_MIN = 15             # marcatore a listing + 15min (finestra da cui prendere i primi trade)
SLOT_SEC = 0.4             # ~durata slot Solana (per stimare i range della ricerca binaria)
MAX_SECONDS = 520
now0 = time.time()


def http(url, tries=3):
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}), timeout=25))
        except urllib.error.HTTPError as e:
            time.sleep((3 if e.code == 429 else 1.5) * (a + 1))
        except Exception: time.sleep(1.5)
    return None


def rpc(rpc_url, method, params, tries=4):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for a in range(tries):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(
                rpc_url, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
                method="POST"), timeout=30))
            if "result" in r: return r["result"]
            time.sleep(0.6 * (a + 1))
        except urllib.error.HTTPError as e:
            time.sleep((4 if e.code == 429 else 1.0) * (a + 1))
        except Exception: time.sleep(1.0 * (a + 1))
    return None


def get_mint(pool):
    d = http(f"{GT}/networks/solana/pools/{pool}?include=base_token")
    try: return d["data"]["relationships"]["base_token"]["data"]["id"].split("_")[-1]
    except: return None


def slot_at_time(rpc_url, target_ts, cur_slot, cache):
    """Ricerca BINARIA dello slot al timestamp del listing. Cache per timestamp (pool coevi condividono)."""
    key = target_ts // 600
    if key in cache: return cache[key]
    age_s = max(0, time.time() - target_ts)
    lo = max(1, cur_slot - int(age_s / SLOT_SEC) - 300000); hi = cur_slot
    c = 0
    while lo < hi and c < 30:
        mid = (lo + hi) // 2
        t = rpc(rpc_url, "getBlockTime", [mid]); c += 1; time.sleep(0.03)
        if t is None: lo = mid + 1; continue
        if t < target_ts: lo = mid + 1
        else: hi = mid
    cache[key] = lo
    return lo


def marker_near(rpc_url, slot):
    """Una signature 'marcatore' dal primo blocco con transazioni cercando INDIETRO da `slot` (cursore temporale).
    Cerca indietro per non finire su slot futuri (token appena nati) che non esistono ancora."""
    for off in range(0, 200):
        s = slot - off
        if s < 1: break
        blk = rpc(rpc_url, "getBlock", [s, {"transactionDetails": "signatures",
                  "rewards": False, "maxSupportedTransactionVersion": 0}]); time.sleep(0.03)
        if blk and blk.get("signatures"): return blk["signatures"][0]
    return None


def parse_swap(txn, mint):
    ts = txn.get("timestamp"); w = txn.get("feePayer"); sig = txn.get("signature")
    if not ts or not sig: return None
    sw = txn.get("events", {}).get("swap")
    if sw:
        ni = sw.get("nativeInput"); no = sw.get("nativeOutput")
        tout = [t for t in sw.get("tokenOutputs", []) if t.get("mint") == mint]
        tin = [t for t in sw.get("tokenInputs", []) if t.get("mint") == mint]
        if ni and tout:
            sol = int(ni.get("amount", 0)) / 1e9
            return {"tx": sig, "ts": ts, "kind": "buy", "usd": round(sol * SOL_USD, 2), "w": w}
        if no and tin:
            sol = int(no.get("amount", 0)) / 1e9
            return {"tx": sig, "ts": ts, "kind": "sell", "usd": round(sol * SOL_USD, 2), "w": w}
    for tt in txn.get("tokenTransfers", []):
        if tt.get("mint") == mint:
            if tt.get("toUserAccount") == w: kind = "buy"
            elif tt.get("fromUserAccount") == w: kind = "sell"
            else: continue
            sol = sum(abs(n.get("amount", 0)) for n in txn.get("nativeTransfers", [])) / 1e9
            return {"tx": sig, "ts": ts, "kind": kind, "usd": round(sol * SOL_USD, 2), "w": w}
    return None


def parse_batch(key, sigs):
    """Helius Enhanced Transactions: parsa fino a 100 firme in 1 chiamata."""
    url = f"https://api.helius.xyz/v0/transactions?api-key={key}"
    body = json.dumps({"transactions": sigs}).encode()
    for a in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(
                url, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
                method="POST"), timeout=45)
            return json.load(r)
        except urllib.error.HTTPError as e:
            time.sleep((3 if e.code == 429 else 1.5) * (a + 1))
        except Exception: time.sleep(1.5)
    return []


def fetch_first_trades(key, mint, listing_ts, cur_slot, slotcache):
    """Salta al listing e prende i PRIMI trade del token (costo costante, gigante o no)."""
    rpc_url = f"https://mainnet.helius-rpc.com/?api-key={key}"
    slot0 = slot_at_time(rpc_url, listing_ts, cur_slot, slotcache)
    if not slot0: return []
    target = min(slot0 + int(EARLY_MIN * 60 / SLOT_SEC), cur_slot - 2)       # marcatore ~listing+15min, mai nel futuro
    marker = marker_near(rpc_url, target)
    if not marker: return []
    sigs = rpc(rpc_url, "getSignaturesForAddress", [mint, {"before": marker, "limit": 1000}])
    if not isinstance(sigs, list) or not sigs: return []
    win = [(s.get("blockTime"), s.get("signature")) for s in sigs
           if s.get("blockTime") and listing_ts <= s["blockTime"] <= listing_ts + 4 * 3600]
    win.sort()                                        # per blockTime crescente = dai PRIMI
    first = [sig for _, sig in win[:PARSE_LIMIT]]
    out = []
    for i in range(0, len(first), 100):
        if time.time() - now0 > MAX_SECONDS: break
        for txn in parse_batch(key, first[i:i + 100]):
            sp = parse_swap(txn, mint)
            if sp: out.append(sp)
    return out


def main():
    K1 = os.environ.get("HELIUS_KEY", "").strip()
    K2 = os.environ.get("HELIUS_KEY2", "").strip() or K1
    if not K1:
        print("SOLANA_HELIUS | manca HELIUS_KEY"); return
    base = "data/multichain/solana"
    if not os.path.exists(f"{base}/pools.json"):
        print("SOLANA_HELIUS | nessun pool solana"); return
    pools = json.load(open(f"{base}/pools.json"))
    os.makedirs(f"{base}/trades", exist_ok=True)
    SHARD = int(os.environ.get("SHARD", "-1")); NSHARDS = int(os.environ.get("NSHARDS", "8"))
    key = K1 if (SHARD < 0 or SHARD < NSHARDS // 2) else K2     # meta' shard su key1, meta' su key2
    ckf = f"{base}/helius_ckpt_{SHARD}.json" if SHARD >= 0 else f"{base}/helius_ckpt.json"
    ck = json.load(open(ckf)) if os.path.exists(ckf) else {}
    mintcache = ck.setdefault("mint", {}); attempts = ck.setdefault("attempts", {})

    firstts = {}
    for cf in glob.glob(f"{base}/candles/*.jsonl.gz"):
        addr = cf.split("/")[-1].replace(".jsonl.gz", "")
        try:
            ts = [int(json.loads(l)["ts"]) for l in gzip.open(cf, "rt") if json.loads(l).get("cl")]
            if ts: firstts[addr] = min(ts)
        except: pass

    def has_preentry(pool):
        tf = f"{base}/trades/{pool}.jsonl.gz"
        if not os.path.exists(tf): return False
        thr = firstts[pool] + 3600
        try:
            for l in gzip.open(tf, "rt"):
                if json.loads(l).get("ts", 1 << 62) <= thr: return True
        except: pass
        return False

    cand = [a for a in pools if a in firstts and (SHARD < 0 or sum(ord(c) for c in a) % NSHARDS == SHARD)]
    cand = [a for a in cand if attempts.get(a, 0) < 3 and not has_preentry(a)]
    cand.sort(key=lambda a: -pools[a].get("seen", 0))
    todo = cand[:POOL_BATCH]

    cur_slot = rpc(f"https://mainnet.helius-rpc.com/?api-key={key}", "getSlot", [])
    if not cur_slot:
        print("SOLANA_HELIUS | getSlot fallito (RPC/key?)"); return
    slotcache = {}
    saved = 0
    for pool in todo:
        if time.time() - now0 > MAX_SECONDS: break
        mint = mintcache.get(pool) or get_mint(pool)
        if not mint: attempts[pool] = 99; continue
        mintcache[pool] = mint; time.sleep(0.3)
        sw = fetch_first_trades(key, mint, firstts[pool], cur_slot, slotcache)
        if not sw: attempts[pool] = attempts.get(pool, 0) + 1; continue
        tf = f"{base}/trades/{pool}.jsonl.gz"; seen = set(); rows = []
        if os.path.exists(tf):
            try:
                for l in gzip.open(tf, "rt"):
                    r = json.loads(l); seen.add(r.get("tx")); rows.append(r)
            except: pass
        for t in sw:
            if t["tx"] not in seen: seen.add(t["tx"]); rows.append(t)
        rows = [r for r in rows if r.get("ts", 0) <= firstts[pool] + 4 * 3600]
        rows.sort(key=lambda r: r.get("ts", 0))
        with gzip.open(tf, "wt") as fo:
            for r in rows: fo.write(json.dumps(r) + "\n")
        if not has_preentry(pool): attempts[pool] = attempts.get(pool, 0) + 1
        saved += 1
    ck["mint"] = mintcache; ck["attempts"] = attempts; json.dump(ck, open(ckf, "w"))
    print(f"SOLANA_HELIUS | shard{SHARD}: {len(todo)} pool, {saved} col giorno-0 (salto diretto al listing)", flush=True)


if __name__ == "__main__":
    main()
