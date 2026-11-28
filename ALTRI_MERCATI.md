# Vale la pena estendere il laghetto? — verifica del 7/11/2026

Richiesta di Nicolò: tre domande, **solo ricerca, nessuna implementazione**.
Aave v3 Core resta armato (guardia nuova aggiunta e **provata**: uccisa la
sentinella, ripartita in 25 secondi da sola).

## Come ho misurato

Eventi di liquidazione **veri**, dai registri, su **quattro finestre separate**
da 3.000 blocchi (40 ore in tutto), perché una coda non si giudica da un
campione solo. Verificato prima che gli indirizzi parlino: Morpho produce 625
log in 300 blocchi, Spark 59, Compound 7 — sono mercati vivi, non indirizzi
sbagliati.

Nota di metodo: Alchemy **non serve** per questo. Il piano gratuito limita
`eth_getLogs` a **10 blocchi** per richiesta (dieci, non diecimila). Chiude i
limiti sulle letture di stato e sul mempool filtrato, non sui registri storici.

## 1. Il laghetto si può estendere?

| mercato | eventi in 40 ore |
|---|---|
| **Morpho Blue** | **22** |
| Aave v3 Core (noi) | 13 |
| Aave v2 | 1 |
| Spark | 0 |
| Compound v3 USDC | 0 |
| Compound v3 WETH | 0 |
| Compound v2 | 0 |
| Fluid | 0 |
| Aave v3 Prime | 0 |

**Sì, e un mercato solo conta: Morpho Blue.** Tutti gli altri sono fermi.
Spark, Compound e Fluid: **zero liquidazioni in 40 ore**. Quindi non è «ci sono
un sacco di mercati»: ce n'è **uno**.

## 2. Ne vale la pena? Il numero che conta non è il totale

Premio di Morpho in 40 ore: **372.742 $**. Ma guardare quel numero sarebbe
l'errore della media che mente:

| | |
|---|---|
| il più grosso, **UN evento** | **366.614 $** (98,4% del totale) |
| il secondo | 3.546 $ |
| il terzo | 2.295 $ |
| mediana | 246 $ |
| **il corpo, senza la coda** | **6.128 $** |
| Aave v3 Core nelle stesse 40 ore | ~5.684 $ |

**Il corpo è equivalente.** La differenza è tutta in **una** coda.

E c'è un secondo filtro che ribalta il conteggio: dei 22 eventi di Morpho,
**solo 7 erano su gettoni di cui sappiamo il prezzo**. Gli altri 15 stanno su
mercati esotici — wSPYx, ynETHx, msETH, FXRP, RLUSD, SYRUP, kBTC — e se non
sappiamo il prezzo è molto probabile che non sappiamo nemmeno venderli.
**Sugli eventi USABILI: Morpho 7, Aave 13.** Aave è il doppio.

## 3. La macchina si sposta senza rivoluzione?

Chiesto alla catena, non alla memoria.

**Si sposta senza toccarlo** (la maggior parte del lavoro di questi giorni):
l'occhio che decodifica l'oracolo, il magazzino delle firme, la consegna alle
3 porte, la mancia a `block.coinbase` dal ricavato, il giudizio della rotta
con 1inch di ricambio, la guardia economica col gas, il C-check, le guardie.

**Va scritto nuovo, ed è modesto:** il contratto deve esporre
`onMorphoLiquidate(uint256,bytes)` o `onMorphoFlashLoan(uint256,bytes)` più un
punto d'ingresso che chiami `liquidate` di Morpho (selettore `d8eabcb8`,
verificato presente).

**Va scritto nuovo, ed è il lavoro vero:** la scoperta delle posizioni.
Aave risponde `getUserAccountData(utente)` in **una** chiamata, con la salute
già calcolata. Morpho no: per ogni **mercato isolato** servono
`position(id,utente)` + `market(id)` + l'oracolo di quel mercato, e la salute
la calcoliamo noi. E non esiste un elenco globale di debitori: va costruito
mercato per mercato dagli eventi, su centinaia di mercati. Tutta la nostra
macchina della sorveglianza — 88.526 debitori, lista corta, composizione,
ordini pronti, appuntamenti — è **cucita su una chiamata che Morpho non ha**.

## Verdetto

**Non adesso.** Tre motivi, in ordine:

1. **Sul corpo non guadagniamo niente** (6.128 contro 5.684 $), e sugli eventi
   usabili ne perdiamo (7 contro 13).
2. **Hai ragione tu sul rischio**: due macchine mezze fatte sono peggio di una.
   La nostra ha attraversato un blocco vero **per la prima volta oggi** e ha
   ancora 6 verifiche rosse.
3. Il lavoro vero non è il contratto: è **rifare la scoperta delle posizioni**
   su un'interfaccia diversa. Giorni, non ore.

**Quando tornarci:** quando la coda diventa raggiungibile. Quell'evento da
366.614 $ chiudeva **7,37 milioni** di debito e vendeva 7,73 milioni di WBTC.
Il prestito lampo non ci serve capitale, ma il tetto del gas sì — e con 0,0415
ETH non potevamo nemmeno promettere il gas di quella transazione. **È la stessa
cassa che apre tutto**: col primo premio il tetto si alza, e allora Morpho
diventa interessante per il motivo giusto, cioè la coda.

## Una cosa da fare SUBITO, e non c'entra col trasloco

**Morpho ha il suo prestito lampo e non ha commissione** (`flashLoan(address,
uint256,bytes)`, selettore `e0232b42`, presente; nessuna funzione di
commissione). Aave dichiara `FLASHLOAN_PREMIUM_TOTAL = 5` punti base: su un
prestito da 161.540 $ sono **80,77 $**.

Possiamo prendere il prestito da **Morpho** e liquidare su **Aave**: è un
cambio dentro la macchina attuale, nessun trasloco, e rende positive le
occasioni marginali che oggi la guardia rifiuta. Da provare su copia della
catena prima di collegarlo.
