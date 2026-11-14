# Imparare a vendere su Curve — un gradino per giro

**Perché.** La catena funziona da capo a fondo tranne l'ultimo passo: per 265
posizioni (sUSDe, osETH, rsETH, syrupUSDT) dopo aver incassato la garanzia
**non sappiamo liquidarla**, perché la loro liquidità sta su Curve e noi
sappiamo vendere solo su Uniswap. Non serve per il dump — quelle posizioni
sono coppie uguali e cadono piano — serve per **le grosse e lente**: la più
vicina ha $1.749.149 di premio a salute 1,0107.

**Come.** Lo stesso schema che ha funzionato la notte del 3/11: un gradino
piccolo per giro, ognuno **provato** prima di passare al successivo. Niente
«studiamo Curve»: gradini che si possono sbagliare uno alla volta.

| # | gradino | stato |
|---|---|---|
| 1 | trovare le vasche Curve per le nostre monete | **fatto**: sUSDe sì (2 vasche) |
| 2 | trovare le vasche che i registri non indicizzano | **fatto**, e col metodo girato: vedi sotto |
| 3 | leggere un preventivo dalla vasca (`get_dy`) e confrontarlo con l'oracolo | **fatto**: osETH→rETH regge fino a 2 milioni al 99,20% |
| 4 | costruire la calldata di scambio da soli (`exchange`) | **fatto**: selettore 0x3df02124 |
| 5 | verificare che l'importo compaia **una volta sola** nella calldata | **fatto**: una volta, offset 68 |
| 6 | capire chi preleva i gettoni (su Curve è la vasca stessa) | **fatto**: la vasca, quindi si passa zero |
| 7 | **provare su una copia del blocco corrente** con una posizione vera | **FATTO: PASSA** su 6 profondità di crollo |
| 8 | collegarlo come secondo ripiego dopo Uniswap | **fatto** |
| 9 | misurare la resa e tarare i tetti per coppia, come su Uniswap | **fatto** per GHO (tetto $5.000) |

## Regole che valgono su tutta la scaletta

- **«Non si può» va provato.** Il gradino 1 l'ha già mostrato: il registro
  dice che la vasca osETH non c'è, ma l'aggregatore la usava — quindi la
  vasca esiste e il registro è incompleto. Mai dedurre il limite della
  realtà dal limite del nostro strumento.
- **Il minimo in uscita si mette a zero**, come su Uniswap: a difendere il
  guadagno c'è la guardia in dollari del contratto, misurata sugli importi
  veri al momento del colpo.
- **Il destinatario non si scrive fisso.** Su Uniswap si usa «chi mi ha
  chiamato»; su Curve va verificato se esiste la stessa possibilità,
  altrimenti serve un accorgimento — un indirizzo scritto fisso manderebbe
  l'incasso al contratto vecchio il giorno che ridistribuiamo.
- **La rotta si sceglie per quanto rende**, non per la liquidità dichiarata.
  Su Uniswap quell'errore faceva prendere vasche che rendevano lo 0,01%.
- **Un no misurato è informazione quanto un sì**: se una coppia non si
  vende nemmeno su Curve, si registra, così il giro non ci spreca passate.


## Quello che i gradini 1-3 hanno insegnato (4/11 mattina)

**Il registro di Curve non basta, e nemmeno le sue fabbriche.** Ho chiesto a
`find_pool_for_coins` del MetaRegistry, di tutte e nove le fabbriche che il
fornitore di indirizzi conosce, con due firme diverse, e anche con **ETH
nativo** invece di WETH — ipotesi sensata, perché le vasche ETH di Curve
spesso usano il gettone finto `0xEeee…EEeE`. Risposta: niente, per osETH,
rsETH e syrupUSDT.

E non era vero. **La vasca c'era.**

**Il metodo che ha funzionato è girato al contrario:** invece di chiedere a
Curve dove sono le vasche, si chiede **al gettone chi lo possiede**. Si
leggono i trasferimenti recenti, si prendono le controparti che tengono un
saldo grosso e sono contratti, e si guarda chi di loro risponde a
`coins(0)`/`coins(1)` — cioè chi *si comporta* da vasca.
Trovata cosi': `0xe080027bd47353b5d1639772b4a75e9ed3658a0d`, **osETH/rETH**,
3.006 osETH dentro.

**E ha aperto una strada che non avevo considerato: due piazze in fila.**
  osETH → rETH su **Curve**    99,65% a 50mila, **99,20% a 2 milioni**
  rETH  → WETH su **Uniswap**  99,97% (gia' misurato)
  strada completa: **sopra il 99%**, ben oltre la soglia del 94%.

Quindi il premio osETH — circa 1,4 milioni su cinque posizioni a salute
1,0195 — **e' raggiungibile**. Non serviva imparare Curve da zero: serviva
un salto in piu'.

**La lezione, scritta perche' me l'ero gia' data e l'ho rifatta:** «non si
puo'» va provato, e va provato *con un altro strumento*, non con lo stesso
strumento due volte. Tre registri che dicono no non sono una prova: sono
tre volte lo stesso modo di guardare.


## Gradini 4-5-6 (4/11, un solo giro)

`exchange(int128,int128,uint256,uint256)` — selettore **0x3df02124**,
l'importo compare **una volta sola** a **offset 68**: nessuna ambiguita', il
contratto sa dove scrivere.

Due cose sono venute gratis:

- **Il destinatario non va scritto.** La versione a quattro argomenti manda
  l'incasso a **chi chiama**, cioe' al nostro contratto qualunque sia il suo
  indirizzo. Su Uniswap ho dovuto usare il gettone finto `address(1)` dopo
  aver sbagliato scrivendo l'indirizzo fisso; qui il problema non esiste.
  (Esiste anche una variante con un parametro `address` per il
  destinatario: **non si usa**, proprio per non reintrodurre quell'errore.)
- **Chi preleva e' la vasca stessa**, quindi `daApprovare` resta zero e il
  contratto autorizza la sede — come su Uniswap.

Resta il gradino 7, ed e' quello che decide: **eseguirlo su una copia del
blocco corrente.** Fra «la calldata si costruisce» e «i soldi arrivano nella
cassa giusta» la notte del 3/11 ci stavano tre difetti che non si vedevano.


## Il piano a due passi funziona (4/11, gradini 4-6 completati)

Il contratto accetta una **lista** di passi, e il passo 2 usa da se' tutto
quello che il passo 1 ha incassato. Quindi una strada su due piazze non
richiede niente di nuovo nel contratto:

    passo 1  osETH -> rETH   su Curve     vasca 0xe080027bd4   offset 68
    passo 2  rETH  -> WETH   su Uniswap   router 0x68b3465833  offset 132

In entrambi i passi l'importo compare **una volta sola** e chi preleva e'
la sede stessa, quindi `daApprovare` resta zero.

Resa misurata, con il premio reale che resta del 7%:

| taglia | Curve | Uniswap | totale | premio reale |
|---|---|---|---|---|
| $100.000 | 99,43% | 99,97% | 99,39% | **6,30%** |
| $500.000 | 99,35% | 99,86% | 99,21% | **6,11%** |
| $1.000.000 | 99,25% | **64,60%** | — | si mangia il premio |

A un milione crolla il **secondo** passo, non il primo: il tetto di questa
strada sta fra mezzo milione e un milione, e la ricerca per dimezzamenti lo
trova da se'. Da notare: senza la misura sul SECONDO passo avremmo messo in
cassetto un ordine che si annulla -- la lezione «la rotta si scegli per
quanto rende» vale su ogni salto, non solo sul primo.

**Resta il gradino 7**, e serve una cosa in piu': la prova sul blocco
corrente oggi sa gestire UN passo solo. Va estesa a due.


## GRADINO 7: PASSA (4/11 pomeriggio)

La liquidazione via **Curve** eseguita per davvero su una copia del blocco
corrente, su una posizione viva (garanzia WETH, debito GHO):

    salute 1,071 -> 0,974 (crollo forzato del 9%)
    in cassa: 568,82 GHO
    sei profondita' di crollo provate, da 0,5% a 20%: tutte PASSANO

Con la guardia di produzione attiva, il tetto per coppia a $5.000 e la
calldata costruita da noi -- nessuna API coinvolta.

**Un difetto trovato arrivando qui, e vale oltre Curve.** L'aggregatore nel
frattempo era TORNATO, e la prova ha ripreso la sua strada: cioe'
l'alternativa si poteva provare **solo quando la fonte principale era
rotta**. Un ripiego che si prova solo in emergenza e' un ripiego **non
provato**. Aggiunto `FORZA_RIPIEGO=1`, che mette l'aggregatore in castigo a
comando: da ora la strada di scorta si prova quando vogliamo, non quando
capita.

**La scaletta e' chiusa.** Restano da tarare i tetti delle altre coppie
Curve (sUSDe, osETH, rsETH): e' lavoro di misura, non di costruzione --
la strada c'e' e funziona.
