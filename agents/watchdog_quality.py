#!/usr/bin/env python3
"""
WATCHDOG_QUALITY — controlla che l'accumulo sia SANO e scrive HEALTH.md (verde/rosso).
Verifica: integrita' (nessun file corrotto), freschezza (i reparti hanno scritto di recente),
crescita (vs snapshot precedente), copertura utile (token con whale+candele). Se qualcosa e' rotto
esce con codice 1 -> GitHub manda una mail al proprietario (alert automatico, PC spento). €0.
"""
import gzip, json, glob, os, re, time

now = int(time.time())
SNAP = "data/health_snapshot.json"
STALE_H = 10         # se un dato non viene scritto da >10h = reparto davvero fermo (GitHub schedula i cron in modo irregolare -> soglia larga per non gridare a vuoto)


def newest_ts(pattern):
    ts = [int(m.group(1)) for f in glob.glob(pattern) for m in [re.search(r"_(\d{10})\.jsonl\.gz$", f)] if m]
    return max(ts) if ts else 0


def main():
    problems = []

    # (1) INTEGRITA
    files = corr = rows = 0
    for f in glob.glob("data/raw/**/*.jsonl.gz", recursive=True):
        files += 1
        try:
            for l in gzip.open(f, "rt"):
                if l.strip(): json.loads(l); rows += 1
        except Exception:
            corr += 1
    if corr: problems.append(f"{corr} file corrotti")

    # (2) FRESCHEZZA (i reparti scrivono?)
    fresh = {"whale": newest_ts("data/raw/whales/backfill_*.jsonl.gz"),
             "candele": max(newest_ts("data/raw/candles/meme_*.jsonl.gz"),
                            newest_ts("data/raw/candles/whalepools_*.jsonl.gz"),
                            newest_ts("data/raw/candles/run_*.jsonl.gz"))}
    for k, t in fresh.items():
        age = (now - t) / 3600 if t else 999
        if age > STALE_H: problems.append(f"{k}: nessun dato nuovo da {age:.0f}h (reparto fermo?)")

    # (3) CONTENUTO + COPERTURA
    w = []
    for f in glob.glob("data/raw/whales/backfill_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                try:
                    d = json.loads(l)
                    if d.get("usd"): w.append(d)
                except: pass
        except: pass
    toks_w = set(x["pool"] for x in w)
    toks_c = set()
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("tf") == "hour": toks_c.add(d["pool"])
        except: pass
    metrics = {"whale": len(w), "wallet": len(set(x["wallet"] for x in w)),
               "token_whale": len(toks_w), "token_candele": len(toks_c),
               "token_utili": len(toks_w & toks_c), "file": files, "righe": rows}

    # (4) CRESCITA vs snapshot precedente
    prev = json.load(open(SNAP)) if os.path.exists(SNAP) else {}
    growth = {k: metrics[k] - prev.get("metrics", {}).get(k, 0) for k in ("whale", "token_utili")}
    # niente crescita da >6h su ENTRAMBI puo' essere normale (storico esaurito) -> solo warning, non rosso

    healthy = len(problems) == 0
    status = "🟢 SANO" if healthy else "🔴 PROBLEMA"

    lines = [f"# HEALTH — whale-radar accumulo", "",
             f"**Stato: {status}**  ·  aggiornato {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}", ""]
    if problems:
        lines += ["## ⚠️ Problemi rilevati"] + [f"- {p}" for p in problems] + [""]
    lines += ["## Metriche",
              f"- Whale accumulate: **{metrics['whale']}** (+{growth['whale']} dall'ultimo check)",
              f"- Wallet distinti: **{metrics['wallet']}**",
              f"- Token con whale: **{metrics['token_whale']}**",
              f"- Token con candele: **{metrics['token_candele']}**",
              f"- **Token UTILI (whale+candele): {metrics['token_utili']}** (+{growth['token_utili']})",
              f"- File dati: {metrics['file']} · righe totali: {metrics['righe']:,} · corrotti: {corr}",
              "",
              "## Freschezza",
              f"- Ultima whale: {(now-fresh['whale'])/3600:.1f}h fa" if fresh['whale'] else "- Ultima whale: mai",
              f"- Ultime candele: {(now-fresh['candele'])/3600:.1f}h fa" if fresh['candele'] else "- Ultime candele: mai",
              ""]
    open("HEALTH.md", "w").write("\n".join(lines))
    json.dump({"ts": now, "metrics": metrics}, open(SNAP, "w"))

    print(f"{status} | " + " · ".join(f"{k}={v}" for k, v in metrics.items()), flush=True)
    if problems:
        print("PROBLEMI:", "; ".join(problems), flush=True)
        raise SystemExit(1)   # -> GitHub manda mail di alert al proprietario


if __name__ == "__main__":
    main()
