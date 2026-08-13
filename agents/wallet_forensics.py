#!/usr/bin/env python3
"""
WALLET_FORENSICS — testa l'ipotesi "i wallet piccoli profittevoli sono sub-wallet di balene/insider".
Per ogni wallet TARGET (piccoli $5-30k, VINCENTI e PERDENTI = gruppo di controllo) traccia il FUNDING:
prima entrata di ETH -> funder immediato (spesso un contratto bridge) -> risale al txHash e prende tx.from =
l'EOA ORIGINE (l'entita' vera che ha pagato). Poi confronta: i VINCENTI condividono origini comuni PIU' dei
PERDENTI? Se si -> sub-wallet coordinati (edge). Se uguale -> e' solo il bridge (nessun edge).
Paced (Blockscout 10/finestra), resumable (checkpoint), batch per run. Scrive FORENSICS.md. €0.
"""
import urllib.request, json, time, os, gzip, glob, statistics as st
from collections import defaultdict, Counter

BS = "https://robinhoodchain.blockscout.com/api"
RPC = "https://rpc.mainnet.chain.robinhood.com"
BS_PAUSE = 8.0          # Blockscout molto restrittivo: pacing largo
BATCH = int(os.environ.get("FORENSIC_BATCH", 8))
CK = "data/forensics_checkpoint.json"
now = int(time.time())


def bs(url, tries=3):
    for _ in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
        except Exception:
            time.sleep(12)
    return None


def rpc(method, params, tries=3):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    for _ in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}), timeout=30)).get("result")
        except Exception:
            time.sleep(2)
    return None


# ---------- 1) calcola wallet TARGET (piccoli vincenti + perdenti) dai nostri dati ----------
def target_wallets():
    cand = {}
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d["tf"] == "hour": cand.setdefault(d["pool"], {})[int(d["ts"])] = (d["cl"], d.get("v", 0))
        except: pass
    for p in cand: cand[p] = dict(sorted(cand[p].items()))
    last = {p: max(k) for p, k in cand.items() if k}
    w = []
    for f in glob.glob("data/raw/whales/backfill_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                x = json.loads(l)
                if x.get("usd") and x.get("ts") and x["pool"] in cand: w.append(x)
        except: pass

    def price(p, ts):
        ks = cand[p]; b = None
        for k in ks:
            if k <= ts + 1800: b = k
            else: break
        return ks[b] if b is not None and abs(b - ts) <= 6 * 3600 else None

    def slip(v): return 0.30 if v < 10000 else 0.10 if v < 100000 else 0.05

    def ret(x, H=72):
        e = price(x["pool"], x["ts"] + 3600)
        if not e or e[0] <= 0: return None
        tgt = x["ts"] + (1 + H) * 3600; ex = price(x["pool"], tgt)
        if ex is None:
            if tgt < now and last.get(x["pool"], 0) < tgt - 3600: exitp = cand[x["pool"]][last[x["pool"]]][0]
            else: return None
        else: exitp = ex[0]
        return (exitp * (1 - slip(e[1]))) / (e[0] * (1 + slip(e[1]))) - 1

    byw = defaultdict(list)
    for x in w:
        r = ret(x)
        if r is not None: byw[x["wallet"]].append((x["usd"], x["pool"], r))
    win, lose = [], []
    for wl, v in byw.items():
        if len(v) < 2: continue
        avg = st.mean([s for s, _, _ in v])
        if not (5000 <= avg <= 30000): continue
        bt = defaultdict(list)
        for s, p, r in v: bt[p].append(r)
        pt = st.mean([st.mean(x) for x in bt.values()])
        (win if pt > 0 else lose).append(wl)
    return win, lose


# ---------- 2) traccia il funding di un wallet fino all'EOA origine ----------
def trace(wl):
    r = bs(f"{BS}?module=account&action=txlistinternal&address={wl}&sort=asc&page=1&offset=20")
    time.sleep(BS_PAUSE)
    ins = []
    if isinstance(r, dict) and isinstance(r.get("result"), list):
        ins = [t for t in r["result"] if t.get("to", "").lower() == wl.lower() and int(t.get("value", 0)) > 0]
    if not ins:  # nessuna entrata interna -> prova le tx normali
        r = bs(f"{BS}?module=account&action=txlist&address={wl}&sort=asc&page=1&offset=20"); time.sleep(BS_PAUSE)
        if isinstance(r, dict) and isinstance(r.get("result"), list):
            ins = [t for t in r["result"] if t.get("to", "").lower() == wl.lower() and int(t.get("value", 0)) > 0]
    if not ins:
        return {"wallet": wl, "funder": None, "origin": None}
    big = max(ins, key=lambda t: int(t["value"]))
    funder = big.get("from", "").lower()
    txh = big.get("hash") or big.get("transactionHash")
    # risali all'EOA che ha ORIGINATO la tx (il vero pagatore, non il contratto-bridge)
    origin = funder
    code = rpc("eth_getCode", [funder, "latest"])
    is_contract = bool(code and code != "0x")
    if is_contract and txh:
        tx = rpc("eth_getTransactionByHash", [txh])
        if isinstance(tx, dict) and tx.get("from"): origin = tx["from"].lower()
    return {"wallet": wl, "funder": funder, "funder_contract": is_contract, "origin": origin,
            "eth": round(int(big["value"]) / 1e18, 3)}


def main():
    os.makedirs("data/raw/forensics", exist_ok=True)
    win, lose = target_wallets()
    ck = json.load(open(CK)) if os.path.exists(CK) else {"done": []}
    done = set(ck["done"])
    # bilancia: alterna vincenti e perdenti non ancora fatti
    todo = [(w, "win") for w in win if w not in done] + [(w, "lose") for w in lose if w not in done]
    todo = todo[:BATCH]
    print(f"target: {len(win)} vincenti, {len(lose)} perdenti | gia' fatti {len(done)} | questo run {len(todo)}", flush=True)

    out = f"data/raw/forensics/fund_{now}.jsonl.gz"; fo = gzip.open(out, "wt"); n = 0
    for wl, grp in todo:
        t = trace(wl); t["group"] = grp
        fo.write(json.dumps(t) + "\n"); n += 1; done.add(wl)
        print(f"  {grp} {wl[:12]} <- origin {str(t.get('origin'))[:12]} (contratto:{t.get('funder_contract')})", flush=True)
    fo.close()
    if n == 0: os.remove(out)
    ck["done"] = list(done); json.dump(ck, open(CK, "w"))

    # ---------- 3) analisi: vincenti vs perdenti condividono origini comuni? ----------
    rows = []
    for f in glob.glob("data/raw/forensics/fund_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"): rows.append(json.loads(l))
        except: pass
    def origins(grp):
        return [r["origin"] for r in rows if r.get("group") == grp and r.get("origin")]
    ow, ol = origins("win"), origins("lose")
    cw, cl = Counter(ow), Counter(ol)
    shared_w = sum(v for v in cw.values() if v >= 2)   # wallet vincenti che condividono un'origine con >=1 altro vincente
    shared_l = sum(v for v in cl.values() if v >= 2)
    pw = (shared_w / len(ow) * 100) if ow else 0
    pl = (shared_l / len(ol) * 100) if ol else 0

    L = [f"# 🕵️ WALLET FORENSICS — sub-wallet di balene?", f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}*", "",
         f"Tracciati finora: **{len(ow)} vincenti**, **{len(ol)} perdenti** (dei {len(win)}+{len(lose)} target).", "",
         "## Test: i VINCENTI condividono un'origine comune piu' dei PERDENTI?",
         f"- Vincenti che condividono l'origine con un altro vincente: **{pw:.0f}%**",
         f"- Perdenti che condividono l'origine con un altro perdente: **{pl:.0f}%** (controllo)",
         "",
         ("✅ **SEGNALE:** i vincenti si raggruppano PIU' dei perdenti -> possibili sub-wallet coordinati." if pw > pl + 15
          else "❌ **NESSUN SEGNALE:** vincenti e perdenti si raggruppano uguale -> e' solo infrastruttura (bridge), non balene coordinate." if ol
          else "⏳ dati insufficienti sul gruppo di controllo, continuo a tracciare."), "",
         "## Origini che finanziano piu' VINCENTI (candidate 'entita' balena')"]
    for o, c in cw.most_common(6):
        if c >= 2: L.append(f"- `{o}` -> {c} wallet vincenti")
    open("FORENSICS.md", "w").write("\n".join(L))
    print(f"\n✅ forensics: +{n} tracciati | vincenti condivisi {pw:.0f}% vs perdenti {pl:.0f}%", flush=True)


if __name__ == "__main__":
    main()
