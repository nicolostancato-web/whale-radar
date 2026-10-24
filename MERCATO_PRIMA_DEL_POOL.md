# Il mercato prima del pool — 6 ottobre 2026

## In una frase

Gli acquisti che ci mancavano non erano un nostro difetto: avvengono su **un altro mercato**, che
esiste **prima** del pool e che non stavamo leggendo. L'ho verificato sulla chain, e ora lo
leggiamo.

## Da dove viene la domanda

Il 5 ottobre, dopo aver corretto sei difetti nei nostri dati, restava un fatto senza spiegazione:

| cosa misuravamo | base | robinhood |
|---|---|---|
| posizioni comprate e mai vendute | 48% | 45% |
| «chiuse» con la vendita PRIMA dell'acquisto | 18,5% | 28,8% |
| gettoni venduti / gettoni comprati (mediana) | 1,61 | 2,11 |
| multiplo mediano sulle sole posizioni verificabili | 1,05X (785 casi) | 0,99X (535 casi) |

Tradotto: **la maggior parte di chi vende questi gettoni non li ha comprati dove guardavamo.**

## Cosa ha detto Grok (costo zero, dall'abbonamento)

Il 6 ottobre ho girato la domanda al secondo revisore — non «rivedi il codice», ma «come se li
procurano, i gettoni?». Risposta con la documentazione in mano:

> Su robinhood il **92,9%** delle commissioni dei lanci passa da **Pons** (116 milioni di dollari
> in 30 giorni, oltre 416.000 lanci). Pons vende i gettoni su una **curva**, e il pool Uniswap
> nasce solo **dopo**. Chi compra sulla curva ha un acquisto vero che un indice di soli scambi
> Uniswap non vede.

Fonte: <https://docs.ponsfamily.com/v2>. Ha anche chiuso tre piste che avevo in testa: nessun
mercato fuori catena per queste monete, la prevendita di Clanker non è aperta a chiunque, e il
launchpad più grande di base mette tutta la fornitura nel pool. Su base il meccanismo è un altro
(l'allocazione del creatore che si sblocca dopo 30 giorni) e **va misurato a parte**.

## Cosa ho verificato io, sulla chain

Non l'ho creduto sulla parola. Tutto quanto segue è misurato il 6 ottobre:

1. **La fabbrica esiste e lavora adesso.** Chain id 4663, l'indirizzo `0x7eD5…EC7e` ha 48.356
   caratteri di codice, e ha lanciato 10 monete negli ultimi 6.000 blocchi.
2. **Gli eventi hanno il nome giusto.** Non li ho riconosciuti a occhio sulla forma dei dati —
   quell'occhio è esattamente ciò che ci ha fatto invertire acquisti e vendite sul 67-78% dei
   pool. Ho scritto il keccak (`agents/firma_evento.py`) e confrontato le firme:
   `CurveBuy(address,address,uint256,uint256,uint256,uint256)` **combacia esattamente** con
   l'evento sulla curva, e `TokenLaunched(address,address,address,address,uint256,uint256)` con
   quello della fabbrica.
3. **Si leggono, con cifre e indirizzi veri.** In 300.000 blocchi (~8 ore di chain): **32.517
   eventi**, 18.416 acquisti e 14.101 vendite, 11.635 coppie (chi riceve × curva).
4. **E sono i nostri.** Degli 8 nostri candidati robinhood trovati in quella finestra, uno paga
   0,1450 di valuta in 11 acquisti sulla curva. In **sole 8 ore** di chain, su tre mesi di dati:
   è l'1,5% dei nostri 525 candidati trovato nello 0,4% della finestra temporale.

## Due cose che ho imparato facendolo

**Chi compra non è chi detiene — la terza volta.** Nell'evento `CurveBuy` ci sono due indirizzi:
chi firma e chi riceve. Nei dati veri sono **diversi nel 25,8% dei casi**. Un indirizzo compra in
4 lanci su 9 per quattro destinatari diversi, e in un caso il destinatario è il creatore della
moneta: è il router che crea e compra nella stessa transazione. Se avessimo attribuito al
compratore, avremmo dato tutto al router. Attribuiamo a **chi riceve**.

**Misurare i limiti invece di assumerli ha risparmiato un giorno e il 97% delle chiamate.** Stavo
per costruire un lettore a finestre di 2.000 blocchi: 34.096 chiamate. Ho misurato cosa accetta
l'RPC, e i limiti sono due: **10.000.000** di blocchi con un filtro sull'indirizzo (l'elenco dei
lanci sta in **7 chiamate**), **30.000** senza filtro (gli scambi costano ~4.546 chiamate, contro
le ~600.000 che costerebbero andando curva per curva).

## Un difetto trovato e corretto nello stesso giro

La prima versione diceva «**coperto 100%**» mentre leggeva il **5%**. Due errori che si
nascondevano a vicenda: la finestra era larga un blocco oltre il limite (30.001 invece di 30.000),
così 18 chiamate su 20 fallivano; e la copertura contava i blocchi **attraversati**, non quelli
**letti**. Corretti entrambi: gli eventi sono passati da 1.664 a 32.517, e ora un blocco conta
come letto solo se sono arrivati **entrambi** i tipi di evento — con uno solo avrei gli acquisti
senza le vendite, cioè metà della contabilità, che è il difetto che questo lavoro nasce per
riparare.

Una copertura che mente è peggio di una mancante: fa leggere «non ha comprato» dove c'è scritto
«non ho guardato».

## Un allarme mio, rientrato

Nello stesso giro ho creduto di aver trovato un settimo difetto: il 76% dei «portafogli» sembrava
avere identificativi da 64 cifre, cioè hash e non indirizzi. **Era una mia assunzione, non un
difetto.** Quei 64 cifre stanno al livello dei *pool*, non dei portafogli, e su Uniswap v4 un pool
non ha un indirizzo: ha un identificativo da 32 byte. I portafogli sono puliti al 100%.

È la stessa famiglia di «dedurre i limiti della realtà dai propri»: avevo dato per scontato che un
pool sia un indirizzo. Stavolta l'ho vista **prima** di scriverla in un riassunto.

## Cosa cambia, e cosa no

**Cambia la contabilità, non la strategia.** Questi acquisti sono un **costo** che non stavamo
contando, non un vantaggio da copiare: chi compra sulla curva **paga**. Il multiplo mediano sulle
posizioni che sapevamo già leggere è 1,05X e 0,99X, e questi acquisti possono solo abbassarlo, mai
alzarlo.

Quello che cambia è che d'ora in poi i numeri sono **completi**, quindi veri. E resta aperta la
domanda che vale: se qualcuno guadagna davvero, lo si vedrà solo ora che vediamo anche quanto ha
pagato.

**Non è ancora il momento di dire «i dati sono veritieri».** Lo dirò quando la corsia avrà
coperto tutta la finestra e un controllo a campione passerà con una moneta e un portafoglio che
Nicolò può aprire e verificare da solo.

## Il meccanismo, in pratica

- `agents/firma_evento.py` — keccak256 in puro Python, per dare un **nome** agli eventi. Si
  verifica da solo su due valori noti, uno dei quali era già stato letto dalla chain.
- `agents/curva_pons.py` — due fasi: l'elenco dei lanci (7 chiamate) e gli acquisti (a 10 fette).
- `.github/workflows/curva_lanci.yml` e `curva.yml` — ogni 12 e ogni 6 ore. Separate in due file
  perché la guardia sul budget somma i budget di un file intero: **si separa il file, non si
  abbassa la guardia.**
- Guardia `curva:1080` e `curva_lanci:2160` aggiunte: 46 corsie con l'orologio, 46 con la guardia.

**Costo: zero.** RPC pubblico della chain, nessuna chiave, nessun conto a consumo.

---

## Primo giro della corsia, e due difetti nella ripartenza (6 ottobre, 08:15)

La corsia ha girato: **7.422.208 eventi** sulla curva — la stima era 7,4 milioni, quindi il
dimensionamento era giusto. Ma la copertura è **irregolare**: 72,7% in media, con una fetta al
**0,4%**.

| fetta | eventi | letto |
|---|---|---|
| 1 | 2 | 100% |
| 2 | 21.839 | 100% |
| 3 | 162.436 | 100% |
| 4 | 575.008 | 99,1% |
| 5 | 728.850 | 97,8% |
| 6 | 772.326 | **30,9%** |
| 7 | 64.753 | **0,4%** |
| 8 | 1.206.794 | **33,9%** |
| 9 | 1.991.393 | 76,1% |
| 10 | 1.898.807 | 89,1% |

La causa è nei log: dieci fette in parallelo prendono `429 Too Many Requests`. Due riparazioni:

**L'attesa era troppo corta.** Quattro tentativi a 1,5-6 secondi, poi la finestra veniva
**abbandonata**. Ma un limite di frequenza è temporaneo, mentre saltare una finestra è definitivo —
e un'assenza nei dati si legge «non ha comprato», non «non ho guardato». Ora sette tentativi, fino
a ~30 secondi sul 429 e sulla connessione chiusa.

**La ripartenza dichiarava di riprendere e non riprendeva.** Le finestre partivano dal blocco
*attuale* meno 69 milioni, e il blocco attuale avanza di ~10 al secondo: al giro dopo ogni inizio
di finestra era spostato, nessuno combaciava con quelli segnati, e si rileggeva tutto. Stampava
«riprendo: 12 finestre già lette» e ne rifaceva 14. Ora la griglia è **ancorata** a posizioni
fisse, le stesse a ogni giro.

Provata facendola tre volte di seguito: **40% → 100% → zero chiamate** perché non restava niente.
Una ripartenza si prova facendola due volte, non leggendola.

Con questo i giri **convergono**: ogni passaggio ogni 6 ore ripara solo i buchi rimasti, invece di
ricominciare e perdere le stesse finestre.

---

## Il guasto silenzioso, e una mia diagnosi sbagliata (6 ottobre, 08:50)

Il secondo giro ha coperto quanto il primo, e per due motivi distinti.

**La ripartenza non si è innescata**, giustamente: il contatore del primo giro non era mai
arrivato sul ramo, perché il `pubblicatore` — lo **scrittore unico** verso il ramo — era fermo da
sei ore. Non per un guasto suo: su questo repo **l'ultimo giro partito da un orologio GitHub è del
23 settembre**, e da tredici giorni tutto gira sui rilanci della maglia di guardie, che vive sul
Mac ed è eseguita dal loop. Il loop quel giro non l'aveva eseguita. Ora è una regola scritta: la
maglia si esegue **all'inizio** di ogni giro, prima del lavoro di contenuto.

**E la mia diagnosi dei fallimenti era sbagliata.** Avevo letto `429 Too Many Requests` nei log
del primo giro e concluso «è la frequenza, dieci fette in parallelo». Ho allungato le attese. Ma
guardando la fetta 7 — 416 finestre perse — ho trovato una cosa peggiore: **zero messaggi di
errore**. Il codice faceva `.get("result")` sulla risposta, e un **errore JSON-RPC non è
un'eccezione**: tornava `None`, e la finestra veniva saltata senza una riga di log.

Il motivo vero, una volta reso visibile:

```
logs matched by query exceeds limit of 10000
```

Non è la frequenza: è un **tetto sui risultati**. Le fette centrali perdevano tutto perché i loro
dati sono più densi (~9.500 eventi per finestra contro ~4.500), non perché chiamassero troppo.
Aspettare più a lungo non serviva a niente — al tentativo dopo la finestra è densa come prima.

**Riparazione:** gli errori dell'RPC ora si leggono e si stampano col loro motivo, e una finestra
troppo densa **si dimezza** invece di essere persa, fino a sei volte (da 30.000 blocchi a ~470).
Provato sulla regione che falliva quasi del tutto:

| blocchi | prima | adesso |
|---|---|---|
| 53.790.000 | niente | 24.351 eventi |
| 56.000.000 | niente | 42.882 eventi |
| 59.000.000 | niente | 12.572 eventi |

**La lezione, scritta nel punto che la può ripetere:** un guasto silenzioso è peggio di un guasto
rumoroso. Il contatore diceva «416 fallite» ed era vero — ma senza il motivo ho inseguito la causa
sbagliata per due giri. Un numero che dice *quanto* senza dire *perché* fa lavorare nella
direzione sbagliata con la coscienza a posto.

---

## I nostri candidati sono lì, e un errore di unità preso per i capelli (6 ottobre, 11:00)

**La ripartenza funziona** (sei fette si sono riprese il contatore dal proprio allegato, senza
aspettare lo scrittore unico), e la copertura è salita: **otto fette su dieci al 100%**, una al
93%, una al 45,7%. Uno o due giri e la finestra storica è completa.

**Il numero che conta: 132 dei nostri 499 candidati — il 26,5% — hanno almeno un acquisto sulla
curva.** Mediana di 14 curve toccate a testa. Quindi un quarto dei portafogli che avevamo
giudicato «bravi» stava comprando in un posto di cui non contavamo niente. **Questo da solo
invalida i multipli calcolati fino a ieri**: erano guadagni senza il costo.

### E qui mi sono fermato prima di scrivere una cifra in euro

Il primo conto diceva «spesa mediana 2,0 e totale 517.684». **Quel totale non significa niente**,
e l'ho scoperto chiedendo alla chain in che valuta si paga. Non è sempre la stessa:

| asset | decimali | lanci (su 1.987) |
|---|---|---|
| NATIVO | 18 | 1.731 |
| USDG | **6** | 83 |
| ORBIO | 18 | 67 |
| NVDA, SPY, GLD… | 18 | 54 |

Sono **28 asset distinti**, e ce ne sono anche di azioni tokenizzate — è la chain di Robinhood.
Due conseguenze: dividere per 10¹⁸ un importo in USDG lo sottostima di **mille miliardi di
volte**, e sommare importi in asset diversi dà un numero senza unità.

È la stessa famiglia dell'errore che il 3 ottobre produsse un valore di 16 milioni di dollari
inesistente. Stavolta però il numero non è uscito dal recinto: l'ho fermato prima.

**Riparazione:** l'elenco dei lanci ora registra l'asset di quotazione di ogni curva con il suo
simbolo e i suoi decimali (28 asset, tutti leggibili, zero ignoti), ogni scambio porta la **sua**
unità, e dove l'asset non si riconosce l'importo resta **grezzo e dichiarato**. Un numero grezzo e
dichiarato si può usare; uno convertito col divisore sbagliato è una bugia con la virgola al posto
giusto.

I contatori accumulati sono stati **buttati**: portavano importi col divisore sbagliato, e un
totale senza unità non è un dato parziale, è un dato falso. Rileggere costa un giro; tenerlo
costava una conclusione.

### Due difetti miei, trovati contandoli

- una mia sostituzione di stamattina, pensata per il file degli scambi, aveva colpito **anche** il
  salvataggio dei lanci, che così accodava un secondo documento JSON che nessuno leggeva: i dati
  nuovi scomparivano in silenzio. Avevo verificato che la modifica ci **fosse**, non **quante
  volte**.
- una seconda modifica non si era agganciata affatto, e me ne sono accorto solo contando le
  occorrenze. Terza volta in due giorni: contare dopo ogni modifica non è pignoleria, è l'unico
  modo di sapere se ho cambiato ciò che credevo.

---

## Una riscrittura non eredita le lezioni (6 ottobre, 11:40)

Il giro dell'elenco lanci sulla finestra intera ha scritto **zero lanci** — e ha scritto un file
**vuoto** sopra uno con 1.987 lanci e 28 valute. Tre difetti sovrapposti, tutti miei:

**1. Avevo dedotto un limite da una prova che non era passata.** Stamattina ho misurato che l'RPC
accetta 10 milioni di blocchi col filtro sull'indirizzo. Ma quella prova era **fallita** per un
fuori-di-uno, e io ne avevo tratto una conclusione comunque. Il limite vero è doppio: ≤10 milioni
di blocchi **e** ≤10.000 risultati. In 10 milioni di blocchi ci sono ~47.000 lanci, quindi tutte e
sette le finestre venivano rifiutate.

**2. Lo stesso fuori-di-uno, in due posti, corretto in uno.** `b + 10.000.000` sono 10.000.001
blocchi inclusi. L'avevo corretto per le finestre degli scambi alle 08:50 e **non** per quelle dei
lanci. Una lezione applicata a un posto solo vale una volta.

**3. La guardia che avevo scritto e poi perso.** Il 5 ottobre avevo messo: *«zero lanci: non
scrivo un file che direbbe che nessun acquisto esiste»*. Poi ho riscritto l'agente in due fasi e
la guardia è rimasta nel pezzo buttato. **Una riscrittura non eredita le lezioni da sola** — e
questa è la cosa che vale più dei tre difetti insieme, perché vale per ogni riscrittura futura.

Riparato tutto e verificato su 20 milioni di blocchi: **247.360 lanci, zero finestre perse, 72
asset di quotazione, tutti con i decimali leggibili.** Il file buono sul ramo non era stato
toccato: il vuoto era rimasto in un allegato.

### E un difetto nella ricerca di Grok, della stessa famiglia

La domanda 3 è tornata con **296 caratteri** — solo la riga di apertura, il corpo mancante — e il
mio agente l'ha segnata come **fatta**. Così il programma avanzava e il fascicolo restava vuoto:
peggio di un errore, perché il registro diceva che era a posto. Ora sotto i 2.000 caratteri si
butta e si ritenta; rifatta, è tornata con 7.465 caratteri.

Nello stesso giro ho tolto il salvataggio delle ricerche da git: un conflitto irrisolto bloccava
ogni commit, e una rete di sicurezza che dipende dallo stato dell'indice di git **è il ramo che si
sta segando**. Ora passa dall'interfaccia di GitHub.

---

## L'indice completo dei lanci, e una correzione a me stesso (6 ottobre, 13:10)

**675.145 lanci**, tutte e sette le finestre della storia lette, zero perse, **72 asset di
quotazione tutti con i decimali leggibili.** L'indice completo c'è.

L'ultimo difetto era che su un errore di *dimensione* il codice riprovava sette volte con attese
fino a 30 secondi. Ma al settimo tentativo la finestra è densa come al primo: aspettare ha senso
su una connessione chiusa, non su «troppi risultati». Con 96 rifiuti in un giro il budget finiva
prima della fine, e la finestra più densa — da sola **283.264 lanci** — restava fuori. Ora
fallisce subito e il dimezzamento parte.

### Una correzione a quello che ho scritto stamattina

Alle 11:00 avevo scritto che il `pubblicatore` intasato «non è colpa mia: i miei allegati sono il
14%». Ho misurato i tempi, e la frase era vera e fuorviante insieme:

| giro | durata | esito |
|---|---|---|
| 07:02 | 46 min | riuscito |
| 08:13 | 51 min | riuscito |
| 09:36 | **56 min** | **fallito** (tetto 60) |

Non è bloccato: è **cronicamente al limite**. E i miei 290 MB a giro sono esattamente il margine
fra 51 e 56 minuti. Non ero la causa — quasi 1 GB è di un'altra corsia — **ma ero la goccia**, e
dire «è il 14%» serviva a togliermi la responsabilità invece che a risolvere.

**Riparato togliendo il mio peso:** questa corsia non ha più bisogno del ramo (si riprende
contatore ed elenco dai propri allegati), quindi le somme non passano più dallo scrittore unico.
Vanno in un allegato che **non si chiama `consegna-`**, così il pubblicatore non lo raccoglie, con
una conservazione di 30 giorni perché non c'è il ramo a fare da archivio. Sul ramo restano i file
piccoli: contatore, copertura e le righe grezze dei candidati, cioè le prove che vanno verificate
a mano.

Il peso che impongo agli altri è una misura, non un'opinione — e si guarda **dopo** ogni
propagazione, non prima.
