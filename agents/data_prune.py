#!/usr/bin/env python3
"""
DATA_PRUNE — riduce il peso del repo SENZA perdere nulla di utile. Due azioni:
  1. STUB: elimina i token con <5 candele (pool morti/mai partiti che non analizziamo mai) + i loro trade.
  2. TRIM: il cervello usa SOLO i trade PRIMA dell'entrata (prima ora dal listing). I file pero' salvano tutta
     la storia (Solana Helius = centinaia di trade/token). Teniamo solo la FINESTRA INIZIALE (listing → +4h):
     riduzione enorme, feature IDENTICHE (safe: i trade post-entrata non li usa nessuno).
Da girare in repo_gc prima dello squash. €0.
"""
import gzip, json, glob, os, time, datetime

# LAPIDE (03/09): il GC cancella i token con meno di 5 candele perche' "tanto non li analizziamo mai".
# Era vero finche' l'unica domanda era "quanto rende". Da stanotte non lo e' piu': il cancello dei creator
# considera un token senza prezzo il caso PEGGIORE, non un dato mancante — e se cancelliamo quei token,
# l'etichetta "morto" finisce per confondere due cose molto diverse: chi non ha mai prodotto un prezzo,
# e chi il prezzo l'aveva ma gliel'abbiamo tolto noi. Il primo e' un disastro, il secondo e' un buco
# nostro. Qui restano le lapidi: indirizzo, quando e perche' l'abbiamo rimosso — poche decine di byte
# ciascuna, e chi analizza puo' distinguere una morte vera da una nostra potatura.
LAPIDI = "data/potati.json"

CHAINS = ["solana", "bsc", "base", "robinhood"]
MIN_CANDLES = 5
EARLY = 4 * 3600     # teniamo i trade fino a +4h dal listing (copre l'entrata +1/3h con margine)
GRAZIA_H = 48        # SALVAGENTE: un pool piu' giovane di 48h NON e' uno stub, ha solo poche candele perche' e'
                     # NATO DA POCO. Senza questo il GC cancellava proprio i token freschi (e li toglieva da
                     # pools.json, quindi non tornavano piu'): il forward restava a secco. Mai piu'.
now = int(time.time())


def eta_h(pools, addr):
    """ore di vita del pool (da created GeckoTerminal, fallback: quando l'abbiamo visto)."""
    p = pools.get(addr) or {}
    c = p.get("created")
    if c:
        try:
            return (now - datetime.datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ")
                    .replace(tzinfo=datetime.timezone.utc).timestamp()) / 3600
        except Exception: pass
    if p.get("seen"): return (now - p["seen"]) / 3600
    return 1e9   # non lo conosciamo affatto: trattalo come vecchio


def main():
    tot_stub = 0; tot_trim = 0; freed = 0.0
    try: lapidi = json.load(open(LAPIDI))
    except Exception: lapidi = {}
    for ch in CHAINS:
        base = f"data/multichain/{ch}"
        if not os.path.isdir(base): continue
        pf = f"{base}/pools.json"
        pools = json.load(open(pf)) if os.path.exists(pf) else {}
        stub = 0; trim = 0; salvati = 0
        for cf in glob.glob(f"{base}/candles/*.jsonl.gz"):
            addr = os.path.basename(cf).replace(".jsonl.gz", "")
            try:
                ts = [int(json.loads(l)["ts"]) for l in gzip.open(cf, "rt") if json.loads(l).get("cl")]
            except Exception:
                continue                                   # file illeggibile: NON si cancella. Nel dubbio si tiene.
            tf = f"{base}/trades/{addr}.jsonl.gz"
            if len(ts) < MIN_CANDLES and eta_h(pools, addr) < GRAZIA_H:
                salvati += 1                               # giovane: gli diamo tempo di crescere
                continue
            if len(ts) < MIN_CANDLES:                      # STUB: elimina tutto, ma lascia la lapide
                freed += os.path.getsize(cf) / 1024 / 1024; os.remove(cf)
                if os.path.exists(tf): freed += os.path.getsize(tf) / 1024 / 1024; os.remove(tf)
                pools.pop(addr, None); stub += 1
                lapidi[addr.lower()] = {"chain": ch, "ts": now, "candele": len(ts)}
                continue
            if os.path.exists(tf):                          # TRIM: tieni solo listing → +4h
                cutoff = min(ts) + EARLY
                rows = []
                try:
                    for l in gzip.open(tf, "rt"):
                        r = json.loads(l)
                        if r.get("ts", 0) <= cutoff: rows.append(r)
                except: rows = None
                if rows is not None:
                    before = os.path.getsize(tf)
                    with gzip.open(tf, "wt") as fo:
                        for r in rows: fo.write(json.dumps(r) + "\n")
                    after = os.path.getsize(tf)
                    if after < before: freed += (before - after) / 1024 / 1024; trim += 1
        json.dump(pools, open(pf, "w"))
        # pulisci i checkpoint dagli addr rimossi
        for ck in ("ckpt.json", "trades_ckpt.json", "helius_ckpt.json", "rpc_ckpt.json"):
            cp = f"{base}/{ck}"
            if os.path.exists(cp):
                try:
                    d = json.load(open(cp))
                    for k in ("done_candles", "done"):
                        if isinstance(d.get(k), list): d[k] = [a for a in d[k] if a in pools]
                    for k in ("last_fetch", "last", "mint"):
                        if isinstance(d.get(k), dict): d[k] = {a: v for a, v in d[k].items() if a in pools}
                    json.dump(d, open(cp, "w"))
                except: pass
        tot_stub += stub; tot_trim += trim
        print(f"  {ch}: {stub} stub rimossi, {trim} trade-file trimmati, {salvati} giovani SALVATI", flush=True)
    json.dump(lapidi, open(LAPIDI, "w"))
    print(f"DATA_PRUNE | {tot_stub} stub + {tot_trim} trim | ~{freed:.1f} MB liberati | "
          f"{len(lapidi)} lapidi", flush=True)


if __name__ == "__main__":
    main()
