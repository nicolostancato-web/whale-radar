"""Il rendimento al netto dei costi come funzione del momento d'ingresso.

PERCHE' (4/10). Misurando i costi e' comparsa una regolarita' che non cercavo: nella colonna
del mercato, piu' tardi si entra meno e' letale — ingresso 5: -11,7%, ingresso 10: -8,0%,
ingresso 25: -3,0%. Monotono, e l'unico caso che passa lo zero dopo i costi e' il piu'
tardivo. E' l'OPPOSTO di come abbiamo ragionato per settimane («prenderla nei primi secondi»).

Tre spiegazioni possibili, e vanno separate prima di crederci:
  (a) entrare dopo evita le monete che muoiono subito -> si vede nel tasso di morte;
  (b) entrare dopo e' un campione DIVERSO: sopravvivono al filtro «arrivare allo scambio 60»
      solo le pool vive, quindi e' sopravvivenza -> si vede nel numero di pool;
  (c) il prezzo iniziale e' piu' alto e il resto scende meno -> si vede nella mediana.
Stampo tutte e tre accanto, cosi' la lettura non puo' barare.
"""
import os
import numpy as np
from combinazioni import carica

MORTA = -0.99
COSTO = 0.02


def al_netto(e, costo):
    out = e - costo
    out[e <= MORTA] = e[e <= MORTA]
    return out


def main():
    chain = os.environ.get("CHAIN", "robinhood")
    momenti = [x.strip() for x in os.environ.get("MOMENTI", "5,10,25,60").split(",")]
    print(f"CURVA | {chain}, costo andata/ritorno {COSTO:.0%}\n")
    print(f"   {'ingresso':>9} {'pool':>8} {'medio':>8} {'netto':>8} {'mediano':>9} "
          f"{'muoiono':>9} {'storia nota':>12}")
    for m in momenti:
        os.environ["ENTRATA_SCAMBIO"] = m
        try:
            righe = carica(chain)
        except SystemExit as err:
            print(f"   {m:>9}  {err}")
            continue
        e = np.array([x["_bersaglio"] for x in righe])
        con_storia = sum(1 for x in righe if x.get("insider_quanti_noti"))
        print(f"   {m:>9} {len(e):8,} {np.mean(e):7.1%} {np.mean(al_netto(e, COSTO)):7.1%} "
              f"{np.median(e):8.1%} {np.mean(e <= MORTA):8.1%} {con_storia:12,}")


if __name__ == "__main__":
    main()
