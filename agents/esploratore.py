#!/usr/bin/env python3
"""
ESPLORATORE — le idee escono DAI NOSTRI DATI, non dalla mia testa.

PERCHE' ESISTE (13/09, richiamo di Nicolo). Le ultime idee le ho ragionate a tavolino: intuizioni
economiche plausibili, tutte morte. Ma noi abbiamo una cosa che a tavolino non si ha — un archivio
che nessun altro ha: 13.000 file di scambi con wallet e importi, 9.700 wallet con un punteggio,
candele su tre chain. Le domande migliori dovrebbero uscire da li'.

IL PERICOLO, ed e' serio. Frugare nei propri dati finche' salta fuori qualcosa TROVA SEMPRE qualcosa:
con abbastanza tentativi il rumore produce figure bellissime. Per questo l'esploratore ha un vincolo
che non puo' aggirare:

  1. guarda SOLO LA META' VECCHIA dei dati, divisa per tempo;
  2. non tocca, non legge e non nomina la meta' recente;
  3. non dichiara nessun vantaggio: PROPONE candidati, e basta.

La meta' recente resta intatta come banco di prova per l'esperimento vero, registrato dopo. Chi trova
un'idea non ha il diritto di giudicarla sugli stessi dati in cui l'ha trovata.

Sola lettura, nessuna chiamata. €0.
"""
import json, gzip, os, glob, time, sys, statistics as st
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MC = "data/multichain"
CHAINS = ("base", "robinhood", "solana")
FINESTRA_H = 1          # gli scambi PRIMA dell'entrata: tutto qui dentro e' passato, mai futuro
MIN_SCAMBI = 8
MIN_EVENTI = 60


def trades(ch, pool):
    f = f"{MC}/{ch}/trades/{pool}.jsonl.gz"
    if not os.path.exists(f): return []
    out = []
    try:
        for l in gzip.open(f, "rt"):
            try:
                r = json.loads(l)
                if r.get("ts"): out.append(r)
            except Exception: pass
    except Exception: return []
    out.sort(key=lambda r: r["ts"]); return out


def righe(ch):
    try:
        import multichain_brain as B
        r = B.load_rows(ch)
        return [x for x in r if x.get("pool")]
    except Exception:
        return []


def candidati(tr, ent, ricorrenti):
    """Domande che i nostri dati possono rispondere e che il modello NON guarda.
    Tutte calcolate solo su quello che e' successo PRIMA di poter comprare."""
    pre = [r for r in tr if r["ts"] <= ent]
    if len(pre) < MIN_SCAMBI: return None
    buy = [r for r in pre if r.get("kind") == "buy"]
    sell = [r for r in pre if r.get("kind") == "sell"]
    if not buy: return None
    usd_b = sum(r.get("usd") or 0 for r in buy)
    usd_s = sum(r.get("usd") or 0 for r in sell)
    per_w = defaultdict(float)
    for r in buy: per_w[r.get("w") or "?"] += r.get("usd") or 0
    quote = sorted(per_w.values(), reverse=True)
    tornati = sum(1 for w, _ in per_w.items() if sum(1 for r in buy if r.get("w") == w) > 1)
    noti = sum(1 for w in per_w if w in ricorrenti)
    return {
        "quanti compratori diversi": len(per_w),
        "quota del piu' grosso": (quote[0] / usd_b) if usd_b else 0.0,
        "acquisto mediano in dollari": st.median([r.get("usd") or 0 for r in buy]),
        "quanti tornano a comprare": tornati / max(1, len(per_w)),
        "venduto su comprato": usd_s / usd_b if usd_b else 0.0,
        "quota di wallet gia' visti da noi": noti / max(1, len(per_w)),
    }


def wallet_ricorrenti(ch, limite=400000):
    """I wallet che compaiono su PIU' token nostri. E' l'unica cosa che sappiamo noi e nessun altro:
    non chi e' bravo — quello l'abbiamo gia' provato e non funziona — ma chi TORNA."""
    conta = defaultdict(int)
    n = 0
    for f in glob.glob(f"{MC}/{ch}/trades/*.jsonl.gz"):
        visti = set()
        try:
            for l in gzip.open(f, "rt"):
                n += 1
                if n > limite: break
                try:
                    w = json.loads(l).get("w")
                    if w: visti.add(w)
                except Exception: pass
        except Exception: pass
        for w in visti: conta[w] += 1
        if n > limite: break
    return {w for w, c in conta.items() if c >= 3}


def main():
    L = ["# 🔎 L'ESPLORATORE — le idee escono dai nostri dati",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · guarda SOLO la metà vecchia · €0*", "",
         "> Le ultime idee le avevo ragionate a tavolino: plausibili, e tutte morte. Ma noi abbiamo una",
         "> cosa che a tavolino non si ha — **un archivio che nessun altro possiede**: 13.000 file di",
         "> scambi con wallet e importi, su tre chain.", "",
         "> **Il pericolo, ed è serio.** Frugare nei propri dati finché salta fuori qualcosa *trova",
         "> sempre* qualcosa: con abbastanza tentativi il rumore produce figure bellissime. Per questo",
         "> l'esploratore guarda **solo la metà vecchia**, non tocca la metà recente, e **non dichiara",
         "> nessun vantaggio**: propone candidati e basta. Chi trova un'idea non ha il diritto di",
         "> giudicarla sugli stessi dati in cui l'ha trovata.", ""]

    for ch in CHAINS:
        rr = righe(ch)
        if len(rr) < MIN_EVENTI:
            L += [f"## {ch}", "", f"> ⏸️ Solo {len(rr)} eventi: troppo pochi per dividere in due metà.", ""]
            continue
        rr.sort(key=lambda r: r["ent"])
        meta = rr[:len(rr) // 2]          # SOLO LA META' VECCHIA. L'altra non la apro.
        ric = wallet_ricorrenti(ch)
        dati = []
        for r in meta:
            c = candidati(trades(ch, r["pool"]), r["ent"], ric)
            if c: dati.append((c, r["ret"]))
        L += [f"## {ch}", "",
              f"Metà vecchia: **{len(meta)}** eventi, di cui **{len(dati)}** con abbastanza scambi. "
              f"Wallet che tornano su 3+ token: **{len(ric):,}**.", ""]
        if len(dati) < 30:
            L += ["> ⏸️ Meno di 30 eventi misurabili: non si propone niente.", ""]
            continue
        L += ["| domanda (dai nostri dati) | alto vs basso, mediana |", "|---|---|"]
        nomi = list(dati[0][0].keys())
        prop = []
        for nome in nomi:
            v = sorted(dati, key=lambda x: x[0][nome])
            q = max(5, len(v) // 4)
            basso = st.median([x[1] for x in v[:q]])
            alto = st.median([x[1] for x in v[-q:]])
            sep = alto - basso
            prop.append((abs(sep), nome, sep))
            L.append(f"| {nome} | **{sep*100:+.1f}%** |")
        prop.sort(reverse=True)
        L += ["", f"> 🔔 **Candidato più promettente su {ch}: «{prop[0][1]}»** "
                  f"({prop[0][2]*100:+.1f}% fra il quarto alto e il quarto basso). Non è un risultato:",
              "> è una **domanda da registrare** e provare sulla metà recente, che qui non è stata",
              "> guardata.", ""]
    L += ["---", "",
          "> **Cosa succede adesso.** Ogni candidato entra in coda come esperimento con il suo criterio",
          "> di morte scritto PRIMA, e viene giudicato sulla metà recente. Se lo giudicassi qui,",
          "> starei misurando quanto sono bravo a trovare figure nel rumore."]
    open("ESPLORATORE.md", "w").write("\n".join(L))
    print("ESPLORATORE | proposte scritte", flush=True)


if __name__ == "__main__":
    main()
