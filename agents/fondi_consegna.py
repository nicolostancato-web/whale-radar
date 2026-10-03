"""Mette una consegna sopra il repository: fondendo cio' che si accumula, sostituendo il resto.

DERIVATO E ACCUMULATO NON SI TRATTANO UGUALE (29/09).

Il pubblicatore copiava e basta. Per l'insieme va bene: si ricalcola da zero ogni volta, e
fonderlo col vecchio significherebbe ritrovarsi lo stesso pool due volte.

Per chi ACCUMULA — universo, censimento, riserve — copiare puo' cancellare righe. La finestra
e' stretta ma reale: se una corsia legge il ramo prima che il pubblicatore ci scriva sopra la
consegna precedente, la sua consegna non contiene quelle righe, e applicarla le fa sparire.
Prima non succedeva perche' le corsie spingevano e `git` fondeva; smettendo di spingere,
la fusione va rifatta qui.

Si fonde per RIGA INTERA: le righe sono immutabili una volta scritte, quindi l'unione senza
duplicati e' esattamente il risultato giusto, e non serve sapere quale campo sia la chiave.
"""
import gzip
import os
import shutil
import sys


def _righe(p):
    ap = gzip.open if p.endswith(".gz") else open
    try:
        with ap(p, "rt", encoding="utf-8", errors="replace") as h:
            return [r for r in h if r.strip()]
    except OSError:
        return []


def fondi(nuovo, vecchio):
    """Torna (righe_da_scrivere, quante_aggiunte, quante_recuperate)."""
    a, b = _righe(vecchio), _righe(nuovo)
    viste = set(a)
    aggiunte = [r for r in b if r not in viste]
    # le righe del ramo che la consegna NON ha: sono quelle che una copia secca cancellerebbe
    recuperate = len(viste - set(b))
    return a + aggiunte, len(aggiunte), recuperate


def principale(cartella_consegna, radice):
    accum = agg = rec = sost = 0
    for base, _, nomi in os.walk(cartella_consegna):
        for nome in nomi:
            src = os.path.join(base, nome)
            rel = os.path.relpath(src, cartella_consegna)
            dst = os.path.join(radice, "data", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if nome.endswith(".jsonl.gz") and os.path.exists(dst):
                righe, a, r = fondi(src, dst)
                with gzip.open(dst, "wt", encoding="utf-8") as h:
                    h.writelines(righe)
                accum += 1
                agg += a
                rec += r
                if r:
                    print(f"   {rel}: {r} righe del ramo che una copia avrebbe cancellato",
                          flush=True)
            else:
                shutil.copy2(src, dst)
                sost += 1
    print(f"   fusi {accum} archivi (+{agg} righe nuove, {rec} salvate), sostituiti {sost} file",
          flush=True)


if __name__ == "__main__":
    principale(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ".")
