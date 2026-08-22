#!/usr/bin/env python3
"""
MULTICHAIN_TRADES — raccoglie i TRADE (buy/sell) per pool su tutte le chain via GeckoTerminal /trades.
Da qui derivano le feature FORTI che su Robinhood danno l'edge: flow (pressione buy/sell) + first-buyers
(chi entra presto = smart-money). L'endpoint /trades da' kind/volume_in_usd/timestamp/wallet per OGNI chain.
Cattura i pool GIOVANI ripetutamente (i trade recenti scorrono via a ~300): finche' il pool e' giovane
raccogliamo i suoi primi trade. Salva raw dedup per tx in data/multichain/<chain>/trades/<addr>.jsonl.gz. €0.
"""
import urllib.request, urllib.error, json, gzip, os, time, calendar

CHAINS = ["solana", "bsc", "base", "robinhood"]
GT = "https://api.geckoterminal.com/api/v2"
MAX_SECONDS = 560
TRADE_BATCH = 90           # pool per run per cui scaricare i trade
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


def to_epoch(s):
    try: return calendar.timegm(time.strptime(s.replace("Z", "GMT"), "%Y-%m-%dT%H:%M:%S%Z"))
    except: return 0


def main():
    os.makedirs("data/multichain", exist_ok=True)
    envc = os.environ.get("CHAIN", "").strip().lower()
    if envc in CHAINS: chain = envc
    else:
        rf = "data/multichain/trot.json"
        rot = json.load(open(rf)) if os.path.exists(rf) else {"i": 0}
        chain = CHAINS[rot["i"] % len(CHAINS)]; rot["i"] = (rot["i"] + 1) % len(CHAINS); json.dump(rot, open(rf, "w"))

    base = f"data/multichain/{chain}"
    poolf = f"{base}/pools.json"
    if not os.path.exists(poolf): print(f"MULTICHAIN_TRADES | {chain}: nessun pool ancora"); return
    pools = json.load(open(poolf))
    os.makedirs(f"{base}/trades", exist_ok=True)
    ckf = f"{base}/trades_ckpt.json"
    ck = json.load(open(ckf)) if os.path.exists(ckf) else {"last": {}}
    ck.setdefault("last", {}); lf = ck["last"]; nowi = int(now0)

    # PRIORITA al PUNTO-ZERO: i pool giovanissimi vanno ri-scaricati SPESSO, prima che i primi trade scorrano
    # via (GeckoTerminal da' solo gli ultimi ~300 → su chain veloci come Solana i primi buy spariscono in minuti).
    never = [a for a in pools if a not in lf]
    young = [a for a in pools if a in lf and nowi - pools[a].get("seen", nowi) < 8 * 3600]   # <8h: ricattura ogni giro
    stale = [a for a in pools if a in lf and a not in young and nowi - lf[a] > 12 * 3600
             and nowi - pools[a].get("seen", nowi) < 6 * 86400]
    # ordine: mai-fatti + giovanissimi PRIMA (i piu' giovani in cima), poi gli stantii
    todo = (sorted(never + young, key=lambda a: -pools[a].get("seen", 0)) + stale)[:TRADE_BATCH]

    total = 0
    for addr in todo:
        if time.time() - now0 > MAX_SECONDS: break
        d = get(f"{GT}/networks/{chain}/pools/{addr}/trades")
        time.sleep(2.2); lf[addr] = nowi
        if not d or not d.get("data"): continue
        # carica esistenti (dedup per tx_hash)
        tf = f"{base}/trades/{addr}.jsonl.gz"
        seen = set(); rows = []
        if os.path.exists(tf):
            try:
                for l in gzip.open(tf, "rt"):
                    r = json.loads(l); seen.add(r.get("tx")); rows.append(r)
            except: pass
        added = 0
        for t in d["data"]:
            a = t["attributes"]; tx = a.get("tx_hash")
            if tx in seen: continue
            seen.add(tx)
            rows.append({"tx": tx, "ts": to_epoch(a.get("block_timestamp", "")), "kind": a.get("kind"),
                         "usd": float(a.get("volume_in_usd") or 0), "w": a.get("tx_from_address")})
            added += 1
        if added:
            rows.sort(key=lambda r: r.get("ts", 0))
            with gzip.open(tf, "wt") as fo:
                for r in rows: fo.write(json.dumps(r) + "\n")
            total += 1
    json.dump(ck, open(ckf, "w"))
    print(f"MULTICHAIN_TRADES | {chain}: {len(todo)} pool interrogati, {total} con trade nuovi "
          f"(mai {len(never)}, giovani {len(stale)})", flush=True)


if __name__ == "__main__":
    main()
