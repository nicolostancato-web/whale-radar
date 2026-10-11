"""Esegue un agente su dati FINTI, per scoprire gli schianti prima di metterlo in cielo.

PERCHE' ESISTE (6/10). Ho aggiunto quattro righe a `dettaglio_candidati.py` usando una
variabile letta QUATTRO RIGHE DOPO. Il file compilava; la corsia e' morta all'esecuzione con
`NameError`, su venti macchine, buttando un giro intero.
E' la lezione che avevo scritto IO, tre ore prima, correggendo un residuo nello stesso modo:
«un file che compila non e' un file che gira». **Scriverla non e' bastato.**

Il motivo per cui non bastava: non avevo un modo ECONOMICO di eseguire il percorso toccato.
Gli agenti leggono decine di migliaia di file che non stanno sul mio disco, quindi «provarlo»
voleva dire aspettare un giro in cielo — e con quell'attesa in mezzo si finisce per pubblicare
e sperare. Questo file toglie la scusa: costruisce un insieme minimo e finto in una cartella
temporanea, e lancia l'agente la' dentro in pochi secondi.

Non verifica che i NUMERI siano giusti: verifica che il codice ARRIVI ALLA FINE. Sono due cose
diverse e questa e' la piu' economica delle due — ed e' quella che oggi e' mancata due volte.
"""
import gzip
import json
import os
import subprocess
import sys
import tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)


def costruisci(cartella, chain="base"):
    """Un insieme minimo ma COMPLETO: pool, scambi, firmatari, liste."""
    base = os.path.join(cartella, "data", "multichain", chain)
    os.makedirs(os.path.join(base, "storico"), exist_ok=True)
    pool = "0x" + "ab" * 20
    gettone = "0x" + "cd" * 20
    valuta = "0x4200000000000000000000000000000000000006"
    portafoglio = "0x" + "ef" * 20
    righe = [{"ts": 1000 + i, "tx": "0x%064d" % i,
              # segni alternati: meta' acquisti, meta' vendite
              "a0": (1 if i % 2 else -1) * 1000,
              "a1": (-1 if i % 2 else 1) * 2000,
              "w": "0x%040d" % i, "dex": 3} for i in range(8)]
    with gzip.open(os.path.join(base, "storico", f"{pool}.jsonl.gz"), "wt") as f:
        for r in righe:
            f.write(json.dumps(r) + "\n")
    json.dump({"coppie": {pool: {"t0": valuta, "t1": gettone, "dex": 3, "nato": 1}}},
              open(os.path.join(base, "coppie.json"), "w"))
    with gzip.open(os.path.join(base, "iniziatori.json.gz"), "wt") as f:
        json.dump({"da": {("0x%064d" % i): portafoglio for i in range(8)}}, f)
    with gzip.open(os.path.join(base, "insider.json.gz"), "wt") as f:
        json.dump({"da": {pool: [portafoglio]}}, f)
    with gzip.open(os.path.join(base, "arbitraggi.json.gz"), "wt") as f:
        json.dump({"da": [], "completo": True}, f)
    d = os.path.join(cartella, "data")
    json.dump({"da": {chain: [portafoglio]}}, open(os.path.join(d, "bravi.json"), "w"))
    json.dump({"da": {chain: [portafoglio]}},
              open(os.path.join(d, "candidati_vincenti.json"), "w"))
    return portafoglio


def prova(agente, chain="base", extra=None):
    with tempfile.TemporaryDirectory() as tmp:
        costruisci(tmp, chain)
        amb = dict(os.environ)
        amb.update({"CHAIN": chain, "BUDGET_SEC": "20", "PYTHONPATH": QUI,
                    "FETTE": "1", "FETTA": "0"})
        amb.update(extra or {})
        r = subprocess.run([sys.executable, os.path.join(QUI, agente)],
                           cwd=tmp, env=amb, capture_output=True, text=True, timeout=180)
        ok = r.returncode == 0
        print(f"  {agente:<34} {'ARRIVA ALLA FINE' if ok else 'SI SCHIANTA'}")
        if not ok:
            for l in (r.stderr or "").strip().splitlines()[-4:]:
                print(f"      {l}")
        return ok


def main():
    agenti = sys.argv[1:] or ["dettaglio_candidati.py", "profitto_persone.py",
                              "arbitraggi.py", "completezza.py", "ritardo_copia.py"]
    print("PROVA A SECCO | eseguo gli agenti su dati finti (non verifico i numeri, "
          "verifico che non si schiantino)")
    falliti = [a for a in agenti if not prova(a)]
    if falliti:
        print(f"\n  {len(falliti)} agenti si schiantano: {', '.join(falliti)}")
        print("  NON vanno messi in cielo cosi': un giro perso vale piu' di questa prova.")
    else:
        print(f"\n  tutti e {len(agenti)} arrivano alla fine")
    return 1 if falliti else 0


if __name__ == "__main__":
    sys.exit(main())
