#!/usr/bin/env python3
"""
RICERCA_LOOP — il TEAM DI RICERCA, che gira IN PARALLELO al motore.

Perche' separato: esploratore e ricercatore sono i due ruoli pesanti (4-5 minuti ciascuno). Tenendoli dentro
il motore, un ciclo passava da 30 a oltre 60 minuti — e i MEETING si diradavano: il team si riuniva la meta'
delle volte. Ma su repo pubblico i job paralleli sono gratis. Quindi: il motore resta magro e veloce (meeting,
controlli, verbali ogni ~30 min), la ricerca gira qui a tutta forza senza rallentare nessuno.

Loop 5.5h con auto-riavvio, come il motore. Alterna le chain. €0.
"""
import subprocess, os, time, signal

START = time.time()
MAX_RUNTIME = 4.5 * 3600      # 4.5h e non 5.5: vedi sotto
CICLO_TIPICO = 30 * 60        # quanto puo' durare un ciclo nel caso peggiore
# NON SI INIZIA UN CICLO CHE NON SI FINIREBBE (04/09, gia' corretto nel motore, qui mancava).
# Il controllo sul tempo si faceva solo PRIMA di iniziare un giro, quindi l'ultimo poteva partire a
# 5h29 e finire oltre le 6h. E' successo davvero: un turno di ricerca e' rimasto "in esecuzione" per
# 8h54, oltre il suo stesso limite, tenendo occupata la corsia — e il successore, gia' in coda, non
# e' partito per ore. Un processo che sfora non e' solo lento: blocca chi viene dopo, e il danno e'
# doppio perche' da fuori sembra soltanto lentezza.
WR_PAT = os.environ.get("WR_PAT", "")
REPO = "nicolostancato-web/whale-radar"
# tutte e quattro: BSC e' la peggiore (-31%) ma resta nel giro — una chain esclusa dalla ricerca
# e' una chain che non miglioreta mai, e non possiamo saperlo in anticipo.
CHAINS = ("base", "solana", "robinhood", "bsc")


def sh(cmd, env=None, timeout=300):
    e = dict(os.environ); e.update(env or {})
    try:
        p = subprocess.Popen(cmd, shell=True, env=e, start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL); p.wait(timeout=15)
        except Exception: pass
    except Exception: pass


def commit(msg):
    subprocess.run('git config user.name "whale-radar-bot"; git config user.email "bot@users.noreply.github.com"', shell=True)
    if subprocess.run(f'git add -A && git commit -m "ricerca {msg}"', shell=True).returncode != 0:
        return
    for _ in range(5):
        subprocess.run('git pull --no-rebase --no-edit -X ours origin main', shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.run('git push origin main', shell=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return
        time.sleep(5)


def main():
    giro = 0
    while time.time() - START < MAX_RUNTIME - CICLO_TIPICO:
        ch = CHAINS[giro % len(CHAINS)]
        if ch == "robinhood":
            # Robinhood ha un pipeline suo (piu' ricco): si ottimizza con l'explorer dedicato, altrimenti
            # cercheremmo ovunque tranne che sulla chain messa meglio
            sh("python agents/explorer_rh.py", {"BUDGET_SEC": "300"}, timeout=340)
        else:
            sh("python agents/explorer.py", {"CHAIN": ch, "BUDGET_SEC": "300"}, timeout=340)
        sh("python agents/team_ricerca.py", {"CHAIN": ch, "BUDGET_SEC": "300"}, timeout=340)
        # I DUE PROCESSI SI SORVEGLIANO A VICENDA: i cron di GitHub saltano (l'heartbeat non girava da 4h),
        # quindi non ci affidiamo solo a loro. Ogni 4 giri la ricerca controlla che il motore sia vivo — e
        # il motore, dal canto suo, e' quello che tiene in vita la ricerca. Nessuno dei due e' solo.
        # COSTI REALI: misura quanto costa DAVVERO entrare e uscire (Jupiter, gratis). Il 15% che
        # assumevamo non era mai stato verificato: la prima misura dice 4% a $25 e 26% a $500.
        if giro % 3 == 0:
            sh("python agents/costi_reali.py",
               {"MAX_TOKEN": "25", "BUDGET_SEC": "260", "SORGENTE": "ricerca"}, timeout=300)
        if giro % 4 == 0:
            sh("python agents/heartbeat.py", timeout=120)
            sh("python agents/ispezione.py", timeout=120)   # e si controlla che TUTTO il team stia lavorando
        commit(f"{ch} giro{giro} {time.strftime('%H:%MZ', time.gmtime())}")
        print(f"RICERCA_LOOP | giro {giro} su {ch} fatto", flush=True)
        giro += 1
    if WR_PAT:
        subprocess.run(f'curl -s -X POST -H "Authorization: token {WR_PAT}" '
                       f'"https://api.github.com/repos/{REPO}/actions/workflows/ricerca.yml/dispatches" '
                       f'-d \'{{"ref":"main"}}\'', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
