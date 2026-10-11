"""RICERCA VENDITORI — chi vende forte nei crolli, e da dove prende i gettoni.

IDEA DI NICOLO' (10/10): «Grok mettiamolo a vedere chi vende forte e da dove prendono
le monete.» La nostra misura dice che i crolli sono folla (90 venditori, il piu' grosso
al 10%) e che i gettoni NON vengono dal primo minuto: quindi la domanda aperta e'
proprio da dove vengono. Questo programma la porta fuori, con i nostri numeri dentro
le domande, cosi' la risposta puo' smentirci invece di compiacerci.
LA RICERCA DI DUE SETTIMANE SULL'ALTRO MONDO: i gettoni ricevuti PRIMA della nascita.

== IL MANDATO (Nicolo', 6/10/2026) ==

«Adesso ci basiamo sul 50% NON nascosto affinche' i dati divengano veritieri. Pero' e' interessante
far girare sempre Grok per accumulare piu' informazioni possibili. Grok in loop deve salvare un
sacco di informazioni su sta roba, perche' magari noi decidiamo di prendere sta strada fra due
settimane. Ecco, Grok ha fatto due settimane di ricerche veramente profonde: dobbiamo sapere tutto,
i link, come si entra, come fa. Magari vediamo che se facciamo delle operazioni, dei bridge cosi',
abbiamo un sacco di gettoni — pero' quello li' e' da fare investigation. E fra due settimane, se
dobbiamo andare nella strada dei 50 nascosti, noi abbiamo una marcia incredibile in piu' perche' e'
due settimane che Grok prende su informazioni.»

Quindi: **questa ricerca NON guida le decisioni di adesso.** Accumula. Il lavoro di adesso e' il
50% che vediamo. Questo e' il vantaggio che vogliamo avere GIA' PRONTO se fra due settimane
serve cambiare strada.

== PERCHE' UN PROGRAMMA DI STUDIO E NON UNA DOMANDA ==

Una domanda sola, ripetuta ogni giorno, torna la stessa risposta e non accumula niente. Il 6/10
ho chiesto a Grok «come si procurano i gettoni» e ha risposto bene — ma una seconda volta avrebbe
ridetto lo stesso. Quindi qui c'e' un ELENCO di domande, ognuna su un pezzo diverso del mondo, e
ogni giro prende la prossima mai fatta. In due settimane le finisce tutte e il fascicolo c'e'.

Il registro di cio' che e' stato chiesto sta in data/ricerca_prelancio.json, cosi' i giri non si
ripetono nemmeno dopo un riavvio.

== COSTO ==

ZERO: passa da `consulta_grok.py`, cioe' dall'abbonamento gia' pagato. Mai dalla chiave a consumo
di xAI — pagare due volte la stessa cosa e' l'errore che ci e' costato 77 euro con Google a
maggio, e il 5/10 ho riaccesso per sbaglio una corsia a consumo proprio su questo.
IMPORTANTE: il programma `grok` e' autenticato sul Mac di Nicolo'. Questa ricerca gira SOLO da
qui, non da GitHub Actions. Non farne una corsia nel cielo: la corsia userebbe la chiave a
consumo, che e' il difetto appena descritto.
"""
import glob
import json
import os
import subprocess
import sys
import time

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRO = os.path.join(QUI, "data", "ricerca_venditori.json")
# DOVE SCRIVE, DICHIARATO IN UN POSTO SOLO (10/10, richiesta di Nicolo': «bisogna
# essere bravi a dirgli di scrivere in un punto e poi noi dobbiamo andare a vedere
# dove scrive»). Prima le ricerche finivano nella radice del repo, mescolate a tutto
# il resto: trovarle era un lavoro. Ora hanno una cartella loro, dichiarata nel
# manifesto, e a fine giro questo agente STAMPA il percorso del file che ha scritto.
CARTELLA = os.path.join(QUI, "ricerca", "venditori")
MIN_ORE = float(os.environ.get("MIN_ORE", "3"))   # non piu' di una ogni 3 ore

# Il programma di studio. Ogni voce: (nome del file, la domanda).
# Ordinate per quanto servono se fra due settimane si cambia strada: prima COME SI ENTRA, poi
# quanto rende, poi i casi particolari.
PROGRAMMA = [
    ("da_dove_prendono_i_gettoni",
     "Su una blockchain EVM dove una moneta nasce su una curva (bonding curve) e poi si diploma "
     "in un pool Uniswap v4, quali sono le strade DOCUMENTATE con cui un indirizzo si trova in "
     "mano una quantita' grande di quella moneta SENZA averla comprata nel pool nel primo "
     "minuto? Elenca i meccanismi concreti e come si riconoscono on-chain: acquisto sulla curva "
     "prima del diploma, allocazione al creatore, trasferimento da un altro indirizzo, "
     "distribuzione automatica, pre-vendita, airdrop, operazioni del contratto della curva. "
     "Per ognuno: quale evento o traccia lascia sulla chain, e come si distingue dagli altri. "
     "Link alla documentazione o al codice del contratto, non riassunti."),
    ("chi_vende_in_un_crollo",
     "Letteratura e analisi pubbliche sul profilo di chi vende durante il crollo di una memecoin "
     "appena quotata: quanti indirizzi distinti partecipano tipicamente, quanto pesa il piu' "
     "grosso, e se esistono studi che misurano la concentrazione delle vendite. Mi interessa il "
     "CONFRONTO con la nostra misura: su 28 crolli di monete appena diplomate abbiamo trovato in "
     "mediana ~90 venditori distinti, il piu' grosso al 10,3% del venduto, e solo il 2% del "
     "venduto proveniente da chi aveva comprato nel primo minuto. Questi numeri sono in linea "
     "con quello che si sa, o siamo noi a misurare male? Se esistono misure diverse, dammi i "
     "numeri e la fonte."),
    ("i_gettoni_del_creatore",
     "Nei lanciatori di memecoin con curva (pump.fun e simili, piu' le implementazioni EVM al "
     "2026): quanta parte dell'offerta resta al creatore o al contratto, con quali blocchi "
     "temporali (vesting), e come si verifica on-chain se quei gettoni sono stati venduti. "
     "Esistono casi documentati in cui il crollo post-diploma e' stato causato dallo sblocco di "
     "quella quota? Numeri, date, indirizzi se pubblici."),
    ("come_si_segue_un_venditore",
     "Dato un indirizzo che ha venduto molto durante un crollo, quali passaggi concreti "
     "permettono di stabilire DA DOVE arrivavano i suoi gettoni, usando solo chiamate a un nodo "
     "pubblico (eth_getLogs, Transfer, traces): la sequenza esatta di query, i limiti pratici, e "
     "gli errori tipici (indirizzi di router e di aggregatori che sembrano persone, trasferimenti "
     "interni invisibili nei log, approvazioni che non sono trasferimenti). Dimmi anche cosa NON "
     "si puo' ricostruire e perche'."),
    ("i_venditori_ricorrenti",
     "Esistono strumenti o studi pubblici che identificano indirizzi che vendono ripetutamente "
     "nei primi minuti di molte monete diverse sulla stessa chain (venditori di professione, "
     "market maker, bot di uscita)? Come si distingue statisticamente un venditore ricorrente da "
     "uno occasionale, e quanti sono tipicamente su una chain nuova? Fonti e numeri."),
]

CORNICE = """Sei un ricercatore che prepara un fascicolo per una decisione che verra' presa fra
due settimane. Non devi convincere nessuno: devi far risparmiare due settimane a chi leggera'.

REGOLE DEL FASCICOLO:
 · ogni affermazione ha un LINK a una fonte primaria (documentazione, contratto, annuncio
   ufficiale). Niente riassunti di riassunti.
 · i numeri hanno la data e la fonte. Se un numero non si puo' avere, scrivi che non si puo'
   avere e perche' — non stimarlo.
 · se la risposta e' «questa cosa non esiste» o «non e' accessibile a chiunque», dillo per primo:
   una chiusura documentata vale quanto una scoperta, perche' evita settimane di lavoro.
 · meglio tre cose verificabili che quindici nominate.
 · alla fine, due righe: COSA USEREI DOMANI e COSA NON VALE LA PENA.

LA DOMANDA DI OGGI:

"""


def _metti_al_sicuro(f):
    """Il documento su GitHub SUBITO, per l'interfaccia e non per git.

    PERCHE'. `consulta_grok` salva con git (commit + pull --rebase + push), e il 6/10 ha
    fallito due volte di fila: un conflitto irrisolto su data/prodotti.json bloccava ogni
    commit successivo, e la seconda ricerca e' rimasta solo sul Mac. Una rete di sicurezza che
    dipende dallo stato dell'indice di git non e' una rete: e' lo stesso ramo che si sta segando
    (lezione del 25/09, qui per la terza volta).
    `pubblica_file.py` passa dall'interfaccia di GitHub e non tocca git: non puo' essere bloccato
    da un conflitto locale.
    """
    r = subprocess.run([sys.executable, os.path.join(QUI, "agents", "pubblica_file.py"),
                        f"ricerca: {os.path.basename(f)}"],
                       cwd=QUI, capture_output=True, text=True, timeout=600)
    ok = "sono su GitHub" in (r.stdout or "")
    print(f"RICERCA | {'al sicuro su GitHub' if ok else 'NON messa al sicuro: ' + (r.stdout or r.stderr or '')[-200:]}",
          flush=True)
    return ok


def _registro():
    if os.path.exists(REGISTRO):
        try:
            return json.load(open(REGISTRO))
        except Exception:
            pass
    return {"fatte": [], "ultima": 0}


def main():
    r = _registro()
    ore = (time.time() - r.get("ultima", 0)) / 3600
    if ore < MIN_ORE:
        print(f"RICERCA | l'ultima e' di {ore:.1f} ore fa (minimo {MIN_ORE}): non ne chiedo "
              f"un'altra. {len(r['fatte'])}/{len(PROGRAMMA)} domande fatte.")
        return 0

    resta = [(n, d) for n, d in PROGRAMMA if n not in r["fatte"]]
    if not resta:
        print(f"RICERCA | il programma e' finito: tutte e {len(PROGRAMMA)} le domande sono state "
              f"fatte e salvate. Per allargarlo, aggiungere voci a PROGRAMMA.")
        return 0
    nome, domanda = resta[0]
    print(f"RICERCA | domanda {len(r['fatte'])+1}/{len(PROGRAMMA)}: {nome}", flush=True)

    fasc = os.path.join(QUI, f"/tmp/fascicolo_{nome}.txt")
    fasc = f"/tmp/fascicolo_{nome}.txt"
    open(fasc, "w").write(CORNICE + domanda + "\n")

    amb = dict(os.environ)
    amb["OUT_FASCICOLO"] = fasc
    amb["OUT_NOME"] = f"RICERCA_VENDITORI_{nome}"
    amb["OUT_DIR"] = CARTELLA
    os.makedirs(CARTELLA, exist_ok=True)
    # cintura: nessuna chiave a consumo nell'ambiente, mai
    for k in ("XAI_API_KEY", "GROK_API_KEY", "X_AI_API_KEY"):
        amb.pop(k, None)
    t0 = time.time()
    prima = set(glob.glob(os.path.join(CARTELLA, f"RICERCA_VENDITORI_{nome}_*.md")))
    p = subprocess.run([sys.executable, os.path.join(QUI, "agents", "consulta_grok.py")],
                       cwd=QUI, env=amb, capture_output=True, text=True, timeout=3000)
    print((p.stdout or "").strip()[-600:], flush=True)

    # UNA RISPOSTA TROPPO CORTA NON E' UNA RISPOSTA. Il 6/10 la domanda 3 e' tornata con 296
    # caratteri — solo la riga di apertura, il corpo mancante — e l'agente l'ha segnata come
    # FATTA. Cosi' il programma avanza e il fascicolo resta vuoto: peggio di un errore, perche'
    # il registro dice che e' a posto. Sotto i 2.000 caratteri si butta e si ritenta.
    nuovi = set(glob.glob(os.path.join(CARTELLA, f"RICERCA_VENDITORI_{nome}_*.md"))) - prima
    MINIMO = 2000
    if nuovi:
        f = max(nuovi, key=os.path.getmtime)
        n_car = len(open(f).read())
        if n_car < MINIMO:
            print(f"RICERCA | la risposta e' di {n_car} caratteri (minimo {MINIMO}): non e' una "
                  f"ricerca, e' un'apertura. NON la segno come fatta, il giro dopo ritenta.")
            os.rename(f, f + ".troppo_corta")
            return 0
        _metti_al_sicuro(f)
    if p.returncode != 0:
        print(f"RICERCA | consulta_grok e' uscito con {p.returncode}: non segno la domanda come "
              f"fatta, cosi' il giro dopo la ritenta. {(p.stderr or '')[:200]}")
        return 0

    r["fatte"].append(nome)
    r["ultima"] = int(time.time())
    r.setdefault("storia", []).append({"nome": nome, "quando": int(time.time()),
                                       "secondi": int(time.time() - t0)})
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    json.dump(r, open(REGISTRO, "w"), indent=1)
    print(f"RICERCA | fatta e segnata: {len(r['fatte'])}/{len(PROGRAMMA)} del programma", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
