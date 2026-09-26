"""SOCIAL LOOP — tiene la corsia social viva dall'interno, invece di sperare in un orologio.

PERCHE' (16/09, scoperto alla prima ora di vita dell'esperimento). Il piano era: un giro ogni dieci
minuti via cron, cosi' la finestra T+5m si misura in tempo. Misurato: in 33 minuti il cron non e'
scattato NEMMENO UNA VOLTA. GitHub limita pesantemente le pianificazioni frequenti sul piano
gratuito, e su un repo occupato le salta proprio.

Non e' un dettaglio di infrastruttura. Se le misure arrivano tardi, la finestra T+5m viene marcata
PERSA ogni singola volta: l'esperimento continuerebbe a girare, i file crescerebbero, e la parte
piu' interessante — cosa succede nei primi minuti — sarebbe sistematicamente vuota. Un
esperimento che si svuota da solo senza fallire e' il modo peggiore di perdere tempo.

Quindi il ritmo se lo tiene da dentro: un giro solo, che resta vivo cinquanta minuti e misura ogni
due, e alla fine si riarma. Lo stesso mestiere che fanno gia' le altre corsie del progetto.
"""
import os
import subprocess
import time

DURATA = int(os.environ.get("DURATA_SEC", 3000))     # cinquanta minuti, poi si riarma
OGNI = int(os.environ.get("OGNI_SEC", 120))
t0 = time.time()


def esegui(comando, ambiente=None, tempo_massimo=600):
    amb = dict(os.environ)
    if ambiente:
        amb.update(ambiente)
    try:
        p = subprocess.run(comando, shell=True, capture_output=True, text=True,
                           timeout=tempo_massimo, env=amb)
        ultima = [l for l in (p.stdout or "").strip().split("\n") if l.strip()]
        return p.returncode, (ultima[-1] if ultima else (p.stderr or "")[:150])
    except subprocess.TimeoutExpired:
        return -1, "tempo scaduto"
    except Exception as e:
        return -1, f"{type(e).__name__}: {e}"


def salva(etichetta):
    subprocess.run('git config user.name "whale-radar-bot"; git config user.email '
                   '"bot@users.noreply.github.com"', shell=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if subprocess.run(f'git add -A data/social && git commit -m "social {etichetta}"', shell=True,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        return False
    for _ in range(8):
        subprocess.run("git pull --no-rebase --no-edit -X ours origin main", shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.run("git push origin main", shell=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return True
        time.sleep(6)
    print("SOCIAL_LOOP | ATTENZIONE: non sono riuscito a spingere", flush=True)
    return False


def main():
    giro = 0
    ultimo_salvataggio = time.time()
    while time.time() - t0 < DURATA:
        giro += 1
        # la rilevazione si autolimita da sola: se non sono passate sei ore, esce subito
        rc_s, out_s = esegui("python agents/social_snapshot.py", tempo_massimo=400)
        rc_e, out_e = esegui("python agents/social_outcome.py",
                             {"BUDGET_SEC": "90"}, tempo_massimo=150)
        if "rilevazione" not in out_s or "aspetto" not in out_s:
            print(f"SOCIAL_LOOP | giro {giro} | {out_s[:110]}", flush=True)
        print(f"SOCIAL_LOOP | giro {giro} | {out_e[:110]}", flush=True)

        # SI SALVA SPESSO, non alla fine: se il runner viene sfrattato a meta' — succede, e oggi
        # e' gia' costato ottanta minuti di coda viva — quello che si perde e' solo l'ultimo pezzo.
        if time.time() - ultimo_salvataggio > 420:
            salva(f"giro {giro} {time.strftime('%H:%MZ', time.gmtime())}")
            ultimo_salvataggio = time.time()

        resta = DURATA - (time.time() - t0)
        if resta <= 0:
            break
        time.sleep(min(OGNI, max(5, resta)))
    salva(f"fine {time.strftime('%H:%MZ', time.gmtime())}")
    print(f"SOCIAL_LOOP | finito dopo {giro} giri in {(time.time()-t0)/60:.0f} minuti", flush=True)


if __name__ == "__main__":
    main()
