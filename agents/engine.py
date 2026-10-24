#!/usr/bin/env python3
"""
ENGINE — il MOTORE UNICO del sistema. Gira in LOOP per ~5.5h eseguendo i reparti IN SEQUENZA, poi si ri-dispatcha
da solo (heartbeat continuo). Nasce perche' i CRON di GitHub Actions sono inaffidabili su repo con molti workflow
(li salta -> reparti fermi 9-15h). Con UN solo processo che gira sempre, GitHub deve gestire 1 avvio invece di 20 cron.
Piu' lento (sequenziale) ma STABILE (scelta di Nicolo: meglio lento e inchiodato che veloce e rotto). €0.
Ogni ciclo (~30min): cattura nuovi pool (il dato che scorre via). Ogni 4 cicli (~2h): storico + calcolo + demo-live.
"""
import subprocess, os, time, signal

START = time.time()


def _impronta_codice():
    """Un'impronta di tutti gli agenti: se cambia, il codice sul repo non e' piu' quello che sto
    eseguendo io. Serve perche' PUBBLICARE NON E' ATTIVARE: python carica i moduli all'avvio, quindi
    un agente nuovo committato adesso restava fermo fino al prossimo riavvio — che poteva essere fra
    cinque ore. E' successo abbastanza volte da smettere di essere un caso: meglio che se ne accorga
    il motore da solo invece che io, ogni volta, guardando i verbali che non arrivano."""
    import hashlib, glob as _g
    h = hashlib.sha256()
    for f in sorted(_g.glob("agents/*.py")):
        try: h.update(open(f, "rb").read())
        except Exception: pass
    return h.hexdigest()


IMPRONTA = _impronta_codice()
MAX_RUNTIME = 4.5 * 3600      # gira 4.5h poi si ri-dispatcha (job GitHub max 6h)
CICLO_TIPICO = 60 * 60        # quanto dura un ciclo nel caso peggiore
# PIU' CARBURANTE AI COLLECTOR (05/09): avevano 110 secondi a testa dentro cicli da ~50 minuti,
# cioe' un quinto del tempo speso a raccogliere e il resto a ragionare su quello che avevamo gia'.
# Ma il verdetto e' bloccato dai DATI, non dal ragionamento: la fascia di validazione di Robinhood
# ha 59 token e finche' non cresce il test sigillato non puo' nemmeno partire.
# Non cambia nessuna regola e nessuna soglia: aumenta solo quanto raccogliamo. E' l'unico modo
# onesto di accelerare un verdetto — tutti gli altri sarebbero aiutare il risultato.
# PERCHE' 4.5h E NON 5.5h (04/09): il controllo sul tempo si faceva solo PRIMA di iniziare un ciclo,
# quindi l'ultimo ciclo poteva iniziare a 5h29 e finire a 6h. Il motore #71 e' arrivato a 5h48 e nel
# frattempo teneva occupata la corsia: il turno successivo, gia' dispatchato, e' rimasto in coda
# un'ora senza poter partire, e con lui il codice nuovo che aspettava di girare.
# Un processo che sfora non e' solo lento: blocca il suo successore, e il danno e' doppio.
CYCLE_SEC = 30 * 60           # un ciclo completo ogni ~30 min
WR_PAT = os.environ.get("WR_PAT", "")
REPO = "nicolostancato-web/whale-radar"


def sh(cmd, env=None, timeout=200):
    """Esegue un reparto. Al timeout uccide TUTTO il gruppo di processi: con shell=True il timeout di
    subprocess.run ammazzava solo la shell e lasciava il python figlio orfano a macinare CPU nel runner,
    rallentando progressivamente ogni ciclo successivo."""
    e = dict(os.environ); e.update(env or {}); e.setdefault("SHARD", "-1")   # niente shard: 1 processo sequenziale
    try:
        p = subprocess.Popen(cmd, shell=True, env=e, start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        return
    try:
        p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            p.wait(timeout=15)
        except Exception:
            pass
    except Exception:
        pass


def commit(msg):
    subprocess.run('git config user.name "whale-radar-bot"; git config user.email "bot@users.noreply.github.com"', shell=True)
    r = subprocess.run(f'git add -A && git commit -m "engine {msg}"', shell=True)
    if r.returncode != 0:
        return
    for _ in range(5):
        subprocess.run('git pull --no-rebase --no-edit -X ours origin main', shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.run('git push origin main', shell=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return
        time.sleep(4)


def main():
    cycle = 0
    while time.time() - START < MAX_RUNTIME - CICLO_TIPICO:   # non iniziare un ciclo che non finiresti
        t0 = time.time()
        # === PRIMA I GUARDIANI (veloci): cosi' i verbali sono sul repo entro pochi minuti, non dopo 90.
        # Un meeting che si tiene ma di cui nessuno legge il verbale e' come non tenerlo.
        # --- TAPPA 1: i guardiani VELOCI (girano in secondi). Commit SUBITO, cosi' i verbali sono
        #     leggibili in pochi minuti. Prima erano in fila coi reparti pesanti e il commit arrivava
        #     dopo ~20 minuti: se il motore veniva riavviato prima, i verbali non uscivano affatto.
        sh("python agents/auditor.py", timeout=90)        # stiamo barando?
        sh("python agents/team_security.py", timeout=90)  # niente credenziali nel repo pubblico
        sh("python agents/team_cfo.py", timeout=90)       # tutto continua a costare zero?
        sh("python agents/goal_base.py", timeout=120)     # la catena del forward Base
        sh("python agents/conoscenza.py", timeout=60)     # cosa ha imparato il team
        sh("python agents/proposte.py", timeout=60)       # cosa aspetta una decisione
        sh("python agents/loop_engine.py", timeout=300)   # I MEETING + l'architetto
        sh("python agents/team_meeting.py", timeout=60)   # il verbale della riunione
        # LOOP 0 — l'ispezione non si ferma MAI. Ha il suo workflow orario e la lancia anche la ricerca,
        # ma se il referto invecchia oltre i 75 minuti la rilancia anche il motore: tre presidi
        # indipendenti, perche' un ispettore che tace e' peggio di un guasto (non lo vedresti nemmeno).
        try:
            eta = (time.time() - os.path.getmtime("ISPEZIONE.md")) / 60 if os.path.exists("ISPEZIONE.md") else 999
        except Exception:
            eta = 999
        if eta > 75:
            sh("python agents/ispezione.py", timeout=150)
        commit(f"verbali{cycle} {time.strftime('%H:%MZ', time.gmtime())}")
        # --- TAPPA 2: i pesanti (dati freschi e misure lunghe), poi si committa di nuovo
        sh("python agents/pulse.py", timeout=200)         # polso dei token giovani
        sh("python agents/sicurezza_token.py",
           {"MAX_TOKEN": "40", "BUDGET_SEC": "280"}, timeout=320)   # si puo' vendere? chi lo controlla?
        sh("python agents/deployer.py", timeout=90)      # chi ha creato il token e i suoi precedenti
        sh("python agents/censimento.py", timeout=180)   # ogni pool ha uno stato: morto o non raccolto?
        sh("python agents/mortalita.py", timeout=120)     # quanti token muoiono e spariscono
        sh("python agents/percentuale.py", timeout=200)   # com'e' FATTA la percentuale
        sh("python agents/validatore.py", timeout=240)    # regge su dati MAI VISTI?
        commit(f"misure{cycle} {time.strftime('%H:%MZ', time.gmtime())}")
        # === OGNI CICLO: cattura i NUOVI pool (i primi trade scorrono via in fretta) ===
        # candele+pool nuovi: BASE PRIORITARIO (ogni ciclo) per sbloccare il demo forward, poi le altre a rotazione
        # DOVE VA LA BANDA (06/09). Era: base due volte, le altre una. Sbagliato — su Base ci sono
        # 1.463 token nati dopo il sigillo e SETTE giudicabili: la resa peggiore, con la fetta piu'
        # grande. Robinhood e Solana ne hanno 46 e 33.
        # Le prove NON si sommano fra chain: sei giornate su Solana piu' sei su BSC non fanno dodici,
        # sono due mercati diversi. Servono 25 prove su CIASCUNA, quindi dividere in quattro parti
        # uguali significa aver bisogno di cento prove invece di venticinque.
        # Due chain e non una: un segnale che regge su Solana E su Robinhood — mercati con
        # microstruttura diversa — e' evidenza molto piu' forte di uno che regge su una sola. Non e'
        # prudenza, e' un test piu' severo.
        # Base e BSC non si spengono: restano in sottofondo, e se maturano le testiamo.
        # TRE CHAIN, NON QUATTRO (06/09). BSC abbandonata: e' la peggiore su tutto (-21% media,
        # -24% robusta, 14% di trade in guadagno) e la piu' povera di token giudicabili.
        # Restano Base, Robinhood e Solana perche' sono TRE MERCATI DIVERSI — microstrutture,
        # ecosistemi e tipi di token diversi — e lo strumento che cerchiamo potrebbe esistere in uno
        # solo dei tre. Tre possibilita' vere valgono piu' di quattro mezze.
        for ch in ("robinhood", "solana", "base", "robinhood", "solana", "base"):
            # BUDGET_SEC 110 < timeout 130: il collector chiude da solo e SALVA il checkpoint (prima veniva killato)
            sh("python agents/multichain_collector.py", {"CHAIN": ch, "BUDGET_SEC": "180"}, timeout=210)
        for ch in ("robinhood", "solana", "base"):
            sh("python agents/multichain_trades.py", {"CHAIN": ch, "BUDGET_SEC": "170"}, timeout=200)
        sh("python agents/solana_helius.py", {"BUDGET_SEC": "290"}, timeout=320)                 # giorno-0 Solana (Helius)
        for ch in ("base",):
            sh("python agents/multichain_rpc.py", {"CHAIN": ch, "BUDGET_SEC": "230"}, timeout=260)   # giorno-0 EVM
        # === OGNI 4 CICLI (~2h): storico Robinhood + CALCOLO + demo-live ===
        # ROBINHOOD HA FAME DI CANDELE (05/09). E' la chain con la configurazione congelata, quindi
        # quella che decide se il test sigillato potra' mai parlare: ha 2.824 pool noti e candele per
        # 725. Il collo di bottiglia non era la velocita' dell'API — era che l'agente ha bisogno di
        # ~4 minuti e il motore gliene dava 3, quindi veniva ucciso a meta' a ogni giro.
        # Ora ha il tempo che gli serve e gira il DOPPIO delle volte: non cambia nessuna regola,
        # aumenta solo il carburante. E' l'unico modo onesto di accelerare un verdetto.
        if cycle % 2 == 0:
            # GLI DICO QUANTO TEMPO HA (08/09). Prima gli davo 320 secondi senza dirglielo: lui ne
            # chiedeva ~500 per il suo lotto e veniva ucciso a meta', perdendo il segnalibro e
            # rifacendo ogni volta gli stessi pool. Ora sa il tetto e si ferma prima, salvando.
            sh("python agents/whale_candles.py", env={"CANDLE_SECONDI": "300"}, timeout=320)
        # GLI ESPERIMENTI GIRANO PIU' SPESSO (08/09). Stavano nel blocco "ogni 4 cicli", cioe' una
        # volta ogni 2-3 ore: e' il ritmo con cui si BRUCIANO le idee, ed e' il vero collo di
        # bottiglia del progetto. Le altre cose di quel blocco (storico, arricchimenti) possono
        # aspettare; un esperimento che aspetta e' un giorno di scadenza sprecato.
        # GLI ESPERIMENTI HANNO UNA CORSIA LORO (09/09). Stavano qui e rubavano tempo all'accumulo
        # che serve a misurarli: ogni minuto speso su un'idea era un minuto tolto ai dati che la
        # devono giudicare. Ora girano in sperimenti_loop.py, in parallelo. Il motore torna a fare
        # una cosa sola: portare dentro i dati.
        if False:
            sh("python agents/sperimentale.py", timeout=300)
            # I MORTI NON SI RILANCIANO (08/09). flussi_obbligati ha avuto il suo verdetto su 29
            # eventi: -2,8% contro i giorni normali, criterio di morte scattato. Tenerlo nel giro
            # sarebbe pagare ogni ciclo per rileggere una risposta che gia' abbiamo. Il posto
            # nella rotazione va all'idea successiva della coda, sempre.
            # esperimento 6 chiuso (la barriera non si vede nei prezzi): il posto passa al 7,
            # che sta ancora accumulando i giorni indipendenti che gli servono per il verdetto.

        if cycle % 4 == 0:
            for a in ("whale_backfill", "whale_enrich", "first_buyers"):
                sh(f"python agents/{a}.py", timeout=180)
            sh("python agents/wallet_insider.py", {"CHAIN": "solana"}, timeout=180)   # angolo insider (Solana)
            # il creator su Solana: 5% di copertura contro il 99% di BSC, e senza quel campo la
            # pista della reputazione su Solana non si puo' nemmeno testare.
            sh("python agents/solana_creator.py", {"MAX_TOKEN": "80", "BUDGET_SEC": "240"}, timeout=300)
            # --- LE PISTE APERTE DOPO LA CONSULENZA DEL 02/09 ---
            # COSTO VERO DI USCITA: il numero da cui dipende ogni altro verdetto, e girava solo a mano.
            sh("python agents/costi_reali.py",
               {"MAX_TOKEN": "25", "BUDGET_SEC": "260", "SORGENTE": "engine"}, timeout=300)
            # RUBRICA: collega pool e token su tutto l'archivio. Non aggiunge dati nuovi, rende
            # utilizzabili quelli che abbiamo gia' — meta' erano due mezzi dati che non si parlavano.
            sh("python agents/rubrica.py", {"BUDGET_SEC": "240"}, timeout=300)
            sh("python agents/costo_modello.py", timeout=90)   # misura e modello devono dire lo stesso
            sh("python agents/curva_costo.py", timeout=200)   # quanto costa uscire secondo la liquidita' vera
            # i token da cui non si esce: vanno marcati PRIMA che le strategie li contino come
            # uscite normali, altrimenti un -100% viene registrato come uno stop a -40%.
            sh("python agents/trappole.py", timeout=90)
            sh("python agents/verdetto.py", timeout=60)   # riuscito, avanti, o chiuso?
            sh("python agents/costo_fuga.py", timeout=90)   # il riassunto delle fughe misurate
            # la lettura UNICA dell'holdout: si rifiuta da sola se i dati non bastano o se e'
            # gia" stata fatta. Meglio non leggere che leggere male: la lettura e' una sola.
            sh("python agents/test_sigillato.py", {"CHAIN": "robinhood"}, timeout=200)
            sh("python agents/disponibilita.py", timeout=200)   # il segnale era usabile in quel momento?
            _ch = ("robinhood", "solana", "base")[(cycle // 4) % 3]
            sh("python agents/creator_gate.py", {"CHAIN": _ch, "MAX_TOKEN": "1500"}, timeout=200)
            sh("python agents/wallet_skill.py", {"CHAIN": _ch, "MAX_TOKEN": "900"}, timeout=280)
            sh("python agents/flusso_cluster.py", {"CHAIN": _ch, "MAX_TOKEN": "700"}, timeout=280)
            sh("python agents/secondo_stadio.py", {"CHAIN": _ch, "MAX_TOKEN": "700"}, timeout=300)
            # LOOP SPERIMENTALE: le idee fuori dal recinto. Gira qui perche' non dipende da una
            # chain sola — guarda il rapporto FRA le chain, che e' cieco a tutti e tre gli
            # esploratori di LOOP 1.
            # quanti acquisti spariscono dal rendimento senza che ce ne accorgiamo
            sh("python agents/acquisti_non_contati.py", {"CHAIN": _ch}, timeout=200)
            # COMMIT QUI (04/09): il blocco di coda dura quasi un'ora e prima committava solo alla
            # fine. Se il turno veniva interrotto a meta' — ed e' successo — si perdeva TUTTO il
            # lavoro delle piste, che e' la parte piu' lenta e piu' preziosa. Un'ora di calcoli che
            # non lascia traccia e' come non averla fatta.
            commit(f"piste{cycle} {time.strftime('%H:%MZ', time.gmtime())}")
            for a in ("multichain_brain", "edge_eval", "learner",
                      "strategy_optimizer", "strategy_optimizer_base", "strategy_optimizer_solana",
                      "demo_live", "demo_live_base", "health_audit"):
                sh(f"python agents/{a}.py", timeout=180)
        commit(f"cycle{cycle} {time.strftime('%H:%MZ', time.gmtime())}")
        print(f"ENGINE | ciclo {cycle} fatto in {int(time.time()-t0)}s", flush=True)
        # CODICE NUOVO SUL REPO? si riparte subito invece di aspettare la fine del turno.
        # Un agente pubblicato e non attivo e' peggio di un agente assente: sembra che ci sia.
        subprocess.run("git pull --no-rebase --no-edit -X ours origin main", shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # RIPARTIRE SI', MA DOPO AVER LAVORATO (corretto 04/09).
        # La prima versione ripartiva a OGNI cambio di codice. Sembrava zelo, era autolesionismo: chi
        # costruisce pubblica ogni ora, quindi il motore si riavviava ogni ora, rifaceva da capo il
        # ciclo 0 — che e' il piu' pesante — e non arrivava MAI in fondo al blocco delle piste.
        # Cinque turni in poche ore, e nessuno che finisse il lavoro. In piu' ogni riavvio occupa la
        # coda e teneva ferma la ricerca.
        # Un sistema che si aggiorna in continuazione e non conclude niente e' peggio di uno un po'
        # vecchio che porta a casa il risultato.
        if cycle >= 2 and _impronta_codice() != IMPRONTA:
            print("ENGINE | codice nuovo e almeno due cicli fatti: mi ri-dispatcho", flush=True)
            break
        cycle += 1
        dt = time.time() - t0
        if time.time() - START < MAX_RUNTIME:
            time.sleep(max(30, CYCLE_SEC - dt))                           # riempi fino a 30min

    # heartbeat: ri-dispatcha il motore per le prossime 5.5h (niente buchi)
    if WR_PAT:
        subprocess.run(
            f'curl -s -X POST -H "Authorization: token {WR_PAT}" '
            f'"https://api.github.com/repos/{REPO}/actions/workflows/engine.yml/dispatches" '
            f'-d \'{{"ref":"main"}}\'', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("ENGINE | ri-dispatchato per il prossimo turno", flush=True)


if __name__ == "__main__":
    main()
