"""Un lucchetto per gli agenti lenti: due copie dello stesso lavoro non si fanno.

PERCHE' ESISTE (11/10). La ricerca di Grok ha prodotto DUE file per la stessa domanda, a tre
minuti di distanza: avevo lanciato l'agente a mano e nel frattempo la maglia l'ha lanciato
anche lei. Due consulenze per una domanda sola — e con un modello a pagamento sarebbe stato
denaro doppio, non solo disordine.

Astra lo aveva scritto fra le regole di coordinamento: «una sola esecuzione attiva per
produttore; se arriva un nuovo ciclo mentre quello precedente e' aperto, NON parte una seconda
copia». Questo e' quel pezzo, nella forma piu' piccola che funziona.

COME: un file con dentro il numero del processo e l'ora. Chi arriva dopo controlla se quel
processo e' ancora vivo: se si', si tira indietro dicendolo; se no — perche' il processo e'
morto male e il lucchetto e' rimasto chiuso — lo scavalca, perche' un lucchetto che non si apre
piu' e' peggio del doppione che doveva evitare.
"""
import json
import os
import sys
import time

CARTELLA = "data/lucchetti"


def _strada(nome):
    return os.path.join(CARTELLA, f"{nome}.json")


def _vivo(pid):
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def prendi(nome, ore_massime=3.0):
    """(True, nota) se il lavoro si puo' fare, (False, motivo) se c'e' gia' qualcuno."""
    os.makedirs(CARTELLA, exist_ok=True)
    p = _strada(nome)
    if os.path.exists(p):
        try:
            d = json.load(open(p))
        except (json.JSONDecodeError, OSError):
            d = {}
        pid, quando = d.get("pid"), d.get("quando", 0)
        eta = (time.time() - quando) / 3600
        if pid and _vivo(pid) and eta < ore_massime:
            return False, (f"c'e' gia' il processo {pid} che lo sta facendo da {eta*60:.0f} "
                           f"minuti: non ne lancio un secondo")
        # il lucchetto e' vecchio o il processo e' morto: lo scavalco, dicendolo
        if pid:
            motivo = ("il processo e' morto senza liberarlo" if not _vivo(pid)
                      else f"e' aperto da {eta:.1f}h, oltre il massimo di {ore_massime}h")
            print(f"LUCCHETTO | {nome}: scavalco il lucchetto del processo {pid} ({motivo})",
                  flush=True)
    json.dump({"pid": os.getpid(), "quando": int(time.time())}, open(p, "w"))
    return True, "lucchetto mio"


def lascia(nome):
    try:
        os.remove(_strada(nome))
    except OSError:
        pass


if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else "prova"
    ok, perche = prendi(nome)
    print(("LIBERO | " if ok else "OCCUPATO | ") + perche)
    if ok:
        lascia(nome)
    sys.exit(0 if ok else 1)
