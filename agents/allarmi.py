"""Gli allarmi che nessuno ha ancora letto. Li legge la maglia a ogni giro.

PERCHE' ESISTE (10/10). Nicolo' ha chiuso tutte le email di GitHub, aggiungendo: «pero' tu devi
assicurarti che sai questi errori». Da quel momento una corsia che esce con errore non avvisa
nessuno. Gli allarmi vengono scritti qui e letti dalla maglia: chi li ha letti resta segnato,
cosi' lo stesso allarme non si ripete all'infinito ma non si perde nemmeno.
"""
import json
import os
import sys
import time

ARCHIVIO = "data/allarmi_da_leggere.jsonl"
LETTI = "data/allarmi_letti.json"


def main():
    if not os.path.exists(ARCHIVIO):
        print("ALLARMI | nessuno")
        return 0
    letti = set(json.load(open(LETTI))) if os.path.exists(LETTI) else set()
    nuovi = []
    for riga in open(ARCHIVIO):
        riga = riga.strip()
        if not riga:
            continue
        try:
            a = json.loads(riga)
        except json.JSONDecodeError:
            continue           # una riga troncata non deve nascondere le altre
        if str(a.get("quando")) not in letti:
            nuovi.append(a)
    if not nuovi:
        print("ALLARMI | nessuno nuovo")
        return 0
    print(f"ALLARMI | {len(nuovi)} DA LEGGERE:")
    for a in nuovi[-5:]:
        q = time.strftime("%d/%m %H:%M", time.localtime(a["quando"]))
        print(f"   {q}  da {a.get('da','?')}: {a['testo'][:200]}")
    if "--segna" in sys.argv:
        letti |= {str(a["quando"]) for a in nuovi}
        json.dump(sorted(letti), open(LETTI, "w"))
        print("ALLARMI | segnati come letti")
    return 0


if __name__ == "__main__":
    sys.exit(main())
