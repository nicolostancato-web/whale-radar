#!/usr/bin/env python3
"""
WHALE_ENRICH — arricchisce OGNI balena (anche STORICA) con le FEATURE-INSIDER, calcolate SOLO con dati fino
all'entrata (ZERO lookahead), precise e immutabili. Spec: INSIDER_FEATURES.md (da deep-search).
Cosi' la Fase 2 trova il pezzo gia' pronto per lo "score insider" (entra piccolo + pre-pump + token giovane +
comprato basso + early buyer + ripetuto). Feature per-balena qui; le feature cross-wallet + funding le unisce
la Fase 2 (dalla forensica). File immutabili per run, dedup per tx+li, resumable, budget-tempo. €0.
"""
import gzip, json, glob, os, time, statistics as st
from collections import defaultdict

now = int(time.time())
CK = "data/enrich_checkpoint.json"
BATCH_SEC = int(os.environ.get("ENRICH_SEC", 600))
YOUNG_H = 168   # token "giovane" = < 7 giorni di vita all'entrata


def load_candles():
    cand = {}
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d["tf"] == "hour": cand.setdefault(d["pool"], {})[int(d["ts"])] = (d["cl"], d.get("v", 0))
        except: pass
    for p in cand: cand[p] = dict(sorted(cand[p].items()))
    return cand


def load_whales():
    w = []
    for f in glob.glob("data/raw/whales/backfill_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                try:
                    x = json.loads(l)
                    if x.get("usd") and x.get("ts") and x.get("wallet"): w.append(x)
                except: pass
        except EOFError: pass
    return w


def main():
    os.makedirs("data/raw/enriched", exist_ok=True)
    cand = load_candles()
    whales = load_whales()
    # precompute: per pool, i ts (ordinati) dei buy-balena e i wallet -> per la POSIZIONE in sequenza (tra le balene)
    pool_buys = defaultdict(list)   # pool -> [(ts, wallet)]
    wallet_pool_ts = defaultdict(list)  # (wallet,pool) -> [ts]
    for x in whales:
        pool_buys[x["pool"]].append((x["ts"], x["wallet"]))
        wallet_pool_ts[(x["wallet"], x["pool"])].append(x["ts"])
    for p in pool_buys: pool_buys[p].sort()

    seen = set()
    for f in glob.glob("data/raw/enriched/feat_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                try: seen.add(json.loads(l)["k"])
                except: pass
        except EOFError: pass

    out = f"data/raw/enriched/feat_{now}.jsonl.gz"; fo = gzip.open(out, "wt"); n = 0
    start = time.time()
    for x in whales:
        if time.time() - start > BATCH_SEC: break
        if x["pool"] not in cand: continue
        k = f"{x.get('tx')}_{x.get('li')}"
        if k in seen: continue
        ts = x["ts"]; ck = cand[x["pool"]]
        ks = [t for t in ck if t <= ts]
        if len(ks) < 3: continue   # poca storia -> si riprende quando ci sono piu' candele
        prices = [ck[t][0] for t in ks if ck[t][0] > 0]
        vols = [ck[t][1] for t in ks]
        if not prices: continue
        entry = prices[-1]; vent = vols[-1]
        pv = [v for v in vols if v > 0]; medv = st.median(pv) if pv else 0
        age_h = round((ts - ks[0]) / 3600, 1)
        # prezzo minimo 24h prima (fallback a vita se token <24h)
        ks24 = [t for t in ks if t >= ts - 24 * 3600]
        p24 = [ck[t][0] for t in ks24 if ck[t][0] > 0] or prices
        pmin24 = min(p24); pmax = max(prices)
        # percentile prezzo storico (frazione di candele-prezzo PRIMA sotto l'entrata)
        prior = prices[:-1] or [entry]
        perc = round(sum(1 for p in prior if p < entry) / len(prior), 3)
        # posizione tra le BALENE del token (proxy di early-buyer): quanti wallet-balena UNICI prima
        prior_wh = set(wl for (t, wl) in pool_buys[x["pool"]] if t < ts)
        seq_pos = len(prior_wh) + 1
        # intervallo dall'ultimo buy dello stesso wallet sullo stesso token
        prev = [t for t in wallet_pool_ts[(x["wallet"], x["pool"])] if t < ts]
        interval_h = round((ts - max(prev)) / 3600, 1) if prev else None

        rec = {"k": k, "wallet": x["wallet"], "pool": x["pool"], "name": x.get("name"),
               "ts": ts, "usd": x["usd"], "entry_price": entry,
               "eta_token_ore": age_h,
               "token_giovane": int(age_h <= YOUNG_H),
               "early_quiet": int(vent <= medv),                    # entrato nel quieto (vol <= mediana)
               "vol_ratio": round(vent / (medv or 1), 2),
               "delta_min_24h": round(entry / pmin24 - 1, 3),       # quanto sopra il minimo recente (0 = sul fondo)
               "percentile_prezzo_storico": perc,                  # <0.2 = comprato basso nella storia
               "price_vs_max": round(entry / pmax, 3) if pmax > 0 else None,
               "seq_pos_balene": seq_pos,                          # 1 = prima balena sul token (early)
               "n_candele_prima": len(ks),
               "intervallo_ultimo_buy_ore": interval_h}           # scaling-in se piccolo
        fo.write(json.dumps(rec) + "\n"); seen.add(k); n += 1
    fo.close()
    if n == 0: os.remove(out)
    ck2 = {"ts": now, "enriched": len(seen)}; json.dump(ck2, open(CK, "w"))
    print(f"✅ enrich: +{n} balene arricchite (feature-insider, no-lookahead) | archivio: {len(seen):,}", flush=True)


if __name__ == "__main__":
    main()
