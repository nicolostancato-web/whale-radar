# La domanda di oggi — 29/09/2026

*«Come posso essere piu' forte, piu' sveglio, piu' preciso di ieri?» — fatta ogni giorno, sui fatti
del giorno. Idea di Nicolo, 27/09: e' la domanda schedulata che fa crescere l'intelligenza invece di
lasciarla ferma.*

**I fatti su cui e' stata fatta:** {"cambiamenti_veri": 27, "scritture_delle_corsie": 146, "righe_di_lezione_aggiunte": 2846, "file_di_codice_toccati": 215, "cambiamenti_su_'ripar'": 26, "titoli_dei_cambiamenti": ["riparazione robinhood/0 06:45Z", "riparazione robinhood/2 06:44Z", "riparazione robinhood/1 06:44Z", "riparazione robinhood/0 06:34Z", "riparazione robinhood/1 06:34Z", "riparazione robinhood/2 06:34Z", "riparazione base/1 06:34Z", "riparazione base/2 06:34Z", "riparazione base/0 06:34Z", "database giro4 06:27Z", "riparazione robinhood/1 06:17Z", "riparazione base/0 06:17Z"], "documenti_prodotti": [], "ipotesi_registrate": [], "verdetti_emessi": [], "giri_di_ricerca": [], "azioni": {"chiuse": 6, "con_un_controllo": 5, "aperte": 3}, "lezioni": {"verificata": 7, "ipotesi": 7}}

---

I parto dai fatti misurati e dal codice, così le azioni puntano a file veri e a un meccanismo che si rifiuta di funzionare, non a una regola da ricordare.I numeri dicono attività alta e intelligenza ferma: 26 riparazioni, zero ipotesi, zero verdetti, zero giri di ricerca. Ora leggo i punti in cui il codice accetta ancora un cambiamento che dovrebbe rifiutare.Il giudizio di ieri è già nel file. Controllo se quelle azioni sono nel codice o se oggi si è ripetuto lo stesso errore con un altro nome.La famiglia è una sola: si aggiorna il pezzo che si ha in mano e si lascia fuori dal percorso che deve riuscire la cosa che potrebbe smentirlo. Oggi si vede nei numeri, non nel racconto. Ventisei dei ventisette cambiamenti veri sono `riparazione` delle stesse sei schegge, due o tre volte in ventotto minuti: `ripara_orario.py` è a `VERSIONE_LOGICA = 10`, e ogni versione nuova svuota il segnalibro e può uscire avendo comunque un titolo che `prove()` conta come lavoro. Duemilaottocentoquarantasei righe di commento sono entrate in duecentoquindici file, e ipotesi, verdetti, documenti e giri di ricerca sono zero. Le due lezioni di oggi, `la-convenzione-che-decide` e `crescita-non-e-salute`, sono in `agents/lezioni.py` con `prova: None`: `verifica()` esce 0 lo stesso. `modello.py` allena ancora su `_uscita`, il decreto «meno di cinque vendite = −98%». `_uscita_100` viene scritto e non ha lettori. `verdetto_h7.esito` resta su `_uscita_min1`: quella prova è sigillata, e va lasciata dov'è. In `agents/sentinella.py` le chiavi tolte il 29/09 sono un commento: il controllo che in due giorni ha visto ogni guasto è stato ristretto nel momento in cui la giornata era fatta di riparazioni. `domande_grok.VERSIONE` è `v2-2026-09-27`. `file_citati` non è chiamato da nessuno.

Il rifiuto sta sulla porta che già esiste, `pubblica.sh`. Una lezione senza un controllo che può fallire non si pubblica. Un giro di riparazione che ha invalidato il segnalibro e ha scritto zero record `ver` non salva e non esce 0. Una chiave tolta da `SORVEGLIATI` senza finire in un controllo che gira davvero ferma la pubblicazione. La domanda a Grok non viene nemmeno costruita se la data non è oggi e se nel testo non ci sono le lezioni ancora ipotesi.

Le quattro cose che funzionano, spremute sullo stesso percorso:

- «Il lavoro avanza» va applicato alla riparazione: il testimone è il numero di record `ver` scritti nel giro, non il titolo del commit.
- L'ipotesi prima dei dati, per le lezioni di oggi, è un caso in `incidenti.py` scritto prima che la voce entri in `LEZIONI`. Senza quel caso la voce non entra.
- La taglia accanto al prezzo è già calcolata. `modello.py` deve leggere `_uscita_100`. H7 non si tocca.
- `pubblica.sh` deve eseguire questi tre rifiuti. Un secondo script finisce come le regole già scritte in dieci file.

Sulle uscite di oggi, che sono vuote. Le due che contano sono le istruzioni a Grok e il canale ipotesi/verdetto.

Le istruzioni sono quelle del 27/09. Chiedono, in generale, come si misura un mercato e come si tiene in piedi un sistema di agenti, e allegano i titoli vecchi di `RICERCA_GITHUB.md`. Non contengono gli id ancora `ipotesi`, né i titoli di commit ripetuti, né le chiavi tolte alla sentinella. `file_citati` scarta niente, perché nessuno lo chiama. Domani `su_x()` e `su_github()` si rifiutano di restituire il testo se la data nella versione non è oggi oppure se nel testo manca un id che `lezioni.verifica()` segna `ipotesi`. La risposta si tiene solo se nomina un file che esiste e un caso che sta in `incidenti.py`. Alzare il numero di versione lasciando gli stessi paragrafi non passa. Nessuna chiamata a `api.x.ai`: si usa `consulta_grok.chiedi`, abbonamento già pagato.

Il verdetto di domani non è un'altra pagina. `la-convenzione-che-decide` entra solo insieme al caso congelato: cinque vendite da polvere, `_uscita` che sembra un guadagno, `_uscita_100` a −0,98. `modello.py` legge quel campo. Rifare la giornata di oggi vorrebbe dire altre duemila righe di commento e un'altra voce con `prova: None`.

Non stai misurando cinque cose che sono già nel codice: quante volte si ripete lo stesso titolo (sono sei bersagli, non ventisei riparazioni); quante lezioni di oggi nascono con `prova` vuota (due su due); l'età di `VERSIONE` (due giorni, e nel JSON non c'è); quanti lettori ha `_uscita_100` (zero); quante chiavi escono da `SORVEGLIATI` in un giorno. `prove()` conta la parola `ripar` e le righe che iniziano con `#`. Entrambe salgono proprio quando l'errore si sta ripetendo.

```azioni
[
  {"cosa": "In agents/domande_grok.py fai sollevare SystemExit da su_x e su_github se la data in VERSIONE non e' oggi UTC o se il testo non contiene ogni id che lezioni.verifica() segna ipotesi e i titoli di commit ripetuti almeno due volte; accetta() scarta la risposta se file_citati e' vuoto o se non nomina un caso presente in incidenti.py; piu_intelligente.main chiama su_x() prima della domanda e si ferma se solleva, e prove() registra la versione. L'invio passa solo da consulta_grok.chiedi", "dove": "agents/domande_grok.py", "perche": "rende impossibile rimandare domani la domanda del 27/09, che non nomina una lezione ancora non provata e quindi non puo' trovare niente di nuovo", "difficolta": "bassa"},
  {"cosa": "In agents/lezioni.py esci 1 se una lezione ha prova vuota, e per le prove porta: esegui il controllo invece di cercare la frase in pubblica.sh; aggiungi in incidenti.py il caso convenzione (cinque vendite da polvere, _uscita che sembra un guadagno, _uscita_100 a -0.98) e aggancialo a la-convenzione-che-decide; in modello.py leggi _uscita_100 al posto di _uscita; pubblica.sh lancia lezioni.py. Non toccare verdetto_h7.esito", "dove": "agents/lezioni.py", "perche": "rende impossibile registrare la scoperta di oggi come commento e continuare a decidere col decreto delle cinque vendite", "difficolta": "media"},
  {"cosa": "In agents/ripara_orario.py, se questo processo ha svuotato fatti perche' VERSIONE_LOGICA e' cambiata, non salvare il segnalibro ed esci 1 quando i record con ver scritti in questo giro sono zero", "dove": "agents/ripara_orario.py", "perche": "rende impossibile la quarta ottimizzazione della riparazione che invalida il segnalibro, riscrive le stesse sei schegge e risulta ugualmente riuscita", "difficolta": "media"},
  {"cosa": "In agents/sentinella.py aggiungi SMALTISCONO, controllato sull'ultimo passaggio registrato da heartbeat, e in pubblica.sh esci 1 se il diff toglie una chiave da SORVEGLIATI senza inserire la stessa stringa in SMALTISCONO; sentinella.py esce 1 se una voce di SMALTISCONO non ha un passaggio recente", "dove": "agents/sentinella.py", "perche": "rende impossibile zittire, dopo un falso allarme, l'unico controllo che in due giorni ha visto ogni guasto silenzioso", "difficolta": "media"}
]
```

---

# La domanda di oggi — 27/09/2026

*«Come posso essere piu' forte, piu' sveglio, piu' preciso di ieri?» — fatta ogni giorno, sui fatti
del giorno. Idea di Nicolo, 27/09: e' la domanda schedulata che fa crescere l'intelligenza invece di
lasciarla ferma.*

**I fatti su cui e' stata fatta:** {"cambiamenti_veri": 940, "scritture_delle_corsie": 5776, "righe_di_lezione_aggiunte": 27, "file_di_codice_toccati": 56, "cambiamenti_su_'ripar'": 859, "cambiamenti_su_'guardia'": 6, "cambiamenti_su_'rete'": 4, "cambiamenti_su_'verific'": 1, "cambiamenti_su_'soccorso'": 4, "titoli_dei_cambiamenti": ["database giro1 08:37Z", "riparazione base/2 08:29Z", "riparazione base/0 08:29Z", "riparazione base/1 08:29Z", "sentinella 08:34Z", "la domanda vale anche sulle cose buone: nessuno critica una proposta che non e' sbagliata", "sentinella 08:21Z", "heartbeat 08:21Z", "accumulator 2026-09-27T08:21Z", "riparazione robinhood/1 08:21Z", "riparazione base/1 08:20Z", "la domanda quotidiana: sui fatti del giorno, sugli errori E su cio' che funziona, e produce azioni con uno stato"], "documenti_prodotti": ["CFO.md", "COORTE.md", "DATABASE_CORSIA.md", "EXPLORER_robinhood.md", "HEARTBEAT.md", "IPOTESI_H7.md", "ISPEZIONE.md", "PER_L_INVESTITORE.md", "QUALITA_DB.md", "RECOVERY_whale-radar.md"], "ipotesi_registrate": ["IPOTESI_H7.md"], "verdetti_emessi": [], "giri_di_ricerca": []}

---

I parto dai fatti misurati e dal codice, così le azioni indicano file veri e non buoni propositi.I leggo le lezioni già scritte, le uscite di oggi e il punto in cui la ricerca e la pubblicazione si rifiutano di procedere.La famiglia è una sola: si aggiorna un anello della catena e l'anello dopo resta quello di ieri. La formula del prezzo è stata corretta in `verso.py`, e `cercatore.py` calcola ancora il rendimento con `pp[-1] / p0` senza `V.valuta`. La taglia è stata scritta in `insieme.py` (`_valuta_sopra_10x`) e `_uscita` resta la mediana dei prezzi appena ci sono cinque vendite: un 10x fatto di polvere passa ancora. Gli operai della riparazione sono stati «migliorati» tre volte e il testimone che guarda se l'archivio cresce non è stato toccato. Tre corsie nuove sono nate come file `.yml`, mentre `heartbeat.CORSIE` e `staffetta.CORSIE` elencano ancora le stesse quattro. Il 45 è rimasto nel codice il giorno in cui è stata cancellata la frase che lo giustificava. In tutti e quattro i casi `pubblica.sh` ha lasciato passare, perché si rifiuta solo se un file non compila.

L'unico gesto che già non si può saltare è quel push. Il rifiuto va messo lì, sulla stessa porta: un metro congelato, un registro unico delle corsie, e il divieto di cancellare la ragione di un numero lasciando il numero.

Le quattro cose che funzionano, spremute:

- La sentinella ha visto i guasti silenziosi, ma `sentinella.yml` ha `continue-on-error: true` e il job chiude con `exit 0`. Il guasto torna verde, che è il difetto che la sentinella esiste per eliminare. `riparazione` non è in `SORVEGLIATI`.
- H7 è registrata prima dei dati. Le soglie stanno in prosa. `verdetto_h4.py` le tiene in costanti; per H7 un file equivalente non c'è, quindi sotto i 600 pool qualunque script può stamparle.
- La taglia ha ucciso l'11% a mano. Sul percorso che cerca ancora, `_uscita` non la consulta.
- `pubblica.sh` ferma la sintassi. Lo stesso script deve fermare il metro falso e la corsia orfana. Un secondo script finisce come le regole già scritte in dieci file.

Domani, sulle uscite di oggi. I giri di ricerca sono zero e i verdetti sono zero: le due uscite che contano sono H7 e le istruzioni di ricerca.

H7 va eseguita da `agents/verdetto_h7.py`, sullo stampo di `verdetto_h4.py`. Sotto i 600 pool giudicabili lo script esce senza stampare i terzi. Le tre condizioni di morte sono costanti, non frasi. L'output ha un campo obbligato, `sopravvivenza_senza_guadagno`, così la trappola già scritta nel documento (sopravvive e non rende) non può essere raccontata come una vittoria. Nessun altro taglio: niente quartili, niente seconda chain.

Le istruzioni a Grok sono ferme a `VERSIONE_PROMPT = "v1-2026-09-16"` in `agents/social_snapshot.py`, e quella domanda chiede quali memecoin hanno attenzione anomala. Una ricerca su GitHub eseguibile dal codice non esiste: `RICERCA_GITHUB.md` è un diario, e un diario non migliora da solo. Domani le due domande vivono in `agents/domande_grok.py`, con una versione nel nome. Il testo riceve i titoli già presenti in `RICERCA_GITHUB.md`. La risposta deve nominare un `file_nostro` che esiste nel repository e la riga che cambierebbe; il parser butta il resto. La domanda chiede un meccanismo (metro, corsia che muore verde, taglia contro prezzo) agganciato a un file nostro. Il giro passa da `consulta_grok.chiedi`: abbonamento già pagato, €0. Non aggiungere chiamate a `api.x.ai`.

Quello che non stai misurando, e che si vede prima del commit: i `.yml` con `schedule` assenti da `heartbeat.CORSIE` (il delta sarebbe stato +3 nell'ora in cui hai creato le corsie); i campi `_` scritti da `insieme.py` e non letti da `cercatore.py`; i commenti cancellati accanto a un assegnamento numerico rimasto uguale. `prove()` conta la parola «ripar» nei messaggi (859) e non il tempo fra il guasto e il momento in cui qualcuno se ne accorge, che è la misura che `PER_L_INVESTITORE.md` chiama apprendimento.

```azioni
[
  {"cosa": "Scrivi agents/prova_metro.py con quattro casi congelati (acquisto contato vendita su token0 e su token1, 10x con taglia da polvere, pool non osservato fino all'orizzonte) e fai calcolare _uscita solo sulle vendite sopra la soglia di taglia, usata sia da insieme.py sia da cercatore.py; pubblica.sh lo esegue e esce 1 se fallisce, e esce 1 anche se il diff cancella un commento nelle prime 40 righe lasciando intatto l'assegnamento numerico accanto", "dove": "pubblica.sh", "perche": "rende impossibile ripubblicare un metro col verso, la taglia o la finestra sbagliati, e un parametro rimasto dopo la cancellazione della sua ragione", "difficolta": "media"},
  {"cosa": "Crea agents/corsie.py come unico elenco (nome, yml, prefisso, minuti, archivio) letto da heartbeat.py, sentinella.py e staffetta.py, registraci database, riparazione, insieme e soccorso, togli continue-on-error e l'exit 0 finale da sentinella.yml, e in pubblica.sh esci 1 se un yml toccato dal commit non e' nell'elenco o non ha ne' il dispatch di se stesso ne' un archivio sorvegliato", "dove": "agents/corsie.py", "perche": "rende impossibile creare o ottimizzare una corsia che il custode non riaccende e che la sentinella non vede ferma", "difficolta": "media"},
  {"cosa": "Scrivi agents/verdetto_h7.py che esce senza stampare i terzi se i pool giudicabili sono meno di 600, applica le tre soglie di IPOTESI_H7 come costanti e scrive sempre il campo sopravvivenza_senza_guadagno", "dove": "agents/verdetto_h7.py", "perche": "rende impossibile sbirciare H7 prima dei 600 pool o venderne la sopravvivenza come un guadagno", "difficolta": "bassa"},
  {"cosa": "Scrivi in agents/domande_grok.py le due domande versionate per X e GitHub, passando i titoli gia' in RICERCA_GITHUB.md e scartando ogni risposta il cui file_nostro non esiste nel repo; il giro le manda solo a consulta_grok.chiedi e prove() registra la versione", "dove": "agents/domande_grok.py", "perche": "rende impossibile ripetere domani la stessa domanda del 16/09 sui token in attenzione, che non nomina un file nostro e quindi non puo' migliorare", "difficolta": "bassa"}
]
```

---

