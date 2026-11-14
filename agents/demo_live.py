#!/usr/bin/env python3
"""
DEMO_LIVE — conto demo-live PERSISTENTE su Robinhood: parte €100, GOAL €3.000. Non e' un backtest ricalcolato
ogni volta: mantiene un SALDO vero in data/demo_live_state.json che vive in avanti. Ogni giro processa i token
NUOVI (che si sono "listati" da quando abbiamo controllato), apre/chiude posizioni con l'allocazione imparata
(10% del saldo per posizione, max 10 — la migliore dal replay), 100% REALISTICO (slippage+fee+gas+LATENZA
pessimista), e RESET a €100 se il budget si brucia sotto €25 (non gratta coi spiccioli). Traccia il saldo nel
tempo. Scrive DEMO_LIVE.md con il conto vero + progresso verso €3.000. €0.
"""
import gzip, json, os, time, sys
import gate
sys.path.insert(0, "agents")
import learner as L

now = int(time.time())
START = 100.0; GOAL = 3000.0; RESET_AT = 25.0
POS_FRAC = 0.10; MAX_POS = 10; THR = 0.30      # allocazione imparata: 10% del saldo, max 10 posizioni
ES = XS = 0.15; FEE = 0.01; GAS = 0.014; LAT_ENTRY = 0.06; LAT_EXIT = 0.06
S = json.load(open("data/strategy.json")) if os.path.exists("data/strategy.json") else {}
TP1 = S.get("tp1", 3.0); TP2 = S.get("tp2", 6.0); TRAIL = S.get("trail", 0.50); HARD = S.get("hard", 0.70); EH = S.get("entry_h", 3)
STATE = "data/demo_live_state.json"


def net_ret(path, size):
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


def build_tokens():
    reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    cand, flow, fbp, wl, fts = L.load_data()
    mp = {a: reg[a].get("name") for a in reg if len(a) == 42 and L._is_meme(reg[a].get("name"))}
    cand = {p: c for p, c in cand.items() if p in mp}
    fts2 = {p: min(cand[p]) for p in cand if cand[p]}
    byname = {}
    for p in cand:
        nm = (mp[p] or "").split(" ")[0]
        if nm not in byname or fts2[p] < fts2[byname[nm]]: byname[nm] = p
    model = json.load(open("data/selection_model.json")) if os.path.exists("data/selection_model.json") else {}
    toks = []
    for nm, p in byname.items():
        lt = fts2[p]; base = lt + EH * 3600; fl = flow.get(p, {}); ent = ep = None
        for t in sorted(cand[p]):
            if t < base: continue
            past = [v for h, v in fl.items() if h <= t]
            if len(past) >= 4 and sum(v[0] + v[1] for v in past) >= 3000 and sum(v[1] for v in past) / (sum(v[0] for v in past) + 1) >= 0.15:
                ent, ep = t, cand[p][t]; break
        if ent is None or not ep: continue
        path = [cand[p][t] for t in sorted(cand[p]) if t >= ent and cand[p][t] > 0]
        if len(path) < 2: continue
        score = 0.5
        if model.get("active"):
            f = L.features_at_entry(p, ent, cand, flow, fbp, wl, fts2)
            if f: score = L.sigmoid(sum(model["w"][j] * (f[j] - model["mu"][j]) / model["sd"][j] for j in range(len(f))) + model["b"])
        toks.append({"pool": p, "name": (mp[p] or "?"), "ent": ent, "xt": sorted(cand[p])[-1],
                     "ret": net_ret(path, max(2.0, START * POS_FRAC)), "score": score})
    toks.sort(key=lambda t: t["ent"])
    return toks


CANCELLO, MOTIVO_CANCELLO = gate.aperto("robinhood")


def main():
    toks = build_tokens()
    st = json.load(open(STATE)) if os.path.exists(STATE) else None
    if st is None:
        st = {"bal": START, "open": [], "entered": [], "resets": 0, "closed": 0,
              "peak": START, "start_ts": now, "reached": False}
    entered = set(st["entered"]); openp = st["open"]

    # PURE FORWARD: entra SOLO su token listati DOPO l'apertura del conto (niente recupero storico = niente illusione).
    newp = [t for t in toks if t["pool"] not in entered and t["ent"] >= st["start_ts"]]
    newp.sort(key=lambda t: t["ent"])
    for tk in newp:
        # chiudi le posizioni scadute prima di questo ingresso
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
                openp.append({"pool": tk["pool"], "name": tk["name"][:20], "xt": tk["xt"], "size": round(size, 2), "ret": tk["ret"]})
        st["peak"] = max(st["peak"], st["bal"] + sum(x["size"] for x in openp))
    # chiudi le posizioni ormai scadute (exit passato)
    for pos in [x for x in openp if x["xt"] <= now]:
        st["bal"] += pos["size"] * (1 + pos["ret"]); openp.remove(pos); st["closed"] += 1

    st["open"] = openp; st["entered"] = list(entered)
    equity = st["bal"] + sum(x["size"] for x in openp)
    json.dump(st, open(STATE, "w"))

    days = (now - st["start_ts"]) / 86400
    pct = min(100, equity / GOAL * 100)
    stato_gate = ("🟢 **LIVE APERTO** — " + MOTIVO_CANCELLO if CANCELLO else
                  "🔴 **LIVE SOSPESO** — " + MOTIVO_CANCELLO)
    L2 = ["# 🎮 DEMO LIVE — conto vero €100 → €3.000 (Robinhood)",
          f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · attivo da {days:.1f} giorni · 100% realistico (costi+gas+LATENZA)*", "",
          f"## {stato_gate}", "",
          ("> Il conto non apre nuove posizioni finche' il LOOP 1 non supera il cancello (vedi STRATEGIA_LOOP.md).\n"
           "> Non e' un guasto: e' la regola. Prima la percentuale, poi i soldi." if not CANCELLO else ""), "",
          f"## 💰 SALDO: €{equity:.0f}   ({pct:.0f}% verso €3.000)",
          f"- Cassa libera: €{st['bal']:.0f} · in {len(openp)} posizioni aperte · picco €{st['peak']:.0f}",
          f"- Trade chiusi: {st['closed']} · reset (budget bruciato): {st['resets']}",
          f"- {'🎯 GOAL €3.000 RAGGIUNTO!' if st['reached'] else f'Mancano €{GOAL-equity:.0f} al goal'}", "",
          f"**Allocazione:** 10% del saldo per posizione, max 10 (la migliore dal replay) · uscita +{EH}h TP {TP1:.0f}x/{TP2:.0f}x trail-{TRAIL*100:.0f}%",
          f"**Latenza modellata:** +{int(LAT_ENTRY*100)}% entrata / +{int(LAT_EXIT*100)}% uscita (oltre slippage) — l'errore Solana non si ripete", ""]
    if openp:
        L2 += ["## Posizioni aperte ora", "| token | size | rendimento atteso |", "|---|---|---|"]
        for x in sorted(openp, key=lambda z: -z["ret"])[:10]:
            L2.append(f"| {x['name']} | €{x['size']:.1f} | {x['ret']*100:+.0f}% |")
    L2 += ["", "> **PURE FORWARD**: entra SOLO su token nati DOPO l'apertura del conto = 100% reale, NIENTE storico (no illusione).",
           "> Parte lento (Robinhood ha pochi token nuovi/giorno) ma ogni euro e' guadagnato in avanti davvero.",
           "> €3.000 richiede mesi. Reset a €100 se scende sotto €25 (impariamo, non grattiamo coi spiccioli)."]
    open("DEMO_LIVE.md", "w").write("\n".join(L2))
    print(f"DEMO_LIVE | saldo €{equity:.0f} ({pct:.0f}% goal) | {len(openp)} aperte | {st['closed']} chiuse | {st['resets']} reset", flush=True)


if __name__ == "__main__":
    main()
