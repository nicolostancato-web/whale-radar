# Il 39-59% delle pool V2/V3 ha «zero acquisti»: non e' il mercato, e' il nostro conto

*5 ottobre 2026 · difetto misurato, causa non ancora localizzata*

## Da dove e' uscito

Inseguendo il perche' «i gettoni usciti superano quelli entrati» per la maggior parte delle
posizioni, l'ipotesi da provare era: il conteggio del lato gettone e' sbagliato sui mercati V4,
dove il pool non e' un contratto ma un id dentro il PoolManager.

## La misura, e non e' una differenza di grado

Le pool hanno due forme di identita': **indirizzo di 42 caratteri** (V2/V3) e **id di 66**
(V4). Confrontando la quota di scambi classificati come ACQUISTO nei primi sei scambi:

| | media | mediana | pool con **zero** acquisti | pool con **soli** acquisti |
|---|---|---|---|---|
| **V2/V3** | 0,23–0,38 | 0,00–0,17 | **39–59%** | 8–18% |
| **V4** | 0,63–0,72 | 0,67–0,83 | 6–9% | 28–39% |

Misurato su quattro insiemi diversi (due chain x due momenti d'ingresso), con risultati
praticamente identici fra loro.

**Le due famiglie sono centrate su lati opposti.** E un numero e' impossibile come fatto di
mercato: **il 39-59% delle pool V2/V3 ha zero acquisti nei primi sei scambi.** Perche' un
gettone appena nato venga scambiato, qualcuno deve comprarlo.

Verificato contro la spiegazione comoda: non e' grossolanita'. Con l'ingresso al secondo
scambio le quote possibili sono 0, ½ e 1, e una mediana di 0 e di 1 potrebbe essere un
artefatto — per questo la tabella e' costruita sull'ingresso al **quinto** scambio, dove le
quote vanno in sesti, e la distribuzione intera e' larga, non degenere.

## Cosa comporta, e l'elenco e' lungo

Tutto cio' che deriva dalla distinzione compra/vende e' sospetto per almeno una delle due
famiglie:

- gli attributi `quota_acquisti`, `pressione_numero`, `pressione_delta`, `quota_solo_compra` —
  **usati nelle ricerche di combinazioni e nei filtri impilati di ieri**;
- la contabilita' per portafoglio (`speso`, `incassato`, i quattro stati di posizione), quindi
  **tutta la tabella di chi guadagna**;
- e per conseguenza il «gettoni usciti maggiori di quelli entrati» che ho inseguito oggi
  **potrebbe essere interamente questo difetto**, non un comportamento.

Le famiglie pesano: V2/V3 e' il 42-47% delle pool su base e il 18-23% su robinhood.

## Cosa NON faccio, e perche'

**Non "aggiusto" il segno.** Sembra ovvio invertire la famiglia che da' lo zero impossibile, ma
quale delle due convenzioni sia quella sbagliata e' un'**inferenza mia**, non una misura: la
plausibilita' («su una moneta nuova si compra piu' di quanto si venda») e' un argomento, e gli
argomenti plausibili sono precisamente quelli che oggi mi hanno fregato tre volte.

La causa va localizzata **nel codice che decodifica l'evento di scambio**, confrontando il segno
registrato con la direzione reale di un trasferimento noto sulla chain. Finche' non e' fatto,
questo e' un difetto **misurato e non spiegato**, e va scritto cosi'.

## E una correzione a me stesso, nello stesso documento

Cercando la causa ho trovato `agents/acquisti_non_contati.py` che alla riga 17 dice «il segno si
rovescia», e ho annunciato che il problema era gia' documentato. **Falso**: quel file parla di
una media che cambia segno quando un acquisto sparisce — una metafora, non la convenzione dei
segni di uno scambio. Ho riconosciuto una parola e creduto di aver riconosciuto un fatto.

---

## Caccia alla causa: due indizi che si contraddicono, e nessuno abbastanza forte

### Indizio 1 — il decodificatore (`agents/storico_evm.py`)

I tre eventi di scambio hanno **tre forme diverse**, e il codice le tratta cosi':

| versione | dati nell'evento | come viene letto |
|---|---|---|
| V2 | quattro importi SENZA segno (`amount0In, amount1In, amount0Out, amount1Out`) | `a0 = a0In − a0Out` → prospettiva della pool |
| V3 | due importi con segno, prospettiva della **pool** | letto diretto |
| V4 | due importi con segno | letto diretto, **come il V3** |

Il sospetto: nel V4 gli importi sono dalla prospettiva di **chi scambia**, non della pool —
cioe' col segno rovesciato. Se e' vero, **la famiglia sbagliata e' V4**.

### Indizio 2 — la meccanica di mercato: comprare ALZA il prezzo

Non richiede la chain, ed e' meccanica e non plausibilita'. Se la classificazione e' giusta,
la quota di acquisti deve correlare **positivamente** col movimento del prezzo.

| | correlazione quota-acquisti / prezzo | prezzo con molti acquisti | con pochi |
|---|---|---|---|
| V2/V3, base | **−0,072** | +11,12% | +16,66% |
| V4, base | **+0,002** | +2,80% | +0,25% |
| V2/V3, robinhood | **−0,031** | −0,04% | −0,08% |
| V4, robinhood | **+0,013** | +2,64% | +0,72% |

La direzione dice **il contrario** dell'indizio 1: il segno della correlazione e' negativo per
V2/V3 e positivo per V4, quindi sarebbe **V2/V3** la famiglia invertita.

### Perche' non concludo

Le correlazioni sono **quasi zero** (−0,07 e +0,01): il test ha poca potenza, e su V2/V3 il
prezzo sale comunque in entrambi i gruppi (+11% e +16,7%). Due indizi deboli e discordanti non
fanno una conclusione, e scegliere quello che conferma la mia prima intuizione e' esattamente il
modo in cui oggi mi sono sbagliato tre volte.

Ho anche provato la verifica diretta sulla chain: la transazione campionata conteneva **nove
scambi V4 e trentotto trasferimenti** — un percorso multi-salto in cui non si distingue chi sia
la pool. Da la' si indovina, non si misura.

### Il test che decide, dichiarato prima

Una transazione con **un solo scambio** e **due soli trasferimenti di gettoni**, una per
famiglia: la' la direzione e' inequivocabile, e il segno registrato si confronta col movimento
reale senza interpretazione. Va cercata con un filtro sul numero di log, non pescata a caso.

Finche' non e' fatto: **l'anomalia e' misurata, la causa e' candidata, e nessuna correzione va
applicata.** Un'inversione applicata alla famiglia sbagliata raddoppierebbe il danno invece di
ripararlo.

---

## Correzione a questo stesso documento: «impossibile» era troppo forte

Sopra ho scritto: «il 39-59% delle pool V2/V3 ha zero acquisti nei primi sei scambi, ed e'
impossibile come fatto di mercato: perche' un gettone venga scambiato qualcuno deve comprarlo».

**Falso.** Chi lancia la moneta mette la **liquidita' iniziale**, cioe' mette nel pool sia il
gettone sia la valuta. Da quel momento lui e i primi detentori possono **vendere dentro quella
liquidita'** senza che nessuno abbia comprato: sei vendite di fila sono perfettamente possibili,
ed e' lo schema classico di una moneta che nasce per essere scaricata.

Quindi il dato non e' impossibile: e' **anomalo nell'asimmetria fra le due famiglie**, che resta
inspiegata (V2/V3 centrata su «quasi solo vendite», V4 su «quasi solo acquisti»). Ma non e' la
prova che ho detto che fosse.

L'errore e' di una famiglia che conosco: **ho dedotto i limiti della realta' dai miei**
(22 settembre). «Non puo' esistere un pool senza acquisti» era un'affermazione sulla mia
immagine del mercato, non sul mercato — e dei pool di memecoin che nascono per essere scaricati
e' pieno.

## La caccia alla causa, fallita in due giri, e cosa consuma

Tentativo 1: cercare una transazione con **un solo scambio e due soli trasferimenti**.
Esaminate 42 transazioni su 25 pool: **nessuna**. Queste pool sono scambiate tramite router e
aggregatori, quindi ogni transazione e' multi-salto.

Tentativo 2: non serve la semplicita' — bastano i trasferimenti **che coinvolgono quella pool**
(uno entra, uno esce), inequivocabili anche dentro un multi-salto. Nessun caso isolabile nel
budget: il filtro «esattamente uno dentro e uno fuori» e' troppo stretto su transazioni che
toccano la stessa pool piu' volte.

**Questo lavoro non va fatto a mano in sessione.** E' una verifica su dati di catena che vuole
un budget di chiamate e pazienza, cioe' una corsia con un tetto di tempo — non venticinque
minuti interattivi. Due giri spesi cosi' sono due giri in cui non ho fatto altro.

## Lo stato, scritto senza abbellirlo

- l'asimmetria fra le famiglie e' **misurata e replicata** su quattro insiemi;
- la sua causa e' **candidata** (la convenzione dei segni nel V4) e **non confermata**;
- i due indizi disponibili **si contraddicono** e sono entrambi deboli;
- la mia affermazione piu' forte («impossibile») era **sbagliata**, e l'ho corretta qui sopra;
- **nessuna correzione e' stata applicata ai dati**, ed e' la decisione giusta.
