"""Il cancello: nessun numero esce se un campione A CASO non passa la prova sulla chain.

LA DIRETTIVA (Nicolo', 5/10, dopo che un nostro «182X» si e' rivelato inesistente):
«Quando mi dici che i dati sono veritieri, mi dai una cripto e un wallet, io apro e devo
vedere che quel wallet ha comprato quella cripto in quella data. Ogni volta che credi che
siano veritieri, vai a verificare tu.»

PERCHE' A CASO E NON SCELTI DA ME. Se scegliessi io i casi da verificare, sceglierei quelli
che reggono — non per disonesta', ma perche' si guarda dove si spera. Il campione si estrae
con un seme dichiarato, e il seme si scrive nel risultato: chiunque puo' rifarlo identico.

LA REGOLA DI USCITA, che e' il punto di tutto il file:
  · se TUTTI i casi del campione risultano VERO → i dati si possono riportare;
  · se ANCHE UNO SOLO risulta FALSO → i dati NON sono veritieri, e non si riporta niente.
Non «si riporta con cautela». Non si riporta. Tre volte in questo progetto siamo andati
avanti su dati sbagliati, e ogni volta il costo e' stato tutto il lavoro costruito sopra.

I verdetti che NON sono bocciature ma non sono promozioni: ARBITRAGGIO (bot MEV, non una
posizione), POSIZIONE APERTA (non ancora chiusa), NON POSSO CONTROLLARE (il servizio non ha
risposto). Si contano a parte, e se sono tanti il campione non e' concludente: anche quello
va detto, invece di leggere il silenzio come un sı'.
"""
import collections
import glob
import gzip
import json
import os
import random
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from prova_sulla_chain import controlla                           # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
QUANTI = int(os.environ.get("QUANTI", 12))
SEME = int(os.environ.get("SEME", 20261005))
MIN_MULTIPLO = float(os.environ.get("MIN_MULTIPLO", 2.0))
MIN_COSTO = float(os.environ.get("MIN_COSTO", 1.0))
PAUSA = float(os.environ.get("PAUSA", 0.5))
BASE = f"data/multichain/{CHAIN}"


def valute(cop):
    q = collections.Counter()
    for v in cop.values():
        for l in ("t0", "t1"):
            a = (v.get(l) or "").lower()
            if len(a) == 42:
                q[a] += 1
    return {a for a, n in q.items() if n > 50}


def main():
    pc = f"{BASE}/coppie.json"
    if not os.path.exists(pc):
        raise SystemExit(f"CAMPIONE | manca {pc}")
    cop = json.load(open(pc))["coppie"]
    val = valute(cop)

    # le posizioni dichiarate: dai pezzi del dettaglio, o dall'archivio se ci sono
    det = {}
    for p in glob.glob(f"{BASE}/dettaglio_candidati_pezzo_*.json"):
        for k, v in json.load(open(p)).items():
            det.setdefault(k, {}).update(v)
    if not det:
        p = f"{BASE}/dettaglio_candidati.json.gz"
        if os.path.exists(p):
            raw = json.load(gzip.open(p, "rt"))
            det = raw.get("da", raw)
    if not det:
        print(f"CAMPIONE | {CHAIN}: nessuna posizione dichiarata da verificare. "
              f"Senza materiale non si promuove niente.")
        return 2

    casi = []
    for chi, pools in det.items():
        for pid, v in pools.items():
            if v.get("stato") != "chiuso" or not v.get("multiplo"):
                continue
            if v["multiplo"] < MIN_MULTIPLO or v.get("speso", 0) < MIN_COSTO:
                continue
            m = cop.get(pid) or cop.get(pid.lower()) or {}
            g = [a for a in ((m.get(l) or "").lower() for l in ("t0", "t1"))
                 if len(a) == 42 and a not in val]
            if len(g) != 1:
                continue
            casi.append({"portafoglio": chi, "gettone": g[0], "pool": pid,
                         "multiplo": v["multiplo"], "speso": v.get("speso"),
                         "incassato": v.get("incassato")})
    print(f"CAMPIONE | {CHAIN}: {len(casi):,} posizioni dichiarate oltre {MIN_MULTIPLO:g}X "
          f"con costo >= {MIN_COSTO:g}$", flush=True)
    if not casi:
        print("   nessun caso: niente da promuovere e niente da bocciare")
        return 2
    random.Random(SEME).shuffle(casi)
    campione = casi[:QUANTI]
    print(f"   campione di {len(campione)} preso A CASO con seme {SEME} "
          f"(rifacibile identico)", flush=True)

    esiti = collections.Counter()
    righe = []
    for c in campione:
        r = controlla(CHAIN, c["portafoglio"], c["gettone"])
        esiti[r["verdetto"]] += 1
        righe.append({**c, **r})
        print(f"   {c['multiplo']:>9.1f}X  {c['portafoglio'][:12]}… / "
              f"{c['gettone'][:12]}… → {r['verdetto']}", flush=True)
        time.sleep(PAUSA)

    veri = esiti.get("VERO", 0)
    falsi = esiti.get("FALSO", 0)
    altro = sum(esiti.values()) - veri - falsi
    fuori = f"data/campione_verificato_{CHAIN}.json"
    veritieri = falsi == 0 and veri >= max(1, len(campione) // 2)
    json.dump({"quando": int(time.time()), "chain": CHAIN, "seme": SEME,
               "campione": len(campione), "esiti": dict(esiti),
               "veritieri": veritieri, "righe": righe},
              open(fuori, "w"), ensure_ascii=False, indent=1)
    print(f"\n   VERI {veri} · FALSI {falsi} · altro {altro} "
          f"({', '.join(f'{k}={v}' for k, v in esiti.items() if k not in ('VERO','FALSO'))})",
          flush=True)
    if falsi:
        print(f"   VERDETTO: i dati NON sono veritieri. {falsi} casi su {len(campione)} "
              f"non esistono sulla chain. NON si riporta nessun numero.", flush=True)
    elif veri < max(1, len(campione) // 2):
        print(f"   VERDETTO: campione NON CONCLUDENTE — solo {veri} verdetti pieni su "
              f"{len(campione)}. Il silenzio non e' un si'.", flush=True)
    else:
        print(f"   VERDETTO: i dati sono VERITIERI su questo campione. "
              f"Si puo' riportare, dichiarando il seme.", flush=True)
    return 0 if veritieri else 1


if __name__ == "__main__":
    sys.exit(main())
