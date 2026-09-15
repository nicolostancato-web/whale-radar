#!/usr/bin/env python3
"""
PAPER_BOT v2 — paper test IN AVANTI col CERVELLO DEL TRADER (soldi FINTI, costi reali al 100%).
Vedi TRADER.md. Impara nel tempo dalle uscite. Rispetto a v1 (compra-tutto ingenuo):
  1. FILTRO TRADEABILITA pre-entrata (no-lookahead, dai dati flow): scarta honeypot / spike da minuti /
     pool morti. Un "5x" che non puoi vendere vale -100%, non lo contiamo.
  2. USCITA A SCAGLIONI invece del TP-5x-unico: 1/3 a 2x, 1/3 a 3.5x, 1/3 a 5x/trailing/timeout.
     Blocca profitto finche' c'e' liquidita', non regala il picco.
  3. LEDGER ricco per imparare (ore flow, volume, sell-ratio, gambe di uscita).
Costi modellati: slippage entrata+uscita, fee DEX x2, gas x2, latenza sulle uscite trailing. €0, cloud.
"""
import gzip, json, glob, os, time, statistics as st

now = int(time.time())
ENTRY_DELAY_H = 3; RECENT_D = 10; MAX_HOLD_D = 30
CAP = 100.0; SIZE = 2.0
# --- costi REALI al 100% ---
ENTRY_SLIP = 0.15; EXIT_SLIP = 0.15; DEX_FEE = 0.01; GAS_USD = 0.014; LAT_PEN = 0.08
# --- filtro tradeabilita (no-lookahead) ---
MIN_HOURS = 4          # ore di flow reale prima di fidarsi (uccide gli spike da minuti)
MIN_VOL = 3000         # volume USD minimo accumulato (uccide i pool morti)
MIN_SELLRATIO = 0.15   # sellUSD/buyUSD minimo (uccide gli honeypot: se nessuno vende, non entri)
# --- uscita a scaglioni ---
L1, L2 = 3.0, 6.0; TRAIL = 0.50; HARD_STOP = 0.70
MONEY = {"weth", "eth", "usdg", "usdc", "usdt", "dai", "usdb", "weth9"}
ST = "data/paper_bot_state.json"; LED = "data/paper_bot_ledger.jsonl.gz"
MODEL = "data/selection_model.json"   # scritto dal learner: quando 'active', seleziona le entrate


import sys
sys.path.insert(0, "agents")
import learner  # una sola definizione delle feature (no drift tra learner e bot)


def _sig(z):
    import math; return 1 / (1 + math.exp(-max(-30, min(30, z))))


def load_model():
    import os, json
    if not os.path.exists(MODEL): return None
    m = json.load(open(MODEL))
    return m if m.get("active") else None


def score_model(m, feats):
    z = sum(m["w"][j] * (feats[j] - m["mu"][j]) / m["sd"][j] for j in range(len(feats))) + m["b"]
    return _sig(z)


def is_meme(n):
    p = [x.strip().split(" ")[0].lower() for x in (n or "").split("/")]
    return not (len(p) == 2 and p[0] in MONEY and p[1] in MONEY)


def net(mult, trailing=False):
    """rendimento netto di una gamba a 'mult'x, con tutti i costi reali. mult NON dipende dal prezzo."""
    ein = (1 + ENTRY_SLIP) * (1 + DEX_FEE)
    eout = mult * (1 - EXIT_SLIP) * (1 - DEX_FEE) * (1 - (LAT_PEN if trailing else 0.0))
    return eout / ein - 1 - (GAS_USD * 2) / SIZE


def main():
    reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    memepools = {a: reg[a].get("name") for a in reg if len(a) == 42 and is_meme(reg[a].get("name"))}
    cand = {}
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d["tf"] == "hour" and d["pool"] in memepools and d.get("cl"):
                    cand.setdefault(d["pool"], {})[int(d["ts"])] = d["cl"]
        except: pass
    for p in cand: cand[p] = dict(sorted(cand[p].items()))
    flow = {}
    for f in glob.glob("data/raw/flow/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d["pool"] in cand:
                    flow.setdefault(d["pool"], {})[int(d["hour"])] = (d["buyusd"], d["sellusd"])
        except: pass
    first_ts = {p: min(cand[p]) for p in cand if cand[p]}
    # first-buyers per lo scoring smart-money (usati solo se il modello e' attivo)
    fb_pool = {}
    for f in glob.glob("data/raw/firstbuyers/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l); fb_pool.setdefault(d["pool"], []).append((d["wallet"], int(d["ts"])))
        except: pass
    wallet_listings = {}
    for pp, lst in fb_pool.items():
        lt = first_ts.get(pp, min((t for _, t in lst), default=0))
        for wlt, _ in lst: wallet_listings.setdefault(wlt, []).append(lt)
    byname = {}
    for p in cand:
        nm = (memepools[p] or "").split(" ")[0]
        if nm not in byname or first_ts[p] < first_ts[byname[nm]]: byname[nm] = p

    state = json.load(open(ST)) if os.path.exists(ST) else {}
    state.setdefault("bot_start", now); state.setdefault("positions", {})
    state.setdefault("entered", []); state.setdefault("rejected", {})
    entered = set(state["entered"]); positions = state["positions"]; rejected = state["rejected"]

    # ---- ENTRATE: filtro tradeabilita (no-lookahead) + SELEZIONE del learner (se ha imparato) ----
    import math
    model = load_model()   # None finche' il learner non ha un segnale affidabile (AUC>=0.60)
    n_selskip = 0
    new_entries = 0; max_open = int(CAP / SIZE)
    for nm, p in byname.items():
        if len(positions) >= max_open: break
        if p in entered or p in positions: continue
        lt = first_ts[p]
        if now - lt < ENTRY_DELAY_H * 3600: continue
        if now - lt > RECENT_D * 86400:
            entered.add(p); continue
        fl = flow.get(p, {}); base = lt + ENTRY_DELAY_H * 3600
        ent = ep = None; einfo = None
        for t in sorted(cand[p]):
            if t < base: continue
            past = [v for h, v in fl.items() if h <= t]
            hrs = len(past); bu = sum(v[0] for v in past); su = sum(v[1] for v in past)
            if hrs >= MIN_HOURS and (bu + su) >= MIN_VOL and su / (bu + 1) >= MIN_SELLRATIO:
                # SELEZIONE appresa: se il modello e' attivo, entra solo se predice alta P(vincita)
                if model is not None:
                    feats = learner.features_at_entry(p, t, cand, flow, fb_pool, wallet_listings, first_ts)
                    if feats is None or score_model(model, feats) < model.get("thr", 0.5):
                        n_selskip += 1; entered.add(p); ent = None; break
                ent, ep, einfo = t, cand[p][t], (hrs, round(bu), round(su)); break
        if ent is None:
            past = list(fl.values()); rejected[p] = {"name": memepools[p], "hrs": len(fl),
                "vol": round(sum(v[0] + v[1] for v in past))}; entered.add(p); continue
        positions[p] = {"name": memepools[p], "entry_price": ep, "entry_ts": ent,
                        "listing_ts": lt, "size": SIZE, "hrs": einfo[0], "buyusd": einfo[1], "sellusd": einfo[2]}
        entered.add(p); new_entries += 1

    # ---- GESTIONE: uscita a scaglioni, ri-simulando la serie dall'entrata ----
    closed = []
    for p in list(positions.keys()):
        pos = positions[p]; ep = pos["entry_price"]
        ser = [(t, v) for t, v in cand.get(p, {}).items() if t >= pos["entry_ts"] and v > 0]
        if not ser: continue
        # 1/3 a 2x (lock), 1/3 a 3.5x (lock), 1/3 CAVALCA il trailing senza tetto (becca i mostri).
        # PRIMA del primo lock: solo hard-stop -70% (do spazio al moonshot, non mi faccio buttare fuori dalla volatilita').
        hi = ep; legs = []; ex_ts = None; done = False; h2 = h35 = False
        for t, v in ser:
            hi = max(hi, v); m = v / ep
            if not h2 and m >= L1: legs.append(("3x", net(L1))); h2 = True
            if not h35 and m >= L2: legs.append(("6x", net(L2))); h35 = True
            if not h2:                          # pre-lock: solo hard stop, lascio respirare
                if v <= ep * (1 - HARD_STOP):
                    legs.append(("stop", net(m))); ex_ts = t; done = True; break
            elif v <= hi * (1 - TRAIL):         # post-lock: trailing dal picco (no tetto, becca i mostri)
                mexit = hi * (1 - TRAIL) / ep
                legs.append((f"trail@{m:.0f}x", net(mexit, trailing=True))); ex_ts = t; done = True; break
        if not done and now - pos["entry_ts"] > MAX_HOLD_D * 86400:
            legs.append(("timeout", net(ser[-1][1] / ep, trailing=True))); ex_ts = ser[-1][0]; done = True
        if done:
            # MISURA IL COSTO DI FUGA ADESSO (04/09). E' l'unico dato che non si recupera dopo: il
            # prezzo che conta e' quello che avresti pagato MENTRE il pool si svuotava, e quel momento
            # dura pochi secondi. Finora tutte le nostre quote erano prese a mercato calmo, cioe' nel
            # momento sbagliato, e il moltiplicatore x3 era un'ipotesi su cosa succede in quello giusto.
            # Solo sulle uscite forzate (stop/trailing): quando esci a target il mercato e' un altro.
            try:
                tipo = legs[-1][0]
                if ("stop" in tipo or "trail" in tipo) and pos.get("mint"):
                    import subprocess as _sp
                    _sp.Popen(["python", "agents/costo_fuga.py"],
                              env={**os.environ, "MINT": pos["mint"], "MOTIVO": tipo},
                              stdout=_sp.DEVNULL, stderr=_sp.DEVNULL, start_new_session=True)
            except Exception: pass
            last = legs[-1][1]
            while len(legs) < 3: legs.insert(len(legs) - 1, ("resto", last))
            ret = sum(x[1] for x in legs[:3]) / 3
            closed.append({"pool": p, "name": pos["name"], "entry_ts": pos["entry_ts"],
                           "exit_ts": ex_ts, "ret": round(ret, 3), "legs": [x[0] for x in legs[:3]],
                           "size": pos["size"], "hrs": pos["hrs"], "buyusd": pos["buyusd"], "sellusd": pos["sellusd"],
                           "peak_mult": round(max(v for _, v in ser) / ep, 1)})
            del positions[p]

    if closed:
        with gzip.open(LED, "at") as fo:
            for c in closed: fo.write(json.dumps(c) + "\n")
    state["positions"] = positions; state["entered"] = list(entered); state["rejected"] = rejected
    json.dump(state, open(ST, "w"))

    # ---- REPORT ----
    led = []
    if os.path.exists(LED):
        for l in gzip.open(LED, "rt"):
            try: led.append(json.loads(l))
            except: pass
    n_closed = len(led); n_open = len(positions); n_rej = len(rejected)
    if led:
        rets = [c["ret"] for c in led]
        final = sum(c["size"] * (1 + c["ret"]) for c in led); inv = sum(c["size"] for c in led)
        port = (final / inv - 1) * 100 if inv else 0
        win = sum(1 for r in rets if r > 0) / len(rets) * 100
        med = st.median(rets) * 100; big = sum(1 for r in rets if r >= 3)
    else:
        port = win = med = big = 0
    days = (now - state["bot_start"]) / 86400
    top = sorted(led, key=lambda c: -c["ret"])[:6]
    L = [f"# 🤖 PAPER BOT v2 — cervello del trader (soldi FINTI)",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · attivo da {days:.1f} giorni · vedi TRADER.md*", "",
         f"**Filtro tradeabilita:** ≥{MIN_HOURS}h flow · ≥${MIN_VOL} volume · sell/buy ≥{MIN_SELLRATIO} (anti honeypot/spike)",
         f"**Uscita a scaglioni:** 1/3 a {L1}x · 1/3 a {L2}x · 1/3 cavalca trailing -{int(TRAIL*100)}% (hard-stop -{int(HARD_STOP*100)}% pre-lock)",
         f"**Costi reali:** slippage {int(ENTRY_SLIP*100)}%+{int(EXIT_SLIP*100)}% · fee {int(DEX_FEE*100)}%×2 · gas ${GAS_USD*2:.3f} · latenza {int(LAT_PEN*100)}%", "",
         f"## Portafoglio (solo token tradeabili)",
         f"- Chiusi: **{n_closed}** | aperti: **{n_open}** | **scartati dal filtro: {n_rej}**",
         f"- **Rendimento portafoglio: {port:+.1f}%** (equal-weight per token)",
         f"- Mediana per-token: {med:+.0f}% | vinti: {win:.0f}% | trade ≥3x: {big}",
         f"- (+{new_entries} nuove entrate questo giro)", "",
         "## Top uscite (per imparare)"]
    for c in top:
        L.append(f"- **{c['name']}** {c['ret']*100:+.0f}% · gambe {'/'.join(c['legs'])} · picco {c.get('peak_mult','?')}x · vol ${c['buyusd']+c['sellusd']}")
    L += ["", "> Coda grassa su token VERI: si perde sulla maggioranza, i pochi mostri vendibili pagano.",
          "> Verdetto onesto in 2-4 settimane sui trade FORWARD. Ogni uscita aggiorna TRADER.md."]
    open("PAPER.md", "w").write("\n".join(L))
    print(f"PAPER v2 | chiuse {n_closed} aperte {n_open} scartate {n_rej} | port {port:+.1f}% | +{new_entries}", flush=True)


if __name__ == "__main__":
    main()
