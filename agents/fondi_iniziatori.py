"""Fonde i nuovi iniziatori nel file principale, DOPO il pull.

Serve perche' le due chain girano insieme: salvando il file intero, chi arriva secondo cancella il
lavoro del primo (25/09: base scesa da 12.581 a 8.052). Qui si unisce invece di sovrascrivere, e si
lavora sullo stato appena scaricato, non su quello di venti minuti fa.
"""
import gzip
import json
import os
import sys

CHAIN = os.environ.get("CHAIN", "robinhood")
FUORI = f"data/multichain/{CHAIN}/iniziatori.json.gz"
NUOVI = f"data/multichain/{CHAIN}/iniziatori_nuovi.json"

if not os.path.exists(NUOVI):
    print(f"FUSIONE | {CHAIN}: niente di nuovo")
    sys.exit(0)
try:
    nuovi = json.load(open(NUOVI))
except Exception:
    print(f"FUSIONE | {CHAIN}: file dei nuovi illeggibile, NON tocco il principale")
    sys.exit(0)
vecchi = {}
# MIGRAZIONE (25/09): il file non compresso da 24 MB, riscritto ogni 25 minuti, era l'ingorgo che
# faceva respingere le spinte delle altre corsie. Si legge il vecchio se c'e' ancora, poi sparisce.
VECCHIO = FUORI[:-3]
if os.path.exists(VECCHIO) and not os.path.exists(FUORI):
    try:
        vecchi = json.load(open(VECCHIO)).get("da", {})
        print(f"FUSIONE | {CHAIN}: migrati {len(vecchi):,} dal file non compresso")
    except Exception:
        pass
    try:
        os.remove(VECCHIO)
    except Exception:
        pass
if os.path.exists(FUORI):
    try:
        vecchi = json.load(gzip.open(FUORI,"rt")).get("da", {})
    except Exception:
        # illeggibile NON vuol dire vuoto: meglio fermarsi che cancellare
        print(f"FUSIONE | {CHAIN}: il file principale e' illeggibile, mi fermo")
        sys.exit(1)
prima = len(vecchi)
vecchi.update(nuovi)
import time
# L'ORA IN FONDO (30/09) — e la spiegazione che avevo scritto qui era SBAGLIATA.
# Avevo scritto che un cambiamento in testa a un archivio compresso «fa divergere tutto il resto»
# e costava 797 MB al giorno. Misurato su un caso costruito: non e' vero. La compressione si
# risincronizza dopo poche decine di byte, quindi un timbro che cambia in testa resta un
# cambiamento LOCALE, e git lo salva come tale.
# Cio' che costa davvero e' l'ORDINE delle righe (vedi censimento.py): rimescolate pesano
# centoventotto volte di piu'. Qui `vecchi.update(nuovi)` aggiunge in coda, quindi va gia' bene.
# La modifica resta perche' non fa male, ma la ragione vera e' un'altra e va detta.
json.dump({"da": vecchi, "acq": int(time.time())}, gzip.open(FUORI, "wt"))
os.remove(NUOVI)
print(f"FUSIONE | {CHAIN}: {prima:,} + {len(nuovi):,} nuovi -> {len(vecchi):,} "
      f"({len(set(vecchi.values())):,} indirizzi distinti)")
