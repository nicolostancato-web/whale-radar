"""Le lezioni del progetto, con uno STATO che NON mi assegno io.

IL PROBLEMA CHE RISOLVE (28/09, dall'audit dell'auto-learning).
Abbiamo decine di lezioni scritte — nei commenti del codice, nei documenti, nei verdetti — e le
trattavo **tutte come verita'**, comprese quelle mai riverificate. Una frase scritta due giorni fa
con convinzione ha lo stesso peso di una provata: e' esattamente il modo in cui un sistema si
convince di sapere cose che non sa.

LA REGOLA, ed e' l'unica cosa che rende questo file diverso da un elenco di buoni propositi:

    **Una lezione e' «verificata» solo se esiste un controllo che la prova E CHE PUO' FALLIRE.**

Lo stato non si dichiara: si DERIVA facendo girare quel controllo. Le lezioni senza un controllo
collegato restano «ipotesi» — vere forse, ma non dimostrate — e il conto di quante siano e' la
misura piu' onesta di quanto sappiamo davvero.

E' anche la difesa contro la trappola dell'auto-overfitting: se una lezione non e' agganciata a
niente che possa contraddirla, non e' conoscenza acquisita, e' una convinzione.
"""
import json
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
FUORI = "data/lezioni.json"

# stato possibile: ipotesi | verificata | smentita | obsoleta
# `prova`: come si verifica. "incidenti:<nome>" o "metro:<nome>" o None (= nessuna prova, resta ipotesi)
LEZIONI = [
 {"id": "chi-ripara-satura", "data": "2026-10-01",
  "scoperta": "Alle 02:34 tredici corsie sono state annullate nello stesso minuto. Ho cercato un "
              "colpevole fra i guardiani, la pulizia della cronologia e le configurazioni. "
              "Il colpevole ero io: avevo rilanciato dieci corsie A MANO in due minuti.",
  "causa": "Trentuno sorgenti possono chiamare le corsie, su venti macchine. La coda e' satura "
           "per costruzione, e un'ondata di rilanci «per sistemare» la fa superare da se' stessa.",
  "correzione": "Nessuna correzione al codice: la correzione e' smettere. In uno stato saturo la "
                "cosa piu' utile e' lasciar drenare, non intervenire.",
  "lezione": "Su una coda satura, rilanciare molte cose insieme per aggiustarle produce "
             "esattamente la tempesta che si vuole spegnere. Chi ripara e' una sorgente di "
             "carico come le altre, e deve contarsi fra i sospetti.",
  "prova": "c-e:agents/lezioni.py|chi-ripara-satura"},

 {"id": "guardiani-stesso-dominio", "data": "2026-10-01",
  "scoperta": "Alle 22:30 un guardiano distruttivo ha ucciso 38 giri, compresi TUTTI E TRE i "
              "guardiani. Non sono mai ripartiti: quattro ore di silenzio, e tre corsie ferme "
              "del tutto, perche' chi doveva rianimarli erano loro stessi.",
  "causa": "Avevo costruito una rete di guardiani che si sorvegliano a vicenda convincendomi "
           "che la probabilita' di guasto fosse il PRODOTTO delle singole. Girano tutti su "
           "GitHub Actions: il colpo che li ha uccisi era UNO. Astra me l'aveva detto alle "
           "20:56 — «dal punto di vista della disponibilita' e' un guardiano solo» — e l'ho "
           "implementato comunque.",
  "correzione": "agents/dal_di_fuori.sh gira sul Mac, fuori da GitHub Actions, a ogni giro del "
                "loop. Non e' definitivo (si ferma con la sessione) ma e' un dominio diverso.",
  "lezione": "Una rete di guardiani sulla stessa infrastruttura non e' una rete: e' un guardiano "
             "con piu' nomi. L'indipendenza si misura sul dominio di guasto, non sul numero.",
  "prova": "c-e:agents/dal_di_fuori.sh|OSSERVATORE IN UN DOMINIO DI GUASTO DIVERSO"},

 {"id": "head-of-line", "data": "2026-10-01",
  "scoperta": "Il pubblicatore — l'UNICO che scrive — e' fallito nel passo di raccolta: un pacco "
              "difettoso su dieci ha fatto cadere il turno e con lui nove consegne sane, "
              "compreso tutto il lavoro della notte in attesa.",
  "causa": "Il passo girava con l'uscita-al-primo-errore e senza protezione per pacco: qualunque "
           "comando inciampato su un pacco uccideva la raccolta intera. Grok da' il nome: "
           "`head-of-line blocking` — un elemento non trattabile blocca il consumatore unico.",
  "correzione": "Il pacco difettoso si salta dicendolo; gli altri passano. E il passo non esce "
                "al primo comando non-zero.",
  "lezione": "Chi e' l'unico a poter fare una cosa deve essere l'ultimo a morire: isola ogni "
             "elemento che tratta, perche' il suo fallimento ferma tutti gli altri.",
  "prova": "c-e:.github/workflows/pubblicatore.yml|head-of-line blocking"},

 {"id": "non-rianimare-i-distruttori", "data": "2026-10-01",
  "scoperta": "38 giri annullati in tre raffiche. Ho accusato il guardiano che avevo risvegliato "
              "io, perche' girava in quegli stessi minuti. CORRETTO alle 03:10: la causa non era "
              "provata. Quei giri erano in CODA su macchine sature, e sono stati superati da "
              "altre chiamate — non uccisi. Avevo letto «partito dopo 0 secondi» come «stava "
              "lavorando», mentre per un giro in coda quel campo vale l'istante di creazione.",
  "causa": "L'ho rianimato ragionando «un guardiano che muore non lo rilancia nessuno» — vero in "
           "generale — senza chiedermi PERCHE' fosse morto il 27 agosto. Ha il potere di "
           "cancellare i giri che considera bloccati.",
  "correzione": "Rimesso a riposo. Il rilancio delle corsie ferme lo fa rianima.py, che non "
                "puo' cancellare niente.",
  "lezione": "Non si rianima un componente che puo' DISTRUGGERE senza prima sapere perche' era "
             "morto — la decisione di rimetterlo a dormire resta giusta per questo. Ma la CAUSA "
             "che gli avevo attribuito era falsa: una correlazione temporale su un campo letto "
             "male. Terza spiegazione plausibile e sbagliata nella stessa notte.",
  "prova": "c-e:.github/workflows/workflow_watchdog.yml|A RIPOSO DALL'1/10"},

 {"id": "tempesta-di-rilanci", "data": "2026-10-01",
  "scoperta": "`scoperta`, `vivo` e `riserve` non avevano UN solo giro riuscito negli ultimi "
              "dieci: quattro cancellazioni in otto minuti. Tre raccoglitori di dati a vuoto, "
              "e l'ho scoperto solo perche' l'inventario l'ha detto.",
  "causa": "La rete di guardiani che ho costruito stanotte per rianimare le corsie ferme: due "
           "guardiani girano insieme, entrambi vedono la corsia ferma, entrambi la rilanciano. "
           "Ogni nuovo giro uccide quello in volo, che risulta fermo, e viene rilanciato di "
           "nuovo. Grok la chiama `retry storm`: il rimedio diventa la malattia.",
  "correzione": "agents/rianima.py: una corsia non si rilancia piu' di una volta per finestra, "
                "e la memoria dei rilanci sta su DISCO, condivisa, non nella testa di ognuno.",
  "lezione": "Quando piu' guardiani possono agire sullo stesso oggetto, la memoria di chi ha "
             "gia' agito va messa fuori da entrambi: due soccorritori che non si parlano fanno "
             "piu' danni di nessuno.",
  "prova": "c-e:agents/rianima.py|retry storm"},

 {"id": "fail-plausible", "data": "2026-10-01",
  "scoperta": "Il 30/09 ho ritentato per TRE ORE una spinta impossibile, leggendo nei registri "
              "«contesa sul ramo». Era un file oltre 100 MB: un rifiuto definitivo.",
  "causa": "L'errore grezzo non veniva classificato: veniva RACCONTATO. Grok ha dato il nome a "
           "questa famiglia citando Wu (arXiv:2606.14589): «fail-plausible» — il modello non "
           "tace l'errore, lo trasforma in un racconto credibile. E un racconto credibile manda "
           "a cercare nel posto sbagliato con la massima convinzione.",
  "correzione": "agents/classifica_errore.py: stringhe note, nessuna interpretazione. TERMINALE "
                "ferma, CONTESA ritenta, SCONOSCIUTO ferma e conserva lo stderr grezzo.",
  "lezione": "Un errore che non riconosci non e' una contesa: classifica il messaggio grezzo "
             "prima di raccontarlo, e se non lo riconosci fermati invece di inventare una causa.",
  "prova": "c-e:agents/classifica_errore.py|SCONOSCIUTO"},

 {"id": "dichiarato-non-e-fatto", "data": "2026-10-01",
  "scoperta": "Ho detto al fondatore «si', la memoria e' salva sul server, vai a dormire "
              "tranquillo». Avevo scritto il codice. La memoria NON era sul server, e quando "
              "ci e' arrivata mancava il file piu' importante: le sue parole.",
  "causa": "Ho usato la dichiarazione di aver fatto una cosa come prova di averla fatta — "
           "l'errore esatto che Astra ci contesta da giorni. Due volte di fila sulla stessa "
           "cosa: il codice collegato, poi l'elenco dei file incompleto.",
  "correzione": "agents/prova_ripristino.py: si riparte da una cartella VUOTA e si verifica che "
                "il sistema restaurato funzioni. Ha pescato entrambi i buchi, io nessuno.",
  "lezione": "Fra «ho collegato il codice» e «ho visto il file sul server» c'e' tutta la "
             "differenza che conta. Quando qualcuno va a dormire sulla tua risposta, la "
             "risposta si verifica prima di darla.",
  "prova": "c-e:agents/prova_ripristino.py|cartella vuota"},

 {"id": "prezzo-ottenibile", "data": "2026-09-30",
  "scoperta": "Il primo numero positivo del progetto (+17,6%) e la combinazione trovata "
              "stanotte (+193,8% fuori campione) muoiono entrambi con UN solo scambio di "
              "latenza: diventano -11,4% e +0,9%.",
  "causa": "Il prezzo d'ingresso di ogni misura era il prezzo dello scambio a cui entriamo — "
           "uno scambio realmente avvenuto, ma non il nostro. Per comprare si manda una "
           "transazione, eseguita DOPO quelle davanti: si paga il prezzo successivo. Sui pool "
           "a raffica costa il 38% in piu' in mediana.",
  "correzione": "insieme.py calcola `_uscita_N_ritardo` col prezzo ottenibile, e dati.py lo "
                "dichiara esito. Da qui si decide su quello.",
  "lezione": "Il prezzo che vedi non e' il prezzo che paghi: paghi quello dello scambio dopo. "
             "Ogni misura di un'entrata va fatta col prezzo OTTENIBILE, non con l'osservato.",
  "prova": "c-e:agents/insieme.py|_uscita_{taglia}_ritardo"},

 {"id": "prova-che-si-sposta", "data": "2026-09-30",
  "scoperta": "Una lezione e' passata da «provata» a «SMENTITA» senza che nessuno la toccasse: "
              "avevo spostato il codice che la dimostrava in un altro file.",
  "causa": "La prova cercava un testo dentro `sentinella.py`; il codice e' finito in "
           "`rianima.py` quando ho messo la funzione in comune fra due guardiani.",
  "correzione": "La prova punta al file dove il codice vive adesso. E questo caso resta come "
                "esempio: il controllo ha fatto il suo mestiere, si e' acceso da solo.",
  "lezione": "Una prova legata a un file si rompe quando il codice trasloca — ed e' un bene: "
             "meglio un controllo che grida per un trasloco che uno che tace per un difetto.",
  "prova": "c-e:agents/lezioni.py|prova-che-si-sposta"},

 {"id": "allarme-senza-lettore", "data": "2026-09-30",
  "scoperta": "Il consulente esterno taceva da sette giorni. Nicolo' se n'e' accorto e me l'ha "
              "chiesto; io no.",
  "causa": "Nessuna corsia lo esegue — si lanciava a mano. E il sistema LO SAPEVA: staffetta.py "
           "scriveva in rosso «tace da 155 ore» in un rapporto che non leggeva nessuno.",
  "correzione": "La riga finisce dentro l'uscita della sentinella e del heartbeat, che si "
                "guardano. Il ritmo delle chiamate resta una decisione di Nicolo': costa.",
  "lezione": "Un allarme che nessuno legge non e' un allarme: e' un archivio di rimpianti. "
             "Ogni controllo nuovo va agganciato a qualcosa che qualcuno guarda davvero.",
  "prova": "c-e:agents/rianima.py|archivio di rimpianti"},

 {"id": "lezione-non-propagata", "data": "2026-09-30",
  "scoperta": "La guardia nuova diceva «ferma da 232 minuti» dove ne erano passati 52. Lo stesso "
              "errore era gia' stato commesso e DOCUMENTATO il 19/09 in workflow_watchdog.py.",
  "causa": "`time.mktime` legge come ora LOCALE e `time.timezone` vale lo scarto STANDARD, non "
           "quello con l'ora legale. Ma la causa vera e' un'altra: la lezione stava scritta in "
           "un file, e io ne stavo scrivendo un altro.",
  "correzione": "Si legge l'ora di GitHub come UTC con datetime; e la lezione va dove il codice "
                "la incontra, non in un file che nessuno apre mentre scrive quello accanto.",
  "lezione": "Una lezione scritta in un file non protegge il file accanto: quando si ripete un "
             "calcolo gia' sbagliato altrove, si copia la riga giusta, non si riscrive a mente.",
  "prova": "c-e:agents/rianima.py|Errore gia' fatto due volte"},

 {"id": "ordine-archivio", "data": "2026-09-30",
  "scoperta": "Il repository e' passato da 4,66 a 7,13 GB in un giorno, con il limite a dieci: "
              "due giorni allo stop totale.",
  "causa": "`censimento.py` riscriveva l'archivio ordinandolo per NUMERO DI SCAMBI, che cambia a "
           "ogni giro: centomila righe rimescolate ogni volta. Un archivio compresso e' un "
           "flusso — rimescolato cambia da capo, e git risalva i 15 MB interi invece delle "
           "righe nuove. Misurato: 0,1 MB in ordine stabile contro 12,8 MB rimescolato.",
  "correzione": "Si ordina per l'indirizzo del pool, che non cambia mai. Chi vuole i piu' "
                "scambiati se li ordina quando legge.",
  "lezione": "Un archivio che si riscrive va tenuto in ordine STABILE: l'ordine non e' una "
             "scelta estetica, e' la differenza fra salvare le righe nuove e risalvare tutto.",
  "prova": "c-e:agents/censimento.py|L'ORDINE DELL'ARCHIVIO COSTA GIGABYTE"},

 {"id": "spento-o-rotto", "data": "2026-09-30",
  "scoperta": "Ho annunciato che una cancellazione aveva ucciso cinque corsie per tredici giorni. "
              "Erano state DISATTIVATE A MANO: lo stato «annullato» era solo l'ultimo giro "
              "interrotto nel momento dello spegnimento.",
  "causa": "Avevo letto l'esito dell'ultimo giro e ne avevo dedotto la causa della fermata. "
           "L'esito dice come e' finito quel giro, non perche' non ce ne sono stati altri.",
  "correzione": "Prima di spiegare perche' una corsia non gira, si chiede il suo STATO "
                "(`workflow.state`): «disabled_manually» e' una decisione, non un guasto.",
  "lezione": "Distingui sempre «spento» da «rotto»: un sistema fermo per scelta e uno fermo per "
             "guasto hanno lo stesso aspetto nei registri e richiedono azioni opposte.",
  "prova": "c-e:LEZIONI_RIPRESE.md|disabled_manually"},

 {"id": "file-oltre-limite", "data": "2026-09-29",
  "scoperta": "Per ore nessuna corsia e' riuscita a pubblicare. Nei registri leggevo «contesa "
              "sul ramo» e convertivo corsie per ridurla: era il sintomo.",
  "causa": "Un solo file, `segnali.jsonl`, aveva superato i 100 MB di limite per file di GitHub. "
           "Un file oltre soglia non rallenta: rende IMPOSSIBILE ogni spinta, a chiunque. "
           "Era cresciuto piano, lo scriveva uno script che nessuna corsia esegue, e "
           "nessuno lo guardava.",
  "correzione": "agents/file_troppo_grandi.py in pubblica.sh: avvisa a 60 MB, blocca a 90. "
                "Il file compresso: 5,6 MB, 175.845 righe intatte.",
  "lezione": "Quando molte cose diverse falliscono insieme, cerca il vincolo unico che le "
             "riguarda tutte prima di riparare ognuna: il sintomo si moltiplica, la causa no.",
  "prova": "c-e:pubblica.sh|file_troppo_grandi"},

 {"id": "chiavi-doppie", "data": "2026-09-29",
  "scoperta": "Per mezz'ora nessuna variante e' potuta partire: GitHub rifiutava la corsia intera "
              "con un 422, e il mio controllo l'aveva dichiarata sana.",
  "causa": "Avevo scritto due volte `if:` nello stesso passo. `yaml.safe_load` davanti a due "
           "chiavi uguali tiene l'ULTIMA e non protesta; GitHub invece butta tutto il file.",
  "correzione": "agents/chiavi_doppie.py, senza dipendenze, dentro pubblica.sh; provato "
                "rimettendo il difetto in una copia e vedendolo pescare la riga giusta.",
  "lezione": "Un controllo deve essere severo quanto chi giudica davvero: se il mio lettore "
             "perdona quello che GitHub rifiuta, sta solo dicendomi quello che voglio sentire.",
  "prova": "c-e:pubblica.sh|chiavi_doppie"},

 {"id": "modifica-condizionata", "data": "2026-09-29",
  "scoperta": "Tre strategie su quattro non sono mai state costruite: la correzione che doveva "
              "farle passare non era mai entrata nel file, e nessuno se n'e' accorto.",
  "causa": "L'avevo scritta come sostituzione CONDIZIONATA (`... if 'FATTA' in t else t`): se il "
           "testo non combacia non cambia niente e non protesta. Il file restava com'era.",
  "correzione": "Ogni sostituzione porta il suo `assert` sul conteggio PRIMA e sul testo DOPO: "
                "se non ha morso, si ferma li'.",
  "lezione": "Una modifica deve gridare quando non ha morso: chi pubblica dice INVARIATO se il file "
             "e' identico a quello gia' pubblicato, che e' il segno che la correzione non e' entrata.",
  "prova": "c-e:agents/pubblica_file.py|INVARIATO"},

 {"id": "salto-ereditato", "data": "2026-09-29",
  "scoperta": "Le varianti leggevano il timbro dell'insieme UFFICIALE: se quello era fresco "
              "uscivano senza costruire nulla, dichiarando successo.",
  "causa": "Il risparmio («non rifarlo se e' fresco») era scritto per un solo prodotto e lo ha "
           "applicato anche a prodotti diversi, che di fresco non avevano niente.",
  "correzione": "insieme.yml: chi chiede una variante la costruisce sempre.",
  "lezione": "Un risparmio vale solo per il prodotto su cui e' stato misurato: quando nasce una "
             "seconda cosa, chiediti su quale delle due il risparmio stava parlando.",
  "prova": "c-e:.github/workflows/insieme.yml|si costruisce sempre"},

 {"id": "verso-dei-prezzi", "data": "2026-09-26",
  "scoperta": "Contavamo gli ACQUISTI come vendite nel 73% dei pool: quale token sia il memecoin "
              "dipende dall'ordine alfabetico degli indirizzi.",
  "causa": "Il segno di `a0` veniva letto come verso senza sapere a quale token appartiene.",
  "correzione": "agents/verso.py: il verso si stabilisce per pool, prima di dare un segno.",
  "lezione": "Prima di dare un segno a una quantita', stabilisci a quale cosa appartiene.",
  "prova": "incidenti:verso"},

 {"id": "finestra-di-osservazione", "data": "2026-09-25",
  "scoperta": "Misuravamo esiti a 24 ore su pool osservati poche ore: le trappole risultavano 35% "
              "invece del vero.",
  "causa": "Chi non aveva vendite perche' NON AVEVAMO GUARDATO finiva fra le trappole.",
  "correzione": "insieme.py: `_giudicabile` in base all'eta' rispetto alla fine della raccolta.",
  "lezione": "Dichiara quanto hai osservato, e misura solo dove l'osservazione copre l'orizzonte.",
  "prova": "incidenti:finestra"},

 {"id": "sopravvivenza-travestita", "data": "2026-09-25",
  "scoperta": "La correzione della mattina era peggio del difetto: «abbiamo visto N ore di scambi "
              "su questo pool» scartava i pool MORTI, cioe' proprio le trappole.",
  "causa": "Il criterio di scarto sapeva gia' come era andata a finire.",
  "correzione": "Il criterio diventa una data (eta'), che non sa nulla dell'esito.",
  "lezione": "Quando scarti dei casi, chiediti se il motivo dello scarto sa gia' come e' andata.",
  "prova": "incidenti:sopravvivenza"},

 {"id": "taglia-accanto-al-prezzo", "data": "2026-09-26",
  "scoperta": "Un 10x che scambiava 32 dollari sembrava un'uscita vera: l'ipotesi H6b dava +11% e "
              "reggeva a tutti i controlli statistici.",
  "causa": "Il prezzo veniva contato senza guardare quanti soldi passavano a quel prezzo.",
  "correzione": "insieme.py: `_uscita_pesata`, il prezzo a cui esce META' DEL DENARO.",
  "lezione": "Un prezzo non e' un'uscita finche' non gli metti accanto una taglia.",
  "prova": "incidenti:taglia"},

 {"id": "riarmo-obbligatorio", "data": "2026-09-27",
  "scoperta": "Tre corsie nuove nate senza riarmo, piu' i due guardiani: su questo repository "
              "GitHub salta i cron, quindi semplicemente non giravano.",
  "causa": "La regola era scritta in dieci file e affidata alla mia memoria.",
  "correzione": "pubblica.sh rifiuta una corsia senza riarmo; provato con una corsia finta.",
  "lezione": "Le cose da ricordare non funzionano; quelle che si rifiutano di passare si'.",
  "prova": "porta:riarmo"},

 {"id": "il-silenziatore", "data": "2026-09-27",
  "scoperta": "Avevo messo `2>/dev/null` sul push per tenere puliti i registri e sono rimasto cieco "
              "per ore sul motivo di un guasto mio.",
  "causa": "Pulizia dei registri preferita alla diagnosi.",
  "correzione": "Tolto il silenziatore; il motivo del fallimento si stampa sempre.",
  "lezione": "La pulizia dei registri non vale mai la cecita' sulle cause.",
  "prova": None},

 {"id": "spiegazione-non-e-causa", "data": "2026-09-27",
  "scoperta": "Sul recupero ho dato tre spiegazioni plausibili di fila, tutte sbagliate, e una "
              "l'avevo gia' scritta come lezione permanente nel codice.",
  "causa": "Ho scambiato una spiegazione che regge per una causa misurata.",
  "correzione": "Si misura prima di scrivere una lezione.",
  "lezione": "Una spiegazione plausibile non e' una causa: finche' non la misuri, non la scrivi.",
  "prova": None},

 {"id": "chi-gira-a-vuoto", "data": "2026-09-28",
  "scoperta": "Due corsie mie giravano 23 volte l'ora con la coda vuota, tenendo in fila i pezzi "
              "che contano: 19 macchine su 20 occupate.",
  "causa": "Riarmi pensati per quando c'era arretrato, rimasti quando l'arretrato era finito.",
  "correzione": "Chi non ha niente da fare aspetta a lungo prima di ripassare.",
  "lezione": "Chi gira a vuoto non e' innocuo: ruba il turno a chi lavora.",
  "prova": None},

 {"id": "la-guardia-che-accetta-il-rotto", "data": "2026-09-28",
  "scoperta": "Il controllo sulle corsie orfane accettava «ha un cron OPPURE si riarma» — e il cron "
              "e' proprio il meccanismo che qui non funziona.",
  "causa": "La guardia accettava come prova di salute la cosa rotta.",
  "correzione": "Ora pretende il riarmo; provato con una corsia col solo cron.",
  "lezione": "Il difetto viene chiuso con un sostituto che gli assomiglia, e il sostituto passa.",
  "prova": "porta:riarmo"},

 {"id": "la-convenzione-che-decide", "data": "2026-09-29",
  "scoperta": "Il fondale su cui abbiamo chiuso una direzione dipendeva per 55 punti dalla regola "
              "«meno di cinque vendite = perdita totale»: una scelta, non una misura.",
  "causa": "Un'assunzione comoda lasciata nel punto in cui si decide il verdetto.",
  "correzione": "insieme.py: si SIMULA di vendere una posizione da 100, 500 e 2000 dollari nel "
                "flusso vero delle vendite. Lo stesso mercato rende +100% o -62% secondo la taglia.",
  "lezione": "Dove una soglia decide il verdetto, non si sceglie la soglia: si simula cio' che "
             "la soglia stava approssimando.",
  "prova": None},

 {"id": "condizionare-sul-futuro", "data": "2026-09-28",
  "scoperta": "Due volte in due giorni ho condizionato su un campo che si conosce solo DOPO aver "
              "comprato: +24,9% il 27/09, +15,0% il 28/09. Col dato visto prima: -12,1%.",
  "causa": "Nessuna barriera fra le caratteristiche e l'esito: bastava scriverne il nome.",
  "correzione": "agents/dati.py: chi chiede le caratteristiche NON riceve i campi dell'esito, e "
                "filtrarci sopra solleva un errore invece di dare un numero.",
  "lezione": "Se una fascia che rende bene e' definita da qualcosa misurato dopo l'entrata, non e' "
             "una strategia: e' sopravvivenza.",
  "prova": "incidenti:futuro"},

 {"id": "crescita-non-e-salute", "data": "2026-09-29",
  "scoperta": "La sentinella ha gridato «iniziatori fermo da 668 minuti». La corsia girava ogni "
              "dieci minuti e riusciva sempre: il file non cresceva perche' aveva smaltito "
              "l'arretrato e non c'era niente da aggiungere.",
  "causa": "Si misurava la crescita su una corsia che SMALTISCE, non su una che RACCOGLIE.",
  "correzione": "Tolta dalla sorveglianza della crescita; che sia viva lo controlla heartbeat, che "
                "guarda se gira invece di quanto produce.",
  "lezione": "La crescita e' salute per chi raccoglie; per chi smaltisce un arretrato, stare fermi "
             "vuol dire essere in pari.",
  "prova": None},

 {"id": "guardiano-che-grida-al-lupo", "data": "2026-09-28",
  "scoperta": "La sentinella ha gridato «previsioni fermo da 177 minuti»: la corsia lavorava "
              "benissimo, e l'archivio sorvegliato non lo scrive lei — e nessuno lo scrive piu'.",
  "causa": "Si sorvegliava un archivio morto, con l'etichetta di una corsia che non lo tocca.",
  "correzione": "Tolto dalla sorveglianza (il dato resta), con il motivo scritto accanto.",
  "lezione": "Si sorveglia cio' che deve crescere; la storia sta ferma per mestiere.",
  "prova": None},

 {"id": "il-test-che-si-adatta", "data": "2026-09-28",
  "scoperta": "Il banco degli incidenti dava 5 dove ne aspettavo 6: la tentazione era cambiare il "
              "numero atteso.",
  "causa": "Non avevo capito perche' 5 (lo scambio d'ingresso non fa parte del «dopo»).",
  "correzione": "Capito il motivo e reso il caso piu' severo, invece di adattare l'attesa.",
  "lezione": "Un test che si adatta al risultato non prova piu' niente.",
  "prova": None},
]


def _gira(comando):
    r = subprocess.run(comando, capture_output=True, text=True, cwd=os.path.dirname(QUI))
    return r.returncode == 0, r.stdout


RADICE = os.path.dirname(QUI)


def verifica():
    """Deriva lo stato facendo girare i controlli. Chi non ne ha resta 'ipotesi'."""
    ok_inc, uscita_inc = _gira([sys.executable, "-B", os.path.join(QUI, "incidenti.py")])
    fuori = []
    for L in LEZIONI:
        p = L.get("prova")
        if not p:
            stato = "ipotesi"
        elif p.startswith("incidenti:"):
            nome = p.split(":", 1)[1]
            riga = [r for r in uscita_inc.splitlines() if nome in r.lower()]
            if not riga:
                stato = "ipotesi"                      # il caso non esiste (piu'): non e' provata
            else:
                stato = "verificata" if "PESCATO" in riga[0] else "smentita"
        elif p.startswith("porta:"):
            # la porta si prova col suo caso finto: qui basta sapere che il controllo c'e'
            testo = open(os.path.join(os.path.dirname(QUI), "pubblica.sh")).read()
            stato = "verificata" if "CORSIA SENZA RIARMO" in testo else "ipotesi"
        elif p.startswith("c-e:"):
            # «nel file X deve comparire il testo Y»: puo' fallire davvero, perche' se qualcuno
            # toglie la correzione il controllo diventa rosso. E' questo che lo rende una prova.
            f, testo = p.split(":", 1)[1].split("|", 1)
            try:
                stato = "verificata" if testo in open(os.path.join(RADICE, f)).read() else "smentita"
            except OSError:
                stato = "smentita"
        elif p.startswith("non-c-e:"):
            # «in nessun file sotto agents/ deve comparire questo modo di scrivere»: e' la forma
            # giusta per le lezioni su COME si scrive il codice, non su cosa calcola.
            ago = p.split(":", 1)[1]
            colpiti = []
            for base, _, nomi in os.walk(os.path.join(RADICE, "agents")):
                for nome in nomi:
                    if nome.endswith(".py"):
                        d = os.path.join(base, nome)
                        if ago in open(d, encoding="utf-8", errors="ignore").read():
                            colpiti.append(d)
            stato = "verificata" if not colpiti else "smentita"
            if colpiti:
                L = dict(L, dove=colpiti[:3])
        else:
            stato = "ipotesi"
        fuori.append(dict(L, stato=stato))
    return fuori


def main():
    lez = verifica()
    conta = {}
    for L in lez:
        conta[L["stato"]] = conta.get(L["stato"], 0) + 1
    print("LEZIONI | stato derivato dai controlli, non dichiarato\n")
    for L in lez:
        segno = {"verificata": "provata ", "smentita": "SMENTITA", "ipotesi": "non provata"}[L["stato"]]
        print(f"   [{segno:11}] {L['lezione'][:78]}")
    print()
    print(f"   provate: {conta.get('verificata',0)} | non provate: {conta.get('ipotesi',0)}"
          f" | smentite: {conta.get('smentita',0)} — su {len(lez)}")
    if conta.get("ipotesi"):
        print("\n   Le 'non provate' non sono false: sono convinzioni. Finche' nessun controllo puo'")
        print("   contraddirle, non contano come conoscenza acquisita.")
    os.makedirs("data", exist_ok=True)
    json.dump(lez, open(FUORI, "w"), indent=1, ensure_ascii=False)
    return 1 if conta.get("smentita") else 0


if __name__ == "__main__":
    raise SystemExit(main())
