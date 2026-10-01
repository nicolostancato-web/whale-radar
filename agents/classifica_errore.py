"""Classifica l'errore GREZZO prima che qualcuno lo racconti. Niente interpretazioni.

IL GUASTO CHE QUESTO CHIUDE (1/10, nome dato da Grok: `fail-plausible`).

Il 30/09 un file oltre i 100 MB ha reso impossibile ogni scrittura. Nei registri si leggeva
«contesa sul ramo» — e il loop ha ritentato per TRE ORE una cosa non ritentabile. Il modello non
aveva taciuto l'errore: l'aveva trasformato in un racconto credibile. E un racconto credibile
manda a cercare nel posto sbagliato con la massima convinzione.

Grok, citando Wu (arXiv:2606.14589): «il modello non tace l'errore: lo trasforma in un racconto
credibile». E il consiglio: «manca un classificatore stupido sullo stderr, prima che il modello
lo riassuma».

Stupido e' il punto. Qui non si interpreta: si confrontano stringhe note.
  · TERMINALE  -> fermarsi. Ritentare non serve, il difetto e' deterministico.
  · CONTESA    -> riprovare ha senso, e' l'unico caso in cui ne ha.
  · SCONOSCIUTO-> fermarsi e CONSERVARE lo stderr grezzo. Non inventare una causa.

La terza riga e' la piu' importante: un errore che non riconosco non e' una contesa.
"""
import re
import sys

TERMINALI = [
    (r"GH001", "file oltre 100 MB: GitHub rifiuta il push intero, per sempre"),
    (r"exceeds GitHub's file size limit", "file oltre il limite per file"),
    (r"Large files detected", "file troppo grandi nel commit"),
    (r"pre-receive hook declined", "il server ha rifiutato: quota, dimensione o regola"),
    (r"remote: Permission to .* denied", "permessi insufficienti sul token"),
    (r"Repository not found", "repository sbagliato o token senza accesso"),
    (r"shallow update not allowed", "copia superficiale: serve fetch+reset, non un retry"),
    (r"refusing to merge unrelated histories", "storie diverse: un retry non le unisce"),
    (r"would clobber existing tag", "conflitto di etichette: va risolto a mano"),
    (r"quota|storage limit|over the limit", "limite di spazio raggiunto"),
]

CONTESE = [
    (r"\(fetch first\)", "qualcuno ha scritto nel frattempo"),
    (r"non-fast-forward", "il ramo e' avanzato: riallinearsi e riprovare"),
    (r"cannot lock ref", "contesa sul riferimento"),
    (r"the remote end hung up|Connection reset|timed out|HTTP 5\d\d",
     "problema di rete o server momentaneo"),
]


def classifica(stderr):
    t = stderr or ""
    for schema, perche in TERMINALI:
        if re.search(schema, t, re.I):
            return "TERMINALE", perche
    for schema, perche in CONTESE:
        if re.search(schema, t, re.I):
            return "CONTESA", perche
    return "SCONOSCIUTO", ("errore che non riconosco: NON lo chiamo contesa e NON ritento. "
                           "Lo stderr grezzo va conservato e letto da un umano.")


def main():
    testo = sys.stdin.read()
    tipo, perche = classifica(testo)
    print(f"ERRORE | {tipo}: {perche}", flush=True)
    if tipo != "CONTESA":
        # LE PRIME RIGHE GREZZE, non un riassunto: e' cio' che mancava il 30/09.
        print("   stderr grezzo (prime 12 righe, senza interpretazione):", flush=True)
        for riga in testo.strip().splitlines()[:12]:
            print(f"   | {riga}", flush=True)
    # 0 = riprova ha senso; 1 = fermati
    sys.exit(0 if tipo == "CONTESA" else 1)


if __name__ == "__main__":
    main()
