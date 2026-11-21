# 🔎 Ricerca GitHub — registro

*Terzo loop, avviato il 22 settembre 2026. Gira in parallelo a quello del database e a quello che
costruisce la macchina del loop 1.*

**Cosa fa.** Cerca su GitHub progetti su memecoin, bot, trading e analisi on-chain; li apre, li
legge, e tira fuori quello che ci serve. Non per copiare: per **non reinventare** quello che
qualcuno ha gia' capito, e per accorgerci di cose che non stavamo guardando.

---

## Le regole di questo registro

**1. «Sembra utile» non e' un esito.** In questo progetto abbiamo gia' pagato caro lo scambio fra
«dichiarato» e «verificato»: nella notte fra il 21 e il 22 settembre il database e' passato da
«esame superato» a «17% di dati sbagliati» in trenta minuti. Quindi qui una cosa risulta **PRESA**
solo quando e' stata fatta girare sui nostri dati e ha prodotto un numero. Tutto il resto e'
**DA PROVARE**, e si vede che non e' stato provato.

**2. La licenza conta.** Si prende codice solo da progetti con licenza permissiva (MIT, Apache),
citando la fonte. Codice senza licenza non si puo' usare, per quanto sia buono. Le IDEE invece si
possono sempre prendere: non si brevetta un ragionamento.

**3. Il valore di solito non e' il codice.** Finora, da tre fonti lette, abbiamo preso **zero righe
di codice e sei idee**. Il codice altrui risolve i problemi altrui: gira su altre chain, con altri
dati, per altri orizzonti. Quello che si trasferisce e' il modo di pensare — e i controlli che a
noi non erano venuti in mente.

---

## PRESO — provato sui nostri dati

### 1. Il controllo di vendibilita' → `agents/vendibilita.py`
**Fonte:** la famiglia dei bot «sniper» per memecoin su Solana, che prima di comprare verificano
che il token si possa RIVENDERE (esistono token progettati per farti entrare e non uscire). Loro lo
chiedono a servizi esterni a pagamento; noi l'abbiamo ricavato dai nostri stessi scambi.

**Perche' ci riguarda piu' che a loro.** Era il rilievo numero uno della revisione esterna:
*«il picco puo' essere reale e il profitto irrealizzabile»*. Nel nostro conteggio un pool del
genere risultava un GUADAGNO: vedevamo il prezzo salire e contavamo la salita.

**Misurato su base, 16.622 pool:**

| esito | quanti |
|---|---|
| normali — escono in molti | 83,1% |
| **sospetti — esce solo uno o due indirizzi** | **16,6%** |
| trappole — nessuno e' mai uscito | 0,3% |

Le trappole vere sono poche. Ma **un pool su sei** e' uno da cui praticamente nessuno esce, e
finora li contavamo come gli altri.

### 2. L'impatto misurato invece che modellato → `agents/impatto_reale.py`
**Fonte:** di rimbalzo, cercando librerie per la matematica degli AMM. Quelle librerie partono
dalle RISERVE del pool, che noi non abbiamo: ci avrebbero dato una formula esatta alimentata da
dati inventati. Cercandole ho capito che l'impatto potevamo **misurarlo** dai nostri scambi.

**Misurato su base, 912.628 osservazioni vere:** movimento di prezzo per scambio, mediano **0,45%**,
novantesimo percentile 4,62%. Il vecchio motore usava **15% fisso** per ogni pool e ogni dimensione.

### 3. L'aggressione a panino → `agents/panino.py`
**Fonte:** i progetti che rilevano attacchi MEV sui mercati decentralizzati (Sandwich Attack Risk
Predictor e simili). La tecnica di riconoscimento e' descritta con precisione: stesso indirizzo due
volte nello stesso blocco e nello stesso pool, versi opposti, e almeno un altro indirizzo IN MEZZO.

**Perche' era un punto cieco.** Stavamo simulando entrate senza considerare che qualcuno si infila
davanti: compra un istante prima facendo salire il prezzo, ci lascia comprare piu' caro, rivende
subito dopo. Non e' una commissione, e' un prezzo di entrata peggiore — e non compare da nessuna
parte se non lo si cerca apposta. Ci servivano solo dati che avevamo gia'.

**Misurato:**

| | base | robinhood |
|---|---|---|
| aggressioni trovate | 1.926 | 1.157 |
| pool colpiti almeno una volta | 6,9% | 4,1% |
| scambi finiti in mezzo | **0,91%** | **0,42%** |

Circa uno scambio su cento. Un costo reale ma contenuto: non e' lui a decidere se abbiamo un
vantaggio.

**L'avvertimento che conta piu' del numero:** chi aggredisce SCEGLIE gli ordini grossi, perche'
sono quelli che ripagano l'agguato. Se il nostro segnale fosse buono, i nostri ordini sarebbero
proprio quelli. Quindi l'uno per cento e' il tasso medio del mercato, non il nostro — e il nostro
va misurato per fascia di dimensione prima di fidarsi.

### 4. Il primo controllo dei nostri dati contro un metro ESTERNO

**Fonte:** lo studio pubblico «Pump.fun Graduation Regime Windows: Survival Analysis of 832.941
Token Launches» (dataset RED-PUMP-2026-v1, licenza CC-BY-4.0), piu' le statistiche su 18,67
milioni di token lanciati.

**Cosa dicono loro:** il **68,7%** dei token ha l'ultimo scambio lo stesso giorno in cui nasce.
Solo il 4,55% supera i 90 giorni.

**Perche' l'ho usato.** Era l'accusa piu' seria della revisione esterna: *«un database puo'
risultare perfetto sui record presenti perche' ha perso proprio quelli difficili»*. Se la nostra
raccolta vedesse solo i pool sopravvissuti abbastanza da farsi notare, la nostra quota di morti
precoci sarebbe molto piu' bassa della loro.

**Misurato sui nostri dati:**

| pool la cui attivita' finisce entro 24 ore | |
|---|---|
| **base (nostro)** | **68,2%** |
| **studio esterno, altra chain, 832.941 token** | **68,7%** |
| robinhood (nostro) | 74,5% |

Mezzo punto di distanza, su chain diverse e raccolte indipendenti. **E' la prima volta che
verifichiamo i nostri dati contro qualcosa di completamente fuori dal nostro sistema**, ed e'
esattamente quello che la revisione ci aveva chiesto: il metro deve nascere fuori dal database.

**L'onesta' d'obbligo:** chain diverse e meccaniche di lancio diverse, quindi la coincidenza
potrebbe essere fortuna. E' una prova, non una dimostrazione — ma punta nella direzione giusta, e
finora avevamo solo prove che punta vano nell'altra.

**Un problema emerso mentre guardavo:** su robinhood **nessun pool supera i 30 giorni** di vita.
Va capito se la chain e' giovane o se la nostra finestra di raccolta e' corta. Finche' non lo
sappiamo, qualunque analisi su orizzonti lunghi su quella chain non ha senso.

---

## DA PROVARE — idee buone, non ancora verificate da noi

### 3. Concentrazione dei primi dieci detentori
I bot rifiutano un token se i primi dieci indirizzi tengono piu' del 25%. E' una condizione
**osservabile al momento della decisione** — quindi ammissibile nel loop 1 — e la possiamo
ricostruire dai nostri scambi contando chi ha accumulato. Da misurare: quanto e' correlata con
l'esito, e se sopravvive alla prova del motore a vuoto.

### 4. Autorita' di emissione e di blocco
Su Solana controllano che il creatore non possa creare altri token ne' bloccare le vendite.
L'equivalente sulle nostre chain sono i contratti con funzioni di blocco o tassa sulla vendita.
Non lo possiamo leggere dagli scambi: servirebbe interrogare il contratto. **Costo da valutare
prima di provarci** — e il nodo di base tronca gia' le richieste a gruppi.

### 5. Il pessimista come ruolo (da TradingAgents)
Un agente il cui unico mestiere e' costruire il caso CONTRO, che discute alla pari con quello a
favore. Piu' forte di cercare errori in una tesi gia' scritta. Gia' scritto nel metodo (§9.ter),
da implementare.

### 6. Il registro delle decisioni che si chiude da solo (da TradingAgents)
Scrivono ogni decisione prima di conoscerne l'esito, e un processo separato la valuta quando la
finestra si chiude — anche quando e' andata male. A noi mancava il pezzo che va a prendere il voto
dopo: senza, ci si ricorda solo delle previsioni azzeccate.

### 5. La fuga con la cassa: non raccogliamo i movimenti di liquidita'

**Fonte:** i progetti che sorvegliano i memecoin su Ethereum e **Base — la nostra chain** — e che
usano come segnale principale i movimenti di LIQUIDITA': quando chi ha creato il token toglie i
soldi dal pool, chi e' dentro resta con un prezzo che non vale niente.

**Noi raccogliamo solo gli scambi.** Quel momento non lo vediamo: nei nostri dati quel token
risulta semplicemente «ha smesso di scambiare».

**Misurato prima di costruire qualcosa** — si cerca l'impronta: l'attivita' finisce di colpo
mentre il prezzo e' vicino al MASSIMO, dopo essere salito.

| | pool esaminati | finiti vicino al massimo | finiti in discesa |
|---|---|---|---|
| base | 1.353 | **9,2%** | 90,8% |
| robinhood | 2.578 | **9,7%** | 90,3% |

**CORREZIONE, un'ora dopo (22/09).** Ho applicato a questo risultato il criterio di
riproducibilita' preso da TradingAgings la mattina stessa — rifallo cambiando un'impostazione e
guarda se sopravvive. **Non sopravvive:**

| base | quota di «fughe» |
|---|---|
| come l'avevo misurato (picco grezzo, primo/ultimo grezzi) | 9,2% |
| picco robusto (95esimo percentile) | 8,1% |
| estremi robusti, picco grezzo | **2,3%** |

Da 2,3% a 9,2% cambiando soltanto COME si misura il picco: un fattore quattro. Su robinhood la
forchetta e' piu' stretta (7,4%-9,1%) ma c'e' anche li'.

**Quindi: il fenomeno esiste, il numero no.** Non posso dire «un pool su undici». Posso dire che
sta fra uno su undici e uno su quaranta, e che in ogni caso quei pool nel nostro conteggio
risultano VINCITORI — il prezzo e' salito e li' e' rimasto — mentre nessuno avrebbe potuto vendere
a quel prezzo.

**E la forchetta non si stringe raffinando la misura:** stiamo indovinando una fuga dall'impronta
invece di vederla. Si stringe solo raccogliendo gli eventi di liquidita'.

Il criterio ha bocciato un mio risultato un'ora dopo che l'avevo adottato. E' la prima volta che
succede, ed e' esattamente il suo mestiere.

**Prossimo passo:** aggiungere alla raccolta gli eventi di liquidita' (aggiunta e rimozione), per
distinguere una fuga da un token semplicemente dimenticato. Non e' una stima da raffinare: e' un
dato che non abbiamo.

### 6. Il «difetto nei prezzi» NON esisteva — era la mia misura

Fra gli esempi erano comparsi pool «saliti di 37 milioni di volte», e avevo concluso che
confondevamo token con decimali diversi.

**Verificato, ed era sbagliato io.** Nessun pool mescola versioni di protocollo (0 su 996), e in
quel pool 67 prezzi su 68 sono coerenti fra loro: il 37.000.000x veniva da UN SOLO scambio
anomalo, ed era il mio uso del massimo a farlo diventare un risultato.

**La lezione vale piu' del non-difetto:** avevo pubblicato una diagnosi («decimali non
normalizzati») dopo aver guardato tre esempi. Guardare gli esempi e' stato giusto — concluderne una
causa senza verificarla no. E' la stessa forma dell'errore che inseguiamo da due giorni, commessa
da me, sul lavoro di diagnosticare errori.

### 7. I fallimenti degli altri — e il pezzo di spazio di ricerca che eliminano

**Fonte:** post-mortem e analisi di chi ha perso soldi con questi bot. E' l'informazione piu' utile
e la meno pubblicizzata: nessuno mette in vetrina cio' che non ha funzionato.

**Tre fatti con i numeri:**

1. Un bot Python molto diffuso: **140 operazioni, risultato netto −22%** dopo costi e slippage. Il
   segnale non era sbagliato — l'esecuzione se l'e' mangiato.
2. Un ordine grosso su un token sottile: **5,7 milioni persi su 9** perche' il prezzo si e' mosso
   del 60% DURANTE l'esecuzione. Il backtest diceva «compra a X», il riempimento e' arrivato a
   X+60%.
3. La raccomandazione di chi c'e' passato: **modellare il DOPPIO dello slippage osservato**, piu'
   100-200 millisecondi di latenza e commissioni piene.

**Cosa prendiamo — il margine di sicurezza sul costo.** Non useremo l'impatto osservato ma il
doppio, come margine. Misurare bene non basta: il nostro impatto e' calcolato su scambi RIUSCITI e
per lo piu' piccoli, e il caso da 5,7 milioni mostra cosa succede fuori da quell'intervallo.

**Cosa elimina — e questa e' la parte che vale di piu'.** Loro consigliano di modellare 100-200
MILLISECONDI di latenza. La nostra, misurata: **1-3 secondi mediani, fino a 15 minuti nel caso
peggiore**. Siamo da dieci a mille volte piu' lenti di quanto serva a una strategia di entrata
rapida.

**Quindi le strategie di tipo «sniper» per noi non esistono, e il loop 1 non deve cercarle.**
Non e' una brutta notizia: e' un pezzo di spazio di ricerca eliminato con una misura, prima di
spenderci settimane. Cio' che cerchiamo deve sopravvivere a una latenza di secondi — il che punta
verso orizzonti piu' lunghi del singolo blocco, non piu' corti.

### 8. Le uscite — e la misura che dice dove NON sta il lavoro

**Fonte:** le strategie di uscita usate nel settore: scaletta di obiettivi (vendi un pezzo a 2x, a
3x, a 5x), trailing stop (esci se ritraccia del 30% dal massimo), uscita a tempo («se in 24 ore non
si e' mosso, esci: le memecoin corrono o muoiono»).

**Invece di adottarne una, ho misurato come si comporta il rendimento sui NOSTRI dati** entrando a
un punto qualunque. Le medie sono inservibili (gli scambi anomali gia' noti), quindi si legge la
mediana.

| | dove sei alla scadenza | massimo toccato nella finestra |
|---|---|---|
| base, 15 min | −0,8% | **+2,0%** |
| base, 24 ore | −1,0% | +4,0% |
| robinhood, 15 min | −5,4% | **+1,2%** |
| robinhood, 24 ore | −10,8% | +5,4% |

**Tre conclusioni, e la terza cambia le priorita' del loop 1.**

1. **Entrando a caso si perde**, su entrambe le chain. Su robinhood si perde progressivamente di
   piu' tenendo piu' a lungo: non e' un mercato che premia la pazienza.

2. **Il massimo toccato e' minuscolo.** Il token tipico, nel suo momento migliore, e' su del 2%.
   Il nostro costo di andata e ritorno, misurato e raddoppiato per prudenza, e' circa **1,8%**.
   Quindi anche uscendo nell'istante perfetto, sul token tipico si guadagna mezzo punto. Su
   robinhood nemmeno quello: 1,2% di massimo mediano e' SOTTO il costo.

3. **Il lavoro non sta nell'uscita, sta nella scelta.** Ottimizzare quando vendere un token che al
   massimo sale del 2% non porta da nessuna parte. Tutto il margine sta nel non entrare sul token
   tipico.

**Conseguenza per il loop 1:** l'uscita si tiene semplice (una scaletta e un trailing, presi dal
settore e non ottimizzati) e lo sforzo va tutto sul filtro d'ingresso — la successione di pattern.
Ottimizzare l'uscita sarebbe anche il modo piu' facile di illudersi: e' il parametro con piu' gradi
di liberta' e meno effetto.

### 9. I token si muovono insieme — e cambia il metro

Domanda che nessun repository poneva, venuta guardando quanto si somigliano i nostri dati: **i
token corrono ognuno per conto suo, o tutti insieme?**

Misurata la quota di token in rialzo, ora per ora: oscilla fra il 22% e il 67%. Se fossero
indipendenti resterebbe stabile. **C'e' un fattore comune che muove tutto.**

**Conseguenza:** «e' salito» non basta. Se in quell'ora saliva il 67% dei token, il nostro e' salito
per compagnia. Il criterio diventa il rendimento in ECCESSO rispetto ai token contemporanei.

E' la prima cosa trovata stasera che non viene da un repository ma da una domanda sui nostri dati —
posta pero' grazie all'abitudine presa leggendo gli altri: chiedersi sempre «rispetto a cosa?».

### 10. La prima misura incoraggiante (23/09, notte)

Il cercatore — il pezzo che cerca la successione di pattern — ha girato per la prima volta e ha
prodotto **41 candidati su 109 combinazioni**. Numero troppo alto per essere creduto: se cerchi
abbastanza, trovi sempre.

Quindi la stessa ricerca, con gli stessi criteri, e' stata fatta girare su dodici mercati
costruiti **senza alcun vantaggio dentro**:

| | candidati |
|---|---|
| dati senza vantaggio (12 mondi) | **2,0 in media** su ~111 combinazioni |
| dati veri | **41** su 109 |

**Venti volte tanto.**

**Cosa dice:** che nei dati veri c'e' qualcosa di piu' del caso.
**Cosa NON dice:** che uno di quei 41 sia vero, ne' quale.

**Il punto debole, dichiarato prima che lo dica il revisore esterno:** il mondo finto l'ho
costruito io, e potrebbe essere troppo facile. Se i dati veri hanno legami interni che il mio mondo
non riproduce, il rumore vero produrrebbe piu' di 2 candidati e il divario si ridurrebbe.

**Un dato che impone prudenza:** il 67% dei mondi VUOTI produce almeno un candidato. Quindi UN
candidato non significa niente — conta solo l'eccesso sul rumore.

**Prossimo passo:** rendere il mondo finto piu' difficile copiando la struttura dai dati veri
invece di inventarla. Se il divario sopravvive, comincia a valere qualcosa.

---

## PROVATO E NON REGGE — con il numero che lo dice

### Il lancio coordinato (indirizzi diversi nel primo blocco)
**Fonte:** le tecniche di «bundle detection» — riconoscere i lanci in cui molti portafogli comprano
nello stesso blocco, perche' sono una persona sola con molti portafogli. Idea ottima, e per giunta
**conoscibile al momento della decisione**, quindi ammissibile nel loop 1.

**Misurato, e non regge. Per due motivi, e il secondo e' piu' importante del primo.**

Primo: i pochi casi disponibili si contraddicono fra le chain.

| | pool con >=3 indirizzi nel primo blocco | vita mediana | vita mediana degli altri |
|---|---|---|---|
| base | 20 | 25,5h | 6,5h (vivono di PIU') |
| robinhood | 7 | 0,1h | 2,3h (vivono di MENO) |

Venti e sette pool, direzioni opposte. Guardando solo base avrei avuto una scoperta in mano;
guardando entrambe, ho rumore. **E' esattamente il meccanismo contro cui serve il motore a vuoto.**

Secondo, e piu' serio: **il 94% dei pool mostra UN SOLO indirizzo nel primo blocco che vediamo.**
Su un mercato dove i lanci coordinati esistono davvero, quel numero non dice «quasi nessun lancio
e' coordinato»: dice che **probabilmente non stiamo vedendo il vero blocco di apertura**, ma solo
il primo in cui la nostra raccolta e' arrivata.

**Il limite che ne esce, e vale per tutto il resto:** prima di usare qualunque condizione che
dipenda dall'INIZIO della vita di un pool — eta', primi compratori, lancio coordinato — dobbiamo
sapere se il nostro primo blocco e' davvero il primo. Finche' non lo sappiamo, quelle condizioni
misurano la nostra raccolta, non il mercato.

### Il seguito: la domanda aveva una risposta, ed e' dura

Il limite sospettato sopra l'ho verificato usando `nascita_vera.json`, dove per una parte dei pool
la nascita e' gia' stata chiesta alla catena.

| | il nostro primo blocco E' la nascita | arriviamo DOPO | ritardo mediano |
|---|---|---|---|
| base | 26,2% | **73,8%** | 3.805 blocchi (~2 ore) |
| robinhood | 8,6% | **91,4%** | 46.696 blocchi |

**Per la grande maggioranza dei pool i nostri dati cominciano ore dopo la nascita del token.**
La prima vita — primi compratori, lancio, prima corsa — non ce l'abbiamo proprio.

**Questo spiega una lamentela vecchia di mesi in questo progetto:** «il filtro becca token di
qualita' ma TARDI». Non era il filtro a essere lento: **sono i dati ad arrivare tardi.**

**Conseguenza operativa per il loop 1:** ogni condizione basata sull'inizio della vita di un pool
si puo' usare solo sul 26% di base e sull'8,6% di robinhood dove l'inizio ce l'abbiamo davvero.
Sul resto misurerebbe QUANDO SIAMO ARRIVATI NOI, non cosa e' successo al token — e le due cose si
assomigliano abbastanza da poter essere scambiate per un anno.

**E indica dove spingere la raccolta:** non piu' storico all'indietro, ma cattura delle nascite.

### Seguire i portafogli vincenti — misurato, e non c'e'

**Fonte:** la categoria piu' diffusa fra i 295 strumenti censiti in una lista curata del settore —
gli «smart money tracker»: si etichettano i portafogli che hanno guadagnato e si copiano.
E' anche un filone che questo progetto insegue da mesi.

**La domanda che decide:** chi ha comprato bene in passato compra bene anche dopo? Senza
persistenza, «smart money» e' solo fortuna passata con un nome elegante.

**Misurato** dividendo i dati in due periodi: il primo per farsi il curriculum, il secondo per
verificarlo.

| | chi andava BENE nel periodo 1 | chi andava MALE nel periodo 1 |
|---|---|---|
| base (558 portafogli) | **+0,01%** | −0,02% |
| robinhood (401 portafogli) | **+0,14%** | −0,43% |

**Su base non c'e' alcuna differenza.** Su robinhood c'e' una separazione di 0,57 punti — ma
l'impatto sul prezzo di UN SOLO scambio, misurato da noi, e' dello 0,45% mediano: **il costo di
entrare si mangia il presunto vantaggio.**

E le due chain non concordano sulla grandezza, il che e' gia' un avvertimento a se'.

**Conclusione: filone chiuso, o quantomeno fortemente scoraggiato.** Non per opinione: per un
numero, confrontato con quanto costa eseguire. E' la seconda volta oggi che una misura chiude una
strada invece di aprirla — e un filone chiuso con un numero vale quanto uno aperto, perche' libera
settimane.

---

## SCARTATO — e perche'

### La discussione fra agenti AI (TradingAgents)
Su un mercato senza bilanci e senza notizie produrrebbe prosa convincente sopra il rumore. E' il
pericolo gia' scritto nel nostro metodo: una spiegazione plausibile convince piu' di una
percentuale alta, e per questo e' piu' pericolosa. Prendiamo la separazione dei ruoli, non la
conversazione.

### Le librerie per l'impatto sui prezzi
Partono dalle riserve dei pool, che non abbiamo. Formula esatta + dati inventati = piu' credibile e
altrettanto falso.

### Lo slippage fisso dei bot letti (±3%)
Anche piu' grezzo del nostro vecchio 15%. Su questo siamo gia' avanti: misuriamo per pool.

### Tutto quello che e' specifico di Solana
Fuori perimetro dal 21/09 (vedi `DECISIONS.md`). Le tecniche si prendono, il codice no.

---

## Nota sulla riproducibilita' (da TradingAgents, e vale per tutti)

Il loro disclaimer e' la riga piu' preziosa che abbiamo letto:

> *«I risultati non sono garantiti... dipendono dal modello, dalla temperatura, dall'intervallo di
> date, dalla qualita' dei dati e dal campionamento.»*

Detto da loro onestamente, per noi e' un criterio: **un risultato che cambia al cambiare di
un'impostazione non e' un vantaggio, e' un campione di un processo casuale.** Prima di promuovere
qualunque cosa, si rifa' con seme diverso, finestra spostata e soglie mosse di poco.
