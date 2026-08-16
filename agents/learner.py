#!/usr/bin/env python3
"""
LEARNER — il pezzo che rende il sistema AUTO-APPRENDENTE (come un modello AI: impara dai propri esiti).
Ad ogni giro: legge il ledger delle uscite del paper bot (esiti NOTI), ricostruisce le FEATURE d'entrata
(no-lookahead) di ogni trade, e ADDESTRA un modello che predice P(trade vincente) dalle feature.
Riporta cosa distingue i mostri dai morti (feature importance) + performance OUT-OF-SAMPLE onesta.
Salva il modello in data/selection_model.json → il paper bot lo usera' per SELEZIONARE le entrate.
Piu' trade accumula, piu' diventa bravo. €0, gira sul cloud, nessuna API a pagamento.

Guardrail (anti-illusione, lezione Solana): NON attiva la selezione finche' non ci sono abbastanza esempi
E l'AUC out-of-sample non batte il caso. Finche' e' cieco, lo dice.
"""
import gzip, json, glob, os, time, math, statistics as st

now = int(time.time())
LED = "data/paper_bot_ledger.jsonl.gz"
MODEL = "data/selection_model.json"
MONEY = {"weth", "eth", "usdg", "usdc", "usdt", "dai", "usdb", "weth9"}
MIN_SAMPLES = 60          # sotto questo il modello e' inaffidabile: non attivare
MIN_AUC = 0.60            # sotto questo non ha imparato niente di utile: non attivare


def load_flow_candles():
    reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    cand = {}
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d["tf"] == "hour" and d.get("cl"): cand.setdefault(d["pool"], {})[int(d["ts"])] = d["cl"]
        except: pass
    for p in cand: cand[p] = dict(sorted(cand[p].items()))
    flow = {}
    for f in glob.glob("data/raw/flow/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                flow.setdefault(d["pool"], {})[int(d["hour"])] = (d["buyusd"], d["sellusd"])
        except: pass
    return cand, flow


def features_at_entry(pool, entry_ts, cand, flow):
    """feature disponibili SOLO col passato (no-lookahead) al momento dell'entrata."""
    fl = flow.get(pool, {}); cs = cand.get(pool, {})
    past = sorted([(h, b, s) for h, (b, s) in fl.items() if h <= entry_ts])
    if not past: return None
    hrs = len(past); bu = sum(x[1] for x in past); su = sum(x[2] for x in past)
    sellratio = su / (bu + 1)
    # accelerazione buy-pressure: ultime 2 ore vs media precedente
    last2 = sum(x[1] for x in past[-2:]); earlier = [x[1] for x in past[:-2]]
    accel = (last2 / 2) / (st.mean(earlier) + 1) if earlier else 1.0
    # profondita' del dump post-listing: prezzo entrata / prezzo listing
    ks = sorted(cs)
    dump = cs[[k for k in ks if k <= entry_ts][-1]] / cs[ks[0]] if ks and cs[ks[0]] else 1.0
    return [hrs, math.log10(bu + su + 1), sellratio, math.log10(accel + 0.01), dump]


FEAT_NAMES = ["ore_flow", "log_volume", "sell_ratio", "log_buy_accel", "dump_depth"]


def sigmoid(z): return 1 / (1 + math.exp(-max(-30, min(30, z))))


def fit_logreg(X, y, iters=3000, lr=0.1):
    """regressione logistica in puro Python (niente dipendenze), con standardizzazione."""
    n, d = len(X), len(X[0])
    mu = [st.mean([X[i][j] for i in range(n)]) for j in range(d)]
    sd = [(st.pstdev([X[i][j] for i in range(n)]) or 1) for j in range(d)]
    Xs = [[(X[i][j] - mu[j]) / sd[j] for j in range(d)] for i in range(n)]
    w = [0.0] * d; b = 0.0
    for _ in range(iters):
        gw = [0.0] * d; gb = 0.0
        for i in range(n):
            p = sigmoid(sum(w[j] * Xs[i][j] for j in range(d)) + b)
            e = p - y[i]
            for j in range(d): gw[j] += e * Xs[i][j]
            gb += e
        for j in range(d): w[j] -= lr * gw[j] / n
        b -= lr * gb / n
    return w, b, mu, sd


def auc(scores, y):
    pos = [s for s, t in zip(scores, y) if t == 1]; neg = [s for s, t in zip(scores, y) if t == 0]
    if not pos or not neg: return 0.5
    c = sum((s > n) + 0.5 * (s == n) for s in pos for n in neg)
    return c / (len(pos) * len(neg))


def main():
    if not os.path.exists(LED):
        print("LEARNER | nessun trade ancora"); return
    led = [json.loads(l) for l in gzip.open(LED, "rt")]
    cand, flow = load_flow_candles()
    X, y, meta = [], [], []
    for c in led:
        f = features_at_entry(c["pool"], c["entry_ts"], cand, flow)
        if f is None: continue
        X.append(f); y.append(1 if c["ret"] > 0 else 0); meta.append(c)
    n = len(X); npos = sum(y)
    lines = ["# 🧠 LEARNER — il sistema impara dai propri trade",
             f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}*", "",
             f"Esempi etichettati: **{n}** (vincenti {npos}, perdenti {n - npos})", ""]

    if n < MIN_SAMPLES or npos < 8 or (n - npos) < 8:
        lines += [f"⏳ **Ancora pochi dati per imparare** (servono ≥{MIN_SAMPLES} trade e ≥8 per classe).",
                  "Il sistema sta accumulando esiti. Come ogni AI: senza abbastanza esempi non generalizza.",
                  "Selezione **NON attiva**: il bot per ora entra su tutti i tradeabili e raccoglie dati."]
        json.dump({"active": False, "n": n}, open(MODEL, "w"))
        open("LEARNING.md", "w").write("\n".join(lines)); print(f"LEARNER | {n} esempi, troppo pochi"); return

    # split temporale onesto: 70% train (piu' vecchi), 30% test (piu' recenti) = out-of-sample vero
    idx = sorted(range(n), key=lambda i: meta[i]["entry_ts"])
    cut = int(n * 0.7); tr, te = idx[:cut], idx[cut:]
    w, b, mu, sd = fit_logreg([X[i] for i in tr], [y[i] for i in tr])

    def score(f): return sigmoid(sum(w[j] * (f[j] - mu[j]) / sd[j] for j in range(len(f))) + b)
    auc_oos = auc([score(X[i]) for i in te], [y[i] for i in te]) if te else 0.5
    imp = sorted(zip(FEAT_NAMES, w), key=lambda x: -abs(x[1]))

    lines += [f"## Performance out-of-sample (onesta): AUC = **{auc_oos:.2f}** (0.5 = caso)",
              "## Cosa predice un vincente (peso appreso, dai dati NON da me):"]
    for nm, wt in imp:
        seg = "＋ alza P(vincita)" if wt > 0 else "－ abbassa P(vincita)"
        lines.append(f"- **{nm}**: {wt:+.2f}  {seg}")

    active = n >= MIN_SAMPLES and auc_oos >= MIN_AUC
    if active:
        lines += ["", f"✅ **Selezione ATTIVA**: AUC {auc_oos:.2f} ≥ {MIN_AUC}. Il bot entrera' solo sui token",
                  "con probabilita' di vincita alta secondo il modello appreso. Si ri-allena ad ogni giro."]
    else:
        lines += ["", f"⚠️ **Selezione non ancora attiva**: AUC {auc_oos:.2f} < {MIN_AUC}, non batte il caso.",
                  "Il modello continua ad accumulare/allenarsi finche' non trova un segnale vero."]
    json.dump({"active": active, "n": n, "auc": round(auc_oos, 3), "w": w, "b": b,
               "mu": mu, "sd": sd, "feat": FEAT_NAMES, "thr": 0.5}, open(MODEL, "w"))
    open("LEARNING.md", "w").write("\n".join(lines))
    print(f"LEARNER | {n} esempi | AUC_oos {auc_oos:.2f} | selezione {'ON' if active else 'OFF'}", flush=True)


if __name__ == "__main__":
    main()
