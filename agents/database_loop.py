#!/usr/bin/env python3
"""
DATABASE_LOOP — la QUINTA corsia: il TERRENO.

PERCHE' ESISTE (14/09, idea di Nicolo). Le altre quattro corsie costruiscono e misurano; nessuna si
occupa del terreno su cui poggiano. I difetti trovati nell'audit — l'embargo che azzerava il 92%
delle feature, i 4.083 file orfani su Robinhood, la join al 9% — erano li' da SETTIMANE e non hanno
mai fatto rumore: li ha trovati un audit a mano, perche' e' stato chiesto.

Questa corsia fa due cose, in continuo:
  1. RACCOGLIE cio' che evapora (i primi scambi dei token appena nati);
  2. CONTROLLA che quello che entra serva a qualcosa — e lo dice ad alta voce quando non serve.

La differenza col motore: il motore raccoglie fra le altre cose. Qui la raccolta e' l'unica cosa, e
c'e' un guardiano che giudica il risultato invece di contare i file.

I NUMERI CHE GIUSTIFICANO QUESTA CORSIA (misurati il 14/09):
  - facciamo ~11.700 interrogazioni al giorno;
  - il tetto della fonte gratuita e' 43.200 al giorno PER INDIRIZZO IP;
  - GitHub concede fino a 20 lavori in parallelo su repo pubblico, ognuno con IP diverso.
Usiamo il 27% di un solo indirizzo. Il collo di bottiglia non era la fonte: era la nostra
architettura sequenziale.

€0: repo pubblico, minuti GitHub gratuiti e illimitati, nessuna API a pagamento.
"""
import subprocess, os, time, signal
import json
import gzip

START = time.time()
MAX_RUNTIME = 4.5 * 3600
CICLO_TIPICO = 15 * 60
MINIMO_GIRO = 180
WR_PAT = os.environ.get("WR_PAT", "")
REPO = "nicolostancato-web/whale-radar"
FETTA = os.environ.get("FETTA", "0")     # quale porzione di lavoro tocca a questa corsia


def sh(cmd, env=None, timeout=300):
    e = dict(os.environ); e.update(env or {})
    try:
        p = subprocess.Popen(cmd, shell=True, env=e, start_new_session=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except Exception as ex:
        return -1, f"non parte: {type(ex).__name__}"
    try:
        out, _ = p.communicate(timeout=timeout)
        righe = [r for r in (out or "").splitlines() if r.strip()]
        return p.returncode, (righe[-1][:130] if righe else "muto")
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL); p.wait(timeout=10)
        except Exception: pass
        return -9, "ucciso: fuori tempo"
    except Exception as ex:
        return -1, type(ex).__name__


def commit(msg):
    subprocess.run('git config user.name "whale-radar-bot"; git config user.email '
                   '"bot@users.noreply.github.com"', shell=True)
    if subprocess.run(f'git add -A && git commit -m "database {msg}"', shell=True).returncode != 0:
        return
    for _ in range(6):
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
        # 1. RACCOLTA — prima cio' che evapora: gli scambi dei token giovani
        for ch in ("robinhood", "base", "solana"):
            if time.time() - START > MAX_RUNTIME - 120: break
            rc, ult = sh("python agents/multichain_trades.py",
                         {"CHAIN": ch, "BUDGET_SEC": "150", "TRADE_BATCH": "120"}, timeout=200)
            esiti.append((f"scambi {ch}", rc, ult))
        rc, ult = sh("python agents/pulse.py", {"BUDGET_SEC": "150"}, timeout=200)
        esiti.append(("battito", rc, ult))
        # 2. CONTROLLO — quello che e' entrato serve a qualcosa?
        # l'elenco dei pool che diventano righe: serve al collettore dello storico per scavare
        # solo dove puo' nascere una riga. Va rifatto spesso, perche' ogni ora ne nascono di nuovi.
        # LA CODA VIVA NON E' PIU' QUI (15/09, poche ore dopo averla messa). L'avevo infilata in
        # cima a questo giro perche' e' l'unico dato che potra' essere certificato — preso mentre
        # succede, ritardo di minuti invece che di settimane — e non volevo rischiare di saltarla.
        # Poi le ho dato una corsia sua (vivo.yml), e per qualche ora ha girato in tutte e due:
        # DUE SCRITTORI SULLA STESSA CARTELLA, che la regola 3 vieta da sempre e per un motivo —
        # due processi che raccolgono gli stessi blocchi si sovrascrivono a vicenda spingendo, e il
        # doppione non si vede perche' i due record sono identici.
        # Sta nella corsia sua, che non divide il tempo con nient'altro. Qui si controlla soltanto
        # che sia viva: se tace, il guardiano lo dice, ma nessuno raccoglie al posto suo.
        # IL RECUPERO DELLE NASCITE (16/09). Le fette non tornano sui propri passi: un pool scoperto
        # dopo che sono passate dal suo blocco di nascita resta senza storia per sempre. Su robinhood
        # sono 354 pool su 768 — il 46% — ed e' la ragione principale per cui l'audit trova solo il
        # 16% di finestre identiche. Lavora a morsi, col segnalibro delle fasce gia' fatte, quindi
        # ogni giro ne chiude qualcuna e non ricomincia mai da capo.
        # (il recupero nascite e' passato in una corsia sua, nascite.yml: qui aveva 420 secondi a
        # giro e chiudeva una fascia ogni sei giri — ottanta ore — rubando tempo ai controlli.)
        # LO SCOPRITORE PER PRIMO (16/09). Chiede alla catena quali pool nascono, invece di
        # chiederlo a un'API che ci mette ore. Prima di lui, nelle ultime 24 ore erano nati 16.514
        # pool su robinhood e il nostro registro ne conosceva CINQUE — mentre noi diciamo di
        # studiare le prime sei ore di vita. Arrivavamo sempre dopo la festa.
        # Va per primo perche' tutto il resto lavora sulla lista che produce lui.
        for ch in ("robinhood", "base"):
            rc, ult = sh("python agents/scopritore.py", {"CHAIN": ch, "BUDGET_SEC": "150"}, timeout=200)
            esiti.append((f"scopritore {ch}", rc, ult))
        # LE COPPIE DI TOKEN (condizione 6, 16/09). Senza, «a0 = 13497419610956700000000» e' un
        # numero senza unita': non si sa di quale token si parla ne' con quante cifre decimali va
        # letto. Eravamo a zero. Si accumula da sola: i pool gia' noti si saltano.
        # IL TEMPO VA A CHI E' INDIETRO (18/09). Erano 240 secondi fissi per chain. Ma robinhood e'
        # al 91% dei pool attivi del censimento e base al 28%: stavo dando lo stesso tempo a chi ha
        # quasi finito e a chi ha 4.300 pool da risolvere. A quel ritmo base ci metteva giorni
        # mentre robinhood ripassava su lavoro gia' fatto.
        # La quota si calcola da quanto manca DAVVERO a ciascuna, con un minimo perche' nessuna si
        # fermi del tutto (le coppie nuove nascono di continuo su entrambe).
        _resta = {}
        for ch in ("robinhood", "base"):
            try:
                _c = json.load(open(f"data/multichain/{ch}/coppie.json")).get("coppie", {})
                _note = {k.lower() for k in _c}
                _n = 0
                with gzip.open(f"data/multichain/{ch}/censimento.jsonl.gz", "rt") as _f:
                    for _l in _f:
                        if not _l.strip():
                            continue
                        _d = json.loads(_l)
                        if _d.get("scambi", 0) >= 20 and _d["pool"] not in _note:
                            _n += 1
                _resta[ch] = _n
            except Exception:
                _resta[ch] = 1
        _tot = sum(_resta.values()) or 1
        for ch in ("robinhood", "base"):
            _q = int(max(90, min(420, 510 * _resta[ch] / _tot)))
            rc, ult = sh("python agents/coppie_token.py", {"CHAIN": ch, "BUDGET_SEC": str(_q)},
                         timeout=_q + 60)
            esiti.append((f"coppie token {ch} ({_resta[ch]} da fare, {_q}s)", rc, ult))
        rc, ult = sh("python agents/elenco_righe.py", timeout=280)
        esiti.append(("elenco righe", rc, ult))
        rc, ult = sh("python agents/integrita.py", {"INTEGRITA_FINESTRE": "10"}, timeout=300)
        esiti.append(("integrita", rc, ult))
        # IL CENSIMENTO, PRIMA ANCORA (17/09, rilievo della revisione esterna). L'«universo
        # indipendente» costruito dall'evento Initialize vede SOLO i pool V4: misurato, zero pool
        # con indirizzo su entrambe le chain, e il 99% del nostro stesso registro ASSENTE da
        # quell'universo. Non era l'universo della chain: era la lista dei V4 nati di recente — e
        # ci avevamo calcolato sopra la copertura «vera», la sopravvivenza e l'accusa di
        # autoreferenzialita' al 97%.
        # Il censimento guarda i log di SWAP su un intervallo dichiarato: ogni pool che ha
        # scambiato ha emesso un log, quale che sia la sua versione. E' completo per costruzione
        # per tutto cio' che conta, e chi non ha mai scambiato non ci serve.
        for ch in ("robinhood", "base"):
            rc, ult = sh("python agents/censimento.py",
                         {"CHAIN": ch, "BUDGET_SEC": "200", "GIORNI": "3"}, timeout=250)
            esiti.append((f"censimento {ch}", rc, ult))
        # LA NASCITA VERA, PRIMA DI TUTTO IL RESTO (17/09). Le candele dicono quando GeckoTerminal
        # si e' ACCORTO di un pool, non quando il pool e' nato: errore mediano +20 ore sui primi
        # 142 misurati, +38 sul lotto dopo, e oltre tre quarti dei casi FUORI dalla finestra di sei
        # ore che diciamo di conservare. Con quel punto di partenza, «le prime sei ore» sono le
        # prime sei ore di un altro momento — e ci contano dentro l'audit di integrita', la
        # classificazione delle esclusioni e la misura «nascite possedute».
        # Va per primo perche' ogni altro controllo lavora su quella data.
        for ch in ("robinhood", "base"):
            rc, ult = sh("python agents/nascita_vera.py", {"CHAIN": ch, "BUDGET_SEC": "220"}, timeout=270)
            esiti.append((f"nascita vera {ch}", rc, ult))
        # LA BONIFICA DELL'ORARIO (16/09, secondo rilievo della revisione esterna). Stamattina ho
        # riparato chi PRODUCE l'istante e ho scritto un documento sul difetto. Il revisore ha fatto
        # notare la cosa ovvia che non avevo visto: documentare un difetto non e' ripararlo. I
        # record gia' scritti hanno ancora l'orario sbagliato — scarto mediano misurato 41,9 minuti
        # — e con quello hanno gia' deciso la propria classe.
        # Il campo `blocco` e' esatto, quindi l'istante vero si recupera sempre. Va a morsi.
        for ch in ("robinhood", "base"):
            rc, ult = sh("python agents/ripara_orario.py", {"CHAIN": ch, "BUDGET_SEC": "200"}, timeout=250)
            esiti.append((f"ripara orario {ch}", rc, ult))
        # LA CANONICITA' (16/09, primo rilievo della revisione esterna). Un record di un blocco
        # riorganizzato ha istante giusto, chiave giusta, quantita' giuste — e racconta una cosa
        # che la catena non ricorda piu'. L'audit di integrita' non lo chiamerebbe «inventato».
        # Prima misura: 2.700 blocchi robinhood e 208 base, zero orfani. Continua a guardare.
        for ch in ("robinhood", "base"):
            rc, ult = sh("python agents/canonicita.py", {"CHAIN": ch, "BUDGET_SEC": "180"}, timeout=230)
            esiti.append((f"canonicita {ch}", rc, ult))
        rc, ult = sh("python agents/qualita_db.py", timeout=280)
        esiti.append(("qualita del terreno", rc, ult))
        # LA SOPRAVVIVENZA (condizione 7, 16/09). Campiona a caso dall'universo preso dalla catena
        # i pool che NON abbiamo, e classifica perche': mai scambiato, sotto soglia, scoperto tardi.
        # Finora il conteggio si faceva sul nostro registro, cioe' si chiedeva al filtro di
        # giudicare se' stesso. Lavora a morsi: la finestra di vita e' 216.000 blocchi e in un giro
        # se ne fa un terzo, quindi il conteggio parziale sopravvive fra un giro e l'altro.
        for ch in ("robinhood", "base"):
            rc, ult = sh("python agents/sopravvivenza.py", {"CHAIN": ch, "BUDGET_SEC": "200"}, timeout=250)
            esiti.append((f"sopravvivenza {ch}", rc, ult))
        rc, ult = sh("python agents/coorte.py", {"COORTE_MAX": "20"}, timeout=200)
        esiti.append(("coorte", rc, ult))

        durata = time.time() - t0
        righe = ["# 🧱 CORSIA DATABASE — il terreno",
                 f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · giro {giro} · fetta {FETTA}*", "",
                 "| passo | esito | ultima cosa detta |", "|---|---|---|"]
        righe += [f"| {n} | {'ok' if c == 0 else f'codice {c}'} | {u} |" for n, c, u in esiti]
        righe += ["", f"*Durata del giro: **{durata:.0f} secondi**.*", "",
                  "> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che",
                  "> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a",
                  "> niente, qui e' un fallimento."]
        try: open(f"DATABASE_CORSIA.md", "w").write("\n".join(righe))
        except Exception: pass
        commit(f"giro{giro} {time.strftime('%H:%MZ', time.gmtime())}")
        print(f"DATABASE | giro {giro} in {durata:.0f}s | " +
              " ".join(f"{n}:{'ok' if c == 0 else c}" for n, c, _ in esiti), flush=True)
        giro += 1
        if durata < MINIMO_GIRO: time.sleep(MINIMO_GIRO - durata)
    if WR_PAT:
        subprocess.run(f'curl -s -X POST -H "Authorization: token {WR_PAT}" '
                       f'"https://api.github.com/repos/{REPO}/actions/workflows/database.yml/dispatches" '
                       f'-d \'{{"ref":"main"}}\'', shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("DATABASE | ri-dispatchata", flush=True)


if __name__ == "__main__":
    main()
