"""Quando un lavoro si divide a fette, ogni fetta scrive un file SUO.

PERCHE' ESISTE (2/10). Ho sbagliato la stessa cosa TRE volte in sei ore:

 1. `iniziatori` a quattro fette: ognuna FONDEVA nello stesso file partendo dalla stessa base.
    Il log diceva «354.066 + 12.108», «+ 6.694», «+ 7.316», «+ 8.582» — quattro versioni, e lo
    scrittore ne prende una. Tre quarti del lavoro perso.
 2. La fusione cancellava UN pezzo su quattro, quindi gli altri tre tornavano ogni giro.
 3. `finanziatori`, scritto un'ora DOPO aver corretto il punto 1: `FUORI` era un nome solo per
    quattro fette. Risultato: 0,1 KB sul ramo invece di quaranta portafogli.

La terza volta e' la piu' istruttiva: avevo la lezione fresca, l'avevo scritta in un commento, e
l'ho riscritta sbagliata in un file nuovo. **Una lezione in un commento protegge il file dove sta,
non il prossimo.** Per questo qui c'e' una funzione: chi la usa non puo' sbagliare, e chi non la
usa si vede.

LA REGOLA, in due righe:
  · ogni fetta scrive `<nome>_pezzo_<fetta>.json` — mai il file finale;
  · il file finale lo scrive UNO SOLO, dopo, dove i pezzi esistono tutti (il pubblicatore).
E' la stessa regola dello scrittore unico su `main`, applicata un livello piu' in basso: **dove
si uniscono i pezzi puo' esserci un solo scrittore.**
"""
import os


def quale_fetta():
    """(indice, quante). (0, 1) se il lavoro non e' diviso."""
    quante = max(1, int(os.environ.get("FETTE", 1)))
    return int(os.environ.get("FETTA", 0)) % quante, quante


def mia_parte(elenco):
    """La parte dell'elenco che tocca a questa fetta. Niente si sovrappone, niente si perde."""
    i, n = quale_fetta()
    return elenco if n == 1 else elenco[i::n]


def mia_parte_stabile(elenco, chiave):
    """La parte che tocca a questa fetta, assegnata per IDENTITA' e non per posizione.

    == PERCHE' NON BASTA elenco[i::n] (7/10/2026) ==

    Per posizione e' corretto solo se l'elenco non cambia mai. Il nostro cresce: ogni giro
    scopre monete graduate nuove. Basta un elemento in piu' in testa e TUTTE le posizioni
    slittano: la moneta che ieri era della fetta 3 oggi e' della fetta 5. La fetta 5 la
    lavora e la scrive; la fetta 3 ce l'ha ancora nel suo contatore «fatte» e non la
    ricancella. Risultato: la stessa riga esiste due volte, e chi somma conta doppio.

    Misurato il 7/10: 30.016 coppie portafoglio×moneta duplicate TRA fette diverse. E' una
    delle due cause del guadagno di 7.740 dollari dove la chain diceva 3,36.

    Con l'identita' (l'indirizzo della moneta) la fetta di una moneta non cambia MAI, nemmeno
    se l'elenco raddoppia. Il prezzo e' che le fette non sono esattamente uguali di dimensione:
    e' un prezzo che si paga volentieri.
    """
    i, n = quale_fetta()
    if n == 1:
        return elenco
    import hashlib
    return [x for x in elenco
            if int(hashlib.sha256(str(chiave(x)).encode()).hexdigest()[:8], 16) % n == i]


def nome_pezzo(radice, nome):
    """Dove scrive QUESTA fetta. Mai il file finale: quello lo fonde un altro, dopo."""
    i, n = quale_fetta()
    return os.path.join(radice, f"{nome}_pezzo_{i}.json")


def pezzi(radice, nome):
    """Tutti i pezzi da fondere. Si usa SOLO dove di scrittori ce n'e' uno."""
    import glob
    return sorted(glob.glob(os.path.join(radice, f"{nome}_pezzo_*.json")))
