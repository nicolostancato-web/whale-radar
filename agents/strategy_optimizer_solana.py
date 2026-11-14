#!/usr/bin/env python3
"""
STRATEGY_OPTIMIZER_SOLANA (loop #3) — impara la STRATEGIA di exit/timing OTTIMALE per BASE (non copiata da Robinhood:
ogni chain ha sfumature diverse). Sweep dei parametri (entry_h, TP1, TP2, trailing, hard-stop): per ogni combo
ricalcola il rendimento scale-out (costi+latenza reali) e misura la MEDIA SELEZIONATA walk-forward (no-lookahead).
Sceglie la combo con la ROBUSTEZZA migliore (media senza i top-3 mostri → non dipendere dalla fortuna). Scrive
data/strategy_solana.json che il demo_live_solana usa. Feature/path pre-calcolati per entry_h → sweep veloce. €0.
"""
import gzip, json, glob, os, sys, time
sys.path.insert(0, "agents")
import multichain_brain as B, learner as L

CHAIN = "solana"; POS = 10.0
ES = XS = 0.15; FEE = 0.01; GAS = 0.014; LAT = 0.06


def net_ret(path, tp1, tp2, trail, hard):
    ep = path[0]; hi = ep; legs = []; h1 = h2 = False
    ein = (1 + ES + LAT) * (1 + FEE)
    def out(mult, tr): return mult * (1 - XS - (LAT if tr else 0)) * (1 - FEE) / ein - 1 - (GAS * 2) / POS
    for v in path:
        if v <= 0: continue
        hi = max(hi, v); m = v / ep
        if not h1 and m >= tp1: legs.append(out(tp1, False)); h1 = True
        if not h2 and m >= tp2: legs.append(out(tp2, False)); h2 = True
        if not h1:
            if v <= ep * (1 - hard): legs.append(out(m, False)); break
        elif v <= hi * (1 - trail): legs.append(out(hi * (1 - trail) / ep, True)); break
    while len(legs) < 3: legs.append(legs[-1] if legs else out(path[-1] / ep if path else 1, True))
    return sum(legs[:3]) / 3


def build(eh):
    """token a entry_h=eh: feature (fisse) + path. Con DIAGNOSTICA per capire dove si perdono i token."""
    rows = []; cnt = {"files": 0, "few_candles": 0, "no_entry": 0, "low_vol": 0, "short_path": 0, "err": 0, "ok": 0}
    for f in glob.glob(f"data/multichain/{CHAIN}/candles/*.jsonl.gz"):
        cnt["files"] += 1
        try:
            cs = []
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("cl"): cs.append([int(d["ts"]), d.get("op"), d.get("hi"), d.get("lo"), d["cl"], d.get("vol")])
            cs.sort()
            if len(cs) < B.MIN_CANDLES: cnt["few_candles"] += 1; continue
            t0 = cs[0][0]; ei = None
            for i, c in enumerate(cs):
                if c[0] >= t0 + eh * 3600: ei = i; break
            if ei is None or ei == 0: cnt["no_entry"] += 1; continue
            pre = cs[:ei + 1]
            if sum((c[5] or 0) for c in pre) < B.MIN_VOL: cnt["low_vol"] += 1; continue
            path = [c[4] for c in cs[ei:] if c[4] and c[4] > 0]
            if len(path) < 2: cnt["short_path"] += 1; continue
            addr = os.path.basename(f).replace(".jsonl.gz", "")
            feats = B.features(pre) + B.trade_features(B.load_trades(CHAIN, addr), cs[ei][0])
            rows.append({"ent": cs[ei][0], "xt": cs[-1][0], "f": feats, "path": path}); cnt["ok"] += 1
        except Exception as e: cnt["err"] += 1
    print(f"  build(eh={eh}): {cnt}", flush=True)
    rows.sort(key=lambda r: r["ent"])
    return rows


def wf_media(rows):
    """walk-forward: media + robustezza (senza top3) dei token selezionati (usa 'ret' gia' impostato)."""
    sel = []; model = None; last_n = 0
    for i, r in enumerate(rows):
        train = [q for q in rows[:i] if q["xt"] < r["ent"]]
        if len(train) < B.WARMUP: sel.append(r["ret"]); continue   # come il brain: includi i pre-warmup
        if model is None or len(train) - last_n >= 15:
            y = [1 if q["ret"] > 0 else 0 for q in train]
            if len(set(y)) >= 2:
                model = L.fit_logreg([q["f"] for q in train], y, iters=500); last_n = len(train)
        if not model: continue
        w, b, mu, sd = model
        s = L.sigmoid(sum(w[j] * (r["f"][j] - mu[j]) / sd[j] for j in range(len(r["f"]))) + b)
        if s >= 0.40: sel.append(r["ret"])
    if len(sel) < 15: return None
    media = (sum(1 + x for x in sel) / len(sel) - 1) * 100
    ss = sorted(sel, reverse=True)[3:]
    robusta = (sum(1 + x for x in ss) / len(ss) - 1) * 100 if ss else media
    return media, robusta, len(sel)


def main():
    best = None
    for eh in (1, 2, 3):
        rows = build(eh)
        if len(rows) < 60: continue
        for tp1 in (3, 4):
            for tp2 in (8, 15):
                for trail in (0.4, 0.5):
                    for hard in (0.7,):
                        for r in rows: r["ret"] = net_ret(r["path"], tp1, tp2, trail, hard)
                        res = wf_media(rows)
                        if not res: continue
                        media, robusta, n = res
                        if best is None or robusta > best[0]:     # priorita alla ROBUSTEZZA (non dipendere dai mostri)
                            best = (robusta, {"tp1": tp1, "tp2": tp2, "trail": trail, "hard": hard, "entry_h": eh,
                                              "media": round(media, 1), "robusta": round(robusta, 1), "n": n})
    if best:
        json.dump(best[1], open("data/strategy_solana.json", "w"))
        # traccia il cambio: un parametro che cambia senza storico e' il sistema che si riscrive
        # le regole da solo (l'auditor lo segnala come possibile imbroglio)
        with open("data/strategy_history.jsonl", "a") as fo:
            fo.write(json.dumps(dict(best[1], chain="solana", ts=int(time.time()))) + "\n")
        print(f"STRATEGY_OPTIMIZER_SOLANA | migliore per Base: {best[1]}", flush=True)
    else:
        print("STRATEGY_OPTIMIZER_SOLANA | dati Base insufficienti per ottimizzare", flush=True)


if __name__ == "__main__":
    main()
