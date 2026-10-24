# I mittenti ricorrenti erano contratti, non persone — e tre ipotesi morte in venti minuti

*5 ottobre 2026 · il grafo dei trasferimenti verso i portafogli bravi*

## Da dove si partiva

La riconciliazione (`IL_GUADAGNO_ERA_CONTABILITA.md`) ha mostrato che il guadagno apparente dei
bravi nasceva da gettoni **venduti senza un acquisto osservato**. Conseguenza logica: il segnale
non e' l'acquisto, e' **chi manda loro i gettoni**. E' anche la forma che Nicolo' indica da mesi.

## Il primo risultato sembrava perfetto

Gli stessi mittenti ricorrono su piu' bravi: `0x64b37e…` su tre portafogli, `0x8366a3…` su tre
altri, `0x26a5d0…` su tre. **La struttura condivisa che cerchiamo**, con la forma giusta.

## Ed era infrastruttura

| mittente | contratto? | nome sulla chain |
|---|---|---|
| `0x54a72d…` | si' | **UniswapV2Pair** |
| `0x8366a3…` | si' | **PoolManager** (Uniswap V4) |
| `0x64b37e…` | si' | **RetailAirdrop** |
| `0x26a5d0…` | si' | — |
| `0xcbf0e9…` | si' | — |

**Tutti e cinque contratti.** Quando compri su un mercato decentralizzato i gettoni te li manda
il contratto della pool: il mittente «ricorrente» e' il mercato, non un finanziatore.

Chiamarli finanziatori sarebbe stato un **falso grave**, e per una ragione che vale annotare:
**aveva esattamente la forma giusta.** Lo stesso indirizzo su molti vincenti e' precisamente il
pattern che cerchiamo — e qui era un router. La forma di un risultato non e' una prova.

## Seconda ipotesi, nata e morta in cinque minuti

`RetailAirdrop` sembrava risolvere tutto: ricevono gettoni gratis e li vendono, quindi nessun
costo, quindi i multipli esplosi. Misurato: **5 bravi su 20** hanno ricevuto da quel contratto,
e la quota mediana dei loro trasferimenti entranti che ne viene e' **0%**.

Spiega una minoranza. Non il quadro.

## Terza ipotesi, nata e morta in dieci minuti

Se `PoolManager` e' Uniswap **V4** e noi non indicizzassimo le pool V4, i loro acquisti
sarebbero invisibili a noi — e il «hanno venduto il 200% di quello che hanno comprato» non
sarebbe un loro comportamento ma **un buco nostro**. Sarebbe stata la spiegazione piu'
importante della giornata.

Verificato: **le pool V4 sono indicizzate.** Sono il 56,1% delle coppie su base e l'**81,6%** su
robinhood (`dex=4`), e il codice le gestisce esplicitamente — i pool V4 non sono contratti, sono
id dentro il PoolManager, e `coppie_token.py` lo dice da settembre. Ipotesi esclusa.

## Cosa resta stabilito, e cosa resta aperto

**Stabilito oggi:**
1. Il **prezzo non si muove** fra il loro ingresso e la loro uscita: 1,00X in ogni fascia di
   costo, su due chain, a ogni ritardo. La misura piu' solida della giornata.
2. Il multiplo in **dollari** e' inaffidabile in **entrambe** le direzioni: gonfiato dai costi
   quasi-zero, deflazionato dalle uscite parziali.
3. Sui giri **davvero chiusi** (gettoni venduti fra il 99% e il 105% dei comprati, n=18 e 15)
   le due misure **concordano** e dicono **1,00X**.
4. I mittenti ricorrenti sono **contratti**, non persone.
5. Le pool V4 **sono** nei nostri dati: il buco di copertura non spiega niente.

**Aperto, e dichiarato come aperto:** perche' per la maggior parte delle posizioni i gettoni
usciti superano quelli entrati. Le tre spiegazioni comode sono morte. La prossima da provare —
e va provata, non assunta — e' che il conteggio dei gettoni per singolo scambio sia sbagliato
sui mercati V4, dove il pool non e' un contratto ma un id: se il lato del gettone viene letto
male su quel tipo di scambio, entrate e uscite non tornano per costruzione.

Tre ipotesi aperte e chiuse in venti minuti, nessuna pubblicata come risultato. Quello e' il
ritmo che il 22 settembre richiedeva un piano intero.
