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
import json
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


def _versione(riga):
    try:
        return json.loads(riga).get("v")
    except Exception:
        return None


def fondi(nuovo, vecchio):
    """Torna (righe_da_scrivere, quante_aggiunte, quante_recuperate, quante_superate).

    LA PROTEZIONE DEVE SAPERE DELLE VERSIONI (7/10, sera). Recuperare dal ramo le righe che la
    consegna non ha e' giusto — nasce da un incidente vero in cui una copia secca cancellava
    dati. Ma recupera anche le righe scritte da una versione PRECEDENTE del codice, e quelle non
    sono dati da salvare: sono dati da rifare.

    Misurato stasera: `tenute_pezzo_0` sul ramo aveva 56.316 righe senza versione e 4.770 a
    versione 8. La corsia potava le vecchie, il pubblicatore le rimetteva, e il file restava
    misto per sempre — cioe' inutilizzabile, perche' chi legge (giustamente) rifiuta un insieme
    che mescola due significati. Due meccanismi giusti che insieme facevano una cosa sbagliata.

    Quindi: se le righe CONSEGNATE dichiarano tutte la stessa versione, le righe del ramo con
    una versione diversa (o senza) sono **superate** e non si recuperano. Si contano e si
    dicono. Se la consegna non dichiara versioni, non si cambia niente: la protezione resta
    com'era, perche' senza il dato non si tira a indovinare.
    """
    a, b = _righe(vecchio), _righe(nuovo)
    vers_nuove = {_versione(r) for r in b}
    superate = 0
    if len(vers_nuove) == 1 and next(iter(vers_nuove)) is not None:
        v = next(iter(vers_nuove))
        prima = len(a)
        a = [r for r in a if _versione(r) == v]
        superate = prima - len(a)
    viste = set(a)
    aggiunte = [r for r in b if r not in viste]
    # le righe del ramo che la consegna NON ha: sono quelle che una copia secca cancellerebbe
    recuperate = len(viste - set(b))
    return a + aggiunte, len(aggiunte), recuperate, superate


def principale(cartella_consegna, radice):
    accum = agg = rec = sost = superate_tot = 0
    for base, _, nomi in os.walk(cartella_consegna):
        for nome in nomi:
            src = os.path.join(base, nome)
            rel = os.path.relpath(src, cartella_consegna)
            dst = os.path.join(radice, "data", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if nome.endswith(".jsonl.gz") and os.path.exists(dst):
                righe, a, r, sup = fondi(src, dst)
                with gzip.open(dst, "wt", encoding="utf-8") as h:
                    h.writelines(righe)
                accum += 1
                agg += a
                rec += r
                if r:
                    print(f"   {rel}: {r} righe del ramo che una copia avrebbe cancellato",
                          flush=True)
                if sup:
                    superate_tot += sup
                    print(f"   {rel}: {sup} righe di una versione precedente NON recuperate "
                          f"(si rifanno, non si salvano)", flush=True)
            else:
                shutil.copy2(src, dst)
                sost += 1
    print(f"   fusi {accum} archivi (+{agg} righe nuove, {rec} salvate, "
          f"{superate_tot} superate), sostituiti {sost} file", flush=True)


if __name__ == "__main__":
    principale(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ".")
