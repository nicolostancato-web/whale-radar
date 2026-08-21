#!/usr/bin/env python3
"""
MULTICHAIN_BRAIN — il CERVELLO + LOOP che impara su TUTTE le chain (Solana/BSC/Base/Robinhood).
Lavora coi soli candele+volume (il multichain non ha ancora flow/first-buyers): ricava le feature dai candele,
incluso un PROXY della pressione compratori (volume su candele verdi / totale). Per ogni chain E combinato:
etichetta i token (entra +3h, uscita scale-out 3x/6x, costi reali), addestra un modello P(vincita), e misura
il WALK-FORWARD ONESTO (no-lookahead: allena solo su token chiusi PRIMA). Scrive MULTICHAIN.md: quale chain
rende di piu' + se la selezione porta edge. €0, cloud. Stesso metodo/disciplina di sempre.
"""
import gzip, json, glob, os, time, math, statistics as st, sys
sys.path.insert(0, "agents")
import learner as L  # fit_logreg, sigmoid, auc, _net

now = int(time.time())
CHAINS = ["solana", "bsc", "base", "robinhood"]
ENTRY_H = 3; MIN_CANDLES = 5; MIN_VOL = 500  # basso: esclude solo i pool morti, TIENE i mostri che partono quieti; WARMUP = 40; THR = 0.40
FEAT = ["dump_depth", "log_vol", "buy_pressure", "volatilita", "log_vol_accel", "frac_verdi"]


def features(pre):
    """feature no-lookahead dai candele fino all'entrata (pre = lista [ts,o,h,l,c,vol])."""
    ep = pre[-1][4]; p0 = pre[0][4] or pre[0][1]
    dump = ep / p0 if p0 else 1.0
    voltot = sum((c[5] or 0) for c in pre)
    green = sum((c[5] or 0) for c in pre if (c[4] or 0) >= (c[1] or 0))
    bp = green / (voltot + 1)
    prices = [c[4] for c in pre if c[4]]
    volat = (max(prices) - min(prices)) / (st.mean(prices) + 1e-12) if len(prices) > 1 else 0.0
    accel = (pre[-1][5] or 0) / (st.mean([(c[5] or 0) for c in pre[:-1]]) + 1) if len(pre) > 1 else 1.0
    n_up = sum(1 for c in pre if (c[4] or 0) >= (c[1] or 0)) / len(pre)
    return [dump, math.log10(voltot + 1), bp, volat, math.log10(accel + 0.01), n_up]


def outcome(after):
    """uscita scale-out 3x/6x/trailing (stessa del paper bot), dai prezzi dopo l'entrata."""
    ep = after[0]; hi = ep; legs = []; h1 = h2 = False; pk = max(after) / ep if after else 1
    for v in after:
        if v <= 0: continue
        hi = max(hi, v); m = v / ep
        if not h1 and m >= 3: legs.append(L._net(3)); h1 = True
        if not h2 and m >= 6: legs.append(L._net(6)); h2 = True
        if not h1:
            if v <= ep * 0.3: legs.append(L._net(m)); break
        elif v <= hi * 0.5: legs.append(L._net(hi * 0.5 / ep, True)); break
    while len(legs) < 3: legs.append(legs[-1] if legs else L._net(after[-1] / ep if after else 1, True))
    return sum(legs[:3]) / 3, pk


def load_rows(chain):
    rows = []
    for f in glob.glob(f"data/multichain/{chain}/candles/*.jsonl.gz"):
        try:
            cs = []
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("cl"): cs.append([int(d["ts"]), d.get("op"), d.get("hi"), d.get("lo"), d["cl"], d.get("vol")])
            cs.sort()
            if len(cs) < MIN_CANDLES: continue
            t0 = cs[0][0]; ei = None
            for i, c in enumerate(cs):
                if c[0] >= t0 + ENTRY_H * 3600: ei = i; break
            if ei is None or ei == 0: continue
            pre = cs[:ei + 1]
            if sum((c[5] or 0) for c in pre) < MIN_VOL: continue          # filtro junk (volume candele)
            after = [c[4] for c in cs[ei:]]
            r, pk = outcome(after)
            rows.append({"ent": cs[ei][0], "xt": cs[-1][0], "f": features(pre), "ret": r, "peak": pk})
        except: pass
    rows.sort(key=lambda r: r["ent"])
    return rows


def walkforward(rows, thr=THR):
    sel = []
    for i, r in enumerate(rows):
        train = [q for q in rows[:i] if q["xt"] < r["ent"]]
        if len(train) < WARMUP: sel.append(r["ret"]); continue
        X = [q["f"] for q in train]; y = [1 if q["ret"] > 0 else 0 for q in train]
        if len(set(y)) < 2: sel.append(r["ret"]); continue
        w, b, mu, sd = L.fit_logreg(X, y)
        s = L.sigmoid(sum(w[j] * (r["f"][j] - mu[j]) / sd[j] for j in range(len(r["f"]))) + b)
        if s >= thr: sel.append(r["ret"])
    return sel


def port(rr): return (sum(1 + x for x in rr) / len(rr) - 1) * 100 if rr else 0.0
def win(rr): return sum(1 for x in rr if x > 0) / len(rr) * 100 if rr else 0.0


def main():
    per = {}
    allrows = []
    for ch in CHAINS:
        rows = load_rows(ch); per[ch] = rows; allrows += rows
    allrows.sort(key=lambda r: r["ent"])

    lines = ["# 🌐 MULTICHAIN BRAIN — il loop che impara su TUTTE le chain",
             f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · walk-forward onesto (no-lookahead) · solo candele+volume*", "",
             "## Per chain: dove rende di più?", "| chain | token | base | selezione | edge | vinti |", "|---|---|---|---|---|---|"]
    for ch in CHAINS:
        rows = per[ch]
        if len(rows) < 20: lines.append(f"| {ch} | {len(rows)} | (pochi dati) | | | |"); continue
        base = [r["ret"] for r in rows]; sel = walkforward(rows)
        lines.append(f"| **{ch}** | {len(rows)} | {port(base):+.0f}% | {port(sel):+.0f}% | {port(sel)-port(base):+.1f}% | {win(sel):.0f}% |")
    # combinato (allena su tutte le chain insieme)
    if len(allrows) >= 40:
        base = [r["ret"] for r in allrows]; sel = walkforward(allrows)
        lines += ["", f"## Combinato ({len(allrows)} token, tutte le chain)",
                  f"- Base: {port(base):+.0f}% | **Selezione: {port(sel):+.0f}%** | edge {port(sel)-port(base):+.1f}% | vinti {win(sel):.0f}%"]
    lines += ["", "> Solo candele+volume finora (buy-pressure = volume candele-verdi). Prossimo: flow/first-buyers per chain.",
              "> GOAL: edge robusto su abbastanza token. Si spinge in loop, si accumula, si aggiungono feature."]
    open("MULTICHAIN.md", "w").write("\n".join(lines))
    tot = sum(len(per[c]) for c in CHAINS)
    print(f"MULTICHAIN_BRAIN | {tot} token su {len(CHAINS)} chain | " +
          " ".join(f"{c}:{len(per[c])}" for c in CHAINS), flush=True)


if __name__ == "__main__":
    main()
