"""«Zero su 54» non e' zero: quanto poco puo' essere, al 95%.

PERCHE' ESISTE (5/10, da una correzione di Astra). Stanotte ho scritto «su base ZERO su 54 dei
mediocri arriva a 2X» come se fosse una separazione perfetta. Astra: «anche zero successi su 54
non dimostra probabilita' zero: sotto ipotesi di indipendenza, il limite superiore unilaterale
al 95% e' circa 5,4%».

E' una famiglia di errore che non avevo nominata: **leggere un conteggio come una
probabilita'**. Zero su 54 e zero su 5.400 sono la stessa frazione e due affermazioni
completamente diverse — la prima dice «sotto il 5,4%», la seconda «sotto lo 0,06%».
Lo stesso vale al contrario: «4 su 4» non e' il 100%, e' «sopra il 40%».

IN POSITIVO: ogni conteggio riportato porta accanto il suo intervallo. Non e' prudenza
retorica: e' la differenza fra una misura e un aneddoto, e si calcola in una riga.

Metodo: intervallo di Clopper-Pearson (esatto, da distribuzione beta), senza dipendenze —
si inverte la binomiale cumulata per bisezione, che su questi numeri e' istantaneo.
"""
import sys


def _coda(k, n, p):
    """P(X <= k) per X binomiale(n, p), per bisezione sulla somma."""
    # calcolo in log per non perdere precisione su n grandi
    import math
    tot = 0.0
    for i in range(0, k + 1):
        if p <= 0.0:
            tot += 1.0 if i == 0 else 0.0
            continue
        if p >= 1.0:
            tot += 1.0 if i == n else 0.0
            continue
        lg = (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
              + i * math.log(p) + (n - i) * math.log1p(-p))
        tot += math.exp(lg)
    return min(max(tot, 0.0), 1.0)


def intervallo(k, n, fiducia=0.95):
    """(basso, alto) per la frazione vera, esatto, unilaterale a `fiducia` su ciascun lato."""
    if n <= 0:
        return (0.0, 1.0)
    alfa = 1.0 - fiducia
    # ALTO: il p piu' grande per cui vedere k o meno successi non e' ancora sorprendente
    lo, hi = 0.0, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        if _coda(k, n, m) > alfa:
            lo = m
        else:
            hi = m
    alto = hi
    # BASSO: simmetrico, visto dall'altra parte
    if k == 0:
        basso = 0.0
    else:
        lo2, hi2 = 0.0, 1.0
        for _ in range(200):
            m = (lo2 + hi2) / 2
            if 1.0 - _coda(k - 1, n, m) > alfa:
                hi2 = m
            else:
                lo2 = m
        basso = lo2
    return (basso, alto)


def dillo(k, n, cosa="casi", fiducia=0.95):
    """La riga da stampare accanto a un conteggio. Mai il conteggio da solo."""
    b, a = intervallo(k, n, fiducia)
    if n == 0:
        return f"{k}/0 {cosa}: niente da dire, il denominatore e' zero"
    return (f"{k}/{n} {cosa} = {k/n:.1%} "
            f"(al {fiducia:.0%}: fra {b:.1%} e {a:.1%})")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        print(dillo(int(sys.argv[1]), int(sys.argv[2]),
                    sys.argv[3] if len(sys.argv) > 3 else "casi"))
    else:
        # i conteggi veri di stanotte, riletti con l'intervallo accanto
        print("I conteggi di stanotte, con il loro intervallo:")
        for k, n, cosa in ((0, 54, "mediocri su base arrivati a 2X"),
                           (19, 73, "portafogli 'bravi' su base"),
                           (44, 76, "portafogli 'bravi' su robinhood"),
                           (26, 5375, "pool robinhood col lanciatore mezzo-morto"),
                           (113, 862, "pool base col lanciatore mezzo-morto")):
            print("   " + dillo(k, n, cosa))
