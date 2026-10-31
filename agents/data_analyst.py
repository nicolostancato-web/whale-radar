#!/usr/bin/env python3
"""
DATA_ANALYST — l'analisi automatica del loop (livello 1). Ogni giorno mina i dati accumulati e tira fuori
la MATERIA PRIMA per le prossime leve: (a) quali feature separano vincenti da morti (forza del segnale),
(b) quali WALLET tornano sui token vincenti (candidati smart-money da trasformare in feature),
(c) cosa hanno in comune i MOSTRI (ret>+100%) all'entrata. Scrive ANALYSIS.md. Onesto: correlazione != causa,
campioni piccoli segnalati. Nessun soldo, nessuna decisione automatica — solo materiale per io+Nicolo. €0.
"""
import gzip, json, os, time, sys, glob, statistics as st
sys.path.insert(0, "agents")
import learner as L

now = int(time.time())


def main():
    cand, flow, fbp, wl, fts = L.load_data()
    reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    mp = {a: reg[a].get("name") for a in reg if len(a) == 42 and L._is_meme(reg[a].get("name"))}
    byname = {}
    for p in cand:
        if p not in mp: continue
        nm = (mp[p] or "").split(" ")[0]
        if nm not in byname or fts[p] < fts[byname[nm]]: byname[nm] = p

    def outcome(cs, ent, ep):
        ser = [cs[t] for t in sorted(cs) if t >= ent and cs[t] > 0]; hi = ep; legs = []; h2 = h35 = False
        pk = max(ser) / ep if ser else 1
        for v in ser:
            hi = max(hi, v); m = v / ep
            if not h2 and m >= 3: legs.append(L._net(3)); h2 = True
            if not h35 and m >= 6: legs.append(L._net(6)); h35 = True
            if not h2:
                if v <= ep * 0.3: legs.append(L._net(m)); break
            elif v <= hi * 0.5: legs.append(L._net(hi * 0.5 / ep, True)); break
        while len(legs) < 3: legs.append(legs[-1] if legs else L._net(ser[-1] / ep if ser else 1, True))
        return sum(legs[:3]) / 3, pk

    # costruisci: per ogni token tradeabile -> feature, ret, picco, wallet first-buyer, tempo
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
        ret, pk = outcome(cand[p], ent, ep)
        wallets = set(w for w, _ in fbp.get(p, []))
        rows.append({"nm": nm, "f": f, "ret": ret, "peak": pk, "wallets": wallets, "ent": ent})

    n = len(rows)
    L2 = ["# 🔬 DATA_ANALYST — materia prima per il loop",
          f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · {n} token tradeabili · correlazione != causa*", ""]
    if n < 30:
        L2.append("⏳ Troppi pochi token per analizzare. Si accumula.")
        open("ANALYSIS.md", "w").write("\n".join(L2)); print("DATA_ANALYST | pochi dati"); return

    win = [r for r in rows if r["ret"] > 0]; los = [r for r in rows if r["ret"] <= 0]
    mon = [r for r in rows if r["peak"] >= 6]

    # (a) forza discriminante di ogni feature (AUC del singolo feature su vincita)
    def single_auc(j):
        pos = [r["f"][j] for r in win]; neg = [r["f"][j] for r in los]
        if not pos or not neg: return 0.5
        c = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg)
        a = c / (len(pos) * len(neg)); return max(a, 1 - a)  # forza = distanza da 0.5
    L2 += ["## (a) Feature attuali: chi porta segnale?", "| feature | forza (0.5=nulla) | media vincenti | media morti |", "|---|---|---|---|"]
    fr = sorted(range(len(L.FEAT_NAMES)), key=lambda j: -single_auc(j))
    for j in fr:
        mw = st.mean([r["f"][j] for r in win]); ml = st.mean([r["f"][j] for r in los])
        L2.append(f"| {L.FEAT_NAMES[j]} | {single_auc(j):.2f} | {mw:.2f} | {ml:.2f} |")

    # (b) wallet che tornano sui VINCENTI (candidati smart-money) — no-lookahead grezzo: tasso di vittoria per wallet
    wstat = {}
    for r in rows:
        for w in r["wallets"]: wstat.setdefault(w, []).append(1 if r["ret"] > 0 else 0)
    cand_w = [(w, sum(v), len(v)) for w, v in wstat.items() if len(v) >= 3]
    cand_w.sort(key=lambda x: (-x[1] / x[2], -x[2]))
    L2 += ["", "## (b) Wallet candidati smart-money (first-buyer su ≥3 token, alto tasso di vittoria)",
           "| wallet | vinti/token | tasso |", "|---|---|---|"]
    for w, wins, tot in cand_w[:8]:
        L2.append(f"| `{w[:14]}…` | {wins}/{tot} | {wins/tot*100:.0f}% |")
    strong = sum(1 for w, wins, tot in cand_w if wins / tot >= 0.6 and tot >= 3)
    L2.append(f"\n→ **{strong} wallet** con ≥60% di vincite su ≥3 token = candidati per una feature 'segue-gli-smart' (da validare no-lookahead).")

    # (c) cosa hanno in comune i MOSTRI vs il resto
    if mon:
        L2 += ["", f"## (c) I MOSTRI (picco ≥6x): {len(mon)}/{n} token — cosa avevano all'entrata"]
        for j in range(len(L.FEAT_NAMES)):
            mm = st.mean([r["f"][j] for r in mon]); mr = st.mean([r["f"][j] for r in rows if r["peak"] < 6])
            if abs(mm - mr) > 0.1 * (abs(mr) + 0.1):
                dirn = "PIÙ ALTO" if mm > mr else "PIÙ BASSO"
                L2.append(f"- **{L.FEAT_NAMES[j]}** {dirn} nei mostri ({mm:.2f} vs {mr:.2f})")

    L2 += ["", "> Questi sono CANDIDATI, non verità. La prossima leva del loop si pesca da qui,",
           "> si costruisce come feature, e si testa in EDGE_EVAL (walk-forward onesto)."]
    open("ANALYSIS.md", "w").write("\n".join(L2))
    print(f"DATA_ANALYST | {n} token | {len(win)} vinc | {len(mon)} mostri | {len(cand_w)} wallet ricorrenti", flush=True)


if __name__ == "__main__":
    main()
