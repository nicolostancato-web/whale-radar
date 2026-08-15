#!/usr/bin/env python3
"""
PAPER_BOT — paper test IN AVANTI della strategia candidata (validazione onesta, soldi FINTI).
Strategia: compra $10 (finti) su OGNI nuova memecoin ~3h dopo il listing (creazione pool), poi gestisce con
TAKE-PROFIT 5x + TRAILING STOP -60%, netto slippage 30%. Cattura la coda grassa. Solo token RECENTI/nuovi
(non lo storico su cui abbiamo fittato, per non barare). Stato in data/paper_state.json (posizioni aperte),
storico chiuse in data/paper_ledger.jsonl.gz. Scrive PAPER.md. Nessuna chiamata esterna (usa le nostre candele). €0.
"""
import gzip, json, glob, os, time, statistics as st

now = int(time.time())
ENTRY_DELAY_H = 3; TP = 5.0; TRAIL = 0.60; SIZE = 2.0
# COSTI REALI AL 100% (lezione Solana: modellare TUTTO)
ENTRY_SLIP = 0.15      # slippage in entrata (compri, muovi il prezzo su)
EXIT_SLIP = 0.15       # slippage in uscita (vendi, muovi il prezzo giu)
DEX_FEE = 0.01         # fee del pool per lato (~0.3-1%)
GAS_USD = 0.014        # gas per tx (misurato on-chain); round-trip = 2x
LAT_PEN = 0.08         # LATENZA: sull'uscita esegui in ritardo -> prezzo gia' sceso ~8% peggio
CAP = 100.0; MAX_HOLD_D = 30; RECENT_D = 10        # entra solo token nati negli ultimi 10gg (semi-forward, no storico vecchio)
MONEY = {"weth", "eth", "usdg", "usdc", "usdt", "dai", "usdb", "weth9"}
ST = "data/paper_bot_state.json"; LED = "data/paper_bot_ledger.jsonl.gz"


def is_meme(n):
    p = [x.strip().split(" ")[0].lower() for x in (n or "").split("/")]
    return not (len(p) == 2 and p[0] in MONEY and p[1] in MONEY)


def main():
    reg = json.load(open("data/pools.json"))["pools"] if os.path.exists("data/pools.json") else {}
    memepools = {a: reg[a].get("name") for a in reg if len(a) == 42 and is_meme(reg[a].get("name"))}
    cand = {}
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d["tf"] == "hour" and d["pool"] in memepools: cand.setdefault(d["pool"], {})[int(d["ts"])] = d["cl"]
        except: pass
    for p in cand: cand[p] = dict(sorted(cand[p].items()))
    first_ts = {p: min(cand[p]) for p in cand if cand[p]}
    # un pool per token (il piu' vecchio)
    byname = {}
    for p in cand:
        nm = (memepools[p] or "").split(" ")[0]
        if nm not in byname or first_ts[p] < first_ts[byname[nm]]: byname[nm] = p

    def price(p, ts):
        ks = cand[p]; b = None
        for k in ks:
            if k <= ts + 1800: b = k
            else: break
        return ks[b] if b is not None and abs(b - ts) <= 6 * 3600 else None

    state = json.load(open(ST)) if os.path.exists(ST) else {}
    state.setdefault("bot_start", now); state.setdefault("positions", {}); state.setdefault("entered", [])
    entered = set(state["entered"]); positions = state["positions"]

    # ---- ENTRATE: nuove memecoin, eta' >= 3h, nate negli ultimi RECENT_D giorni ----
    new_entries = 0
    max_open = int(CAP / SIZE)
    for nm, p in byname.items():
        if len(positions) >= max_open: break        # capitale pieno: salta (come nel reale)
        if p in entered: continue
        lt = first_ts[p]
        if now - lt < ENTRY_DELAY_H * 3600: continue           # troppo giovane: entrera' al prossimo giro
        if now - lt > RECENT_D * 86400: entered.add(p); continue  # troppo vecchia (storico): salta
        ep = price(p, lt + ENTRY_DELAY_H * 3600)
        if not ep or ep <= 0: continue
        positions[p] = {"name": memepools[p], "entry_price": ep, "entry_ts": lt + ENTRY_DELAY_H * 3600, "size": SIZE, "high": ep}
        entered.add(p); new_entries += 1

    # ---- GESTIONE: TP 5x / trailing -60% / timeout, ri-simulando dalla serie ----
    closed = []
    for p in list(positions.keys()):
        pos = positions[p]
        ser = [(t, v) for t, v in cand.get(p, {}).items() if t >= pos["entry_ts"] and v > 0]
        if not ser: continue
        hi = pos["entry_price"]; exitp = None; reason = None; ex_ts = None
        for t, v in ser:
            hi = max(hi, v)
            if v >= pos["entry_price"] * TP: exitp = pos["entry_price"] * TP; reason = "TP_5x"; ex_ts = t; break   # esci al 5x (ordine reale), non al gap
            if v <= hi * (1 - TRAIL): exitp = v; reason = "trailing"; ex_ts = t; break
        if exitp is None and now - pos["entry_ts"] > MAX_HOLD_D * 86400:
            exitp = ser[-1][1]; reason = "timeout"; ex_ts = ser[-1][0]
        if exitp is not None:
            # entrata: prezzo peggiore per slippage+fee ; uscita: slippage+fee (+ latenza se trailing)
            eff_entry = pos["entry_price"] * (1 + ENTRY_SLIP) * (1 + DEX_FEE)
            lat = LAT_PEN if reason == "trailing" else 0.0
            eff_exit = exitp * (1 - EXIT_SLIP) * (1 - DEX_FEE) * (1 - lat)
            gas_pct = (GAS_USD * 2) / pos["size"]                 # gas fisso come % della size
            ret = eff_exit / eff_entry - 1 - gas_pct
            closed.append({"pool": p, "name": pos["name"], "entry_ts": pos["entry_ts"], "exit_ts": ex_ts,
                           "ret": round(ret, 3), "reason": reason, "size": pos["size"]})
            del positions[p]
        else:
            pos["high"] = hi

    # append chiuse al ledger (immutabile)
    if closed:
        with gzip.open(LED, "at") as fo:
            for c in closed: fo.write(json.dumps(c) + "\n")
    state["positions"] = positions; state["entered"] = list(entered)
    json.dump(state, open(ST, "w"))

    # ---- REPORT: portafoglio paper ----
    led = []
    for f in [LED]:
        if os.path.exists(f):
            for l in gzip.open(f, "rt"):
                try: led.append(json.loads(l))
                except: pass
    n_closed = len(led); n_open = len(positions)
    if led:
        rets = [c["ret"] for c in led]
        invested = sum(c["size"] for c in led)
        final = sum(c["size"] * (1 + c["ret"]) for c in led)
        port = (final / invested - 1) * 100 if invested else 0
        win = sum(1 for r in rets if r > 0) / len(rets) * 100
        x5 = sum(1 for r in rets if r >= 4)
    else:
        port = win = x5 = 0
    days = (now - state["bot_start"]) / 86400
    L = [f"# 🤖 PAPER BOT — strategia coda grassa (soldi FINTI)",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · attivo da {days:.1f} giorni*", "",
         f"**Strategia:** compra ${SIZE:.0f} su ogni memecoin +{ENTRY_DELAY_H}h dal listing · TP {TP:.0f}x · trailing -{TRAIL*100:.0f}% · slippage {SLIP*100:.0f}%", "",
         f"## Portafoglio (chiuse)",
         f"- Trade chiusi: **{n_closed}** | aperti: **{n_open}**",
         f"- **Rendimento portafoglio: {port:+.1f}%**",
         f"- Vinti: {win:.0f}% | trade 5x+: {x5}",
         f"- (+{new_entries} nuove entrate questo giro)", "",
         "> Coda grassa: si perde sulla maggioranza, i pochi mostri pagano. Serve TEMPO (settimane) per giudicare.",
         "> Se dopo 2-4 settimane il portafoglio e' positivo su tanti token diversi -> edge reale -> size vera piccola."]
    open("PAPER.md", "w").write("\n".join(L))
    print(f"PAPER | chiuse {n_closed} aperte {n_open} | port {port:+.1f}% | +{new_entries} entrate", flush=True)


if __name__ == "__main__":
    main()
