"""Cerca una regola che funzioni ESEGUITA, non sulla carta.

PERCHE' (15/10). La 50-5 su carta rendeva +9,8%. Eseguita davvero fa -2,1%, e il live ci ha
detto esattamente dove si perde: non nello stop (che incassa 0,908 invece di 0,950, cioe'
-4,4%) ma nel bersaglio, che incassa 1,203 invece di 1,500 — venti punti. Non per lentezza:
le uscite partono in sei secondi. E' che il prezzo resta sopra +45% per 6,9 secondi, quindi
arriviamo sempre sul bordo del picco.

Quindi qui non si simula piu' l'uscita al prezzo del tocco: si esce al prezzo REALMENTE
osservato qualche secondo dopo, come fa la macchina. Una regola che sopravvive a questo e'
una regola che possiamo incassare.
"""
import json
import os
import statistics
import sys

SEC = 0.093                      # secondi per blocco, misurati
COSTO = 1.0591                   # costo vero di andata e ritorno, misurato
RITARDO = float(os.environ.get("RITARDO_SEC", "6"))   # il nostro giro, misurato
STATO = "data/multichain/robinhood/prova_nella_curva.json"


def esito(cam, stop, bers):
    """Resa di una posizione, uscendo al primo prezzo visto RITARDO secondi dopo il tocco."""
    for i, (b, x) in enumerate(cam):
        if x <= stop or (bers and x >= bers):
            for b2, x2 in cam[i:]:
                if (b2 - b) * SEC >= RITARDO:
                    return x2 / COSTO - 1
            return cam[-1][1] / COSTO - 1
    return cam[-1][1] / COSTO - 1


def cammino_intero(p):
    """Il cammino PIU' quello che e' successo dopo l'uscita.

    SENZA QUESTO LA SIMULAZIONE E' CIECA DOVE SERVE (15/10). Il cammino si ferma nell'istante
    in cui la posizione chiude: cercando «il prezzo sei secondi dopo il tocco» non si trova
    niente e si finisce per usare il prezzo del tocco stesso — cioe' si simula di essere
    infinitamente veloci, che e' esattamente l'illusione che il live ha smontato. I punti
    registrati dopo l'uscita sono la parte che mancava.
    """
    return (p.get("cammino") or []) + (p.get("dopo_uscita") or [])


def main():
    st = json.load(open(STATO))
    pos = [p for p in st["posizioni"].values()
           if p.get("dopo_uscita") and len(p.get("cammino") or []) > 2]
    pos.sort(key=lambda p: p.get("aperta_il", 0))
    mz = len(pos) // 2
    print(f"CERCA UNA REGOLA CHE REGGA ALL'ESECUZIONE — {len(pos)} cammini, "
          f"uscita {RITARDO:.0f}s dopo il tocco\n")
    righe = []
    for stop in (0.98, 0.95, 0.9, 0.85, 0.8, 0.7, 0.5):
        for bers in (1.1, 1.15, 1.2, 1.3, 1.5, 2.0, 3.0, None):
            r = [esito(cammino_intero(p), stop, bers) for p in pos]
            a = [esito(cammino_intero(p), stop, bers) for p in pos[:mz]]
            b = [esito(cammino_intero(p), stop, bers) for p in pos[mz:]]
            sd = statistics.stdev(r) if len(r) > 1 else 0
            righe.append((statistics.mean(r), 1.96 * sd / len(r) ** 0.5, stop, bers,
                          statistics.mean(a), statistics.mean(b)))
    righe.sort(reverse=True)
    print(f"{'stop':>6}{'bersaglio':>11}{'resa':>9}{'+/-':>7}{'1a meta':>10}{'2a meta':>10}")
    print("-" * 56)
    for m, ic, s, bb, a, b in righe[:12]:
        print(f"{s:>6}{str(bb):>11}{m*100:>+8.2f}%{ic*100:>7.1f}{a*100:>+9.2f}%{b*100:>+9.2f}%")
    print("-" * 56)
    buone = [x for x in righe if x[0] - x[1] > 0 and x[4] > 0 and x[5] > 0]
    print(f"\n   regole positive con l'intervallo che NON tocca lo zero "
          f"e positive in entrambe le meta': {len(buone)} su {len(righe)}")
    for m, ic, s, bb, a, b in buone[:5]:
        print(f"      stop {s} bersaglio {bb}: {m*100:+.2f}% +/-{ic*100:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
