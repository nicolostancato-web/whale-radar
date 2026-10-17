"""Il controllo che conta: a PARI quantita' di storia, chi ha un passato migliore muore meno?

LA FAMIGLIA DI ERRORE CHE QUESTO CONTROLLA (sopravvivenza). Un portafoglio ha un passato
soltanto se e' ancora qui. Se guardo «chi ha un passato buono muore meno», posso stare
leggendo «chi e' sopravvissuto e' sopravvissuto». Il 3/10 questo controllo ha ucciso
l'effetto su robinhood sul bersaglio-rendimento: il segno cambiava (-2, +14, -7).

IN POSITIVO: si confronta DENTRO lo stesso scaglione di quanta-storia. Se a pari numero di
osservazioni passate il passato MIGLIORE muore meno, la sopravvivenza non spiega piu' niente:
e' tenuta ferma per costruzione.
"""
import os
import numpy as np
from combinazioni import carica

MORTA = -0.99
MIN_LATO = 120


def main():
    chain = os.environ.get("CHAIN", "base")
    righe = [x for x in carica(chain) if x.get("insider_quanti_noti")]
    n = len(righe)
    morti = np.array([1.0 if x["_bersaglio"] <= MORTA else 0.0 for x in righe])
    quanti = np.array([float(x["insider_quanti_noti"]) for x in righe])
    storia = np.array([float(x["insider_storia"] or 0.0) for x in righe])
    print(f"CONTROLLO | {chain}: {n:,} pool con passato noto, "
          f"{morti.mean():.1%} muoiono", flush=True)
    print(f"\n   {'storia nota':>14} {'pool':>7} {'muoiono se passato':>20} "
          f"{'muoiono se passato':>20} {'scarto':>8}")
    print(f"   {'(osservazioni)':>14} {'':>7} {'PEGGIORE':>20} {'MIGLIORE':>20} {'':>8}")
    scaglioni = [(1, 1), (2, 2), (3, 4), (5, 9), (10, 29), (30, 10**9)]
    pesi, scarti = [], []
    for lo, hi in scaglioni:
        m = (quanti >= lo) & (quanti <= hi)
        if m.sum() < 2 * MIN_LATO:
            continue
        s, mm = storia[m], morti[m]
        taglio = float(np.median(s))
        basso, alto = s <= taglio, s > taglio
        if basso.sum() < MIN_LATO or alto.sum() < MIN_LATO:
            continue
        a, b = float(mm[basso].mean()), float(mm[alto].mean())
        et = f"{lo}" if lo == hi else (f"{lo}+" if hi > 10**8 else f"{lo}-{hi}")
        print(f"   {et:>14} {int(m.sum()):7,} {a:19.1%} {b:19.1%} "
              f"{(a-b)*100:+7.1f}")
        pesi.append(int(m.sum()))
        scarti.append((a - b) * 100)
    if scarti:
        peso = np.array(pesi, float)
        print(f"\n   scarto medio pesato: {float(np.average(scarti, weights=peso)):+.1f} punti "
              f"su {int(peso.sum()):,} pool, in {len(scarti)} scaglioni")
        print(f"   scaglioni con lo stesso segno (passato migliore muore meno): "
              f"{sum(1 for z in scarti if z > 0)}/{len(scarti)}")


if __name__ == "__main__":
    main()
