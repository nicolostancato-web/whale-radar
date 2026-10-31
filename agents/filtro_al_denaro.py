"""Il filtro anti-azzeramento, misurato in soldi al prezzo pagabile.

Evitare le morti e' utile solo se cambia il conto. Qui si misura il rendimento medio
DOPO il filtro, sul pezzo di tempo mai visto, con la soglia scelta sul pezzo precedente
e non ritoccata. E si stampa sempre la copertura accanto: un filtro che lascia passare
l'1% non e' una strategia.
"""
import os
import numpy as np
from combinazioni import carica

MORTA = -0.99


def riga(etichetta, esiti):
    if len(esiti) == 0:
        return
    print(f"   {etichetta:<34} {len(esiti):7,} {np.mean(esiti):9.1%} "
          f"{np.median(esiti):9.1%} {np.mean(esiti <= MORTA):9.1%}")


def main():
    chain = os.environ.get("CHAIN", "base")
    righe = [x for x in carica(chain) if x.get("insider_quanti_noti")]
    n = len(righe)
    a = int(n * 0.72)
    scelgo, giudico = righe[:a], righe[a:]
    s_sc = np.array([float(x["insider_storia"] or 0.0) for x in scelgo])
    # la soglia si fissa sul pezzo di scelta: il quinto peggiore si butta
    taglio = float(np.quantile(s_sc, 0.20))
    e = np.array([x["_bersaglio"] for x in giudico])
    s = np.array([float(x["insider_storia"] or 0.0) for x in giudico])
    print(f"FILTRO | {chain}: soglia insider_storia > {taglio:+.3f} "
          f"(quinto peggiore del pezzo di scelta, {len(scelgo):,} pool)")
    print(f"   giudico su {len(giudico):,} pool mai visti\n")
    print(f"   {'':<34} {'pool':>7} {'medio':>9} {'mediano':>9} {'muoiono':>9}")
    riga("tutto il mercato", e)
    riga("dopo il filtro", e[s > taglio])
    riga("scartati dal filtro", e[s <= taglio])
    vivi = e[(s > taglio) & (e > MORTA)]
    riga("dopo il filtro, non morti", vivi)
    passa = e[s > taglio]
    if len(passa):
        print(f"\n   il filtro lascia passare {len(passa)/len(e):.1%} del mercato")
        print(f"   scarto contro il mercato: "
              f"{(np.mean(passa) - np.mean(e))*100:+.1f} punti")


if __name__ == "__main__":
    main()
