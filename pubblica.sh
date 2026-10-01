#!/bin/bash
# PUBBLICA SOLO CIO' CHE COMPILA (25/09).
#
# Il controllo di sintassi lo facevo gia'. Il 25/09 ho pubblicato lo stesso un file rotto — un
# commento infilato dentro un'espressione — perche' avevo legato il controllo alla pubblicazione
# con `;` invece che con `&&`: il controllo falliva, e il push partiva un comando dopo.
#
# La lezione NON e' «stare piu' attento a quale segno uso»: e' che un controllo la cui bocciatura
# non ferma niente non e' un controllo, e' un commento.
# IN POSITIVO: **si pubblica da qui, e da qui la pubblicazione non parte se qualcosa non compila.**
#
# uso:  ./pubblica.sh "messaggio del commit"
set -e

[ -n "$1" ] || { echo "manca il messaggio del commit"; exit 1; }

echo "— controllo che tutto compili"
python3 - <<'PY'
import ast, pathlib, sys
rotti = []
for f in sorted(pathlib.Path("agents").glob("*.py")):
    try:
        ast.parse(f.read_text())
    except SyntaxError as e:
        rotti.append(f"{f}:{e.lineno} {e.msg}")
if rotti:
    print("NON PUBBLICO, questi file sono rotti:")
    for r in rotti:
        print("   ", r)
    sys.exit(1)
print("   tutti i file di agents/ compilano")
PY

echo "— controllo che il metro sia ancora quello di ieri"
# UN DIFETTO DEL METRO NON SI VEDE GUARDANDO IL RISULTATO: il risultato sembra sempre plausibile.
# In una settimana quattro strumenti di misura rotti ci hanno fatto uccidere o salvare strategie
# sbagliate, e ogni volta ce ne siamo accorti giorni dopo. Qui il banco di prova gira PRIMA di ogni
# pubblicazione: se una risposta nota cambia, non si pubblica.
# `-B`: niente bytecode salvato. Senza, il banco di prova puo' leggere una versione VECCHIA del
# codice rimasta in cache e dichiarare rotto un metro sano — e' successo la prima volta che l'ho
# provato. **Un controllo che grida al lupo viene disattivato**, quindi il falso allarme e' un
# difetto grave quanto il difetto mancato.
python3 -B agents/chiavi_doppie.py || exit 1
python3 -B agents/file_troppo_grandi.py || exit 1

echo "— nessun segreto esce dalle corsie (il repository e' PUBBLICO)"
# La chiave del consulente vive fra i segreti perche' la sua corsia giri da sola. Ma il
# repository e' pubblico e io posso modificare le corsie: un `echo $CHIAVE` messo per debug la
# regalerebbe a chiunque. Qui si rifiuta la pubblicazione se una corsia stampa un segreto.
python3 -B agents/segreti_non_escono.py || exit 1

echo "— le decisioni permanenti sono ancora rispettate?"
# IL SISTEMA SI SCORDA LE DECISIONI (30/09, rilievo di Nicolo'). Non gli errori: le DECISIONI.
# Astra andava chiamato tre volte al giorno dal 23/09 e non lo chiamava nessuno; il sistema che
# avevamo costruito per non dimenticare — compliance_check.py, strategy.yaml — era sparito.
# Qui una violazione GRAVE ferma la pubblicazione. Una dichiarazione senza controllo non basta.
python3 -B agents/decisioni.py || exit 1
python3 -B agents/prova_metro.py

echo "— controllo che i guasti di ieri verrebbero ancora pescati"
# IL BANCO DEGLI INCIDENTI VERI. Quattro guasti realmente accaduti, ognuno costato ore o giorni,
# tutti avvenuti PRIMA che esistessero le difese che oggi dovrebbero fermarli. Qui passa dal codice
# vero: fa girare `insieme.py` su dati costruiti come quelli veri, non riscrive le formule.
# Provato rimettendo i difetti: il banco se ne accorge. Vedi `agents/incidenti.py`.
python3 -B agents/incidenti.py

echo "— controllo che nessuna corsia nasca orfana"
python3 - <<'PY_CORSIE'
import glob, os, re, subprocess, sys

# UNA CORSIA NUOVA NASCE COL RIARMO (27/09). In due giorni ne ho create TRE senza, e me ne sono
# accorto solo trovandole ferme ore dopo — GitHub salta i cron sui repository occupati, quindi una
# corsia senza riarmo semplicemente non gira. La regola l'avevo scritta in dieci file e violata lo
# stesso: **le cose da ricordare non funzionano, quelle che si rifiutano di passare si'.**
# Qui la pubblicazione si FERMA se un workflow nuovo o modificato non sa rimettersi in coda da solo.
cambiati = subprocess.run(["git", "status", "--porcelain", "--", ".github/workflows"],
                          capture_output=True, text=True).stdout.split()
yml = sorted({c for c in cambiati if c.endswith(".yml")})
if not yml:
    print("   nessun workflow toccato")
    sys.exit(0)
orfane = []
for f in yml:
    if not os.path.exists(f):
        continue
    t = open(f).read()
    nome = os.path.basename(f)[:-4]
    si_riarma = f"workflows/{nome}.yml/dispatches" in t
    ha_orario = "- cron:" in t
    # NON BASTA AVERE UN ORARIO (28/09). La prima versione di questo controllo accettava «ha un
    # cron OPPURE si riarma». Ma su questo repository **il cron e' proprio la cosa che non
    # funziona**: GitHub lo salta quando il repo e' occupato, e il nostro lo e' sempre.
    # Cioe' la guardia accettava come prova di salute il meccanismo rotto. Ci sono passati sotto il
    # naso `heartbeat` e `sentinella` — i due guardiani che si accorgono quando le altre corsie
    # muoiono — che potevano morire nel modo esatto che esistono per scoprire.
    # E' la famiglia nominata dalla domanda di oggi: **il difetto viene chiuso con un sostituto che
    # gli assomiglia, e il sostituto passa.**
    # Ora si pretende il riarmo. L'orario resta utile come rete, non come prova.
    # UN'ESENZIONE DICHIARATA, NON UN'ECCEZIONE SILENZIOSA (30/09). Trentatre' corsie non hanno
    # il riarmo, e aggiungerlo a tutte NON e' la cosa giusta: le macchine gratis in parallelo sono
    # venti, e il 25/09 il riarmo su sei corsie ha AFFAMATO quelle critiche — tre sono cadute.
    # Per alcune il solo orario e' corretto: girano poche volte al giorno per natura (una pulizia,
    # uno specchio, un rapporto). Ma la differenza fra «va bene a orario» e «me ne sono
    # dimenticato» non si vede guardando il file: va SCRITTA.
    # Quindi si accetta una corsia senza riarmo solo se dichiara il motivo con questa riga:
    #     # SENZA RIARMO: <perche' il solo orario basta per questa corsia>
    esente = "SENZA RIARMO:" in t
    # UNA CORSIA MANUALE NON HA NIENTE DA TENERE VIVO (30/09). Il controllo pretendeva il riarmo
    # anche da chi non ha orologio: ma senza orologio la corsia parte solo quando la lancio io,
    # e riarmarla vorrebbe dire farla girare per sempre da sola — l'opposto di cio' che voglio.
    # Serve per mettere A RIPOSO i relitti senza cancellarli: codice intatto, orologio spento.
    if not ha_orario:
        print(f"   {nome}: nessun orologio — parte solo a mano, niente da tenere vivo")
        continue
    if not si_riarma and not esente:
        orfane.append(nome + (" (ha solo il cron, che qui non basta)" if ha_orario else ""))
    elif esente:
        print(f"   {nome}: senza riarmo, ma il motivo e' dichiarato nel file")
for o in orfane:
    # IL MESSAGGIO DEVE DIRE LA COSA GIUSTA (28/09). Era rimasto «non ha ne' riarmo ne' orario»
    # anche dopo che il controllo era diventato «serve il riarmo»: una diagnosi che manda a cercare
    # il problema sbagliato. Le diagnosi imprecise costano piu' del difetto che descrivono.
    print(f"   CORSIA SENZA RIARMO: {o} — il solo cron non basta, GitHub lo salta sui repo occupati")
sys.exit(1 if orfane else 0)
PY_CORSIE

echo "— il critico guarda cosa stai cambiando"
# Puo' RIFIUTARE. Guarda due cose che non posso giudicare mentre le commetto: se sto aggiustando
# solo gli strumenti con cui il sistema si misura (la trappola dell'esame ottimizzato), e se sto
# cambiando troppe cose insieme. Si passa dichiarando il motivo — che resta scritto.
python3 -B agents/critico.py

echo "— controllo che i file di lavoro non restino solo qui"
# SI PUBBLICA DALL'INTERFACCIA DI GITHUB, NON CON GIT (28/09).
# La copia di lavoro e' superficiale — serve, perche' l'intera storia pesa gigabyte e il disco si
# era riempito. Ma cosi' git non puo' dimostrare la parentela dei commit, e il server rifiuta il
# push dicendo «sei indietro» ANCHE quando sei allineato. Non e' contesa: e' un limite strutturale,
# e nessun numero di tentativi lo supera. Ne ho fatti venti prima di capirlo, e nel frattempo avevo
# pure rimesso il silenziatore che nascondeva il motivo — lo stesso errore corretto ieri.
# I file si mandano uno per uno con l'interfaccia che GitHub offre apposta: niente storia, niente
# parentele, niente corse. Se qualcuno scrive lo stesso file nel frattempo, il server dice
# «conflitto», si rilegge la sua versione e si riprova. Vedi `agents/pubblica_file.py`.
# L'ASSENZA NEGA, NON PERMETTE (1/10, inversione dettata da Astra).
# Fino a stanotte questa porta chiedeva «i controlli hanno segnalato rosso?»: se un controllo
# SPARIVA — come e' sparito compliance_check.py senza che nessuno se ne accorgesse — la risposta
# era «no» e si pubblicava lo stesso. L'assenza di allarme veniva letta come assenza di problemi.
# Ora si pretende un'AUTORIZZAZIONE: emessa da tutti i controlli obbligatori, piu' recente di
# mezz'ora, e legata all'impronta ESATTA dei file. Cambiare un file dopo il controllo la annulla.
FILE_DA_PUBBLICARE=$(git status --porcelain | awk '{print $NF}' | grep -v '^$' || true)
python3 -B agents/autorizzazione.py emetti $FILE_DA_PUBBLICARE || exit 1
python3 -B agents/autorizzazione.py valida $FILE_DA_PUBBLICARE || exit 1

exec python3 -B agents/pubblica_file.py "$1"
