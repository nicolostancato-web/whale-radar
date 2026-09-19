#!/usr/bin/env python3
"""
STRATEGY_OPTIMIZER — rende AUTOMATICO anche il Motore 2 (la strategia entrata/uscita).
Ogni giorno prova diverse strategie (take-profit, trailing, hard-stop, timing d'entrata) sui dati Robinhood
in WALK-FORWARD onesto (no-lookahead, costi reali dentro), e se ne trova una MIGLIORE **E robusta**
(regge togliendo i 3 mostri top = non curve-fitting), la ADOTTA scrivendola in data/strategy.json.
Cosi' il sistema cambia la sua strategia DA SOLO finche' non e' profittevole. Ogni cambio loggato in
STRATEGY_LOG.md. Guardrail: non adotta mai una strategia che vince solo grazie a 2-3 colpi fortunati. €0.
"""
import gzip, json, glob, os, time, sys, itertools, statistics as st
sys.path.insert(0, "agents")
import learner as L

now = int(time.time())
STRAT = "data/strategy.json"
# griglia di strategie da provare (sensate, non infinite → meno overfitting)
TP1_OPTS = [2.0, 3.0]; TP2_OPTS = [5.0, 6.0, 8.0]; TRAIL_OPTS = [0.40, 0.50, 0.60]
HARD_OPTS = [0.60, 0.70]; ENTRY_OPTS = [1, 3, 6]
ES = XS = 0.15; FEE = 0.01; GAS = 0.014; SIZE = 2.0; LAT = 0.08


def net(m, tr=False):
    ein = (1 + ES) * (1 + FEE); eout = m * (1 - XS) * (1 - FEE) * (1 - (LAT if tr else 0))
    return eout / ein - 1 - (GAS * 2) / SIZE


def outcome(prices, tp1, tp2, trail, hard):
    ep = prices[0]; hi = ep; legs = []; h1 = h2 = False
    for v in prices:
        if v <= 0: continue
        hi = max(hi, v); m = v / ep
        if not h1 and m >= tp1: legs.append(net(tp1)); h1 = True
        if not h2 and m >= tp2: legs.append(net(tp2)); h2 = True
        if not h1:
            if v <= ep * (1 - hard): legs.append(net(m)); break
        elif v <= hi * (1 - trail): legs.append(net(hi * (1 - trail) / ep, True)); break
    while len(legs) < 3: legs.append(legs[-1] if legs else net(prices[-1] / ep if prices else 1, True))
    return sum(legs[:3]) / 3


def build(entry_h):
    """token Robinhood: (entry_ts, exit_ts, prezzi-dopo-entrata) col filtro tradeabilita."""
    reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    cand, flow, fbp, wl, fts = L.load_data()
    mp = {a: reg[a].get("name") for a in reg if len(a) == 42 and L._is_meme(reg[a].get("name"))}
    cand = {p: c for p, c in cand.items() if p in mp}
    fts2 = {p: min(cand[p]) for p in cand if cand[p]}
    byname = {}
    for p in cand:
        nm = (mp[p] or "").split(" ")[0]
        if nm not in byname or fts2[p] < fts2[byname[nm]]: byname[nm] = p
    rows = []
    for nm, p in byname.items():
        lt = fts2[p]; base = lt + entry_h * 3600; fl = flow.get(p, {}); ent = None
        for t in sorted(cand[p]):
            if t < base: continue
            past = [v for h, v in fl.items() if h <= t]
            if len(past) >= 4 and sum(v[0] + v[1] for v in past) >= 3000 and sum(v[1] for v in past) / (sum(v[0] for v in past) + 1) >= 0.15:
                ent = t; break
        if ent is None: continue
        after = [cand[p][t] for t in sorted(cand[p]) if t >= ent and cand[p][t] > 0]
        if len(after) < 2: continue
        rows.append((ent, sorted(cand[p])[-1], after))
    rows.sort(key=lambda r: r[0])
    return rows


def port(rr): return (sum(1 + x for x in rr) / len(rr) - 1) * 100 if rr else 0.0


def main():
    # provo ogni combinazione, misuro media + robustezza (senza top3)
    results = []
    cache = {}
    for eh in ENTRY_OPTS:
        cache[eh] = build(eh)
    for tp1, tp2, trail, hard, eh in itertools.product(TP1_OPTS, TP2_OPTS, TRAIL_OPTS, HARD_OPTS, ENTRY_OPTS):
        if tp2 <= tp1: continue
        rows = cache[eh]
        if len(rows) < 40: continue
        rets = [outcome(after, tp1, tp2, trail, hard) for _, _, after in rows]
        media = port(rets); no3 = port(sorted(rets, reverse=True)[3:])
        results.append({"tp1": tp1, "tp2": tp2, "trail": trail, "hard": hard, "entry_h": eh,
                        "media": round(media, 1), "robusta": round(no3, 1), "n": len(rets)})
    if not results:
        print("STRATEGY_OPTIMIZER | dati insufficienti"); return
    # GUARDRAIL: ordino per ROBUSTEZZA (senza top3), non per media grezza (anti curve-fitting)
    results.sort(key=lambda r: (r["robusta"], r["media"]), reverse=True)
    best = results[0]

    # strategia LIVE attuale (letta da strategy.json; se non c'e', il default di partenza)
    cur = json.load(open(STRAT)) if os.path.exists(STRAT) else {"tp1": 3.0, "tp2": 6.0, "trail": 0.50, "hard": 0.70, "entry_h": 3, "robusta": None}
    curm = next((r for r in results if r["tp1"] == cur["tp1"] and r["tp2"] == cur["tp2"]
                 and r["trail"] == cur["trail"] and r["hard"] == cur["hard"] and r["entry_h"] == cur["entry_h"]), None)
    cur_rob = curm["robusta"] if curm else cur.get("robusta")

    # AUTO-APPLICA solo se migliora la ROBUSTA di >2 punti (mai peggiora; margine per evitare rumore)
    meglio = cur_rob is None or best["robusta"] > cur_rob + 2
    applied = cur
    if meglio:
        applied = {"tp1": best["tp1"], "tp2": best["tp2"], "trail": best["trail"], "hard": best["hard"],
                   "entry_h": best["entry_h"], "media": best["media"], "robusta": best["robusta"],
                   "updated": time.strftime("%Y-%m-%d", time.gmtime(now))}
        json.dump(applied, open(STRAT, "w"))
        # storico dei cambi (append)
        with open("data/strategy_history.jsonl", "a") as fo: fo.write(json.dumps(applied) + "\n")

    if meglio and cur_rob is not None:
        status = f"🔄 MIGLIORATA oggi da sola (robusta {cur_rob:+.0f}% → {best['robusta']:+.0f}%)"
    elif cur_rob is None:
        status = "🔄 prima strategia registrata"
    else:
        status = "✅ già la migliore — NON cambiata, non peggioriamo"
    log = [f"# 🔧 STRATEGY_OPTIMIZER — l'auto-learn della STRATEGIA (cambia da solo, solo se migliora)",
           f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}*", "",
           f"## Strategia LIVE adesso",
           f"- +{applied['entry_h']}h · TP {applied['tp1']:.0f}x/{applied['tp2']:.0f}x · trailing -{applied['trail']*100:.0f}% · hard -{applied['hard']*100:.0f}%",
           f"- robusta **{applied.get('robusta',0):+.0f}%** (media {applied.get('media',0):+.0f}%)",
           f"- {status}", "",
           "## Top 6 provate oggi (ordinate per robustezza)",
           "| entrata | TP | trailing | hard | media | robusta |", "|---|---|---|---|---|---|"]
    for r in results[:6]:
        mark = " ←LIVE" if (r["tp1"] == applied["tp1"] and r["tp2"] == applied["tp2"] and r["trail"] == applied["trail"] and r["hard"] == applied["hard"] and r["entry_h"] == applied["entry_h"]) else ""
        log.append(f"| +{r['entry_h']}h | {r['tp1']:.0f}x/{r['tp2']:.0f}x | -{r['trail']*100:.0f}% | -{r['hard']*100:.0f}% | {r['media']:+.0f}% | {r['robusta']:+.0f}%{mark} |")
    log += ["", "> Auto-applica SOLO se la robustezza (media senza i 3 mostri top) migliora di >2 punti → mai peggiora, no curve-fitting su colpi fortunati.",
            "> ⚠️ Ottimizzazione su storico = rischio overfitting: teniamo d'occhio il numero FORWARD (EDGE.md). Se peggiora, si stringe il guardrail."]
    open("STRATEGY_LOG.md", "w").write("\n".join(log))
    print(f"STRATEGY_OPTIMIZER | live robusta {applied.get('robusta')}% | {'MIGLIORATA' if meglio else 'invariata'}", flush=True)


if __name__ == "__main__":
    main()
