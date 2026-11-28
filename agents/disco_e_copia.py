"""LA GUARDIA SUL DISCO E SULLA COPIA DI LAVORO.

== PERCHE' ESISTE (6/10/2026, secondo incidente dello stesso tipo) ==

Il disco del Mac e' arrivato a 93 MB liberi su 228 GB, e `git fetch` ha cominciato a fallire con
«Out of diskspace». Non e' la prima volta: il 5/10 un `gc` interrotto da disco pieno aveva
CORROTTO la copia di lavoro (mancavano HEAD e config) e l'avevo dovuta riparare a mano.

La causa non era un file grosso: era la copia stessa, 16 GB di cui 16 in `.git/objects`, mentre i
dati veri erano 134 MB. La copia nasce `--depth 1`, ma ogni `git fetch origin main` battuto a mano
ne APPROFONDISCE la storia: era arrivata a 1.694 commit, con tre pacchetti da 4,5 + 4,5 + 2,4 GB
in gran parte sovrapposti, piu' un `tmp_pack` da 5,2 GB lasciato da un repack abortito.
Ricreata da zero: **60 MB invece di 16 GB**.

== PERCHE' UNA GUARDIA E NON UNA REGOLA ==

La regola («non approfondire la copia») dipende dalla mia attenzione, e la mia attenzione su questa
cosa ha gia' fallito due volte in due giorni. Quando una regola e' stata violata due volte, serve
un MECCANISMO che la veda da solo. E' lo stesso motivo per cui esistono `non_salvato.sh` e
`rifai_copia.sh`.

Questa guardia non cancella niente: GUARDA e URLA. Cancellare mentre il disco e' pieno e' proprio
il gesto che corrompe le copie.

== COSA GUARDA ==

 1. lo spazio libero sul disco — sotto 2 GB git comincia a fallire, sotto 5 e' zona di rischio;
 2. la copia di lavoro: quanto pesa `.git` RISPETTO ai dati utili, e quanti commit ha di storia
    (una copia superficiale sana ne ha pochi);
 3. i resti dei repack abortiti (`tmp_pack_*`), che sono spazzatura pura e vanno via a mano.
"""
import os
import shutil
import subprocess
import sys

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBERO_ROSSO = 2.0      # GB: sotto questa soglia git fallisce
LIBERO_GIALLO = 5.0     # GB
COMMIT_MAX = 50         # una copia superficiale sana; a 1.694 pesava 16 GB
RAPPORTO_MAX = 20       # .git non deve pesare piu' di 20 volte i dati utili


def _gb(n):
    return n / (1024 ** 3)


def _comando(args):
    try:
        r = subprocess.run(args, cwd=QUI, capture_output=True, text=True, timeout=60)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def _peso(p):
    tot = 0
    for radice, _, file in os.walk(p):
        for f in file:
            try:
                tot += os.path.getsize(os.path.join(radice, f))
            except OSError:
                pass
    return tot


def main():
    problemi = []

    libero = _gb(shutil.disk_usage(QUI).free)
    if libero < LIBERO_ROSSO:
        problemi.append(f"GRAVE  disco a {libero:.2f} GB liberi: git FALLISCE sotto i 2 GB, e un "
                        f"fetch o un gc interrotto qui CORROMPE la copia (succede il 5/10)")
    elif libero < LIBERO_GIALLO:
        problemi.append(f"disco a {libero:.1f} GB liberi: zona di rischio, sotto i 2 si rompe")
    else:
        print(f"DISCO E COPIA | {libero:.1f} GB liberi")

    gitdir = os.path.join(QUI, ".git")
    if not os.path.isdir(gitdir):
        print("DISCO E COPIA | non sono in una copia git: non ho niente da guardare")
        return 0

    resti = []
    pacchi = os.path.join(gitdir, "objects", "pack")
    if os.path.isdir(pacchi):
        resti = [f for f in os.listdir(pacchi) if f.startswith("tmp_pack")]
    if resti:
        peso = sum(os.path.getsize(os.path.join(pacchi, f)) for f in resti)
        problemi.append(f"GRAVE  {len(resti)} resti di repack abortito ({_gb(peso):.1f} GB): "
                        f"spazzatura pura, togliere con "
                        f"`rm -f .git/objects/pack/tmp_pack_* .git/gc.log`")

    p_git = _peso(gitdir)
    p_dati = _peso(os.path.join(QUI, "data")) if os.path.isdir(os.path.join(QUI, "data")) else 0
    n = _comando(["git", "rev-list", "--count", "HEAD"])
    n = int(n) if n and n.isdigit() else None
    superficiale = os.path.exists(os.path.join(gitdir, "shallow"))

    print(f"DISCO E COPIA | .git {_gb(p_git):.2f} GB, dati utili {_gb(p_dati):.2f} GB, "
          f"storia {n if n is not None else '?'} commit"
          f"{' (superficiale)' if superficiale else ''}")

    if superficiale and n is not None and n > COMMIT_MAX:
        problemi.append(f"la copia e' nata superficiale ma ha {n:,} commit di storia: ogni "
                        f"`git fetch origin main` la APPROFONDISCE. A 1.694 commit pesava 16 GB. "
                        f"Rifarla: clone --depth 1 --filter=blob:none --sparse (60 MB)")
    if p_dati > 0 and p_git > RAPPORTO_MAX * p_dati:
        problemi.append(f".git pesa {p_git/p_dati:.0f} volte i dati utili: pacchetti sovrapposti, "
                        f"la copia va rifatta invece di ripulita (un gc a disco pieno la rompe)")

    if not problemi:
        print("DISCO E COPIA | spazio e copia di lavoro in salute")
        return 0
    for x in problemi:
        print(f"   {x}")
    # non blocca la pubblicazione: con il disco pieno NON pubblicare e' peggio che pubblicare,
    # perche' quello che non e' pubblicato e' esattamente quello che si perde (lezione del 25/09).
    return 0


if __name__ == "__main__":
    sys.exit(main())
