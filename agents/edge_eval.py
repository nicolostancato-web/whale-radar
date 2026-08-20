#!/usr/bin/env python3
"""
EDGE_EVAL — lo STRUMENTO DEL LOOP: misura ogni giorno, in modo ONESTO (walk-forward, no-lookahead),
quanto edge ha oggi il sistema con i dati+feature attuali. Logga il numero nel tempo → vediamo l'ago
muoversi verso il GOAL. Nessuna illusione in-sample: alleno il modello SOLO sui token gia' chiusi PRIMA
di ognuno, esattamente come girerebbe live. Scrive EDGE.md (il cruscotto del progresso). €0, cloud.

GOAL: walk-forward portafoglio chiaramente positivo e robusto (non nel rumore) su abbastanza token.
Finche' non ci siamo: si accumulano dati e si aggiungono leve. Decide Nicolo quando basta. Mai mollare.
"""
import gzip, json, os, time, sys, statistics as st
sys.path.insert(0, "agents")
import learner as L

now = int(time.time())
THR = 0.40; WARMUP = 40
HIST = "data/edge_history.jsonl"


def build_rows(cand, flow, fbp, wl, fts, reg):
    mp = {a: reg[a].get("name") for a in reg if len(a) == 42 and L._is_meme(reg[a].get("name"))}
    byname = {}
    for p in cand:
        if p not in mp: continue
        nm = (mp[p] or "").split(" ")[0]
        if nm not in byname or fts[p] < fts[byname[nm]]: byname[nm] = p

    def outcome_ts(cs, ent, ep):
        ser = [(t, cs[t]) for t in sorted(cs) if t >= ent and cs[t] > 0]
        hi = ep; legs = []; h2 = h35 = False; xt = ser[-1][0] if ser else ent
        for t, v in ser:
            hi = max(hi, v); m = v / ep
            if not h2 and m >= 3: legs.append(L._net(3)); h2 = True
            if not h35 and m >= 6: legs.append(L._net(6)); h35 = True
            if not h2:
                if v <= ep * 0.3: legs.append(L._net(m)); xt = t; break
            elif v <= hi * 0.5: legs.append(L._net(hi * 0.5 / ep, True)); xt = t; break
        while len(legs) < 3: legs.append(legs[-1] if legs else L._net(ser[-1][1] / ep if ser else 1, True))
        return sum(legs[:3]) / 3, xt

    rows = []
    for nm, p in byname.items():
        lt = fts[p]; base = lt + 3 * 3600; fl = flow.get(p, {}); ent = ep = None
        for t in sorted(cand[p]):
            if t < base: continue
            past = [v for h, v in fl.items() if h <= t]
            hrs = len(past); bu = sum(v[0] for v in past); su = sum(v[1] for v in past)
            if hrs >= 4 and bu + su >= 3000 and su / (bu + 1) >= 0.15: ent, ep = t, cand[p][t]; break
        if ent is None or not ep: continue
        f = L.features_at_entry(p, ent, cand, flow, fbp, wl, fts)
        if f is None: continue
        ret, xt = outcome_ts(cand[p], ent, ep)
        rows.append({"ent": ent, "xt": xt, "f": f, "ret": ret})
    rows.sort(key=lambda r: r["ent"])
    return rows


def walkforward(rows):
    sel = []
    for i, r in enumerate(rows):
        train = [q for q in rows[:i] if q["xt"] < r["ent"]]
        if len(train) < WARMUP: sel.append(r["ret"]); continue
        X = [q["f"] for q in train]; y = [1 if q["ret"] > 0 else 0 for q in train]
        if len(set(y)) < 2: sel.append(r["ret"]); continue
        w, b, mu, sd = L.fit_logreg(X, y)
        s = L.sigmoid(sum(w[j] * (r["f"][j] - mu[j]) / sd[j] for j in range(len(r["f"]))) + b)
        if s >= THR: sel.append(r["ret"])
    return sel


def port(rr): return (sum(1 + x for x in rr) / len(rr) - 1) * 100 if rr else 0.0
def win(rr): return sum(1 for x in rr if x > 0) / len(rr) * 100 if rr else 0.0


def main():
    cand, flow, fbp, wl, fts = L.load_data()
    reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    rows = build_rows(cand, flow, fbp, wl, fts, reg)
    base = [r["ret"] for r in rows]
    sel = walkforward(rows)
    rec = {"date": time.strftime("%Y-%m-%d", time.gmtime(now)), "n_tok": len(rows),
           "base_port": round(port(base), 1), "base_win": round(win(base), 0),
           "sel_n": len(sel), "sel_port": round(port(sel), 1), "sel_win": round(win(sel), 0),
           "edge": round(port(sel) - port(base), 1)}
    # log immutabile (una riga al giorno; sostituisce quella di oggi se rigira)
    hist = []
    if os.path.exists(HIST):
        for l in open(HIST):
            try:
                d = json.loads(l)
                if d.get("date") != rec["date"]: hist.append(d)
            except: pass
    hist.append(rec)
    with open(HIST, "w") as fo:
        for d in hist: fo.write(json.dumps(d) + "\n")

    # cruscotto
    trend = hist[-10:]
    L2 = ["# 📊 EDGE — cruscotto del loop (walk-forward ONESTO verso il goal)",
          f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · no-lookahead, come girerebbe live*", "",
          f"## Oggi ({rec['n_tok']} token tradeabili)",
          f"- Entra su tutti:  {rec['base_port']:+.0f}%  (vinti {rec['base_win']:.0f}%)",
          f"- **Con selezione: {rec['sel_port']:+.0f}%**  (vinti {rec['sel_win']:.0f}%, {rec['sel_n']} entrati)",
          f"- **EDGE della selezione: {rec['edge']:+.1f}%**", "",
          "> GOAL: edge chiaramente positivo e ROBUSTO (non nel rumore) su abbastanza token → poi size vera piccola.",
          "> Finche' non ci siamo: piu' dati + nuove leve. Si spinge in loop. Decide Nicolo quando basta.", "",
          "## Andamento (l'ago si muove?)",
          "| data | token | edge selezione |", "|---|---|---|"]
    for d in trend:
        L2.append(f"| {d['date']} | {d['n_tok']} | {d.get('edge', 0):+.1f}% |")
    open("EDGE.md", "w").write("\n".join(L2))
    print(f"EDGE_EVAL | {rec['n_tok']} token | base {rec['base_port']:+.0f}% | sel {rec['sel_port']:+.0f}% | edge {rec['edge']:+.1f}%", flush=True)


if __name__ == "__main__":
    main()
