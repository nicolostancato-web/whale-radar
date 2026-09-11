#!/usr/bin/env python3
"""
WALLET_SCORES — track-record VIVO di ogni wallet-balena (dato derivato, ricalcolato ad ogni run).
NON e' accumulo grezzo: legge le whale (chi/quanto/quando) + le candele, e per ogni wallet calcola
com'e' andata dopo i suoi acquisti (24h, e 72h/168h appena le candele lo permettono). Aggrega per wallet
e classifica: DUMB (denaro stupido, perde in modo persistente — segnale validato out-of-sample),
WATCH (candidato smart, da confermare sulla finestra multi-giorno), THIN (troppo pochi acquisti per giudicare).
Scrive data/wallet_scores.json (scoreboard) + stampa un riassunto. Nessuna chiamata esterna, €0.
La classificazione e' DESCRITTIVA: serve a EVITARE il denaro stupido e a tenere d'occhio i possibili smart.
"""
import gzip, json, glob, os, statistics as st
from collections import defaultdict

MIN_BUYS = 4          # sotto questa soglia un wallet non e' giudicabile
WINDOWS = (24, 72, 168)


def load_candles():
    cand = {}
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("tf") == "hour":
                    cand.setdefault(d["pool"], {})[int(d["ts"])] = d["cl"]
        except EOFError:
            pass
    for p in cand:
        cand[p] = dict(sorted(cand[p].items()))
    return cand


def load_whales():
    w = []
    for f in glob.glob("data/raw/whales/backfill_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                try:
                    d = json.loads(l)
                    if d.get("usd") and d.get("wallet") and d.get("ts"):
                        w.append(d)
                except: pass
        except EOFError:
            pass
    return w


def main():
    cand = load_candles()
    whales = [x for x in load_whales() if x["pool"] in cand]
    print(f"whale misurabili (pool con candele): {len(whales)}", flush=True)

    def price_at(p, ts):
        b = None
        for k in cand[p]:
            if k <= ts + 1800: b = k
            else: break
        return cand[p][b] if b is not None and abs(b - ts) <= 6 * 3600 else None

    def ret(x, hours):
        e = price_at(x["pool"], x["ts"]); l = price_at(x["pool"], x["ts"] + hours * 3600)
        return (l / e - 1) if e and l and e > 0 else None

    byw = defaultdict(list)
    for x in whales:
        rets = {f"r{h}": ret(x, h) for h in WINDOWS}
        byw[x["wallet"]].append({"ts": x["ts"], "pool": x["pool"], "name": x.get("name"), "usd": x["usd"], **rets})

    scores = []
    for wallet, buys in byw.items():
        buys.sort(key=lambda b: b["ts"])
        r24 = [b["r24"] for b in buys if b["r24"] is not None]
        rec = {"wallet": wallet, "n_buys": len(buys), "n_meas24": len(r24),
               "usd_tot": sum(b["usd"] for b in buys), "pools": len(set(b["pool"] for b in buys)),
               "first_ts": buys[0]["ts"], "last_ts": buys[-1]["ts"]}
        for h in WINDOWS:
            rs = [b[f"r{h}"] for b in buys if b[f"r{h}"] is not None]
            if rs:
                rec[f"avg{h}"] = round(st.mean(rs), 4); rec[f"med{h}"] = round(st.median(rs), 4)
                rec[f"pos{h}"] = round(sum(1 for r in rs if r > 0) / len(rs), 2); rec[f"n{h}"] = len(rs)
        # classificazione descrittiva (basata sul segnale validato: denaro stupido = perde in modo persistente a 24h)
        if len(r24) < MIN_BUYS:
            rec["tag"] = "thin"
        elif rec.get("avg24", 0) < -0.20 and rec.get("pos24", 1) <= 0.30:
            rec["tag"] = "dumb"        # da EVITARE / fade
        elif rec.get("med24", -1) > 0.05 or rec.get("pos24", 0) >= 0.60:
            rec["tag"] = "watch"       # possibile smart, confermare su multi-giorno
        else:
            rec["tag"] = "neutral"
        scores.append(rec)

    scores.sort(key=lambda r: (r["n_buys"], r["usd_tot"]), reverse=True)
    os.makedirs("data", exist_ok=True)
    json.dump({"updated": int(__import__("time").time()), "n_wallet": len(scores), "wallets": scores},
              open("data/wallet_scores.json", "w"), indent=0)

    from collections import Counter
    tags = Counter(r["tag"] for r in scores)
    print(f"wallet totali: {len(scores)} | {dict(tags)}", flush=True)
    judg = [r for r in scores if r["tag"] != "thin"]
    print(f"--- giudicabili (>= {MIN_BUYS} acquisti misurabili): {len(judg)} ---", flush=True)
    for tag in ("dumb", "watch"):
        sel = [r for r in judg if r["tag"] == tag][:8]
        if sel:
            print(f"  [{tag.upper()}]", flush=True)
            for r in sel:
                print(f"    {r['wallet'][:12]}.. | {r['n_buys']:2} buy | ${r['usd_tot']:>7,} | "
                      f"24h avg {r.get('avg24',0)*100:+5.0f}% pos {r.get('pos24',0)*100:.0f}% | pools {r['pools']}", flush=True)
    print("\n✅ wallet_scores.json aggiornato (scoreboard vivo)", flush=True)


if __name__ == "__main__":
    main()
