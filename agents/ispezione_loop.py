#!/usr/bin/env python3
"""
ISPEZIONE_LOOP — il LOOP 0 come PROCESSO PERMANENTE, non come cron.

Perche' (31/08, dopo 3h40 di silenzio del loop 0): l'ispezione dipendeva da un cron orario di GitHub, e i
cron di GitHub SALTANO — e' successo tre volte in un giorno. I due presidi di riserva non hanno aiutato,
perche' un processo Python carica il proprio codice all'avvio: motore e ricerca stavano eseguendo la loro
versione vecchia, senza le chiamate all'ispezione. Risultato: il controllore taceva e nessuno lo sapeva.

Ora il LOOP 0 e' un processo suo, che gira in continuo come il motore e la ricerca: ispeziona ogni 15
minuti, committa, e alla fine del turno si ri-dispatcha da solo. Tre processi indipendenti, ognuno dei quali
puo' morire senza portarsi dietro gli altri — e questo e' quello che controlla che gli altri due lavorino.
€0 (repo pubblico).
"""
import subprocess, os, time, signal

START = time.time()
MAX_RUNTIME = 4.5 * 3600      # 4.5h e non 5.5: vedi sotto
CICLO_TIPICO = 15 * 60        # quanto puo' durare un ciclo nel caso peggiore
# NON SI INIZIA UN CICLO CHE NON SI FINIREBBE (04/09, gia' corretto nel motore, qui mancava).
# Il controllo sul tempo si faceva solo PRIMA di iniziare un giro, quindi l'ultimo poteva partire a
# 5h29 e finire oltre le 6h. E' successo davvero: un turno di ricerca e' rimasto "in esecuzione" per
# 8h54, oltre il suo stesso limite, tenendo occupata la corsia — e il successore, gia' in coda, non
# e' partito per ore. Un processo che sfora non e' solo lento: blocca chi viene dopo, e il danno e'
# doppio perche' da fuori sembra soltanto lentezza.
OGNI = 15 * 60                 # un'ispezione ogni 15 minuti: in questa fase vogliamo essere aggressivi
WR_PAT = os.environ.get("WR_PAT", "")
REPO = "nicolostancato-web/whale-radar"


def sh(cmd, timeout=200):
    try:
        p = subprocess.Popen(cmd, shell=True, start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL); p.wait(timeout=10)
        except Exception: pass
    except Exception: pass


def commit(msg):
    subprocess.run('git config user.name "whale-radar-bot"; git config user.email "bot@users.noreply.github.com"',
                   shell=True)
    if subprocess.run(f'git add -A && git commit -m "loop0 {msg}"', shell=True).returncode != 0:
        return
    for _ in range(5):
        subprocess.run('git pull --no-rebase --no-edit -X ours origin main', shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.run('git push origin main', shell=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return
        time.sleep(4)


def main():
    giro = 0
    while time.time() - START < MAX_RUNTIME - CICLO_TIPICO:
        t0 = time.time()
        sh("git pull --no-rebase --no-edit -X theirs origin main", timeout=60)  # leggi il lavoro degli altri
        sh("python agents/ispezione.py", timeout=200)
        sh("python agents/heartbeat.py", timeout=120)      # e controlla che il motore sia vivo
        commit(f"giro{giro} {time.strftime('%H:%MZ', time.gmtime())}")
        print(f"LOOP0 | ispezione {giro} fatta", flush=True)
        giro += 1
        dt = time.time() - t0
        if time.time() - START < MAX_RUNTIME:
            time.sleep(max(30, OGNI - dt))
    if WR_PAT:
        subprocess.run(f'curl -s -X POST -H "Authorization: token {WR_PAT}" '
                       f'"https://api.github.com/repos/{REPO}/actions/workflows/loop0.yml/dispatches" '
                       f'-d \'{{"ref":"main"}}\'', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("LOOP0 | ri-dispatchato", flush=True)


if __name__ == "__main__":
    main()
