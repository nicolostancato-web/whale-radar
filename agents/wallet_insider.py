#!/usr/bin/env python3
"""
WALLET_INSIDER — l'ANGOLO NUOVO per Solana: chi COMPRA PRIMA che il token pompi, ripetutamente.
Le feature classiche (candele+flow+first-buyers) non predicono su pump.fun (-16%): non e' la strategia, e' la
SELEZIONE. Qui cambiamo lente: non guardiamo il token, guardiamo CHI lo compra. Per ogni wallet contiamo in quanti
token e' stato first-buyer (primi minuti) e quanti di quelli sono poi andati bene → score insider.
NO-LOOKAHEAD FEROCE: lo score di un wallet al tempo T usa SOLO token gia' RISOLTI prima di T (e' l'errore che ci ha
illusi su Solana la prima volta: mai piu'). Misura il LIFT onesto (token con insider vs base rate) e scrive INSIDER.md.
Output: data/insider_events.jsonl.gz (storia wallet, append-only) + data/insider_scores.json (consumabile dal brain). €0.
"""
import gzip, json, glob, os, time, sys
sys.path.insert(0, "agents")
import multichain_brain as B

CHAIN = os.environ.get("CHAIN", "solana")
FIRST_MIN = 60        # "first buyer" = compra nella prima ORA di vita (sempre PRIMA dell'entrata a +3h)
RESOLVE_H = 24        # esito del token deciso entro 24h dall'entrata (non a fine storia 168h): lo storico wallet
                      # si popola 7x piu' in fretta E gli insider cambiano wallet troppo spesso per aspettare 7 giorni
MIN_EV = 2            # un wallet conta come ricorrente da 2 apparizioni risolte in su
GOOD = 0.60           # score (win-rate smussato) sopra cui lo chiamiamo insider
MIN_CASI = 40         # sotto questo numero di token-con-insider NON si canta vittoria (e' rumore)
now = int(time.time())


def token_rows(chain):
    """token della chain con candele: entry a +3h (come il brain), esito reale, buy dei primi FIRST_MIN minuti."""
    rows = []
    for f in glob.glob(f"data/multichain/{chain}/candles/*.jsonl.gz"):
        try:
            cs = []
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("cl"): cs.append([int(d["ts"]), d.get("op"), d.get("hi"), d.get("lo"), d["cl"], d.get("vol")])
            cs.sort()
            if len(cs) < B.MIN_CANDLES: continue
            t0 = cs[0][0]; ei = None
            for i, c in enumerate(cs):
                if c[0] >= t0 + B.ENTRY_H * 3600: ei = i; break
            if ei is None or ei == 0: continue
            if sum((c[5] or 0) for c in cs[:ei + 1]) < B.MIN_VOL: continue
            horizon = cs[ei][0] + RESOLVE_H * 3600
            after = [c[4] for c in cs[ei:] if c[0] <= horizon]
            if len(after) < 2: continue
            ret, peak = B.outcome(after)
            addr = os.path.basename(f).replace(".jsonl.gz", "")
            tr = B.load_trades(chain, addr)
            early = {}                                    # wallet -> usd comprati nei primi minuti
            for t in tr:
                if t["kind"] == "buy" and t0 <= t["ts"] <= t0 + FIRST_MIN * 60:
                    early[t["w"]] = early.get(t["w"], 0.0) + t.get("usd", 0.0)
            rows.append({"addr": addr, "t0": t0, "ent": cs[ei][0], "xt": min(horizon, cs[-1][0]),
                         "ret": ret, "peak": peak, "y": 1 if ret > 0 else 0, "early": early})
        except Exception:
            pass
    rows.sort(key=lambda r: r["ent"])
    return rows


def score_of(n, w):
    """win-rate smussato (Laplace): con pochi dati resta vicino a 0.5, non si esalta su 1 colpo fortunato."""
    return (w + 1.0) / (n + 2.0)


def main():
    rows = token_rows(CHAIN)
    if len(rows) < 40:
        print(f"WALLET_INSIDER | solo {len(rows)} token: troppo pochi, si accumula", flush=True); return

    # ---- passata WALK-FORWARD: per ogni token, score dei suoi early-buyer con SOLO il passato risolto ----
    hist = {}                     # wallet -> [n, wins]  (stato aggiornato solo con token gia' risolti)
    pend = []                     # token risolti ma non ancora "assorbiti" (xt <= ent del token corrente)
    pi = 0
    lift_rows = []                # (ha_insider, y, ret) per il test onesto
    resolved = sorted(rows, key=lambda r: r["xt"])
    for r in rows:
        while pi < len(resolved) and resolved[pi]["xt"] < r["ent"]:     # assorbi tutto cio' che si e' chiuso prima
            q = resolved[pi]; pi += 1
            for w in q["early"]:
                h = hist.setdefault(w, [0, 0]); h[0] += 1; h[1] += q["y"]
        ins_usd = 0.0; best = 0.5
        for w, usd in r["early"].items():
            n, wins = hist.get(w, (0, 0))
            if n >= MIN_EV:
                s = score_of(n, wins)
                best = max(best, s)
                if s >= GOOD: ins_usd += usd
        tot_usd = sum(r["early"].values())
        r["insider_frac"] = ins_usd / (tot_usd + 1.0)
        r["insider_max"] = best
        lift_rows.append((1 if r["insider_frac"] > 0 else 0, r["y"], r["ret"]))

    # ---- score FINALI (tutto lo storico) per il consumo live del brain ----
    hist2 = {}
    for r in rows:
        for w in r["early"]:
            h = hist2.setdefault(w, [0, 0]); h[0] += 1; h[1] += r["y"]
    rec = {w: [n, wins, round(score_of(n, wins), 3)] for w, (n, wins) in hist2.items() if n >= MIN_EV}
    os.makedirs("data", exist_ok=True)
    json.dump({"chain": CHAIN, "ts": now, "min_ev": MIN_EV, "good": GOOD, "n_token": len(rows),
               "wallets": rec}, open("data/insider_scores.json", "w"))
    with gzip.open("data/insider_events.jsonl.gz", "wt") as fo:
        for r in rows:
            fo.write(json.dumps({"addr": r["addr"], "xt": r["xt"], "y": r["y"],
                                 "frac": round(r["insider_frac"], 3), "max": round(r["insider_max"], 3)}) + "\n")

    # ---- LIFT ONESTO: i token con almeno un insider vanno meglio della media? ----
    con = [(y, ret) for h, y, ret in lift_rows if h]
    sen = [(y, ret) for h, y, ret in lift_rows if not h]
    def wr(g): return sum(y for y, _ in g) / len(g) * 100 if g else 0.0
    def pf(g): return (sum(1 + r for _, r in g) / len(g) - 1) * 100 if g else 0.0
    base_wr = wr(con + sen); base_pf = pf(con + sen)
    lift = wr(con) - base_wr

    def pvalue(k, n, p):
        """P(almeno k vincenti su n) se il caso decidesse — se e' minuscola, non e' fortuna."""
        if n == 0: return 1.0
        c = 1.0; tot = 0.0
        for i in range(0, n + 1):
            if i: c = c * (n - i + 1) / i
            if i >= k: tot += c * (p ** i) * ((1 - p) ** (n - i))
        return min(1.0, tot)
    k_con = sum(y for y, _ in con)
    pv = pvalue(k_con, len(con), base_wr / 100) if con else 1.0
    ric = len(rec); top = sorted(rec.items(), key=lambda kv: (-kv[1][2], -kv[1][0]))[:15]

    verdetto = ("✅ **SEGNALE VERO**: i token toccati da wallet insider vincono molto di piu' della media, "
                f"e non e' fortuna (p={pv:.4f})"
                if lift > 3 and len(con) >= MIN_CASI and pv < 0.01 else
                f"🟡 **PROMETTENTE**: lift {lift:+.0f}pt su {len(con)} token (p={pv:.3f}) — serve arrivare a "
                f"{MIN_CASI} casi prima di cantare vittoria"
                if lift > 3 and len(con) >= 5 else
                "⏳ **ANCORA NIENTE**: il lift non e' sopra il rumore — si accumula e si stringe la definizione")
    L = [f"# 🕵️ INSIDER — chi compra PRIMA del pump ({CHAIN})",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · walk-forward ONESTO (score dal solo passato risolto)*", "",
         f"## Verdetto: {verdetto}", "",
         "| | token | vinti | media strategia |", "|---|---|---|---|",
         f"| **con insider** (early-buy da wallet ricorrenti vincenti) | {len(con)} | **{wr(con):.0f}%** | {pf(con):+.0f}% |",
         f"| senza insider | {len(sen)} | {wr(sen):.0f}% | {pf(sen):+.0f}% |",
         f"| *tutti (base rate)* | {len(lift_rows)} | *{base_wr:.0f}%* | *{base_pf:+.0f}%* |", "",
         f"**LIFT = {lift:+.1f} punti** di win-rate rispetto alla media · **p = {pv:.4f}** "
         f"(probabilita' di vedere {k_con} vincenti su {len(con)} per puro caso) · casi {len(con)}/{MIN_CASI}", "",
         f"## Wallet ricorrenti trovati: **{ric}** (≥{MIN_EV} apparizioni da first-buyer, su {len(rows)} token)", ""]
    if top:
        L += ["| wallet | apparizioni | vinti | score |", "|---|---|---|---|"]
        L += [f"| `{w[:6]}…{w[-4:]}` | {n} | {wins} | {s:.2f} |" for w, (n, wins, s) in top]
    L += ["", "> **Come si legge**: lo score di un wallet e' il suo win-rate smussato da first-buyer. La feature per un",
          "> token e' la frazione di USD comprata nei primi 30 min da wallet gia' noti come vincenti — calcolata SOLO",
          "> con token chiusi PRIMA, mai col senno di poi. Se il LIFT sale, l'angolo insider e' quello giusto per Solana.",
          "> Prossimo passo se il lift regge: la feature entra nel cervello (multichain_brain) e si ri-misura l'edge."]
    open("INSIDER.md", "w").write("\n".join(L))
    print(f"WALLET_INSIDER | {len(rows)} token | {ric} wallet ricorrenti | con-insider {len(con)} "
          f"| lift {lift:+.1f}pt", flush=True)


if __name__ == "__main__":
    main()
