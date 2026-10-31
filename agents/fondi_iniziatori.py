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

# TUTTE LE FETTE, NON UNA (2/10). Da quando il lavoro si divide fra lavori paralleli, ognuno
# scrive il suo `iniziatori_nuovi_<fetta>.json`: fondere solo quello senza numero butterebbe il
# lavoro di tre quarti dei lavori, in silenzio.
import glob
pezzi = sorted(glob.glob(f"data/multichain/{CHAIN}/iniziatori_nuovi*.json"))
if not pezzi:
    print(f"FUSIONE | {CHAIN}: niente di nuovo")
    sys.exit(0)
nuovi = {}
illeggibili = 0
for q in pezzi:
    try:
        nuovi.update(json.load(open(q)))
    except Exception:
        illeggibili += 1
# I NONCE SI FONDONO COME GLI INIZIATORI (2/10): stesso meccanismo, file separato.
pezzi_n = sorted(glob.glob(f"data/multichain/{CHAIN}/nonce_nuovi*.json"))
if pezzi_n:
    nonce_nuovi = {}
    for q in pezzi_n:
        try:
            nonce_nuovi.update(json.load(open(q)))
        except Exception:
            pass
    f_n = f"data/multichain/{CHAIN}/nonce.json.gz"
    vecchi_n = {}
    if os.path.exists(f_n):
        try:
            vecchi_n = json.load(gzip.open(f_n, "rt")).get("da", {})
        except Exception:
            vecchi_n = {}
    if nonce_nuovi:
        prima = len(vecchi_n)
        vecchi_n.update(nonce_nuovi)
        with gzip.open(f_n, "wt") as h:
            json.dump({"acq": int(__import__("time").time()), "da": vecchi_n}, h)
        print(f"FUSIONE | {CHAIN}: nonce {prima:,} -> {len(vecchi_n):,}")
        for q in pezzi_n:
            try:
                os.remove(q)
            except Exception:
                pass

print(f"FUSIONE | {CHAIN}: {len(pezzi)} pezzi trovati"
      + (f", {illeggibili} illeggibili (NON li invento)" if illeggibili else ""))
if not nuovi:
    print(f"FUSIONE | {CHAIN}: i pezzi non contengono niente, NON tocco il principale")
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
# SI CANCELLANO TUTTI I PEZZI FUSI, NON UNO (2/10). Qui c'era `os.remove(NUOVI)`: fondeva
# quattro pezzi (le quattro fette) e ne cancellava uno solo, quindi gli altri tre tornavano a
# ogni giro — non si perde niente, ma la cartella cresce e ogni fusione rifa' lavoro gia' fatto.
# Per i nonce qui sopra lo facevo gia' bene: due pezzi dello stesso meccanismo scritti in due
# momenti diversi divergono, ed e' il motivo per cui conviene scriverli insieme.
for q in pezzi:
    try:
        os.remove(q)
    except Exception:
        pass
print(f"FUSIONE | {CHAIN}: {prima:,} + {len(nuovi):,} nuovi -> {len(vecchi):,} "
      f"({len(set(vecchi.values())):,} indirizzi distinti)")
