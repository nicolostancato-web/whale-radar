"""Dove uscire: al raddoppio, piu' in alto, o lasciando correre con un cordino.

PERCHE' (10/10). Tre monete su 27 hanno toccato il massimo DOPO la nostra uscita, e due erano
vincenti che avevano gia' incassato il +90%: poi sono arrivate a 8,70x e 6,04x. La regola viva
prende il raddoppio e scappa. La domanda e' se quel «e scappa» ci costa i colpi grossi.

Si misura sul cammino (versione 2, ogni punto porta gli estremi del suo intervallo), con la
stessa simulazione validata contro la regola viva: scarto massimo 3 punti su 21 posizioni.

LE REGOLE DI ONESTA' SONO LE STESSE del file sullo stop: si stampa tutta la griglia, si guarda
la forma, e nessuna riga entra nella regola viva da qui. Con 21 chiusure e otto varianti, la
migliore e' per costruzione fortunata: serve una previsione registrata prima, su monete che
ancora non esistono.
"""
import json
import statistics
import sys

PROVA = "data/multichain/robinhood/prova_in_avanti.json"
CAMMINO = "data/multichain/robinhood/cammino_posizioni.json"
ORIZZONTE_BLOCCHI = 600_000
COSTI = 0.95


def simula(cam, bersaglio=2.0, cordino=None, stop=None):
    """bersaglio: dove si incassa. cordino: dopo il bersaglio si segue il massimo e si esce
    se il prezzo scende di questa frazione sotto il massimo visto. stop: uscita in perdita."""
    attivo = False
    massimo = 0.0
    ultimo = 1.0
    for p in cam:
        b, x = p[0], p[1]
        if b > ORIZZONTE_BLOCCHI:
            break
        mn = p[2] if len(p) > 2 else x
        mx = p[3] if len(p) > 3 else x
        ultimo = x
        if not attivo:
            if stop and mn <= stop:
                return stop * COSTI
            if mx >= bersaglio:
                if cordino is None:
                    return bersaglio * COSTI
                attivo = True
                massimo = mx
        else:
            massimo = max(massimo, mx)
            if mn <= massimo * (1 - cordino):
                return massimo * (1 - cordino) * COSTI
    return (massimo * (1 - cordino) if attivo and cordino else ultimo) * COSTI


def riga(nome, r):
    sd = statistics.stdev(r) if len(r) > 1 else 0
    ic = 1.96 * sd / len(r) ** 0.5
    m = statistics.mean(r)
    print(f"{nome:<30}{m*100:>8.1f}%{f'±{ic*100:.1f}':>10}{statistics.median(r)*100:>9.1f}%"
          f"{sum(1 for x in r if x > 0):>7}{max(r)*100:>9.0f}%")


def main():
    pos = json.load(open(PROVA))["posizioni"]
    cam = json.load(open(CAMMINO))["monete"]
    casi = [(cam.get(t) or {}).get("cammino") for t, p in pos.items()
            if p["stato"] == "chiusa" and (cam.get(t) or {}).get("cammino")]
    print(f"USCITA | {len(casi)} posizioni chiuse\n")
    print(f"{'regola':<30}{'media':>9}{'interv.':>10}{'mediana':>9}{'vinte':>7}{'meglio':>9}")
    print("-" * 74)
    riga("2x secco (la regola viva)", [simula(c) - 1 for c in casi])
    for b in (3.0, 5.0):
        riga(f"{b:.0f}x secco", [simula(c, bersaglio=b) - 1 for c in casi])
    for cd in (0.3, 0.5, 0.6):
        riga(f"2x poi cordino -{cd*100:.0f}%", [simula(c, cordino=cd) - 1 for c in casi])
    riga("2x + stop 0,30", [simula(c, stop=0.30) - 1 for c in casi])
    riga("2x poi cordino -50% + stop 0,30",
         [simula(c, cordino=0.5, stop=0.30) - 1 for c in casi])
    print("-" * 74)
    print("'meglio' e' il risultato della posizione migliore: serve a vedere se la media di una\n"
          "riga vive su un caso solo. Se l'intervallo contiene lo zero, la riga non dice niente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
