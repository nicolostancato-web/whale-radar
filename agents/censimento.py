#!/usr/bin/env python3
"""
CENSIMENTO — perche' un pool non produce dati: e' MORTO o non l'abbiamo raccolto?

Il buco piu' grave segnalato dalla consulenza esterna (01/09), e costa pochissimo chiuderlo: arriva a una
serie utilizzabile solo il 21% dei pool Base, l'11% di Solana, il 10% di BSC. I nostri tassi di morte
(6/17/15%) NON spiegano il 78-90% mancante. Significa che stiamo trattando come "assenti" pool che invece
non abbiamo mai interrogato — e ogni percentuale che calcoliamo e' su un campione di sopravvissuti
selezionato da noi stessi, non dal mercato.

Qui ogni pool scoperto riceve uno STATO TERMINALE esplicito. Nessun pool sparisce in silenzio.
Scrive CENSIMENTO.md + data/censimento.json. Sola lettura. €0.
"""
import json, os, glob, gzip, time, datetime

CHAINS = ["base", "solana", "bsc"]
now = int(time.time())

STATI = {
    "vivo": "ha una serie utilizzabile (>=5 punti)",
    "troppo_giovane": "nato da meno di 6 ore: non ha ancora avuto tempo",
    "mai_interrogato": "NON l'abbiamo mai chiesto — limite nostro, non del mercato",
    "interrogato_senza_dati": "l'abbiamo chiesto e non ha mai prodotto scambi: nato morto",
    "serie_troppo_corta": "ha qualche dato ma sotto la soglia utilizzabile",
    "sparito": "aveva dati e ha smesso di aggiornarsi da oltre 48h",
}


def eta_ore(p):
    c = p.get("created")
    if c:
        try:
            return (now - datetime.datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ")
                    .replace(tzinfo=datetime.timezone.utc).timestamp()) / 3600
        except Exception: pass
    return (now - p.get("seen", now)) / 3600


def censisci(chain):
    base = f"data/multichain/{chain}"
    if not os.path.exists(f"{base}/pools.json"): return None
    try: pools = json.load(open(f"{base}/pools.json"))
    except Exception: return None
    tentati = set()
    if os.path.exists(f"{base}/ckpt.json"):
        try: tentati = set(json.load(open(f"{base}/ckpt.json")).get("last_fetch", {}))
        except Exception: pass

    serie = {}
    for f in glob.glob(f"{base}/candles/*.jsonl.gz") + glob.glob(f"{base}/pulse/*.jsonl.gz"):
        a = os.path.basename(f).replace(".jsonl.gz", "")
        try:
            ts = [int(json.loads(l)["ts"]) for l in gzip.open(f, "rt") if json.loads(l).get("cl")]
        except Exception:
            continue
        if ts: serie[a] = (len(ts), max(ts))

    conta = {k: 0 for k in STATI}
    for a, p in pools.items():
        n, ultimo = serie.get(a, (0, 0))
        if n >= 5:
            conta["sparito" if now - ultimo > 48 * 3600 else "vivo"] += 1
        elif eta_ore(p) < 6:
            conta["troppo_giovane"] += 1
        elif a not in tentati:
            conta["mai_interrogato"] += 1
        elif n == 0:
            conta["interrogato_senza_dati"] += 1
        else:
            conta["serie_troppo_corta"] += 1
    conta["_totale"] = len(pools)
    return conta


def main():
    out = {}
    for ch in CHAINS:
        c = censisci(ch)
        if c: out[ch] = c
    json.dump({"ts": now, "chain": out}, open("data/censimento.json", "w"))

    L = ["# 📋 CENSIMENTO — che fine ha fatto ogni pool che abbiamo scoperto",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}*", "",
         "> **Perché esiste**: dicevamo che il 60% dei token era \"inutilizzabile\", ma non sapevamo *perché*.",
         "> Un pool senza dati perché è nato morto è un'informazione sul mercato; un pool senza dati perché",
         "> non l'abbiamo mai interrogato è un limite nostro. Confonderli significa calcolare le percentuali",
         "> su un campione selezionato da noi invece che dal mercato.", "",
         "| chain | totale | vivi | troppo giovani | **mai interrogati** (limite nostro) | **nati morti** | serie corta | spariti |",
         "|---|---|---|---|---|---|---|---|"]
    for ch, c in out.items():
        L.append(f"| **{ch}** | {c['_totale']} | {c['vivo']} | {c['troppo_giovane']} | "
                 f"**{c['mai_interrogato']}** | **{c['interrogato_senza_dati']}** | "
                 f"{c['serie_troppo_corta']} | {c['sparito']} |")
    L += [""]
    for ch, c in out.items():
        interrogati = c["_totale"] - c["mai_interrogato"] - c["troppo_giovane"]
        if interrogati > 0:
            morte = c["interrogato_senza_dati"] / interrogati * 100
            cop = c["mai_interrogato"] / c["_totale"] * 100
            L += [f"**{ch}** — dei pool che abbiamo davvero interrogato, il **{morte:.0f}% è nato morto**. "
                  f"Ma il **{cop:.0f}%** dei pool scoperti non l'abbiamo mai chiesto: quello non dice niente "
                  f"sul mercato, dice quanto siamo lenti a raccogliere."]
    L += ["", "## Cosa significa per le percentuali", "",
          "Le nostre analisi girano solo sui **vivi**. Se i \"nati morti\" fossero token che avremmo comprato",
          "e su cui avremmo perso tutto, la percentuale vera è più bassa di quella che vediamo. Se invece",
          "sono pool che non avremmo mai toccato (nessun volume, nessuno scambio), allora il campione è",
          "corretto. **La differenza fra i due casi si misura con il volume nelle prime ore, e va misurata",
          "prima di fidarsi di qualunque numero.**", "",
          "> Nessun pool sparisce più in silenzio: ognuno ha uno stato dichiarato."]
    open("CENSIMENTO.md", "w").write("\n".join(L))
    print("CENSIMENTO | " + " · ".join(
        f"{ch} vivi {c['vivo']}/{c['_totale']} (mai interrogati {c['mai_interrogato']})" for ch, c in out.items()),
        flush=True)


if __name__ == "__main__":
    main()
