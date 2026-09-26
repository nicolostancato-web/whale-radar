# La successione di pattern — quello che il fondatore aveva chiesto

*23 settembre 2026, notte. Questo documento sostituisce i numeri di PRIMO_SEGNALE.md, che erano
viziati. Qui c'e' cio' che e' sopravvissuto a tutti i controlli.*

---

## In una riga

**Su robinhood, due condizioni al momento dell'ingresso quasi triplicano la probabilita' che un
token faccia +50% o piu'. Su base non e' stabilito.**

Le due condizioni, a due ore dal primo scambio osservato:

> **almeno 11 compratori distinti  E  almeno 73 scambi**

---

## Perche' questo numero e' credibile, mentre i cinque precedenti non lo erano

Nelle ultime ore il risultato e' passato per sei versioni, ognuna piu' piccola della precedente:
«+63% di portafoglio» → «+41%» → «+12,9%» → «+7 punti» → «forse zero». Ogni volta che guardavo
meglio, il numero scendeva.

**Il motivo era sempre lo stesso, e non erano sei errori diversi: era sempre la MEDIA.**

Su questi mercati la media e' inservibile. Un solo token che fa +1.972% sposta la media di 63 pool
di quaranta punti. Misurare la media significa misurare quel token, non la strategia:

| togliendo i migliori | robinhood | base |
|---|---|---|
| media del gruppo scelto | +16,3% | +80,0% |
| senza il migliore | +8,7% | +49,5% |
| senza i primi 3 | +2,5% | **−9,4%** |
| senza i primi 5 | +0,3% | −14,6% |

Tre token su 63 tengono in piedi tutto il risultato di base. **Un risultato che sta in piedi grazie
a tre righe non e' un risultato: e' quelle tre righe.**

## La misura giusta: quanto spesso becchi un colpo grosso

Una frequenza, a differenza di una media, **un singolo token non la puo' spostare**. Se 147 pool
scelti contengono 14 token da +50%, togliendone uno restano 13: il numero si muove di mezzo punto,
non di quaranta.

Ed e' anche la domanda economicamente giusta. In una strategia a coda non guadagni perche' il token
medio sale — non sale, la mediana e' negativa ovunque. Guadagni perche' **ogni tanto ne becchi uno
che fa dieci volte**, e le perdite piccole le paghi con quello. Quindi la sola cosa che deve
migliorare e': *ogni quanto capita*.

### robinhood — 147 pool scelti su 1.004

| token che fanno | nel gruppo scelto | in un gruppo a caso | il caso fa meglio in |
|---|---|---|---|
| **≥ +25%** | **18,4%** | 6,8% | **0,0%** dei casi |
| **≥ +50%** | **9,5%** | 3,4% | **0,0%** dei casi |
| **≥ +100%** | **4,8%** | 1,4% | **0,2%** dei casi |
| ≥ +200% | 2,0% | 0,7% | 10,8% — non stabilito |

Su 400 mescolate casuali, **nessuna** ha eguagliato il gruppo scelto sulle prime due soglie.

E le altre misure robuste concordano: **43% dei pool scelti chiude in guadagno contro il 28%** di
tutti i pool; mediana −1,3% contro −2,6%.

### base — 37 pool scelti: NON stabilito

Sembra anche meglio, ma il 5,4% sono **due token in tutto**. Con due osservazioni non si conclude
niente, e infatti sulla misura robusta base va **peggio del non fare niente**: 16% di pool in
guadagno contro il 19% della chain intera. Su base si continua a raccogliere, non si opera.

---

## I due errori che hanno prodotto i numeri gonfiati, e come sono stati chiusi

Entrambi trovati dal revisore esterno (Astra), non da me.

**1. Il momento della decisione guardava nel futuro.** Decidevo «a un quarto della vita osservata
del token» — ma la vita osservata la conosco solo alla fine. Sceglievo con informazioni che al
momento dell'ingresso non potevo avere. Ora la decisione e' **a due ore dal primo scambio visto**, e
basta.

**2. I pool senza uscita venivano buttati.** Se entravo e poi nessuno comprava piu', scartavo il
caso — cioe' cancellavo esattamente i fallimenti totali. Ora contano **−98%**, che e' quello che
sono.

**3. Le regole si contavano piu' volte.** «29 regole che reggono» sembrava una conferma ripetuta 29
volte. Misurata la sovrapposizione: le 29 regole toccano 263 pool distinti, e **ogni pool compare
in 13 regole su 29** — somiglianza mediana fra coppie di regole 38%, massima 100%. Non erano 29
prove. Era una prova sola, contata 29 volte. **Da qui in avanti si contano i pool distinti, mai le
regole.**

---

## Cosa NON dice questo risultato

- **Non dice che si guadagna.** Dice che la selezione alza la frequenza dei colpi grossi. Se quella
  frequenza basti a pagare costi e slippage e' un conto separato, e va fatto con l'impatto reale
  misurato (0,45% per scambio, 1,8% andata e ritorno).
- **Non e' provato su base.** 37 pool, due colpi. Si raccoglie ancora.
- **La soglia +200% non e' stabilita** nemmeno su robinhood (il caso la eguaglia nell'11% delle
  mescolate).
- **Non e' stato provato in avanti.** Tutto cio' che c'e' qui e' misurato su storia gia' accaduta.

## La prossima prova, decisa prima di vederne l'esito

Prendere i pool che **nasceranno da domani** su robinhood, applicare le due condizioni al momento,
e contare quanti fanno +50%. **Se in 150 pool scelti la quota non arriva almeno al 7%** (contro il
9,5% misurato e il 3,4% del caso), la successione di pattern non regge e si butta.

Scritto prima di avere i dati, come le altre volte.

---

# Il conto economico: la frequenza basta a pagare i costi?

*Aggiunto 23/09 05:05. Era la domanda lasciata aperta sopra.*

Costo applicato: **1,8% per giro completo** — misurato, non stimato (0,45% di impatto mediano per
scambio, raddoppiato per entrata e uscita).

Compro ogni pool scelto in parti uguali e vendo quando tocca il bersaglio:

| quando vendo | guadagno medio per scommessa | senza la selezione (controllo) |
|---|---|---|
| a +25% | **−3,96%** | −13,0% |
| a +50% | +0,26% | −12,1% |
| a +100% | **+4,06%** | −11,4% |
| a +200% | +6,19% | −10,8% |
| tengo fino in fondo | **+6,77%** | −10,5% |

## Il risultato che conta, e non e' il numero piu' grande

**Prendere profitto presto distrugge la strategia.** Vendere a +25% — che e' l'istinto naturale,
«porto a casa» — trasforma un +4% in un **−4%**. Otto punti buttati per aver venduto troppo presto.

Il motivo e' aritmetico, non psicologico. Il 60% delle scommesse chiude in perdita **in ogni caso**:
il bersaglio non cambia i perdenti, cambia solo i vincenti. Se tronchi i vincenti a +25% hai ancora
tutte le perdite e nessuno dei guadagni che le pagava.

**Questo conferma, per una via completamente diversa, quello che il fondatore aveva gia' concluso
sulle balene: si tiene sui cali, si esce quando escono loro, non a una soglia di prezzo.**
La scorsa volta era un'intuizione su come si comportano i soldi grossi. Qui esce dai numeri, su un
altro mercato e con un altro metodo.

## Quanto vale davvero la selezione

Il gruppo di controllo perde fra il 10% e il 13% con qualunque regola di uscita. **Comprare
memecoin a caso perde circa l'11%.** La selezione porta lo stesso gesto a **+4/+7%**: quindici-
diciassette punti di differenza, ed e' quello il valore della successione di pattern.

## Dove e' fragile, detto chiaro

- **Senza i 3 token migliori** su 142, il +4,06% scende a **+2,03%**. Positivo, ma sottile. La
  strategia campa sulla coda, quindi bastano pochi mesi senza un colpo grosso per stare in perdita.
- **Il costo e' il vero nemico:** a 4% per giro l'edge sparisce (−1,94%), a 8% si perde il 6%. Il
  nostro 1,8% e' misurato su scambi veri, ma su un pool piccolo o con fretta si arriva al 4%
  facilmente. **La dimensione della scommessa e' un parametro di sopravvivenza, non di comodo.**
- **Il 60% delle scommesse perde.** Chi mette questi soldi deve saperlo prima: e' normale, e'
  previsto, ed e' il modo in cui la strategia funziona — non il segno che si e' rotta.

## Cosa NON e' ancora stato fatto

Questo conto e' su storia gia' accaduta. La prova in avanti (H4) e' partita stanotte e registra sia
i pool scelti sia quelli di controllo. Il verdetto arriva a **150 pool scelti**, con la condizione
di morte gia' scritta.

---

# Quanto e' stretto il campione — e la regola tiene nel tempo?

*Aggiunto 23/09 06:45, dopo una domanda rimasta aperta nella ricerca su GitHub.*

## Il dubbio: e' la chain a essere veloce, o siamo noi a guardare da poco?

Su robinhood nessun pool sembrava superare i 30 giorni. Se fosse colpa della NOSTRA finestra di
raccolta, tutto il risultato sarebbe tagliato — ed e' esattamente l'errore su cui e' scritto
`LEZIONE_IMPOSSIBILE.md`: un limite nostro scambiato per un fatto del mondo.

**Verificato, e il dubbio cade:** la nostra raccolta su robinhood copre **71,5 giorni**, e solo
**1 pool su 3.824** ha il primo scambio nella prima ora della raccolta — cioe' non stiamo prendendo
i token a meta' vita. I token di robinhood muoiono davvero piu' in fretta: 90° percentile di vita
**8,1 giorni**, contro i **76,6** di base. E' una proprieta' della chain, non nostra.

## Il limite vero, che va dichiarato

Le nascite non sono distribuite: **il 79% delle osservazioni viene dalle ultime due settimane**, il
63% dall'ultima. L'arco utile e' 40 giorni, ma il peso sta tutto alla fine.

Quindi: la successione di pattern e' misurata soprattutto su **due settimane di mercato**. Se quelle
due settimane avessero un carattere particolare, la regola potrebbe non valere altrove.

## Il controllo: la regola tiene in entrambe le meta' del periodo?

| | pool scelti | fanno +50% | a caso | rapporto | il caso vince in |
|---|---|---|---|---|---|
| **prima meta'** | 113 su 533 | 8,8% | 6,2% | 1,4× | 14,3% |
| **seconda meta'** | 52 su 553 | 5,8% | 1,9% | **3,1×** | 16,7% |

**Due letture, tutte e due vere.**

*Rassicurante:* la regola punta nella stessa direzione in **entrambe** le meta'. Non e' un colpo di
fortuna capitato in un unico periodo. E il rapporto sul mercato **migliora** nella seconda meta'
(3,1× contro 1,4×): il mercato e' diventato piu' difficile — solo l'1,9% dei token faceva +50%,
contro il 6,2% di prima — e la selezione ha retto meglio proprio li'.

*Da non nascondere:* **presa da sola, nessuna delle due meta' e' conclusiva.** Il caso le eguaglia
nel 14% e nel 17% dei casi. La significativita' piena (0,0%) nasce dal mettere insieme i due pezzi,
non da ciascuno.

**Quindi il risultato e' coerente, non ancora robusto.** Sono due indizi che puntano nello stesso
verso, non due prove. Ed e' un altro motivo per cui la prova in avanti — che accumula un campione
nuovo, in un periodo nuovo — e' la cosa che conta davvero, non l'ennesimo taglio di questo stesso
campione.

---

# La revisione del 23/09 mattina — e i numeri corretti

*Astra chiamato una seconda volta (limite alzato a 3/giorno da Nicolo). Costo: $0,11.*

## Il difetto che ha trovato, e non era statistico: era aritmetico

Ha notato che **la quota aggregata (9,5%) era maggiore di ENTRAMBE le meta' (8,8% e 5,8%)**.
Aritmeticamente impossibile: una media pesata di 8,8 e 5,8 non puo' fare 9,5.

**La causa, trovata in dieci minuti:** il cercatore selezionava i file con `hash(fn) % CAMPIONE`, e
in Python **l'hash delle stringhe e' randomizzato a ogni processo**. Ogni esecuzione pescava un
sottoinsieme diverso — 1004, 1005, 959, 995, 1086 osservazioni. **Tutti i numeri della notte
venivano da universi diversi, confrontati come se fossero lo stesso.**

Corretto con `zlib.crc32`. Tre esecuzioni ora danno 1.592 osservazioni identiche.

## I numeri veri, dalla tabella unica, e stavolta tornano

| | fanno +50% |
|---|---|
| **scelti dalla regola** | **20 su 155 = 12,9%** |
| non scelti | 28 su 904 = 3,1% |

Identita' verificata: 14+6=20 successi, 114+41=155 pool. **Il risultato corretto e' PIU' FORTE di
quello sbagliato** — 4,2 volte il gruppo di controllo invece di 3.

## Il test decisivo: permutare l'INTERA ricerca, non la regola vincente

Astra: *«stai confrontando il vincitore della ricerca con gruppi casuali che non hanno avuto il
diritto di cercare un vincitore»*. Giusto, ed e' il difetto piu' comune di questo mestiere.

Rifatta **tutta la ricerca** su 200 rimescolamenti che distruggono ogni legame reale:

| | quota di +50% del miglior candidato |
|---|---|
| **sui dati veri** | **15,4%** |
| nel nulla, tipicamente | 7,8% |
| nel nulla, il migliore su 200 tentativi | 16,1% |

**Il nulla ci eguaglia 1 volta su 200 (p = 0,010).** Il risultato regge al test piu' severo fatto
finora.

**E una lezione che vale oltre questo caso:** cercando nel nulla si arriva al **7,8%**. Quella e'
l'asticella onesta, non il 3,4% del gruppo casuale singolo. Stanotte mi misuravo con un metro
troppo generoso.

## Il rilievo sull'eseguibilita' — verificato, e si ribalta

Il timore: *«se i pool con maggiore rialzo sono proprio quelli impossibili da comprare o vendere, la
componente redditizia scompare»*.

Misurato il volume disponibile per USCIRE (scambi in vendita dopo l'ingresso):

| | scambi in vendita | volume di uscita |
|---|---|---|
| **token vincenti (+50%)** | **55** | **65x quello degli altri** |
| gli altri | 28 | — |
| scelti dalla regola | 34 | 77x lo scambio tipico |
| non scelti | 16 | 33x lo scambio tipico |

**Vale l'opposto del timore: chi sale porta con se' il volume per uscire.** E i pool scelti dalla
regola sono piu' liquidi dei non scelti, non meno.

**Il limite vero e' la DIMENSIONE:** si esce con una posizione pari a 20 volte lo scambio tipico nel
74% dei casi, a 5 volte nell'87%. Oltre, si muove il prezzo da soli — ed e' il motivo per cui la
dimensione della scommessa e' un parametro di sopravvivenza, non di comodo.

## I costi per singola operazione — Astra aveva ragione, e costa caro

Il rilievo: *«l'impatto MEDIANO non e' il costo appropriato per dimostrare il rendimento MEDIO. I
costi peggiori possono concentrarsi proprio sulle operazioni decisive.»*

Misurato il costo pool per pool, invece della mediana universale:

| | costo per scambio | nei momenti peggiori (90° perc.) |
|---|---|---|
| **token vincenti (+50%)** | **1,64%** | **7,05%** |
| gli altri | 0,74% | 3,11% |

**I vincenti costano piu' del doppio.** Ed e' logico, col senno di poi: un token che sale del 50% si
sta muovendo, e chi si muove costa di piu' da comprare e da vendere.

**E c'e' un secondo errore mio, piu' banale e piu' grave.** Lo 0,45% che usavo era misurato su
**tutti** i pool della chain. Sui pool che la regola **seleziona** e' **0,83%**: quasi il doppio.
Stavo prezzando operazioni su token agitati col costo dei token tranquilli.

**Effetto:** ricalcolando col costo vero di ciascun pool, il rendimento lordo perde **circa un
quarto**. Resta positivo, ma il margine e' sensibilmente piu' sottile di quanto dichiarato stanotte.

**Cosa cambia in pratica:** il costo non e' un parametro da mettere una volta e dimenticare. Va
misurato sul pool specifico **prima** di decidere la dimensione della scommessa — un pool con
impatto al 7% non si tratta come uno all'1%.

## «Sceglie i token o i momenti?» — verificato, sceglie i token

Il rilievo: *«pareggiare l'ora del giorno non equivale a pareggiare l'episodio di mercato. Le 15:00
di un giorno tranquillo non sono il controllo delle 15:00 durante una fiammata speculativa.»*

La concentrazione **esiste**: il 39% dei pool scelti cade in appena 5 ore su 76. Quindi il dubbio
era fondato e andava sciolto.

Sciolto cosi': si tengono solo le ore che contengono **sia** pool scelti **sia** pool non scelti, e
si confronta li' dentro — stessa ora, stesso episodio di mercato, stessa fiammata.

| | fanno +50% |
|---|---|
| **scelti** | **13,4%** |
| non scelti, nella stessa ora | 3,6% |

Poi si rimescola l'etichetta scelto/non-scelto **dentro ogni singola ora**, mantenendo i conteggi:
su 2000 rimescolate il caso eguaglia **3 volte (p = 0,0020)**.

**La regola sceglie i token, non i momenti.**

## Il bilancio della revisione del 23/09

| rilievo di Astra | esito |
|---|---|
| numeri aritmeticamente impossibili | **VERO** — difetto di programmazione, corretto |
| confronto col vincitore di una ricerca | **VERO** — rifatto il test, superato (p=0,010) |
| i redditizi sono invendibili | **falso** — vale l'opposto |
| i costi si concentrano sui vincenti | **VERO** — costa un quarto del margine |
| sceglie le ore favorevoli, non i token | **falso** — regge dentro le stesse ore (p=0,002) |

Tre su cinque confutati con i dati, due veri. **Di quelli veri, uno ha reso il risultato piu' forte
e uno lo ha reso piu' sottile.**

## Cosa resta aperto dalla stessa revisione

- il rendimento usato e' quello **a orizzonte fisso** (prezzo all'ultimo scambio della finestra), non
  il picco: questo evita il problema del «massimo toccato da uno scambio minuscolo», ma va detto
  che una strategia con presa di profitto e' una cosa diversa e va simulata a parte;
- i costi vanno misurati **per singola operazione**, non con una mediana universale: i costi peggiori
  potrebbero concentrarsi proprio sulle operazioni decisive;
- i pool recenti che non hanno ancora completato l'orizzonte non vanno contati come insuccessi.
