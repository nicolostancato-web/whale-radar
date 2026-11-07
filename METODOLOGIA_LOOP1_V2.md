# 🔬 Loop 1 — metodo, versione 2

*21 settembre 2026, notte · PROPOSTA · il loop 1 resta SPENTO*

La v1 è stata sottoposta ad Astra come revisore esterno indipendente. Ha prodotto dieci rilievi e
**il documento ne è uscito parecchio ridimensionato**. Questa versione li incorpora.

La v1 resta in `METODOLOGIA_LOOP1.md` — non la cancello: serve a vedere cosa credevo di aver
risolto e non avevo risolto.

---

## 0. Cosa è cambiato, e perché

| dove | la v1 diceva | cosa non andava | la v2 dice |
|---|---|---|---|
| istanti | «solo record con `orario: catena`» | certifica un'etichetta, non l'affidabilità; e non distingue *quando è avvenuto* da *quando l'abbiamo saputo* | due tempi separati + test di invarianza al futuro (§2) |
| record scartati | «scartiamo il 5% non verificato» | quel 5% potrebbe essere proprio i pool morti e illiquidi: scartarli seleziona il mercato facile | si delimita l'effetto dei mancanti, non si nascondono (§2.3) |
| molteplicità | «Benjamini-Hochberg, non Bonferroni che è troppo severo» | **avevo scelto la protezione in base a quanto è facile superarla**; e BH non protegge il vincitore | si valida la *pipeline intera* su dati senza vantaggio (§3) |
| eseguibilità | «i candidati non eseguibili si escludono» | è una selezione nuova, e usa volume futuro rispetto al segnale | registro di tutti i segnali con stati, nessuna cancellazione postuma (§4) |
| cassaforte | «una apertura per ipotesi» | cento ipotesi = cento sbirciate | contatore per l'**intero programma**, e un custode separato (§5) |
| indipendenza | «200 pool per cella, bootstrap a blocchi» | pool ≠ osservazioni indipendenti; posizioni a cavallo fra le fasi | cluster dichiarati, tagli sugli **esiti** non sulle nascite (§6) |
| soglie | numeri scelti | guardrail organizzativi presentati come garanzie statistiche | derivate da un'analisi di potenza, o si dichiara «non identificabile» (§7) |
| mediana | «la media di portafoglio è ciò che finisce sul conto» | l'equivalenza non regge senza capitale, sizing, concorrenza fra segnali | si misura se il guadagno dipende da pochi eventi mai ripetuti (§8) |
| loop 0 | «sorveglia che il loop 1 rispetti il metodo» | **la stessa mano** → non è verifica indipendente; e un controllo era logicamente sbagliato | blocca da fuori invece di osservare da dentro (§9) |

Una frase della v1 va citata perché è istruttiva: avevo scritto *«Benjamini-Hochberg, non
Bonferroni che sarebbe troppo severo qui»*. In un documento il cui scopo dichiarato è impedire di
auto-ingannarsi, **avevo scelto il controllo statistico in base a quanto è facile passarlo**, e non
me ne ero accorto. È il motivo per cui la revisione esterna non è un lusso.

---

## 1. Cosa resta valido dalla v1

Non tutto è caduto. Restano:

- la diagnosi del loop 1 attuale: 90 configurazioni, si prende la migliore, **si applica da sola**;
- «togliere i tre migliori» è un autogol su una distribuzione a coda destra;
- lo slippage fisso al 15% è una finzione che favorisce i casi dove sbaglia di più;
- l'auto-applicazione va tolta;
- l'unità di analisi è il pool, non lo scambio;
- la soglia «almeno 20 scambi» guarda il futuro e va sostituita prima di accendere;
- cercare **condizioni** è più pericoloso che cercare parametri, non meno.

Quest'ultimo punto Astra non l'ha contestato, e resta il cuore del problema.

---

## 2. I due tempi: quando è successo, quando l'abbiamo saputo

Il rilievo più utile della revisione, perché è una distinzione che non avevo proprio.

Ogni evento porta **tre** marcature, non una:

| campo | significato |
|---|---|
| `event_time` | quando è avvenuto sulla chain |
| `posizione` | l'ordinamento dentro il blocco (chi viene prima) |
| `available_at` | **quando è diventato leggibile dal nostro decisore** |

Una transazione avvenuta prima della decisione può essere arrivata a noi dopo. Usarla è conoscenza
del futuro anche se il suo istante è verificato: tutto il lavoro di questi giorni sugli istanti
risolve il primo campo, non il terzo.

**Una feature è ammessa solo se `available_at < t_decisione`.** Non `event_time`.

### 2.1 Il test di invarianza al futuro

Il controllo che rende la regola verificabile invece che dichiarata:

1. si calcola la decisione usando **solo** il prefisso disponibile a `t_decisione`;
2. si aggiungono gli eventi successivi;
3. **la decisione precedente non deve cambiare.**

Se cambia, da qualche parte stiamo leggendo il futuro. Questo test si esegue su un campione a ogni
giro, e il suo esito si riporta.

### 2.1.bis Quanto ne abbiamo davvero — misurato, non stimato

Il terzo tempo in parte **ce l'abbiamo già**: ogni record porta `ts` (quando è avvenuto), `acq`
(quando l'abbiamo raccolto) e `ritardo` = la differenza. Non lo stavamo usando come cancello.

Ma `acq` è una disponibilità **vera** solo per i record presi dal vivo. Per quelli ricostruiti a
posteriori dice soltanto quando abbiamo fatto il recupero, e come informazione sulla conoscibilità
vale zero. Il campo `classe` distingue i due casi, e misurato oggi (campione 1 file su 40):

| | `point-in-time` (disponibilità vera) | `ricostruzione-storica` + `recupero-buco` |
|---|---|---|
| base | **16,6%** | 83,4% |
| robinhood | **37,5%** | 62,5% |

Ritardo di raccolta sui soli point-in-time: **mediano 1-3 secondi, novantesimo percentile 180-361
secondi, massimo 899 secondi**. Quindici minuti, sul caso peggiore.

**Tre conseguenze, tutte scomode:**

1. Le feature di decisione possono usare **solo i record point-in-time** — cioè oggi un sesto dei
   dati su base e poco più di un terzo su robinhood. I ricostruiti servono per gli **esiti** (cosa
   è successo dopo), mai per stabilire cosa era sapibile prima.
2. Il ritardo non è trascurabile e va **dentro la simulazione**: un segnale che si basa su un
   evento arrivato con sei minuti di ritardo va valutato a sei minuti di ritardo, non a zero.
3. Se dopo questo filtro il campione point-in-time è troppo piccolo per l'analisi di potenza
   (§7), la risposta corretta è **raccogliere più dati dal vivo**, non allentare il requisito.

Questo è anche un argomento a favore del lavoro in corso: ogni ora che i raccoglitori girano dal
vivo produce dati che valgono per la decisione, mentre il recupero storico produce dati che
valgono solo per l'esito.

### 2.2 Lo storico del creatore

Trappola concreta che Astra ha nominato: «come sono andati i pool precedenti dello stesso
creatore» sembra passato, ma se uno di quei pool è ancora aperto il suo *esito* è futuro. Si usa
solo l'esito dei pool **già chiusi** a `t_decisione`.

### 2.3 Il 5% non verificato non si butta: si delimita

La v1 diceva «si usano solo i record verificati». Ma i record non verificati potrebbero essere
sistematicamente i pool morti, caotici, illiquidi — cioè i casi difficili. Scartarli in silenzio
significa **misurare il mercato facile e chiamarlo il mercato**.

Quindi si riporta sempre, accanto a ogni risultato:

- quanti record/pool sono esclusi e **come sono fatti** rispetto agli inclusi (liquidità, età,
  numero di scambi, chain, periodo);
- un **intervallo di sensibilità**: quanto cambierebbe il risultato se i mancanti avessero avuto
  esiti sfavorevoli plausibili.

Se quell'intervallo contiene lo zero, il risultato vale **solo per il sottoinsieme verificabile** e
va scritto così, non attribuito alla popolazione.

---

## 3. La molteplicità: si valida la pipeline, non il test

La v1 sceglieva una correzione statistica. Astra ha mostrato che non basta: Benjamini-Hochberg
controlla la quota di false scoperte fra quelle **dichiarate**, non la probabilità che l'unica
configurazione mandata in produzione sia falsa. E con celle sovrapposte, rendimenti dipendenti e
ipotesi adattive, contare i confronti non rende validi i p-value.

**La v2 non si affida a una correzione. Misura il tasso di falsi allarmi dell'intero procedimento.**

### 3.1 La prova del motore a vuoto

Prima di poter promuovere qualunque risultato, si fa girare **l'intera pipeline** — ricerca delle
soglie, scelta delle uscite, sizing, filtri, scelta del test, scelta delle finestre — su dati
**sintetici costruiti senza alcun vantaggio**, ma con:

- la stessa asimmetria a destra dei rendimenti veri;
- la stessa dipendenza fra token contemporanei;
- la stessa frequenza di eventi rari.

E si misura: **quante volte promuove almeno un candidato?**

Se su dati dove per costruzione non c'è niente la pipeline promuove qualcosa nel 30% dei casi,
allora una promozione sui dati veri vale quanto quella. La soglia dichiarata prima: **non più del
5%**. Se il tasso misurato è più alto, la pipeline non è validata e non si promuove niente —
non si aggiusta la soglia.

Questa è la difesa che nella v1 mancava, ed è più forte di qualunque correzione, perché misura
quello che ci interessa davvero: *quanto facilmente questa macchina trova cose che non ci sono.*

### 3.2 Cosa si dichiara prima

1. la famiglia completa dei test confermativi;
2. **quale errore vogliamo controllare** — la quota di false scoperte nel catalogo, oppure la
   probabilità di almeno una falsa promozione. Sono cose diverse e si sceglie prima;
3. la procedura, compatibile con dipendenza e selezione.

---

## 4. Il registro dei segnali: niente si cancella dopo

La v1 escludeva i candidati «non eseguibili». Astra: è una selezione nuova, e per giunta basata su
volume futuro rispetto al segnale.

**Nessun segnale si cancella.** Ognuno finisce nel registro con uno stato:

| stato | significato |
|---|---|
| `rifiutato_prima` | scartato in base a informazioni già disponibili a `t_decisione` |
| `tentato_fallito` | tentato e non eseguito — **con i costi sostenuti** |
| `eseguito_parziale` | riempito in parte |
| `comprato_liquidato` | ciclo completo |
| `comprato_non_liquidabile` | comprato e **non vendibile**: perdita totale, non un candidato da scartare |

Il risultato si calcola **sul capitale iniziale e sul calendario dell'intero processo**, includendo
la cassa ferma, i tentativi falliti e le posizioni ancora aperte alla fine.

E cade una frase della v1 che avevo scritto con sicurezza: *«un pool che non ha mai fatto nulla è
un'osservazione con rendimento negativo»*. **Falso**, se non avremmo mai potuto comprarlo. Un pool
che non avremmo potuto toccare non è né un guadagno né una perdita: è fuori dall'universo
investibile, e va dichiarato tale prima, non dopo.

---

## 5. La cassaforte: un contatore per tutto il programma

La v1 diceva «una apertura per ipotesi». Cento ipotesi nominalmente diverse sono cento sbirciate
sullo stesso periodo, e ogni esito informa la ricerca successiva anche senza ritentare l'ipotesi
bocciata.

**Il contatore vale per l'intero programma di ricerca**, non per identificativo.

Inoltre:

- **inventario degli accessi passati.** Ciò che è già stato guardato durante riparazioni, grafici o
  analisi precedenti è **contaminato**, e chiamarlo oggi «cassaforte» non lo rende mai visto.
  Questo inventario va fatto prima di dichiarare quale periodo è la cassaforte.
- **prima di ogni valutazione finale si congela tutto**: candidati, codice, dati, costi, sizing e
  regola di promozione. Poi si valuta.
- **un custode separato esegue la valutazione**, e chi ha fatto la ricerca non tocca quei dati.
- dopo la restituzione dei risultati **quel periodo è consumato**: per nuove decisioni serve un
  periodo nuovo mai osservato, o un protocollo sequenziale con budget d'errore fissato prima.

---

## 6. Indipendenza: contare le scommesse, non le righe

Duecento pool possono essere pochissime scommesse indipendenti. Vanno dichiarati i legami:

- **stesso token su più pool** → una scommessa, non tante;
- **stesso creatore o stessa campagna** → famiglia correlata;
- **shock che attraversano le due chain** → contemporanei, non indipendenti.

Si riporta sempre: **numero di cluster**, concentrazione (quanto pesa il più grande) e sensibilità
degli intervalli a diverse lunghezze di blocco.

### 6.1 Il taglio si fa sugli esiti, non sulle nascite

Rilievo che mi era completamente sfuggito: una posizione **aperta** in esplorazione può **chiudersi**
durante la conferma. Tagliare per data di nascita del pool non separa gli esiti.

Quindi ogni osservazione porta due intervalli — quello delle feature e quello dell'esito — e
un'osservazione il cui esito sconfina nella fase successiva **esce dalla fase precedente**.

---

## 7. Le soglie: derivate, non scelte

I numeri della v1 (200 pool, 50/25/25, due condizioni, tre finestre) erano guardrail organizzativi
presentati come garanzie statistiche. La v2 li tratta come **provvisori fino all'analisi di
potenza**:

1. si definisce l'**effetto minimo in unità economiche** — quanto deve rendere, su quale capitale e
   quale orizzonte, per valere il rischio e il margine di errore sui costi. Non «significativo»:
   *quanto*;
2. si misura, sulla pipeline a vuoto (§3.1), **quanta potenza** abbiamo di rilevare quell'effetto
   con N osservazioni e quella durata di finestra;
3. da lì escono il campione minimo e la lunghezza delle finestre.

Se i dati non bastano, l'esito è **«non identificabile con questo campione»** — non una soglia più
bassa.

Nota su «tre finestre consecutive»: possono essere tre pezzi dello stesso episodio di mercato. Le
finestre vanno scelte per coprire **regimi diversi**, e il regime va dichiarato.

---

## 8. Mediana e media: la domanda giusta

Astra conferma la critica alla mediana ma smonta la mia conclusione. *«L'unico meccanismo che
funziona nelle memecoin è la coda»* era una premessa che davo per acquisita, ed è da dimostrare.
E «media di portafoglio» non significa niente senza capitale, sizing, concorrenza fra segnali,
reinvestimento e orizzonte.

**La formulazione corretta è la sua**: non serve sostituire la media con la mediana — serve poter
distinguere un **rendimento atteso positivo** da una **stima dominata da pochi eventi non
replicati**.

Quindi si definisce prima il processo patrimoniale completo (capitale, quanto per posizione,
cosa succede quando due segnali competono, se si reinveste, su quale orizzonte si chiude il
conto), e accanto al risultato si riporta sempre:

- **quanti eventi sostengono il guadagno** (se sono cinque su duemila, si dice);
- il contributo dei maggiori vincitori e dei cluster al risultato;
- il risultato escludendoli, **come diagnostica e non come criterio** (differenza fondamentale
  rispetto al `robusta` del codice attuale, che lo usava per decidere);
- se quegli eventi ricompaiono nei periodi indipendenti, o sono successi una volta sola.

E un limite del bootstrap da tenere presente: **non inventa eventi rari mai osservati**. Se la coda
vera è più grassa di quella vista, gli intervalli sono ottimisti.

---

## 9. Loop 0: blocca da fuori, o è teatro

Il rilievo più duro, e il più giusto. Parole sue:

> *«La stessa mano non rende il sorvegliante inutile; rende illegittimo chiamarlo verifica
> indipendente. Se controlla soltanto contatori e file prodotti dal sorvegliato, è prevalentemente
> teatro.»*

E mi ha trovato un errore logico nella v1: il controllo «zero record scartati ⇒ il cancello è
rotto» è **sbagliato**, perché zero può essere corretto se il filtro avviene prima della lettura.

Il loop 0 diventa una difesa vera solo se:

1. **impedisce materialmente**, invece di osservare: i permessi di lettura della cassaforte e di
   scrittura della configurazione operativa stanno **fuori** dal loop 1, e il loop 1 non li ha;
2. **usa log prodotti dall'infrastruttura di accesso**, non dal processo sorvegliato;
3. **esegue test avversariali preparati da un revisore diverso**, non derivati dalle stesse
   funzioni che dovrebbero fallire: leakage deliberato, lettura non autorizzata, modifica senza
   approvazione, acquisto non vendibile, e **riproduzione deliberata dell'artefatto di agosto**;
4. **misura sé stesso**: quota di violazioni intercettate, falsi allarmi, tempo di rilevazione.
   Ogni caso critico noto dev'essere intercettato, e se non lo è il loop 0 è scoperto lì.

### 9.1 E intanto va allineato al presente

Indipendentemente dal loop 1, oggi il loop 0 dichiara **«36 componenti non rispondono»** cercando
agenti che abbiamo spento noi su chain fuori perimetro. Tre stati invece di due — *funziona*,
*fermo per decisione*, *rotto* — e solo il terzo è un allarme.

Un cruscotto che segnala rosso quando tutto va bene smette di essere letto, e quando il rosso sarà
vero non se ne accorgerà nessuno.

---

## 9.bis Tre regole prese da fuori (22/09)

Dal metodo di lavoro di un analista crypto, portato dal fondatore come materiale di studio. Quasi
tutto il suo impianto non ci riguarda — e' analisi fondamentale di progetti con ricavi, sblocchi,
tesoreria e concorrenti, mentre noi guardiamo memecoin senza fondamentali su un orizzonte di
minuti. Ma tre cose sono trasversali e qui mancavano.

### 9.bis.1 La lista dei candidati si costruisce, non si eredita

*«Non partire da un elenco predeterminato: costruisci un insieme ampio di candidati, elimina, e
presenta solo i finalisti.»*

Serve a non analizzare sempre le stesse cose per abitudine. Per noi e' la stessa cosa che ha
contestato la revisione esterna: **il denominatore deve nascere fuori dal database**. Se la
popolazione la ricaviamo da cio' che gia' raccogliamo, misuriamo la qualita' del nostro sguardo,
non quella del mercato.

### 9.bis.2 Ogni ipotesi porta scritto, PRIMA, cosa la ucciderebbe

*«Cerca aggressivamente di smentire ogni tesi. Dichiara quale evidenza la invaliderebbe.»*

Questo ci mancava, ed e' il pezzo piu' utile. Abbiamo un revisore esterno che cerca le falle
**dopo**, ma nessuna regola che obblighi a dichiarare in anticipo **quale risultato farebbe cadere
l'ipotesi**. Senza quella dichiarazione si puo' sempre razionalizzare un esito deludente: si
restringe una condizione, si cambia finestra, si trova la spiegazione.

Quindi ogni riga di `IPOTESI.md` deve contenere, scritta prima di misurare:

- la condizione attesa e la direzione;
- **la soglia sotto la quale l'ipotesi e' morta** — non «poco convincente»: morta;
- cosa faremmo se il risultato fosse a meta', deciso prima e non dopo.

Un'ipotesi senza condizione di morte non entra nel registro.

### 9.bis.3 Ogni risultato finisce con «su cosa potrei sbagliarmi»

*«Prima di rispondere, sfida le tue conclusioni: cosa mi sfugge? Quale assunzione e' piu' debole?
Cosa mi farebbe cambiare idea?»*

Sezione obbligatoria in ogni esito del loop 1, non facoltativa. Deve nominare **l'assunzione piu'
debole** invece di lasciarla implicita, e dire quale misura la metterebbe alla prova.

Non e' una formalita': il 22/09 il database e' passato da «esame superato» a «17% di dati
sbagliati» esattamente perche' qualcuno ha fatto quella domanda a voce alta.

### 9.bis.4 Cosa NON prendiamo, e perche'

Quello stesso metodo chiede un **punteggio unico** («Research Score») per confrontare le
opportunita' in tabella. E' comodo, ed e' esattamente l'errore del vecchio loop 1: comprimere un
fenomeno in un numero e poi inseguire quel numero. Il resto di questo documento esiste per non
farlo.

Prendiamo la disciplina, non la classifica.

---

## 9.ter Tre cose da TradingAgents (22/09)

Repository studiato su indicazione del fondatore: un sistema di agenti AI che discutono per
decidere operazioni su azioni — analista dei fondamentali, delle notizie, del sentiment, poi un
ricercatore ottimista e uno pessimista che si sfidano, un gestore del rischio, un responsabile che
approva.

**Quasi tutto il suo impianto non ci riguarda**, e non per snobismo: le memecoin non hanno bilanci,
non hanno copertura giornalistica, e il loro «sentiment» E' la manipolazione che stiamo cercando di
misurare — analizzarlo significherebbe prendere il rumore per segnale. Inoltre il loro orizzonte e'
di giorni e il nostro di minuti: un modello che ragiona trenta secondi arriva a corsa finita, e
costerebbe una chiamata a pagamento per ogni decisione.

Tre cose pero' sono strutturali e valgono.

### 9.ter.1 Il pessimista e' un RUOLO, non un controllo finale

Loro hanno un agente il cui unico mestiere e' costruire il caso contro, e che discute alla pari con
quello a favore. Noi abbiamo Astra che cerca le falle **dopo** che l'ipotesi e' formulata.

La differenza conta: cercare errori in una tesi gia' scritta e' piu' debole che **costruire la tesi
opposta**. Quindi ogni ipotesi del loop 1 deve arrivare in coppia:

- la spiegazione proposta;
- **la spiegazione alternativa piu' forte che riusciamo a costruire** — di solito: «e' un artefatto
  di esecuzione», «e' un effetto di periodo», «e' selezione sui sopravvissuti».

Se non riusciamo a costruire l'alternativa, non e' perche' non c'e': e' perche' non abbiamo
guardato abbastanza. Quella e' la condizione per passare, non un di piu'.

### 9.ter.2 Il registro delle decisioni si chiude da solo

Scrivono ogni decisione PRIMA di conoscerne l'esito, e la valutano automaticamente quando la
finestra di detenzione si chiude, raggruppando per giudizio dato.

E' la registrazione preventiva resa MECCANISMO invece che buona intenzione — ed e' il pezzo che
alla v2 mancava. Non basta scrivere le ipotesi prima: serve che il punteggio arrivi da solo, dopo,
senza che nessuno debba ricordarsi di andarlo a prendere. Altrimenti si ricordano le previsioni
azzeccate e si dimenticano le altre.

Quindi: ogni segnale registrato porta la sua finestra di valutazione, e un processo separato lo
chiude e lo segna — anche quando e' andato male. Soprattutto quando e' andato male.

### 9.ter.3 La loro riga piu' preziosa e' il disclaimer

> *«I risultati del backtest non sono garantiti... dipendono dal modello, dalla temperatura,
> dall'intervallo di date, dalla qualita' dei dati e dal campionamento.»*

Detto onestamente da loro, e' un avvertimento per noi: **i loro risultati non sono riproducibili**.

Da qui una condizione che alla v2 mancava e che aggiungiamo: **un risultato che cambia al cambiare
di un'impostazione non e' un vantaggio, e' un campione di un processo casuale.** In pratica, prima
di promuovere qualunque cosa:

- si rifa' con un seme diverso;
- si rifa' con una finestra spostata;
- si rifa' con le soglie mosse di poco.

Se il risultato sopravvive a tutte e tre, puo' passare al vaglio successivo. Se ne cade anche una
sola, il risultato era della configurazione, non del mercato.

### 9.ter.4 Cosa NON prendiamo

**La discussione fra agenti.** Un dibattito fra modelli produce prosa convincente, non evidenza — e
su un mercato senza fondamentali produrrebbe narrativa sopra il rumore. E' esattamente il pericolo
gia' scritto in questo documento: una spiegazione plausibile convince piu' di una percentuale alta,
e per questo e' piu' pericolosa.

Prendiamo la separazione dei ruoli. Non la conversazione.

---

## 9.quater Non abbiamo l'inizio della vita dei pool (22/09, misurato)

Verificato contro le nascite gia' chieste alla catena:

| | il nostro primo blocco E' la nascita | arriviamo dopo | ritardo mediano |
|---|---|---|---|
| base | 26,2% | 73,8% | 3.805 blocchi (~2 ore) |
| robinhood | 8,6% | 91,4% | 46.696 blocchi |

Quindi **ogni condizione che dipende dalla prima vita di un pool** — eta' al momento della
decisione, primi compratori, concentrazione iniziale, lancio coordinato — e' utilizzabile solo
sulla minoranza di pool di cui abbiamo davvero l'inizio. Altrove misurerebbe quando e' arrivata la
nostra raccolta.

Questo NON si risolve con un filtro: e' un buco nella raccolta. Si risolve o restringendo la
popolazione a quei pool (dichiarandolo), o raccogliendo le nascite d'ora in avanti.

---

## 9.quinquies Due vincoli presi dai fallimenti altrui (22/09)

**Il costo si modella al DOPPIO di quello osservato.** Chi ha perso soldi con questi bot raccomanda
di raddoppiare lo slippage storico. Il motivo vale anche per noi: il nostro impatto e' misurato su
scambi RIUSCITI e per lo piu' piccoli. Un caso documentato: ordine grosso su token sottile, 5,7
milioni persi su 9 perche' il prezzo si e' mosso del 60% durante l'esecuzione.

**Le strategie di entrata rapida sono fuori dal nostro spazio di ricerca.** Chi le fa modella
100-200 millisecondi di latenza. La nostra, misurata, e' di **1-3 secondi mediani e fino a 15
minuti** nel caso peggiore: da dieci a mille volte piu' lenta.
Il loop 1 non deve cercare vantaggi che vivono dentro il singolo blocco — non li potremmo cogliere
nemmeno se li trovasse. Cio' che cerchiamo deve sopravvivere a una latenza di secondi.

E' un pezzo di spazio eliminato con una misura invece che con settimane di tentativi.

---

## 9.sexies Il metro e' l'ECCESSO, non il rendimento (22/09 sera, misurato)

I token si muovono insieme, e non poco. Misurata la quota di token in rialzo ora per ora:

| | base | robinhood |
|---|---|---|
| ore peggiori (decimo percentile) | 35% | 22% |
| ora tipica | 50% | 45% |
| ore migliori (novantesimo) | 67% | 61% |

Se fossero indipendenti quella quota resterebbe stabile. Oscilla di **31-39 punti**: esiste un
fattore comune — l'umore del momento — che muove tutto insieme.

**Conseguenza sul criterio.** Se in quell'ora saliva il 67% dei token e il nostro e' salito, non
abbiamo scelto bene: **abbiamo partecipato**. Un metro assoluto premia chi ha provato la strategia
in una settimana buona.

Quindi il criterio primario del loop 1 diventa il **rendimento in ECCESSO rispetto ai token
contemporanei** — mediana della sezione trasversale della stessa ora, stessa chain — non il
rendimento assoluto. Il rendimento assoluto resta come descrittivo, perche' e' quello che finisce
sul conto, ma non puo' decidere da solo se una regola seleziona.

**E rafforza due cose gia' decise:**
- il ricampionamento a blocchi temporali (i token contemporanei non sono osservazioni
  indipendenti: contarli come tali stringe gli intervalli molto piu' del vero);
- la necessita' di giornate DIVERSE, non di tante ore della stessa giornata. Tre finestre dentro
  lo stesso umore di mercato sono una finestra sola guardata tre volte.

---

## 10. Quando possiamo dire «forse c'e' qualcosa» — versione 2

Tutte, non una scelta:

1. l'ipotesi era **scritta prima** (o, se esplorativa, riconfermata da zero su dati mai visti);
2. la **pipeline a vuoto** promuove qualcosa in meno del 5% dei casi (§3.1);
3. il risultato supera l'**effetto minimo economico** dichiarato prima, non solo lo zero;
4. regge su **regimi diversi**, non su tre finestre dello stesso episodio;
5. regge sulla **cassaforte**, valutata da un custode separato, col programma congelato;
6. il **registro dei segnali** è completo: nessuna cancellazione postuma, i non liquidabili contati
   come perdita totale;
7. **l'esecuzione è validata** contro dati reali di esecuzione, non solo modellata (§11);
8. il guadagno **non dipende da pochi eventi mai ripetuti** (§8);
9. **l'effetto dei dati mancanti è delimitato** e non contiene lo zero (§2.3);
10. Astra ha **provato a spiegarlo altrimenti** e non ci è riuscito.

E anche allora si chiama *ipotesi che ha superato i controlli*. La parola edge si usa quando ha
fatto soldi veri, piccoli, in avanti.

---

## 11. Esecuzione: il punto dove siamo più deboli

Astra ha messo qui il rilievo numero uno, e va preso sul serio: **il modello di slippage migliore
può riprodurre il fantasma di agosto con più credibilità matematica di prima.**

Ricostruire le riserve dai soli scambi omette aggiunte e rimozioni di liquidità. Una curva a
prodotto costante non descrive ogni pool. E restano fuori: ordinamento delle transazioni, latenza,
fallimenti, restrizioni di vendita, imposte del token, competizione per l'esecuzione.

Il caso peggiore che nomina è quello che dovrebbe toglierci il sonno: **il picco può essere reale e
il profitto irrealizzabile.**

Quindi, prima di ammettere qualunque risultato economico:

- identificare la meccanica di ogni pool e **rifiutare quelli non supportati**;
- ricostruire lo **stato**, non solo gli scambi;
- confrontare il simulatore con una **raccolta prospettica** di preventivi ed esiti realmente
  osservati;
- misurare separatamente: errore sulla quantità ricevuta, ritardo, frequenza di fallimento, e
  **falsi positivi di vendibilità**;
- dove non ci sono osservazioni sufficienti, scrivere **«esecuzione non validata»** invece di
  applicare un costo convenzionale.

---

## 12. Cosa manca per costruirlo

1. il criterio point-in-time che sostituisce «almeno 20 scambi», e quanto cambia la popolazione;
2. `available_at`: in parte c'è già (`acq` sui record point-in-time), ma copre solo il 16,6% di
   base e il 37,5% di robinhood — vedi §2.1.bis. Il resto dei dati non può reggere decisioni;
3. lo stato dei pool (riserve nel tempo) per l'esecuzione, non solo gli scambi;
4. la pipeline a vuoto da costruire prima di qualunque ricerca vera;
5. l'inventario degli accessi passati, per sapere quale periodo può davvero fare da cassaforte;
6. l'esame del database in verde;
7. chi fa il **custode** e chi scrive i **test avversariali**: non possono essere la stessa mano
   che scrive il loop 1.

Il punto 7 non è risolvibile dentro questo progetto con un solo esecutore. La proposta onesta:
**il custode è Astra**, con un fascicolo che contiene i risultati e non il ragionamento che li ha
prodotti — così giudica il risultato senza essere stato guidato a giudicarlo bene.
