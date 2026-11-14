#!/usr/bin/env python3
"""LE CHIAVI SI LEGGONO DALLA FONTE DI VERITA', A RUNTIME.

Nicolo' tiene tutte le credenziali in UN solo file, e la regola e' che non
vivano da nessun'altra parte: non nel codice, non nel repo, non in una
cartella temporanea. Il 7/11 la cartella di lavoro (che sta sotto /private/tmp)
ci ha cancellato la chiave dell'email e il C-check e' morto a meta' per 1,6
ore -- quindi la lezione non e' «rimetti il file», e' «non tenerlo qui».

Questo modulo legge, non copia. Non stampa mai il valore: solo la sua
lunghezza e un'impronta corta, perche' un valore sbagliato va distinto da un
valore assente senza mostrarlo a nessuno.
"""
import hashlib, os, re

FILE = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")


def _testo():
    if not os.path.exists(FILE):
        return None
    try:
        return open(FILE, errors="ignore").read()
    except Exception:
        return None


def sezione(nome):
    """il blocco di testo sotto `=== NOME ===` fino alla sezione dopo"""
    t = _testo()
    if not t:
        return None
    # L'INTESTAZIONE PUO' AVERE IL VALORE SULLA STESSA RIGA.
    # Il 7/11 Nicolo' ha scritto `=== 1INCH === <chiave>` su una riga sola e
    # il lettore ha detto «sezione ASSENTE», perche' pretendevo
    # l'intestazione da sola (ancora `$`). E' la SECONDA volta nello stesso
    # giorno che la mia rigidita' fa sembrare un errore suo: prima le
    # parentesi angolari, ora la riga unica. La regola generale: un lettore
    # di configurazione scritta a mano accetta la forma che trova.
    m = re.search(r"^=+\s*" + re.escape(nome) + r"\s*=+", t, re.M | re.I)
    if not m:
        return None
    resto = t[m.end():]
    fine = re.search(r"^=+\s*\w", resto, re.M)
    return resto[:fine.start()] if fine else resto


def _pulisci(v):
    """IL VALORE PUO' ARRIVARE VESTITO. Trovato il 7/11: la chiave era
    incollata dentro le parentesi angolari del mio esempio (`<chiave>`), e il
    lettore diceva «non trovata» -- che e' la risposta peggiore possibile,
    perche' sembra un errore di Nicolo' quando e' una rigidita' mia.
    Chi legge si adatta alla forma umana, non il contrario."""
    return (v or "").strip().strip("<>\"'`,;").strip()


def alchemy():
    """la chiave API Alchemy, oppure None. Non la stampa mai."""
    s = sezione("ALCHEMY")
    if not s:
        return None
    # una chiave Alchemy e' una stringa di 32+ caratteri alfanumerici,
    # a volte dentro un URL wss://eth-mainnet.g.alchemy.com/v2/<chiave>
    m = re.search(r"/v2/([A-Za-z0-9_-]{20,})", s)
    if m:
        return _pulisci(m.group(1))
    for riga in s.splitlines():
        if re.search(r"(api[\s_-]*key|chiave)", riga, re.I):
            dopo = riga.split(":", 1)[-1] if ":" in riga else riga
            m = re.search(r"([A-Za-z0-9_-]{18,})", dopo)
            if m:
                return _pulisci(m.group(1))
    m = re.search(r"\b([A-Za-z0-9_-]{18,})\b", s)
    return _pulisci(m.group(1)) if m else None


def _dalla_sezione(nome, etichette=("api[\\s_-]*key", "authorization",
                                    "secret", "chiave", "token")):
    """la credenziale della sezione, qualunque etichetta abbia usato Nicolo'.
    CHI LEGGE SI ADATTA ALLA FORMA UMANA: il 7/11 la chiave Alchemy era
    incollata dentro le parentesi angolari del mio esempio e il lettore
    diceva «non trovata» -- che sembra un errore suo quando e' rigidita' mia.
    """
    s = sezione(nome)
    if not s:
        return None
    for riga in s.splitlines():
        if any(re.search(e, riga, re.I) for e in etichette):
            dopo = riga.split(":", 1)[-1] if ":" in riga else riga
            m = re.search(r"([A-Za-z0-9_.\-]{18,})", dopo)
            if m:
                return _pulisci(m.group(1))
    m = re.search(r"\b([A-Za-z0-9_.\-]{18,})\b", s)
    return _pulisci(m.group(1)) if m else None


def uno_inch():
    return _dalla_sezione("1INCH")


def bloxroute():
    return _dalla_sezione("BLOXROUTE")


def impronta(v):
    return hashlib.sha256(v.encode()).hexdigest()[:10] if v else None


if __name__ == "__main__":
    print("   file delle credenziali:",
          "presente" if _testo() else "ASSENTE")
    print("   sezione ALCHEMY:",
          "presente" if sezione("ALCHEMY") else "ASSENTE")
    for nome, f in (("ALCHEMY", alchemy), ("1INCH", uno_inch),
                    ("BLOXROUTE", bloxroute)):
        k = f()
        print(f"   {nome:10s} "
              + (f"{len(k)} caratteri, impronta {impronta(k)} "
                 f"(NON la stampo)" if k
                 else ("sezione presente ma chiave non trovata"
                       if sezione(nome) else "sezione ASSENTE")))
