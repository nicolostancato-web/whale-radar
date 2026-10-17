"""La guardia: chiede a `rianima` chi e' muto e lo rilancia. Pochi secondi, nessuna scrittura.

PERCHE' E' UN FILE E NON DUE RIGHE DENTRO IL WORKFLOW (2/10). La prima versione metteva il
codice Python dentro `run: |` nel file della corsia, con le righe a colonna zero. Dentro un
blocco YAML le righe devono essere piu' indentate della chiave: a colonna zero il blocco si
CHIUDE, e `import rianima` diventa una chiave YAML di primo livello. File illeggibile.
GitHub allora non sa nemmeno come si chiama la corsia — nei registri compariva
`.github/workflows/guardia.yml` invece di `guardia` — e FALLISCE a ogni suonata: nove email in
un'ora, le stesse che avevo passato la notte a spegnere.

E' la seconda volta in un giorno che un file di corsia illeggibile manda email a raffica (la
prima era `riserve`, con `steps:` vuoto). La lezione: **il codice sta nei file di codice.**
Dentro i workflow vanno comandi di una riga, dove non esiste indentazione da sbagliare.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rianima                                                    # noqa: E402

righe = rianima.tutto()
for r in righe:
    print("GUARDIA |", r, flush=True)
if not righe:
    print("GUARDIA | tutte le corsie sorvegliate sono nei limiti", flush=True)
