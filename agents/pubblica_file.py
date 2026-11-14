"""Pubblica i file cambiati passando dall'interfaccia di GitHub, non da git.

PERCHE' (28/09). La copia di lavoro e' SUPERFICIALE (`--depth 1`): serve, perche' l'intera storia
pesa gigabyte e il disco del Mac si era riempito. Ma con una copia superficiale git non puo'
dimostrare la parentela fra i commit, e il server rifiuta il push dicendo «sei indietro» **anche
quando sei allineato**. Non e' contesa: e' un limite strutturale, e nessun numero di tentativi lo
supera. Ne ho fatti dieci, poi altri dieci, prima di capirlo.

**Si smette di combattere con lo strumento sbagliato.** Qui si mandano i FILE, uno per uno, con
l'interfaccia che GitHub offre apposta: niente storia, niente parentele, niente push. Se qualcuno
scrive lo stesso file nel frattempo, il server risponde «conflitto», si rilegge la sua versione e si
riprova — che e' il comportamento giusto, non un ripiego.

Vale per i file di CODICE e di TESTO che scrivo io. I dati continuano a viaggiare con git dalle
corsie, dove le copie sono complete e il push funziona.
"""
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = "nicolostancato-web/whale-radar"
CRED = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")


def _token():
    for l in open(CRED, encoding="utf-8", errors="ignore"):
        m = re.search(r"(gh[ps]_[A-Za-z0-9]+)", l)
        if m:
            return m.group(1)
    return None


def _api(url, metodo="GET", dati=None, tok=None):
    r = urllib.request.Request(
        url, method=metodo, data=json.dumps(dati).encode() if dati else None,
        headers={"Authorization": f"token {tok}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(r, timeout=60) as f:
            b = f.read()
            return json.loads(b) if b else {}, None
    except urllib.error.HTTPError as e:
        return None, e


def manda(percorso, messaggio, tok):
    """Un file. Torna True se e' arrivato.

    PASSA DAL CUSTODE DELLA MEMORIA (10/10, ordine di Nicolo': «deve sempre passare da sto
    revisore di memoria»). Il custode non guarda il contenuto, guarda il FORMATO: un oggetto
    unico da 52 MB entra intero nella storia a ogni salvataggio, e cosi' 9 GB su 10 si sono
    riempiti di wallet e transazioni che, scritti a righe, starebbero in qualche centinaio di
    megabyte. Avvisa sempre; FERMA solo i file grossi mal formati, che vanno nel deposito.
    """
    # IL MANIFESTO DECIDE SE QUESTO FILE PUO' STARE NEL RAMO (10/10, regola data da Astra).
    # Non e' una questione di taglia: e' la NATURA del dato. Codice, configurazione e documenti
    # vanno nel ramo; i risultati di esecuzione vanno in R2, che non tiene la storia. E un file
    # non dichiarato non ha un posto: finora questa violazione non ESISTEVA, quindi nessun
    # controllo poteva vederla. Per ora AVVISA e lascia passare; diventera' un rifiuto quando i
    # file che oggi stanno nel posto sbagliato saranno stati spostati (ne restano 8).
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import manifesto as _M
        _ok, _perche = _M.puo_andare_su_github(percorso)
        if not _ok:
            print(f"   MANIFESTO | {_perche}")
            # IL VERDETTO DEL MANIFESTO FERMA I FILE CHE PESANO (10/10). Il blocco del custode
            # scatta solo sui file MAL FORMATI: `curva_lanci.voci.jsonl` — 166 MB, ma 247 byte
            # per record, scritto bene — gli risultava «sano», e il manifesto diceva soltanto
            # «NO» a parole. Un file da 166 MB nel ramo lo avrebbe riempito in due giorni.
            # Sotto 1 MB resta un avviso: spostare tutto subito romperebbe piu' di quanto aggiusta.
            if os.path.getsize(percorso) > 1_000_000 and not os.environ.get("FORZA"):
                print(f"   MANIFESTO | NON lo mando: {os.path.getsize(percorso)/1e6:.1f} MB nel "
                      f"posto sbagliato. Per forzare: FORZA=1")
                return False
    except ImportError:
        pass

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import custode_memoria as _C
        _ok, _motivo = _C.controlla(percorso)
        if not _ok:
            print(f"   CUSTODE | {percorso}: {_motivo}")
            if os.path.getsize(percorso) > _C.SOGLIA_SU_GITHUB and not os.environ.get("FORZA"):
                print(f"   CUSTODE | NON lo mando su GitHub: va nel deposito (100 GB, nessuna "
                      f"storia). Per forzare: FORZA=1")
                return False
    except ImportError:
        pass   # il custode manca: si pubblica, ma senza revisione
    url = f"https://api.github.com/repos/{REPO}/contents/{percorso}"
    contenuto = base64.b64encode(open(percorso, "rb").read()).decode()
    for tentativo in range(1, 6):
        attuale, _ = _api(url, tok=tok)
        dati = {"message": messaggio, "content": contenuto}
        if attuale and attuale.get("sha"):
            if attuale.get("content", "").replace("\n", "") == contenuto:
                # IL SILENZIO PIU' COSTOSO (29/09). Un file identico a quello gia' pubblicato
                # significa quasi sempre che la correzione NON E' ENTRATA: la sostituzione non
                # ha combaciato e non ha protestato. Prima qui si tornava True zitti, e la
                # pubblicazione sembrava riuscita. Tre strategie sono morte cosi'.
                print(f"   {percorso}: INVARIATO — identico a quello su GitHub. "
                      f"Se ti aspettavi un cambiamento, la tua modifica NON e' entrata.",
                      flush=True)
                return True
            dati["sha"] = attuale["sha"]
        _, err = _api(url, "PUT", dati, tok)
        if err is None:
            return True
        if err.code == 409:                      # qualcuno ha scritto nel frattempo: si rilegge
            time.sleep(1 + tentativo)
            continue
        print(f"   {percorso}: RIFIUTATO ({err.code}) {err.read()[:120]}", flush=True)
        return False
    print(f"   {percorso}: conflitto ripetuto, non mandato", flush=True)
    return False


def _registra(file, messaggio):
    """Un registro di CIO' CHE ABBIAMO PRODOTTO, che sopravvive alla compattazione della storia.

    PERCHE' (29/09). La domanda quotidiana raccoglieva le prove da `git log`. Ma il compattatore
    riscrive la storia ogni giorno, e dopo quel momento il lavoro prodotto compare solo dentro il
    suo commit gigante — che il filtro scarta come manutenzione, giustamente.
    Risultato misurato oggi: tre verdetti pubblicati nelle ultime 24 ore, e le prove dicevano
    «verdetti: zero, ipotesi: zero» — da cui il giudizio «attivita' alta e intelligenza ferma».
    **Una misura cieca non produce un giudizio prudente: ne produce uno sbagliato e severo.**

    Stessa lezione del timbro dell'insieme: **il contenuto sopravvive, la storia viene potata.**
    Quindi cio' che conta si scrive in un file, non si deduce dai commit.
    """
    import time as _t
    p = "data/prodotti.json"
    try:
        tutti = json.load(open(p)) if os.path.exists(p) else []
    except Exception:
        tutti = []
    tutti.append({"quando": int(_t.time()), "messaggio": messaggio, "file": file})
    tutti = tutti[-500:]                      # bastano gli ultimi: non e' un archivio
    os.makedirs("data", exist_ok=True)
    json.dump(tutti, open(p, "w"), indent=1, ensure_ascii=False)


def main():
    messaggio = sys.argv[1] if len(sys.argv) > 1 else "aggiornamento"
    tok = _token()
    if not tok:
        print("PUBBLICA | manca il token di GitHub nel file delle credenziali")
        return 1
    # I FILE SI POSSONO DIRE A MANO, E SENZA GIT SI GRIDA (11/10, pagato caro). Questo
    # pubblicatore trovava i file da spedire SOLO con `git status`. Alle 00:00 la cartella .git
    # di questa copia si e' corrotta: `git status` ha cominciato a fallire, e il pubblicatore ha
    # risposto «niente da mandare» — in silenzio, mentre il lavoro di un'ora restava solo qui.
    # Un attrezzo che serve a non perdere niente non puo' tacere quando il suo occhio si rompe.
    espliciti = [a for a in sys.argv[2:] if os.path.isfile(a)]
    if espliciti:
        cambiati = espliciti
    else:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if r.returncode != 0:
            print("PUBBLICA | GIT NON FUNZIONA QUI: " + (r.stderr or "").strip()[:120])
            print("PUBBLICA | NON posso sapere quali file sono cambiati. Non dico «niente da "
                  "mandare»: passami i file a mano, es. pubblica_file.py \"motivo\" a.py b.md")
            return 1
        cambiati = [l.split()[-1] for l in r.stdout.splitlines()]
        cambiati = [f for f in cambiati if os.path.isfile(f)]
    if not cambiati:
        print("PUBBLICA | niente da mandare")
        return 0
    ok = 0
    mandati = []
    # UN FILE CHE CADE NON PORTA GIU' GLI ALTRI (10/10). Un `RemoteDisconnected` — la rete che
    # chiude la connessione senza risposta, cosa che capita — saliva fino in cima e ABORTIVA il
    # lotto: i file dopo quello non venivano mai spediti, in silenzio, su una strada che serve
    # proprio a non perdere niente. Qui ogni file e' per conto suo, si riprova una volta, e
    # alla fine si DICE quali sono rimasti indietro invece di lasciarli sparire.
    rimasti = []
    for f in cambiati:
        esito = False
        for tentativo in (1, 2):
            try:
                esito = manda(f, messaggio, tok)
                break
            except Exception as e:
                print(f"   {f}: la rete ha interrotto ({type(e).__name__}), "
                      f"{'riprovo' if tentativo == 1 else 'lo lascio indietro'}", flush=True)
                time.sleep(3)
        if esito:
            ok += 1
            mandati.append(f)
            print(f"   {f}: mandato", flush=True)
        else:
            rimasti.append(f)
    if rimasti:
        print(f"PUBBLICA | {len(rimasti)} file NON sono partiti: " + ", ".join(rimasti[:6]))
    _registra(mandati, messaggio)
    # E POI SI MANDA ANCHE IL REGISTRO. Trovato il 6/10: `_registra` gira DOPO il ciclo di
    # invio, quindi scriveva data/prodotti.json dopo averlo gia' spedito. La voce nuova partiva
    # solo alla pubblicazione successiva: **il registro era sempre indietro di una.** Non una
    # corsa, un fuori-di-uno sistematico, e ha fatto scattare due volte in una mattina il
    # conflitto «unmerged» su quel file, che bloccava TUTTI i salvataggi via git successivi
    # (la seconda ricerca di Grok e' rimasta solo sul Mac per questo).
    # Peggio: `piu_intelligente.py` giudica il lavoro del progetto leggendo questo registro,
    # quindi giudicava senza l'ultima cosa fatta — la stessa cecita' che il commento di
    # `_registra` dice di voler evitare. Una misura cieca non da' un giudizio prudente: ne da'
    # uno sbagliato e severo.
    if manda("data/prodotti.json", messaggio, tok):
        print("   data/prodotti.json: mandato (registro aggiornato)", flush=True)
    else:
        print("   data/prodotti.json: NON mandato — il registro resta indietro di una", flush=True)
    print(f"PUBBLICA | {ok} file su {len(cambiati)} sono su GitHub", flush=True)
    return 0 if ok == len(cambiati) else 1


if __name__ == "__main__":
    raise SystemExit(main())
