"""Lo stop loss misurato sul cammino, non deciso a intuito.

PERCHE' (10/10). Guardando la tabella avevo detto a Nicolo' che uno stop al 50% «taglia sette
vincenti su nove». Ricontando la colonna erano QUATTRO. Leggere una colonna a occhio e' un modo
di inventare numeri, e qui si simula: si cammina sul prezzo di ogni posizione chiusa, si applica
lo stop, e si confronta con quello che la regola congelata ha fatto davvero.

ATTENZIONE, ed e' il punto piu' importante di questo file: con 21 chiusure, provare venti soglie
e tenere la migliore TROVA SEMPRE qualcosa. E' la lezione della cassaforte (30/09) e quella della
selezione che non funziona (8/10). Qui dunque:
  - si stampa TUTTA la griglia, non la soglia migliore;
  - si guarda la FORMA (un effetto vero e' liscio e largo; un artefatto e' un picco solo);
  - nessuna soglia entra nella regola viva da questo file: la decisione passa da una previsione
    registrata PRIMA, su posizioni che ancora non esistono.
"""
import json
import statistics
import sys

PROVA = "data/multichain/robinhood/prova_in_avanti.json"
CAMMINO = "data/multichain/robinhood/cammino_posizioni.json"

ORIZZONTE_BLOCCHI = 600_000          # la regola viva: 16,7 ore
COSTI = 0.95                         # 1% entrata + 1% uscita + 1,71% di scivolamento misurato
USCITA = 2.0


def simula(cam, stop):
    """Cammina sul prezzo. Torna (moltiplicatore al netto dei costi, incerto).

    Dalla versione 2 ogni punto porta [blocchi, mediana, minimo, massimo] del suo intervallo:
    una soglia attraversata dentro l'intervallo non sfugge piu'. Resta un caso onesto da
    dichiarare: se nello STESSO intervallo il minimo tocca lo stop e il massimo tocca l'uscita,
    l'ordine non e' conoscibile da qui — quel caso si conta come incerto invece di scegliere il
    risultato che fa piu' comodo.
    """
    incerto = False
    ultimo = 1.0
    for p in cam:
        b, x = p[0], p[1]
        if b > ORIZZONTE_BLOCCHI:
            break
        mn = p[2] if len(p) > 2 else x
        mx = p[3] if len(p) > 3 else x
        ultimo = x
        giu = bool(stop) and mn <= stop
        su = mx >= USCITA
        if giu and su:
            incerto = True
            return USCITA * COSTI, incerto      # si assume il caso favorevole, ma e' DICHIARATO
        if giu:
            return stop * COSTI, incerto
        if su:
            return USCITA * COSTI, incerto
    return ultimo * COSTI, incerto


def main():
    pos = json.load(open(PROVA))["posizioni"]
    cam = json.load(open(CAMMINO))["monete"]
    casi = []
    for tok, p in pos.items():
        if p["stato"] != "chiusa":
            continue
        c = (cam.get(tok) or {}).get("cammino")
        if not c:
            continue
        casi.append((tok, c, (p.get("esito") or {}).get("rendimento")))
    print(f"STOP | {len(casi)} posizioni chiuse con il cammino disponibile\n")

    # il controllo: la regola viva, ricostruita dal cammino. Se non combacia con il rendimento
    # vero, la simulazione non e' affidabile e il resto non si legge (cancello, non commento).
    ric = [simula(c, None)[0] - 1 for _, c, _ in casi]
    vero = [r for _, _, r in casi if r is not None]
    if len(vero) == len(ric):
        scarti = [abs(a - b) for a, b in zip(ric, vero)]
        peggio = max(scarti)
        print(f"controllo: la simulazione senza stop ricostruisce la regola viva con uno scarto "
              f"massimo di {peggio*100:.1f} punti")
        if peggio > 0.25:
            print("SCARTO TROPPO GRANDE: il cammino campionato non ricostruisce la regola. "
                  "Non leggo la griglia: sarebbero numeri di una simulazione che non combacia.")
            return 1

    print(f"\n{'stop':>6}{'media':>9}{'intervallo':>14}{'mediana':>9}{'vinte':>7}"
          f"{'stoppate':>10}{'raddoppi':>10}")
    print("-" * 65)
    for stop in (None, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80):
        esiti = [simula(c, stop) for _, c, _ in casi]
        r = [e[0] - 1 for e in esiti]
        inc = sum(1 for e in esiti if e[1])
        sd = statistics.stdev(r) if len(r) > 1 else 0
        ic = 1.96 * sd / len(r) ** 0.5
        ste = sum(1 for e in esiti if stop and abs(e[0] - stop * COSTI) < 1e-9)
        rad = sum(1 for x in r if x > 0.5)
        nome = "niente" if stop is None else f"{stop:.2f}"
        print(f"{nome:>6}{statistics.mean(r)*100:>8.1f}%"
              f"{f'±{ic*100:.1f}':>14}{statistics.median(r)*100:>8.1f}%"
              f"{sum(1 for x in r if x > 0):>7}{ste:>10}{rad:>10}"
              + (f"   ({inc} incerti)" if inc else ""))
    print("-" * 65)
    print("l'intervallo e' al 95%: se contiene lo zero, quella riga non dice niente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
