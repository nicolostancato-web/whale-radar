"""Nessuna pubblicazione senza un'autorizzazione valida, recente e riferita A QUESTO contenuto.

L'INVERSIONE (1/10, dettata da Astra e vera).

Fino a stanotte la porta chiedeva: «i controlli hanno segnalato rosso?». Se un controllo
SPARIVA — come e' sparito compliance_check.py senza che nessuno se ne accorgesse — la risposta
era «no» e si pubblicava. **L'assenza di allarme veniva letta come assenza di problemi.**

Astra: «il criterio corretto non e' "il controllo ha segnalato rosso?", ma: esiste
un'autorizzazione valida, recente e riferita esattamente a questo pacco, emessa dal controllo
obbligatorio previsto dalla politica vigente? L'assenza di autorizzazione deve NEGARE la
pubblicazione.»

Qui l'assenza nega. Un'autorizzazione vale solo se:
  · e' stata emessa da TUTTI i controlli obbligatori elencati in OBBLIGATORI;
  · e' piu' recente di MASSIMA_ETA secondi;
  · porta l'impronta ESATTA dei file che si stanno per pubblicare.

Cambiare i file dopo il controllo invalida l'autorizzazione: e' il caso in cui prima si passava.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)
TIMBRO = os.path.join(RADICE, "data", "autorizzazione.json")
MASSIMA_ETA = 1800        # mezz'ora: oltre, il mondo puo' essere cambiato

# I controlli SENZA I QUALI NON SI PUBBLICA. Se uno di questi sparisce, la porta si chiude:
# e' esattamente il caso che ci e' sfuggito quando compliance_check.py e' scomparso.
OBBLIGATORI = [
    ("chiavi doppie", "agents/chiavi_doppie.py"),
    ("file troppo grandi", "agents/file_troppo_grandi.py"),
    ("decisioni permanenti", "agents/decisioni.py"),
    ("metro congelato", "agents/prova_metro.py"),
    ("guasti storici", "agents/incidenti.py"),
]


# IL TIMBRO NON PUO' FAR PARTE DI CIO' CHE TIMBRA (1/10). Emettendo l'autorizzazione si scrive
# `data/autorizzazione.json`, che compare fra i file da pubblicare: l'impronta cambiava subito
# dopo essere stata calcolata e la porta si chiudeva su se stessa. Anche lo stato dei controlli,
# che i controlli stessi riscrivono mentre girano, va tenuto fuori.
ESCLUSI = ("data/autorizzazione.json", "data/decisioni_stato.json", "data/lezioni.json")


def impronta(file_da_pubblicare):
    h = hashlib.sha256()
    for p in sorted(x for x in file_da_pubblicare if x not in ESCLUSI):
        h.update(p.encode())
        try:
            with open(os.path.join(RADICE, p), "rb") as f:
                h.update(f.read())
        except OSError:
            h.update(b"<assente>")
    return h.hexdigest()


def emetti(file_da_pubblicare):
    """Fa girare TUTTI i controlli obbligatori. Emette il timbro solo se passano tutti."""
    esiti = {}
    for nome, percorso in OBBLIGATORI:
        p = os.path.join(RADICE, percorso)
        if not os.path.exists(p):
            # UN CONTROLLO SPARITO NON E' UN CONTROLLO PASSATO: e' la porta che si chiude.
            print(f"   AUTORIZZAZIONE NEGATA: manca il controllo obbligatorio «{nome}» "
                  f"({percorso}). Un controllo che sparisce non e' un controllo che passa.",
                  flush=True)
            return None
        r = subprocess.run([sys.executable, "-B", p], capture_output=True, text=True, timeout=600)
        esiti[nome] = r.returncode
        if r.returncode != 0:
            print(f"   AUTORIZZAZIONE NEGATA da «{nome}»:", flush=True)
            for riga in (r.stdout + r.stderr).strip().splitlines()[-6:]:
                print(f"      {riga}", flush=True)
            return None
    timbro = {"quando": int(time.time()),
              "impronta": impronta(file_da_pubblicare),
              "file": sorted(x for x in file_da_pubblicare if x not in ESCLUSI),
              "controlli": esiti}
    os.makedirs(os.path.dirname(TIMBRO), exist_ok=True)
    json.dump(timbro, open(TIMBRO, "w"), indent=1)
    print(f"   autorizzazione emessa: {len(OBBLIGATORI)} controlli passati, "
          f"{len(file_da_pubblicare)} file", flush=True)
    return timbro


def valida(file_da_pubblicare):
    """Vero solo se esiste un'autorizzazione recente per ESATTAMENTE questi file."""
    try:
        t = json.load(open(TIMBRO))
    except (OSError, ValueError):
        print("   NEGATA: non esiste nessuna autorizzazione. L'assenza nega, non permette.",
              flush=True)
        return False
    eta = time.time() - t.get("quando", 0)
    if eta > MASSIMA_ETA:
        print(f"   NEGATA: l'autorizzazione ha {eta/60:.0f} minuti (massimo {MASSIMA_ETA//60}). "
              f"Un via libera vecchio parla di un mondo che non c'e' piu'.", flush=True)
        return False
    atteso = impronta(file_da_pubblicare)
    if t.get("impronta") != atteso:
        print("   NEGATA: i file sono cambiati DOPO il controllo. L'autorizzazione vale per il "
              "contenuto esatto che e' stato controllato, non per il nome dei file.", flush=True)
        return False
    return True


if __name__ == "__main__":
    file_da_pubblicare = sys.argv[2:]
    if sys.argv[1] == "emetti":
        sys.exit(0 if emetti(file_da_pubblicare) else 1)
    sys.exit(0 if valida(file_da_pubblicare) else 1)
