#!/usr/bin/env python3
"""
DEMO_LIVE_BASE — conto demo-live PERSISTENTE dedicato a BASE (loop #2 "profitto"). Gemello di demo_live (Robinhood)
ma con STRATEGIA DEDICATA: legge data/strategy_base.json (parametri exit/timing ottimizzati SUI DATI BASE dal loop #3
strategy_optimizer_base — perche' ogni chain ha sfumature diverse). Il loop #1 "percentuale" e' il cervello Base
(modello walk-forward). Conto vero €100 → €3.000 che vive in avanti: seleziona col modello Base (no-lookahead),
apre/chiude 10% del saldo (max 10), uscita scale-out coi parametri BASE, costi+latenza reali, RESET a €100 se brucia.
PURE FORWARD (solo token Base nati dopo l'apertura). Stato in data/demo_live_base_state.json. Scrive DEMO_LIVE_BASE.md. €0.
"""
import gzip, json, glob, os, time, sys
sys.path.insert(0, "agents")
import multichain_brain as B, learner as L
import gate

CHAIN = "base"
now = int(time.time())
START = 100.0; GOAL = 3000.0; RESET_AT = 25.0
POS_FRAC = 0.10; MAX_POS = 10; THR = 0.30
ES = XS = 0.15; FEE = 0.01; GAS = 0.014; LAT_ENTRY = 0.06; LAT_EXIT = 0.06   # costi+latenza reali (come Robinhood)
STATE = "data/demo_live_base_state.json"

# STRATEGIA DEDICATA A BASE (loop #3 la ottimizza; default = punto di partenza sensato, poi diverge da Robinhood)
S = json.load(open("data/strategy_base.json")) if os.path.exists("data/strategy_base.json") else {}
TP1 = S.get("tp1", 3.0); TP2 = S.get("tp2", 8.0); TRAIL = S.get("trail", 0.4); HARD = S.get("hard", 0.7); EH = S.get("entry_h", 1)


def net_ret(path, size):
    """rendimento realistico scale-out coi parametri BASE (TP1/TP2/TRAIL/HARD), con slippage+fee+gas+latenza."""
    ep = path[0]; hi = ep; legs = []; h1 = h2 = False
    ein = (1 + ES + LAT_ENTRY) * (1 + FEE)
    def out(mult, tr):
        eout = mult * (1 - XS - (LAT_EXIT if tr else 0)) * (1 - FEE)
        return eout / ein - 1 - (GAS * 2) / size
    for v in path:
        if v <= 0: continue
        hi = max(hi, v); m = v / ep
        if not h1 and m >= TP1: legs.append(out(TP1, False)); h1 = True
        if not h2 and m >= TP2: legs.append(out(TP2, False)); h2 = True
        if not h1:
            if v <= ep * (1 - HARD): legs.append(out(m, False)); break
        elif v <= hi * (1 - TRAIL): legs.append(out(hi * (1 - TRAIL) / ep, True)); break
    while len(legs) < 3: legs.append(legs[-1] if legs else out(path[-1] / ep if path else 1, True))
    return sum(legs[:3]) / 3


def scored_tokens():
    """costruisce i token Base con entry (a EH ore), feature (candele+flow), path prezzi, ret BASE e score walk-forward."""
    rows = []
    for f in B.serie_files(CHAIN):          # candele + PULSE (i token freschi vivono li')
        try:
            cs = []; nato = None
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("t0"): nato = int(d["t0"])            # nascita vera (righe del pulse)
                if d.get("cl"): cs.append([int(d["ts"]), d.get("op"), d.get("hi"), d.get("lo"), d["cl"], d.get("vol")])
            cs.sort()
            if len(cs) < B.MIN_CANDLES: continue
            t0 = nato or cs[0][0]; ei = None
            if cs[0][0] > t0 + EH * 3600: continue             # preso troppo tardi: finestra d'entrata persa
            for i, c in enumerate(cs):
                if c[0] >= t0 + EH * 3600: ei = i; break          # ENTRY timing BASE (EH da strategy_base)
            if ei is None or ei == 0: continue
            pre = cs[:ei + 1]
            if sum((c[5] or 0) for c in pre) < B.MIN_VOL: continue
            path = [c[4] for c in cs[ei:] if c[4] and c[4] > 0]
            if len(path) < 2: continue
            addr = os.path.basename(f).replace(".jsonl.gz", "")
            entry_ts = cs[ei][0]
            feats = B.features(pre) + B.trade_features(B.load_trades(CHAIN, addr), entry_ts)
            rows.append({"ent": entry_ts, "xt": cs[-1][0], "addr": addr, "f": feats,
                         "ret": net_ret(path, max(2.0, START * POS_FRAC))})
        except: pass
    rows.sort(key=lambda r: r["ent"])
    # score walk-forward (modello Base, allenato solo sui token risolti PRIMA = no-lookahead)
    model = None; last_n = 0; out = []
    for i, r in enumerate(rows):
        train = [q for q in rows[:i] if q["xt"] < r["ent"]]
        score = 0.5
        if len(train) >= B.WARMUP:
            if model is None or len(train) - last_n >= 10:
                y = [1 if q["ret"] > 0 else 0 for q in train]
                if len(set(y)) >= 2:
                    model = L.fit_logreg([q["f"] for q in train], y, iters=800); last_n = len(train)
            if model:
                w, b, mu, sd = model
                score = L.sigmoid(sum(w[j] * (r["f"][j] - mu[j]) / sd[j] for j in range(len(r["f"]))) + b)
        out.append({"pool": r["addr"], "ent": r["ent"], "xt": r["xt"], "ret": r["ret"], "score": score})
    out.sort(key=lambda t: t["ent"])
    return out


CANCELLO, MOTIVO_CANCELLO = gate.aperto("base")


def main():
    toks = scored_tokens()
    st = json.load(open(STATE)) if os.path.exists(STATE) else None
    if st is None:
        st = {"bal": START, "open": [], "entered": [], "resets": 0, "closed": 0,
              "peak": START, "start_ts": now, "reached": False}
    entered = set(st["entered"]); openp = st["open"]

    newp = [t for t in toks if t["pool"] not in entered and t["ent"] >= st["start_ts"]]  # PURE FORWARD
    newp.sort(key=lambda t: t["ent"])
    for tk in newp:
        for pos in [x for x in openp if x["xt"] <= tk["ent"]]:
            st["bal"] += pos["size"] * (1 + pos["ret"]); openp.remove(pos); st["closed"] += 1
        if st["bal"] >= GOAL: st["reached"] = True
        if st["bal"] < RESET_AT:
            st["resets"] += 1; st["bal"] = START; openp.clear()
        entered.add(tk["pool"])
        if tk["score"] >= THR and len(openp) < MAX_POS and CANCELLO:
            size = max(2.0, st["bal"] * POS_FRAC)
            if size <= st["bal"]:
                st["bal"] -= size
                openp.append({"pool": tk["pool"], "xt": tk["xt"], "size": round(size, 2), "ret": tk["ret"]})
        st["peak"] = max(st["peak"], st["bal"] + sum(x["size"] for x in openp))
    for pos in [x for x in openp if x["xt"] <= now]:
        st["bal"] += pos["size"] * (1 + pos["ret"]); openp.remove(pos); st["closed"] += 1

    st["open"] = openp; st["entered"] = list(entered)
    equity = st["bal"] + sum(x["size"] for x in openp)
    json.dump(st, open(STATE, "w"))

    days = (now - st["start_ts"]) / 86400
    pct = min(100, equity / GOAL * 100)
    stato_gate = ("🟢 **LIVE APERTO** — " + MOTIVO_CANCELLO if CANCELLO else
                  "🔴 **LIVE SOSPESO** — " + MOTIVO_CANCELLO)
    lines = ["# 🎮 DEMO LIVE — conto vero €100 → €3.000 (BASE)",
             f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · attivo da {days:.1f} giorni · strategia DEDICATA a Base*", "",
             f"## {stato_gate}", "",
             ("> Il conto non apre nuove posizioni finche' il LOOP 1 non supera il cancello (vedi STRATEGIA_LOOP.md).\n"
              "> Non e' un guasto: e' la regola. Prima la percentuale, poi i soldi." if not CANCELLO else ""), "",
             f"## 💰 SALDO: €{equity:.0f}   ({pct:.0f}% verso €3.000)",
             f"- Cassa libera: €{st['bal']:.0f} · {len(openp)} posizioni aperte · picco €{st['peak']:.0f}",
             f"- Trade chiusi: {st['closed']} · reset: {st['resets']}",
             f"- {'🎯 GOAL €3.000 RAGGIUNTO!' if st['reached'] else f'Mancano €{GOAL-equity:.0f}'}", "",
             f"**Selezione:** modello Base walk-forward (loop percentuale), P(win)≥{THR}",
             f"**Strategia BASE (loop #3):** entra +{EH}h · scale-out {TP1:.0f}x/{TP2:.0f}x · trail -{TRAIL*100:.0f}% · hard -{HARD*100:.0f}%",
             "> PURE FORWARD: solo token Base nati DOPO l'apertura. Loop gemello di Robinhood, ma tarato su Base."]
    open("DEMO_LIVE_BASE.md", "w").write("\n".join(lines))
    print(f"DEMO_LIVE_BASE | saldo €{equity:.0f} ({pct:.0f}%) | {len(openp)} aperte | {st['closed']} chiuse | {st['resets']} reset", flush=True)


if __name__ == "__main__":
    main()
