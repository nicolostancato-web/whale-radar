# La macchina vera — 23 settembre 2026, notte

*Scritto dopo una critica giusta del fondatore: «abbiamo i modelli piu' forti del pianeta e ne

> **⚠️ Metro corretto il 25/09.** I tassi di trappola citati qui sono **ottimistici**: col metro
> giusto (pool giudicati per eta', non per ore osservate) le trappole sono il **43% su robinhood**
> e il **53% su base**, con media −41% / −52%. Vedi la correzione in testa a `DIREZIONE_CHIUSA.md`.

usciamo con «entriamo dopo due ore se ci sono 50 compratori»».*

## Aveva ragione, e la diagnosi e' peggiore di «troppo semplice»

Non era il metodo a essere povero: erano i **dati in ingresso**. Il loop 1 sceglieva fra CINQUE
numeri grezzi (compratori, scambi, ritmo, il loro rapporto, l'eta'). Ho affamato il modello e poi mi
sono lamentato che fosse banale.

Ogni scambio contiene: portafoglio, importo CON SEGNO, blocco, posizione nel blocco, dex. Da li' si
ricavano **33 caratteristiche** che non avevo mai calcolato.

## Cosa c'e' adesso

| | prima | adesso |
|---|---|---|
| caratteristiche | 5 contatori | **33** |
| pool nell'analisi | 1.058 (un quinto, solo i piu' attivi) | **9.598** (tutti) |
| metodo | due soglie cercate a mano | modello che **incrocia tutte** le caratteristiche |
| validazione | permutazione nello stesso campione | addestra sul passato, giudica sul **futuro** |

Le 33 caratteristiche, per famiglia: **pressione** (squilibrio fra acquisti e vendite, in volume e in
numero, e se sta crescendo o calando); **concentrazione** (Gini degli importi, quota del primo
scambio, quota dei primi tre, rapporto massimo/mediano); **partecipanti** (Gini dei portafogli, quota
del primo, chi compra e basta contro chi gira, portafogli nuovi nella seconda meta'); **tempo**
(ritmo, accelerazione, irregolarita', buco massimo, scambi nello stesso blocco = automi); **prezzo**
(percorso, caduta dal massimo, volatilita', quota di salite, impatto tipico).

## Le due illusioni di oggi, e la loro radice comune

**Illusione 1 — il campione che lusinga.** La regola «11 compratori e 73 scambi» dava 4,2 volte il
controllo. Misurata su TUTTA la popolazione invece che su un quinto dei pool piu' attivi: **0,4x**,
cioe' peggio di non fare niente. La prova sul futuro aveva detto 0,5x. **Aveva ragione lei.**

**Illusione 2 — il prezzo che mente.** Il modello a 33 caratteristiche dava capacita' predittiva
**0,92** sul futuro e un decimo migliore al **92%** con mediana **+66%**. Numeri impossibili.
Lo stesso identico calcolo con l'esito misurato sul prezzo MEDIANO della finestra invece che
sull'ULTIMO scambio:

| esito misurato con | capacita' | decimo migliore | mediana | in perdita |
|---|---|---|---|---|
| l'ultimo prezzo | 0,881 | 92,2% | +65,9% | 5% |
| **il prezzo mediano** | **0,602** | **21,0%** | **−2,5%** | **56%** |

Il modello non prevedeva i guadagni: sceglieva i pool con **pochi scambi dopo l'ingresso** (mediana
8 contro 37), dove l'ultimo prezzo e' una singola stampa ballerina.

**La radice e' la stessa: una misura che lusinga.** Una volta il campione, una volta il prezzo. Ed
entrambe hanno superato controlli statistici seri — permutazioni, walk-forward, test sull'intera
ricerca. **Nessun test statistico salva da un metro storto**, perche' i test misurano la relazione
fra numeri, non se quei numeri dicono la verita'.

## Dove siamo, col metro giusto

Modello a 33 caratteristiche, esito col prezzo mediano, giudicato su 2.880 pool mai visti:

- capacita' di ordinare sul futuro: **0,682** (0,5 = caso)
- decimo migliore: **13,5%** fanno +50% contro il **7,6%** di tutti → **1,8 volte**
- rendimento medio del decimo migliore: **+7,1%** contro **+3,6%**

**0,68 e' un numero che puo' essere vero.** 0,92 no, e avrei dovuto sospettarlo prima di esserne
contento.

**Il campanello da tirare per primo domani:** i cinque gruppi NON sono ordinati — il quarto quinto fa
26,7% e il quinto solo 7,5%. Un segnale solido sale in fila. Questo no.

## Il seguito della stessa notte: altre due falle, e il fondale vero

**Falla 3 — il «dopo» era il «durante».** L'esito prendeva anche gli scambi con lo STESSO secondo
dell'ingresso: per circa un pool su cinque il prezzo di uscita era simultaneo a quello di entrata.
Ora servono almeno 60 secondi di distacco e almeno 5 prezzi.

**Falla 4 — il fondale non era mai stato misurato.** Con tutte le falle chiuse:

| | rendimento medio a 6 ore |
|---|---|
| comprare TUTTI i memecoin nuovi a 2 ore | **−12,9%** |
| comprare il decimo migliore scelto dal modello | **−18,8%** |

**Il modello sceglie PEGGIO del caso.** Capacita' di ordinare 0,658 — ma ordina verso il basso.

E il numero che nessuna misura precedente aveva mai mostrato: **questo mercato, comprato cosi',
perde il 13%.** Tutti i «vantaggi» della giornata erano misurati contro un fondale sbagliato.

## Le quattro illusioni di una giornata, e la causa unica

| illusione | cosa la reggeva |
|---|---|
| la regola a 4,2x | campione ristretto ai pool piu' attivi |
| il modello a 0,92 | esito sull'ultimo prezzo, ballerino |
| il 23% di pool «vivi» | esito misurato nello stesso secondo dell'ingresso |
| ogni vantaggio apparente | fondale di mercato mai misurato |

**Nessuna era una strategia sbagliata: erano tutte metri storti.** E hanno superato permutazioni,
walk-forward e validazione temporale — perche' quei test misurano la coerenza fra numeri, non se i
numeri dicono il vero.

**Il guadagno della notte non e' una strategia: e' un metro dritto.** Da domani, quando qualcosa
sembrera' funzionare, la probabilita' che sia vero e' molto piu' alta.

## Le tre domande

**Come essere piu' forte?** Non aggiungendo modelli: smettendo di affamarli. Le 33 caratteristiche
erano gia' nei dati che avevamo da mesi.

**Come essere piu' furbo?** Diffidando dei risultati belli con la stessa energia dei brutti. Oggi ho
difeso un 4,2x per ore e smontato uno 0,92 in dieci minuti. Erano falsi entrambi.

**Come spaccare tutto?** Misurando bene. Le illusioni non nascono da strategie sbagliate — quelle si
buttano gratis — ma da metri storti, che rendono indistinguibile il buono dal cattivo.

---

# La mappa del fondale — e perche' entravamo nel momento peggiore

*24 settembre, notte fonda. La prima cosa solida della giornata, e non e' una strategia: e' una mappa.*

Quanto rende comprare un memecoin nuovo, al variare di QUANDO entro e QUANTO tengo. Nessuna
selezione, tutti i 10.733 pool di robinhood, esito col prezzo mediano.

**Probabilita' che faccia +50%**

| entro a | tengo 1h | tengo 3h | tengo 6h | tengo 12h | tengo 24h |
|---|---|---|---|---|---|
| **0,5h** | 2,7% | 4,3% | 8,4% | 11,2% | **11,9%** |
| 1h | 1,4% | 2,5% | 7,0% | 10,6% | 11,3% |
| 2h | 0,9% | 2,3% | 4,6% | 8,5% | 9,2% |
| 4h | 0,9% | 1,6% | 4,1% | 6,6% | 7,5% |
| 8h | 0,6% | 1,3% | 1,8% | 4,5% | 5,2% |

**Due andamenti monotoni, senza una sola eccezione in 25 caselle:** prima entri meglio e', piu'
tieni meglio e'. Un andamento su tutta una griglia e' molto piu' difficile da falsificare di una
soglia fortunata.

**Ed eravamo nella casella sbagliata su ENTRAMBE le dimensioni:** entrata a 2 ore, tenuta 6. Con
mezz'ora e 24 ore la probabilita' di un colpo grosso **raddoppia**.

Il rendimento mediano resta **−1,8% ovunque**: il token tipico non si muove. Tutto il gioco e' nella
coda — conferma che l'unica misura sensata e' la frequenza dei colpi grossi.

*(Nota: i −98% nella colonna «tengo 1h» a 4 e 8 ore sono un artefatto della regola che pretende
almeno 5 prezzi nella finestra; non sono perdite reali.)*

## Il modello nella casella migliore: promettente, e poi ridimensionato

Rifatto l'insieme a 0,5h / 24h: 9.393 pool, l'11,8% fa +50% (contro il 4,6% di prima).

- capacita' sul futuro **0,830**, decimo migliore **61,6%** contro 17,2% → 3,6 volte
- sopravvive a togliere OGNI misura di prezzo (0,812) e anche la concentrazione (0,791)
- con esiti mescolati crolla a 0,309: nessuna perdita di informazione, il codice e' pulito
- con intervallo di sicurezza fra addestramento e prova: regge (0,825)

**Ma spostando il taglio temporale il risultato si sgonfia:**

| addestro sul primo | vantaggio del decimo migliore | mediana | quota di +50% nel periodo |
|---|---|---|---|
| **50%** | 2,1× | **−1,8%** | 5,1% |
| 60% | 3,8× | +12,2% | 10,9% |
| 80% | 5,7× | **+77,5%** | 16,6% |

**Il mercato recente e' tre volte piu' generoso di quello vecchio**, e quasi tutta la forza del
risultato viene da li'. Nella finestra piu' antica la mediana e' **negativa**.

E' lo stesso schema che aveva ingannato al mattino: un risultato concentrato nelle ultime settimane.

**Conclusione: una capacita' di ordinare esiste** — regge anche nella finestra peggiore, 2,1 volte —
**ma e' modesta e dipende dal regime.** Non e' un edge: e' un indizio, misurato con un metro dritto.
