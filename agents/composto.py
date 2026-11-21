"""Il conto composto: bersaglio piccolo, stop, ripetuto molte volte. Paga?

L'IPOTESI DI NICOLO' (12/10): «basta un 10%, ma se ne fai 50 di operazioni. Prova a fare un
focus qua, i dati ce li hai.»

PERCHE' SERVE UN FILE A PARTE. La media per operazione non risponde: puo' essere positiva mentre
il capitale si azzera. Ieri la riga «niente stop» aveva media -21% e capitale composto **-100%**,
cioe' zero: una sola perdita del 90% cancella dieci vincite da +20%, e la media non lo mostra.
Il composto e' il numero che somiglia al conto in banca.

DUE MODI DI REINVESTIRE, entrambi stampati perche' dicono cose diverse:
  · TUTTO su ogni operazione: e' il piu' citato e il piu' fragile. Basta una perdita vicina al
    100% e il capitale non torna piu'.
  · UNA FRAZIONE FISSA (un decimo) per operazione: e' quello che Nicolo' aveva proposto il 9/10
    («parti da 100 e dividi»), e sopravvive alle code grasse.

L'ORDINE E' CRONOLOGICO. Un composto calcolato su operazioni mescolate non significa niente: il
risultato dipende dall'ordine, e l'ordine vero e' quello in cui sono accadute.
"""
import json
import os
import statistics
import sys

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
COSTO = 1.02


def _cammini():
    """Tutti i cammini disponibili, pre e post diploma, in ordine di tempo."""
    fuori = []
    p = f"{BASE}/prova_nella_curva.json"
    if os.path.exists(p):
        for k, x in json.load(open(p))["posizioni"].items():
            # SOLO LE CHIUSE (12/10). I cammini delle posizioni aperte sono troncati a adesso:
            # una che crollera' domani oggi sembra neutra, e il conto composto ne esce
            # ottimista. Erano 8 su 39 nella prima versione di questa analisi.
            if x["stato"] != "chiusa":
                continue
            if x.get("cammino") and len(x["cammino"]) > 1:
                fuori.append((x["aperta_il"], "curva", x["cammino"]))
    p = f"{BASE}/cammino_posizioni.json"
    q = f"{BASE}/prova_in_avanti.json"
    if os.path.exists(p) and os.path.exists(q):
        st = json.load(open(q))["posizioni"]
        for t, x in json.load(open(p))["monete"].items():
            c = x.get("cammino")
            if c and len(c) > 1 and t in st and st[t]["stato"] == "chiusa":
                # il cammino del post-diploma ha [blocchi, mediana, min, max]: si usano i primi due
                fuori.append((st[t]["aperta_il"], "diploma", [[r[0], r[1]] for r in c]))
    fuori.sort()
    return fuori


def esito(cam, stop, bersaglio):
    for _b, x in cam:
        if stop and x <= stop:
            return stop / COSTO
        if bersaglio and x >= bersaglio:
            return bersaglio / COSTO
    return (cam[-1][1] if cam else 1.0) / COSTO


def main():
    tutti = _cammini()
    gruppi = {"tutte": tutti,
              "solo dentro la curva": [x for x in tutti if x[1] == "curva"],
              "solo dopo il diploma": [x for x in tutti if x[1] == "diploma"]}
    for nome, g in gruppi.items():
        if len(g) < 5:
            continue
        print(f"\n=== {nome.upper()} — {len(g)} operazioni, in ordine di tempo ===")
        print(f"{'bersaglio':>10}{'stop':>7}{'media':>8}{'in utile':>10}"
              f"{'TUTTO reinvestito':>20}{'un decimo per volta':>22}")
        print("-" * 79)
        for bers in (1.1, 1.15, 1.2, 1.3, 1.5):
            for st in (0.95, 0.9, 0.8):
                xs = [esito(c, st, bers) for _q, _t, c in g]
                tutto = 1.0
                for x in xs:
                    tutto *= x
                cap = 1.0
                for x in xs:
                    cap = cap * 0.9 + cap * 0.1 * x      # un decimo in gioco, il resto fermo
                print(f"{(bers-1)*100:>9.0f}%{(st-1)*100:>6.0f}%"
                      f"{(statistics.mean(xs)-1)*100:>7.0f}%{sum(1 for x in xs if x > 1):>6}/{len(xs)}"
                      f"{(tutto-1)*100:>19.0f}%{(cap-1)*100:>21.0f}%")
        print("-" * 79)
        print("«TUTTO reinvestito» va letto per primo quando e' negativo: se azzera il capitale,\n"
              "la media positiva della stessa riga non serve a niente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
