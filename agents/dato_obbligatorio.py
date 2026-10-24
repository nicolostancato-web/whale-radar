"""Un dato che entra in un conto non ha un ripiego: o c'e' o ci si ferma.

Nato il 24/10: `fee()` non rispondeva e il codice assumeva 0,30%. Quel ripiego
ha retto tre ore di analisi e quattro misure, producendo rendimenti del 10.697%
annuo. La commissione vera era 0,0004%: tutto andava diviso per 750.

Un errore si annuncia, un ripiego no: prende il posto del dato e si comporta
come un dato. Quindi qui si alza un'eccezione, e il programma muore rumoroso.
"""
class DatoMancante(Exception): pass

def intero(valore, cosa, chi=""):
    """Converte un risultato esadecimale, RIFIUTANDOSI se manca."""
    if valore is None or valore in ("0x", ""):
        raise DatoMancante(
            f"{cosa} non e' leggibile{' da '+chi if chi else ''}: "
            f"misurala dai dati o fermati, NON metterci una costante plausibile")
    return int(valore, 16)

def richiesto(valore, cosa, chi=""):
    if valore is None:
        raise DatoMancante(f"{cosa} non e' leggibile{' da '+chi if chi else ''}")
    return valore
