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
ENTRY_H = 3; MIN_CANDLES = 5; MIN_VOL = 500  # basso: esclude solo i pool morti, TIENE i mostri che partono quieti
WARMUP = 40; THR = 0.40
FEAT = ["dump_depth", "log_vol", "buy_pressure", "volatilita", "log_vol_accel", "frac_verdi",
        "sell_ratio", "log_buyusd", "log_nfirstbuyers", "buy_accel"]


def load_trades(chain, addr):
    tf = f"data/multichain/{chain}/trades/{addr}.jsonl.gz"
    if not os.path.exists(tf): return []
    out = []
    try:
        for l in gzip.open(tf, "rt"):
            r = json.loads(l)
            if r.get("ts"): out.append(r)
    except: pass
    out.sort(key=lambda r: r["ts"]); return out


def _ritardo():
    """il ritardo con cui i dati arrivano DA NOI (misurato: 3-7 ore, vedi agents/disponibilita.py).

    Aggiunto il 04/09. Le feature erano gia' oneste sul passato — verificato ricalcolandole senza i
    dati futuri, e vengono identiche. Ma essere oneste non basta: un bot vero non puo' decidere su
    dati che non ha ancora scaricato. Senza questo taglio entriamo all'ora giusta con informazioni
    che a quell'ora non avevamo.
    Nel dubbio si usa il ritardo PEGGIORE fra le chain: sbagliare per prudenza costa occasioni perse,
    sbagliare per ottimismo costa soldi."""
    import os as _o, json as _j
    f = _o.environ.get("RITARDO")
    if f is not None:
        try: return max(0, int(float(f)))
        except Exception: pass
    try:
        d = _j.load(open("data/ritardo_reale.json")).get("ritardi") or {}
        v = [x.get("tipico_s") for x in d.values() if x.get("tipico_s")]
        return max(v) if v else 0
    except Exception:
        return 0


RITARDO_OSS = _ritardo()


def trade_features(trades, entry_ts):
    """feature no-lookahead dai trade fino all'entrata, E arrivate davvero fino a noi."""
    pre = [t for t in trades if t["ts"] <= entry_ts - RITARDO_OSS]
    if not pre: return [0.5, 0.0, 0.0, 1.0]   # neutro se non abbiamo ancora i trade
    buy = sum(t["usd"] for t in pre if t["kind"] == "buy")
    sell = sum(t["usd"] for t in pre if t["kind"] == "sell")
    sell_ratio = sell / (buy + 1)
    nfb = len(set(t["w"] for t in pre if t["kind"] == "buy"))
    # accelerazione buy: ultimo 30% dei trade vs il resto
    k = max(1, len(pre) // 3); last = pre[-k:]; rest = pre[:-k]
    lb = sum(t["usd"] for t in last if t["kind"] == "buy") / max(1, len(last))
    rb = sum(t["usd"] for t in rest if t["kind"] == "buy") / max(1, len(rest)) if rest else lb
    accel = lb / (rb + 1)
    return [sell_ratio, math.log10(buy + 1), math.log10(nfb + 1), math.log10(accel + 0.01)]


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


SIZE_RIF = 10.0     # euro per posizione: serve a stimare l'impatto di mercato


def outcome(after, minimi=None, impatto=0.0):
    """uscita scale-out 3x/6x/trailing, dai prezzi dopo l'entrata.

    ULTIMO METRO ALLINEATO (01/09). Le correzioni sui costi — rug intrabar e impatto di mercato — erano
    entrate in chi CERCA (explorer) ma non in chi produce il NUMERO UFFICIALE per base/solana/bsc, che e'
    questo file. Base risultava -11% qui e -26% nella ricerca. E il cancello del live guarda il numero
    ufficiale: si sarebbe aperto su quindici punti di illusione."""
    ep = after[0]; hi = ep; legs = []; h1 = h2 = False; pk = max(after) / ep if after else 1

    def netto(mult, tr=False):
        ein = (1 + L.ES) * (1 + L.FEE)
        uscita = min(0.60, L.XS + impatto)
        eout = mult * (1 - uscita) * (1 - L.FEE) * (1 - L.LAT * (2 if tr else 1))
        return eout / ein - 1 - (L.GAS * 2) / SIZE_RIF

    for i, v in enumerate(after):
        if v <= 0: continue
        hi = max(hi, v); m = v / ep
        basso = (minimi[i] if minimi and i < len(minimi) and minimi[i] else v)
        if not h1 and m >= 3: legs.append(netto(3)); h1 = True
        if not h2 and m >= 6: legs.append(netto(6)); h2 = True
        if not h1:
            if basso <= ep * 0.3: legs.append(netto(min(basso, ep * 0.3) / ep)); break
        elif basso <= hi * 0.5: legs.append(netto(min(basso, hi * 0.5) / ep, True)); break
    while len(legs) < 3: legs.append(legs[-1] if legs else netto(after[-1] / ep if after else 1, True))
    return sum(legs[:3]) / 3, pk


def serie_files(chain):
    """i file-serie della chain: le candele scaricate + il PULSE dei token giovani (che il collector OHLCV non
    riesce a coprire: free tier saturo). Il pulse ha lo stesso formato, quindi entra qui senza altre modifiche."""
    fs = glob.glob(f"data/multichain/{chain}/candles/*.jsonl.gz")
    have = {os.path.basename(f) for f in fs}
    fs += [f for f in glob.glob(f"data/multichain/{chain}/pulse/*.jsonl.gz") if os.path.basename(f) not in have]
    return fs


def load_rows(chain):
    rows = []
    for f in serie_files(chain):
        try:
            cs = []; nato = None
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("t0"): nato = int(d["t0"])            # nascita vera (righe del pulse)
                if d.get("cl"): cs.append([int(d["ts"]), d.get("op"), d.get("hi"), d.get("lo"), d["cl"], d.get("vol")])
            cs.sort()
            if len(cs) < MIN_CANDLES: continue
            t0 = nato or cs[0][0]; ei = None
            if cs[0][0] > t0 + ENTRY_H * 3600: continue   # preso troppo tardi: la finestra d'entrata e' persa
            for i, c in enumerate(cs):
                if c[0] >= t0 + ENTRY_H * 3600: ei = i; break
            if ei is None or ei == 0: continue
            pre = cs[:ei + 1]
            if sum((c[5] or 0) for c in pre) < MIN_VOL: continue          # filtro junk (volume candele)
            dopo = cs[ei:]
            after = [c[4] for c in dopo]
            minimi = [(c[3] if c[3] else c[4]) for c in dopo]        # minimo candela: rug intrabar
            vols = [(c[5] or 0) for c in pre if c[5]]
            vol_ora = (sum(vols) / len(vols)) if vols else 0.0
            impatto = min(0.45, SIZE_RIF / (vol_ora + 1.0))          # impatto di mercato sui pool sottili
            r, pk = outcome(after, minimi, impatto)
            entry_ts = cs[ei][0]
            addr = os.path.basename(f).replace(".jsonl.gz", "")
            feats = features(pre) + trade_features(load_trades(chain, addr), entry_ts)   # candele + FLOW/first-buyers
            rows.append({"ent": entry_ts, "xt": cs[-1][0], "f": feats, "ret": r, "peak": pk})
        except: pass
    rows.sort(key=lambda r: r["ent"])
    return rows


def walkforward(rows, thr=THR):
    sel = []; model = None; last_n = 0
    for i, r in enumerate(rows):
        train = [q for q in rows[:i] if q["xt"] < r["ent"]]
        if len(train) < WARMUP: sel.append(r["ret"]); continue
        if model is None or len(train) - last_n >= 10:   # ri-allena ogni 10 token (veloce, non cambia molto)
            y = [1 if q["ret"] > 0 else 0 for q in train]
            if len(set(y)) >= 2:
                model = L.fit_logreg([q["f"] for q in train], y, iters=800); last_n = len(train)
        if model is None: sel.append(r["ret"]); continue
        w, b, mu, sd = model
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
             f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · walk-forward onesto (no-lookahead) · candele + FLOW + first-buyers*", "",
             "## 📊 MEDIA STRATEGIA per chain (quanto rende in media per token)",
             "| chain | token analizzati | con trade | **MEDIA** | senza top3 | compra-tutto | vinti | mostri 6x+ |",
             "|---|---|---|---|---|---|---|---|"]
    # Robinhood: usiamo i dati COMPLETI (edge_eval, pipeline RPC ricco) — non il multichain a meta'
    rh = None
    if os.path.exists("data/edge_history.jsonl"):
        try:
            recs = [json.loads(l) for l in open("data/edge_history.jsonl") if l.strip()]
            if recs: rh = recs[-1]
        except: pass
    for ch in CHAINS:
        if ch == "robinhood" and rh:
            a = "✅" if rh.get("sel_no3", 0) >= 0 else "⚠️"
            lines.append(f"| **robinhood** *(dati completi)* | {rh['n_tok']} | ✓ pieni | **{rh['sel_port']:+.0f}%** | {a} {rh.get('sel_no3',0):+.0f}% | {rh['base_port']:+.0f}% | {rh['sel_win']:.0f}% | — |")
            continue
        rows = per[ch]
        ntr = len(glob.glob(f"data/multichain/{ch}/trades/*.jsonl.gz"))
        mon = sum(1 for r in rows if r["peak"] >= 6)
        cov = ntr / max(1, len(rows))
        if len(rows) < 20:
            lines.append(f"| {ch} | {len(rows)} | {ntr} | (pochi dati) | | | | |"); continue
        if cov < 0.6:   # dati flow ancora a meta': non mostro un numero fasullo, mostro il progresso
            lines.append(f"| **{ch}** | {len(rows)} | {ntr} | ⏳ **in riempimento ({cov*100:.0f}%)** | attendi | | | {mon} |"); continue
        base = [r["ret"] for r in rows]; sel = walkforward(rows)
        no3 = port(sorted(sel, reverse=True)[3:]) if len(sel) > 5 else 0.0
        aff = "✅" if no3 >= 0 else "⚠️"
        lines.append(f"| **{ch}** | {len(rows)} | {ntr} | **{port(sel):+.0f}%** | {aff} {no3:+.0f}% | {port(base):+.0f}% | {win(sel):.0f}% | {mon} |")
        # storico per chain: e' la misura che il loop "percentuale" guarda per capire se l'ago si muove
        with open("data/multichain_history.jsonl", "a") as fo:
            fo.write(json.dumps({"ts": now, "chain": ch, "media": round(port(sel), 1),
                                 "robusta": round(no3, 1), "n": len(rows), "vinti": round(win(sel), 1)}) + "\n")
    lines += ["", "> **robinhood** = pipeline maturo (dati completi, il numero VERO). solana/bsc/base = nuovo pipeline **in riempimento** (colonna 'con trade' ancora a meta') → i loro numeri saliranno."]
    # combinato (allena su tutte le chain insieme)
    total_tr = sum(len(glob.glob(f"data/multichain/{ch}/trades/*.jsonl.gz")) for ch in CHAINS if ch != "robinhood")
    total_tok = sum(len(per[ch]) for ch in CHAINS if ch != "robinhood")
    ocov = total_tr / max(1, total_tok)
    newchains = [r for ch in CHAINS if ch != "robinhood" for r in per[ch]]
    if len(newchains) >= 40 and ocov >= 0.6:
        base = [r["ret"] for r in newchains]; sel = walkforward(newchains)
        no3 = port(sorted(sel, reverse=True)[3:]) if len(sel) > 5 else 0.0
        aff = (f"✅ AFFIDABILE (senza i 3 mostri top: {no3:+.0f}%)" if no3 >= 0
               else f"⚠️ INSTABILE (senza i 3 mostri top: {no3:+.0f}%)")
        lines += ["", f"## Nuove chain combinate ({len(newchains)} token: solana+bsc+base)",
                  f"- **MEDIA STRATEGIA: {port(sel):+.0f}%** per token (su €100 → €{100*(1+port(sel)/100):.0f}) · vinti {win(sel):.0f}%",
                  f"- {aff}"]
    else:
        lines += ["", f"## Nuove chain (solana+bsc+base) — ⏳ in riempimento ({ocov*100:.0f}% dei token ha i trade)",
                  "> I numeri multichain diventano validi sopra il 60% di copertura trade. Ora si accumula (€0, ogni ora)."]
    lines += ["", "> Ora usa candele + FLOW (buy/sell) + first-buyers dai trade GeckoTerminal. Le feature forti si riempiono man mano che il trades collector accumula.",
              "> GOAL: edge robusto su abbastanza token. Si spinge in loop, si accumula, si aggiungono feature."]
    open("MULTICHAIN.md", "w").write("\n".join(lines))
    tot = sum(len(per[c]) for c in CHAINS)
    print(f"MULTICHAIN_BRAIN | {tot} token su {len(CHAINS)} chain | " +
          " ".join(f"{c}:{len(per[c])}" for c in CHAINS), flush=True)


if __name__ == "__main__":
    main()
