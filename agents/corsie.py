"""L'elenco delle corsie — DEDOTTO dai file, non scritto a mano.

IL DIFETTO CHE LO FA NASCERE (27/09, trovato dalla domanda quotidiana al suo primo giro).
`heartbeat.py` e `staffetta.py` avevano ognuno il proprio elenco, scritto a mano, con QUATTRO
corsie: motore, ricerca, loop 0, sperimenti. Nel frattempo le corsie sono diventate una cinquantina,
comprese quelle che raccolgono i dati che non tornano — `vivo`, `storico` — e le tre nate ieri.
**I guardiani sorvegliavano quattro corsie su cinquanta e dichiaravano che andava tutto bene.**

E' la famiglia di errore piu' costosa che abbiamo: *si aggiorna un anello della catena e l'anello
dopo resta quello di ieri.* Un elenco scritto a mano e' una cosa da RICORDARE, e in due giorni ho
dimostrato che le cose da ricordare le dimentico.

**Quindi qui non c'e' nessun elenco da aggiornare: si guarda nella cartella dei workflow.**
Una corsia nuova e' sorvegliata perche' ESISTE, non perche' qualcuno si e' ricordato di iscriverla.
"""
import glob
import os
import re

CARTELLA = ".github/workflows"

# Le uniche cose scritte a mano: le ECCEZIONI, e ognuna con la sua ragione.
# Il prefisso del commit quando non coincide col nome della corsia.
PREFISSO_DIVERSO = {
    "engine": "engine ",
    "loop0": "loop0 ",
}
# Chi non va sorvegliato, e perche'.
FUORI = {
    "repo_gc": "gira una volta al giorno e riscrive la storia: il silenzio e' il suo stato normale",
    "pubblicatore": "non scrive dati propri, porta quelli degli altri",
    "soccorso": "gira solo quando c'e' qualcosa da recuperare: il silenzio vuol dire che va bene",
    "piu_intelligente": "una volta al giorno, di proposito",
}


def _minuti_cron(testo):
    """Ogni quanto gira, dai cron dichiarati. None se non ha un orario."""
    righe = re.findall(r"- cron:\s*['\"]([^'\"]+)['\"]", testo)
    if not righe:
        return None
    migliore = None
    for c in righe:
        p = c.split()
        if len(p) < 5:
            continue
        m, h = p[0], p[1]
        if m.startswith("*/"):
            passo = int(m[2:] or 60)
        elif "," in m:
            passo = max(1, 60 // (m.count(",") + 1))
        elif h.startswith("*/"):
            passo = int(h[2:] or 1) * 60
        elif h == "*":
            passo = 60
        else:
            passo = 24 * 60
        migliore = passo if migliore is None else min(migliore, passo)
    return migliore


def elenco(cartella=CARTELLA):
    """[(nome, file, prefisso del commit, minuti di silenzio tollerati)] per le corsie da sorvegliare.

    I minuti tollerati sono TRE volte il ritmo dichiarato: sotto si urlerebbe a ogni ritardo
    normale, sopra si scoprirebbero i morti il giorno dopo. Minimo 45, massimo un giorno.
    """
    fuori = []
    for p in sorted(glob.glob(os.path.join(cartella, "*.yml"))):
        nome = os.path.basename(p)[:-4]
        if nome in FUORI or nome.startswith("_"):
            continue
        try:
            t = open(p).read()
        except Exception:
            continue
        passo = _minuti_cron(t)
        if passo is None:
            continue                      # senza orario non c'e' un silenzio da misurare
        tolleranza = max(45, min(24 * 60, passo * 3))
        fuori.append((nome, os.path.basename(p), PREFISSO_DIVERSO.get(nome, nome + " "), tolleranza))
    return fuori


if __name__ == "__main__":
    e = elenco()
    print(f"{len(e)} corsie sorvegliate (dedotte dai file, non da una lista)")
    for nome, f, pref, t in e:
        print(f"   {nome:22} ogni tanto -> silenzio tollerato {t:4} min   (commit «{pref}»)")
    print(f"\nescluse di proposito: {', '.join(FUORI)}")
