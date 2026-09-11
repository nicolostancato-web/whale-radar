#!/usr/bin/env python3
"""
SPERIMENTI_LOOP — la QUARTA corsia permanente: le idee.

PERCHE' ESISTE (09/09). Fin qui gli esperimenti giravano dentro il motore, un giro ogni due cicli.
Cioe' idee e accumulo si contendevano la stessa corsia: ogni minuto speso a misurare un'idea era un
minuto tolto ai dati che servono a misurarla. Il collo di bottiglia del progetto non e' avere una
buona idea — ne abbiamo una coda — e' quanto in fretta ognuna riceve il suo verdetto. Sette piste
chiuse in tre giorni lo dimostrano: le idee si bruciano in fretta, se le si lascia correre.

Adesso sono quattro processi indipendenti: motore (accumulo), ricerca (la percentuale per chain),
loop 0 (il controllore) e questo (le idee). Ognuno puo' morire senza portarsi dietro gli altri, e
nessuno ruba il tempo agli altri.

NON SI INIZIA UN CICLO CHE NON SI FINIREBBE: il controllo sul tempo si fa PRIMA di ogni giro, con il
margine di un ciclo intero. Un processo che sfora blocca il successore gia' in coda, e da fuori
sembra soltanto lentezza. E' gia' successo, e non si ripete.

€0: repo pubblico, GitHub Actions gratuite.
"""
import subprocess, os, time, signal

START = time.time()
MAX_RUNTIME = 4.5 * 3600
CICLO_TIPICO = 20 * 60
MINIMO_GIRO = 240      # un giro non puo' durare meno di 4 minuti: sotto, sta girando a vuoto
WR_PAT = os.environ.get("WR_PAT", "")
REPO = "nicolostancato-web/whale-radar"

# GLI ESPERIMENTI VIVI. I morti non stanno qui: rileggere una risposta che abbiamo gia' e' un ciclo
# pagato per niente. Quando uno muore si toglie e si prende il successivo dalla coda.
VIVI = [
    ("agents/liquidita_impegnata.py", 300),   # 7: i soldi che entrano contro il prezzo che sale
    ("agents/sperimentale.py", 320),          # il tritacarne delle idee fuori dal recinto
    ("agents/due_gambe.py", 180),             # il netto vale solo se misurato sulla sua chain
    ("agents/costo_chain.py", 180),
    ("agents/costo_evm.py", 280),
    ("agents/ritardo.py", 200),             # il segnale sopravvive al nostro ritardo?
    ("agents/esaurimento.py", 200),             # il segnale sopravvive al nostro ritardo?           # il costo vero su base e robinhood, dalla catena             # il netto vale solo se misurato sulla sua chain
    ("agents/staffetta.py", 120),             # il passaggio di consegne: sempre per ultimo, legge gli altri
]
# 8 (costo d'uscita) tolto: premessa caduta, 1161 eventi su 1161 sotto la soglia. I morti non si
# rilanciano — rileggere una risposta che abbiamo gia' e' un giro pagato per niente.

# QUANTO COSTA DAVVERO UN GIRO (09/09): dodici secondi per tutti e tre gli esperimenti. Il primo
# sospetto era che morissero all'avvio; il registro ha detto che no, girano e finiscono — sono
# semplicemente economici. Quindi la corsia NON e' satura: il collo di bottiglia non e' il calcolo,
# sono le idee da mettere dentro. Quando la coda si riempie, qui c'e' posto per venti esperimenti.


# NON BUTTARE VIA QUELLO CHE DICONO (09/09). Alla prima accensione questa corsia ha fatto 708 giri
# in 35 minuti: tre secondi a giro, cioe' gli esperimenti morivano all'avvio e io non potevo saperlo
# perche' mandavo uscita ed errori nel nulla. Un processo che gira a vuoto e' peggio di uno fermo:
# consuma minuti, riempie la storia di commit e da fuori sembra attivita'.
def sh(cmd, timeout=300):
    """Torna (codice, ultima riga detta). Il codice serve a capire, non solo ad andare avanti."""
    try:
        p = subprocess.Popen(cmd, shell=True, start_new_session=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except Exception as e:
        return -1, f"non parte: {type(e).__name__}"
    try:
        out, _ = p.communicate(timeout=timeout)
        righe = [r for r in (out or "").splitlines() if r.strip()]
        return p.returncode, (righe[-1][:120] if righe else "muto")
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL); p.wait(timeout=10)
        except Exception: pass
        return -9, "ucciso: fuori tempo"
    except Exception as e:
        return -1, f"{type(e).__name__}"


def commit(msg):
    subprocess.run('git config user.name "whale-radar-bot"; git config user.email '
                   '"bot@users.noreply.github.com"', shell=True)
    if subprocess.run(f'git add -A && git commit -m "sperimenti {msg}"', shell=True).returncode != 0:
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
        sh("git pull --no-rebase --no-edit -X theirs origin main", timeout=60)
        esiti = []
        for script, tetto in VIVI:
            if not os.path.exists(script):     # un esperimento tolto non deve fermare la corsia
                esiti.append((script, "assente", ""))
                continue
            if time.time() - START > MAX_RUNTIME - 60:
                break
            rc, ultima = sh(f"python {script}", timeout=tetto)
            esiti.append((script, "ok" if rc == 0 else f"codice {rc}", ultima))
        # IL REGISTRO DELLA CORSIA: se un esperimento smette di funzionare deve VEDERSI, non
        # sparire in silenzio dentro un giro che continua allegramente.
        righe = ["# 🧪 CORSIA SPERIMENTI — cosa e' successo nell'ultimo giro",
                 f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · giro {giro}*", "",
                 "| esperimento | esito | ultima cosa detta |", "|---|---|---|"]
        righe += [f"| `{s.split('/')[-1]}` | {e} | {u} |" for s, e, u in esiti]
        righe += ["", "> Un giro che dura pochi secondi non e' un giro veloce: e' un giro in cui",
                  "> nessuno ha lavorato. Per questo qui sotto c'e' anche quanto e' durato."]
        durata = time.time() - t0
        righe += [f"", f"*Durata del giro: **{durata:.0f} secondi**.*"]
        try:
            open("SPERIMENTI.md", "w").write("\n".join(righe))
        except Exception: pass
        commit(f"giro{giro} {time.strftime('%H:%MZ', time.gmtime())}")
        print(f"SPERIMENTI | giro {giro} in {durata:.0f}s | " +
              " ".join(f"{s.split('/')[-1]}:{e}" for s, e, _ in esiti), flush=True)
        giro += 1
        # PAVIMENTO DEL GIRO: se tutto e' finito in pochi secondi qualcosa non va, e continuare a
        # sbattere contro il muro il piu' in fretta possibile non aiuta nessuno.
        if durata < MINIMO_GIRO:
            time.sleep(MINIMO_GIRO - durata)
    if WR_PAT:
        subprocess.run(f'curl -s -X POST -H "Authorization: token {WR_PAT}" '
                       f'"https://api.github.com/repos/{REPO}/actions/workflows/sperimenti.yml/dispatches" '
                       f'-d \'{{"ref":"main"}}\'', shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("SPERIMENTI | ri-dispatchato", flush=True)


if __name__ == "__main__":
    main()
