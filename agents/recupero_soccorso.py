"""Rimette dentro i dati salvati dalla rete di sicurezza, UNENDO invece di sovrascrivere.

PERCHE' ESISTE (27/09). Quando una corsia di raccolta non riesce a spingere, il suo lavoro esce
come allegato invece di morire col runner (vedi `vivo.yml`, passo «Rete di sicurezza»). Stanotte e'
successo davvero: 1,48 GB di blocchi in diretta salvati alle 04:13 che altrimenti non sarebbero
tornati.

MA UN SOCCORSO NON SI RIVERSA ADDOSSO AL PRESENTE. L'allegato e' una fotografia di quel momento:
da allora altre corsie hanno scritto, e altri scambi sono arrivati. Copiarlo sopra recupererebbe
il vecchio cancellando il nuovo — si chiamerebbe recupero e sarebbe una perdita.
**Si uniscono le righe, tenendo tutto quello che esiste da una parte o dall'altra.**

Le righe sono eventi immutabili: uno scambio identificato da (transazione, indice del log) e' lo
stesso fatto ovunque si trovi. Quindi l'unione e' sicura e l'ordine non conta.
"""
import glob
import gzip
import json
import os
import sys


def chiave(r):
    """Cosa rende unico uno scambio. La coppia (transazione, indice) e' l'identita' sulla catena."""
    tx, li = r.get("tx"), r.get("li")
    if tx is not None and li is not None:
        return (tx, li)
    return json.dumps(r, sort_keys=True)     # ripiego: la riga stessa


def leggi(p):
    try:
        with gzip.open(p, "rt") as f:
            return [json.loads(l) for l in f if l.strip()]
    except Exception:
        return []


ELENCO_TOCCATI = "/tmp/soccorso_toccati.txt"


def unisci(da_soccorso, dentro, solo=None):
    """Torna (file toccati, righe recuperate, righe gia' presenti).

    `solo`: se dato, si guardano SOLO questi file invece di tutto l'allegato.

    PERCHE' (27/09). Al primo giro si legge tutto: negli allegati vecchi sono 67.000 file e 30
    milioni di righe. Ma quelli con qualcosa di nuovo sono 199. Se il push viene rifiutato e
    bisogna rifare l'unione sullo stato piu' recente, rileggere gli altri 66.800 e' lavoro buttato:
    misurato, TRENTACINQUE minuti dentro l'unione invece di pochi secondi.
    Al primo giro si scopre quali file contano; dai tentativi dopo si guardano solo quelli.
    """
    toccati = recuperate = gia = 0
    nomi_toccati = []
    elenco = solo if solo is not None else sorted(
        glob.glob(os.path.join(da_soccorso, "**", "*.jsonl.gz"), recursive=True))
    for p in elenco:
        rel = os.path.relpath(p, da_soccorso)
        dest = os.path.join(dentro, rel)
        vecchie = leggi(p)
        if not vecchie:
            continue
        attuali = leggi(dest) if os.path.exists(dest) else []
        viste = {chiave(r) for r in attuali}
        nuove = [r for r in vecchie if chiave(r) not in viste]
        if not nuove:
            gia += len(vecchie)
            continue
        tutte = attuali + nuove
        # si riordina per istante: i file sono letti in ordine cronologico da chi analizza
        tutte.sort(key=lambda r: (r.get("ts", 0), r.get("li", 0)))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        # SI SCRIVE A FIANCO E POI SI SPOSTA: se il processo muore a meta', il file buono resta
        # quello di prima invece di diventare un troncone illeggibile.
        tmp = dest + ".nuovo"
        with gzip.open(tmp, "wt") as f:
            for r in tutte:
                f.write(json.dumps(r) + "\n")
        os.replace(tmp, dest)
        toccati += 1
        nomi_toccati.append(p)
        recuperate += len(nuove)
        gia += len(vecchie) - len(nuove)
    if solo is None:
        # si lascia scritto quali file contano: i tentativi dopo non rileggono tutto l'allegato
        with open(ELENCO_TOCCATI, "w") as f:
            f.write("\n".join(nomi_toccati))
    return toccati, recuperate, gia


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("uso: recupero_soccorso.py <cartella_soccorso> <cartella_destinazione>")
        raise SystemExit(2)
    solo = None
    if "--solo-toccati" in sys.argv and os.path.exists(ELENCO_TOCCATI):
        solo = [l for l in open(ELENCO_TOCCATI).read().split("\n") if l.strip()]
        print(f"RECUPERO | guardo solo i {len(solo)} file che al primo giro avevano qualcosa",
              flush=True)
    t, r, g = unisci(sys.argv[1], sys.argv[2], solo)
    print(f"RECUPERO | {t} file toccati, {r} righe RECUPERATE, {g} gia' presenti", flush=True)
    if r == 0:
        print("   (nessuna riga nuova: il soccorso era gia' rientrato per altra via)", flush=True)
