"""Riparte davvero dal deposito, in una cartella vuota. Non un checksum: un ripristino.

PERCHE' ESISTE (1/10, rilievo di Astra). Il deposito verificava la copia riscaricandola e
confrontando l'impronta. Astra: «"verificata" puo' significare soltanto che il file trasferito
ha lo stesso hash. Questo non prova che siano stati salvati tutti gli oggetti necessari, che
sia la versione giusta, che esistano catalogo e credenziali di recupero, che un ambiente nuovo
sappia ripartire da quel deposito. **La prova decisiva e' un ripristino in ambiente pulito.**»

Aveva ragione: non avevamo mai provato a RIPARTIRE. Qui si scarica in una cartella vuota e si
verifica che il sistema restaurato sappia fare il suo mestiere — non che i byte coincidano.
"""
import os
import shutil
import subprocess
import sys
import tempfile

QUI_RADICE = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# I pezzi senza i quali non si riparte. Se uno manca, il deposito e' una speranza, non una copia.
INDISPENSABILI = [
    "agents/decisioni.py", "agents/autorizzazione.py", "agents/lezioni.py",
    "agents/insieme.py", "agents/combinazioni.py", "agents/prova_avanti.py",
    "agents/memoria_conversazione.py", "pubblica.sh",
    "PROVA_IN_AVANTI.md", "DECISIONS.md",
    "data/memoria/parole_del_fondatore.jsonl.gz",
    "data/loop1/modello_congelato.json",
]


def main():
    import deposito as D
    dove = tempfile.mkdtemp(prefix="ripristino_")
    print(f"RIPRISTINO | cartella vuota: {dove}", flush=True)
    if D.ritira_cartella("memoria.tar.gz", dove) is None:
        print("   FALLITO: non sono riuscito a ritirare la memoria dal deposito", flush=True)
        sys.exit(1)
    n = sum(len(f) for _, _, f in os.walk(dove))
    print(f"   ritirati {n} file", flush=True)

    mancanti = [p for p in INDISPENSABILI if not os.path.exists(os.path.join(dove, p))]
    if mancanti:
        print(f"   FALLITO: dal deposito mancano {len(mancanti)} pezzi indispensabili:",
              flush=True)
        for p in mancanti[:10]:
            print(f"      {p}", flush=True)
        sys.exit(1)

    # LA PROVA VERA: il sistema restaurato sa ancora fare il suo mestiere?
    # Non «i byte coincidono», ma «le decisioni si possono ancora verificare da qui».
    r = subprocess.run([sys.executable, "-B", "agents/decisioni.py"],
                       cwd=dove, capture_output=True, text=True, timeout=300)
    riga = next((x for x in r.stdout.splitlines() if x.startswith("DECISIONI |")), "")
    if not riga:
        print("   FALLITO: dal ripristino non riesco nemmeno a verificare le decisioni", flush=True)
        print((r.stdout + r.stderr)[-400:], flush=True)
        sys.exit(1)
    print(f"   il sistema restaurato funziona: {riga}", flush=True)

    parole = os.path.join(dove, "data/memoria/parole_del_fondatore.jsonl.gz")
    import gzip as _gz
    q = sum(1 for _ in _gz.open(parole, "rt", encoding="utf-8"))
    print(f"   la memoria del fondatore e' li': {q:,} messaggi", flush=True)
    # SI LASCIA LA PROVA, CON LA DATA (1/10). Una prova riuscita una volta e mai piu' ripetuta
    # e' indistinguibile da una mai fatta: qui resta la data, e chi legge sa quanto e' vecchia.
    import json as _j, time as _t
    _j.dump({"quando": int(_t.time()), "file": n, "messaggi_fondatore": q},
            open(os.path.join(os.path.dirname(QUI_RADICE), "data", "ripristino_provato.json")
                 if False else "data/ripristino_provato.json", "w"), indent=1)
    print("RIPRISTINO | RIUSCITO: da una cartella vuota il sistema riparte.", flush=True)
    shutil.rmtree(dove, ignore_errors=True)


if __name__ == "__main__":
    main()
