# Ricerca Grok — Base — come_si_gradua

Modello grok-4.7. Costo: ZERO (abbonamento). Tempo: 340s. 2/2 con risposta.

---

### Sulla principale piattaforma di lancio di Base: esiste una soglia che fa passare una moneta dalla curva al mercato vero? Quanto vale, in che valuta? Col link.

Cerco sulla piattaforma di lancio principale di Base se esiste una soglia di passaggio dalla bonding curve al mercato, e il valore ufficiale.Le fee degli ultimi 30 giorni sono spartite tra più launchpad. Verifico quale usa davvero una curva che “gradua” e qual è la soglia ufficiale.**Su Bankr e su o1, le due piattaforme che oggi si dividono i lanci su Base, quella soglia non esiste.** La moneta nasce già su un pool Uniswap v4. Non c'è un secondo momento in cui esce da una curva e entra in un mercato diverso.

Sui fee degli ultimi 30 giorni (dato DefiLlama al 7 ottobre 2026) o1 è al 34,9% e Bankr al 34,0%. Il 7 ottobre Bankr da sola ha fatto il 62% della giornata. Clanker, terza, funziona allo stesso modo: pool Uniswap dal primo blocco, senza graduation.

* Bankr (Base): multicurve Doppler già su Uniswap v4, liquidità bloccata, migrator disattivato (`NoOpMigrator`). Nessun evento on-chain di graduation. Coppia di default in WETH. [Docs Bankr](https://docs.bankr.bot/faq/token-launching) · [meccanica Doppler/Bankr](https://docs.bitquery.io/docs/blockchain/Base/base-bankr-api/) · [opzione no-migration di Doppler](https://docs.doppler.lol/core-concepts/liquidity-migration-options)
* o1: il mercato Uniswap v4 si apre al lancio, con FDV iniziale intorno a 4.000 dollari. [Docs o1](https://docs.o1.exchange/launchpad/introduction)
* Clanker: stesso schema, niente curva. [Docs Clanker](https://clanker.gitbook.io/documentation/general/token-deployments)

L'unica piattaforma grande su Base che ha ancora il passaggio curva → mercato è **Virtuals** (agenti AI, non il launchpad meme per volume). La soglia ufficiale è **42.000 VIRTUAL**. Quando la curva ha accumulato quella liquidità, il protocollo crea da solo il pool Uniswap v2 e blocca gli LP per 10 anni. La cifra è in token VIRTUAL, non in dollari né in ETH. [Virtuals Launch Mechanics](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/virtuals-launch-mechanics)

### Alla graduazione, il prezzo del nuovo mercato coincide con l'ultimo prezzo della curva, oppure c'e' un salto? Col link alla documentazione o al contratto.

Cerco nel progetto e nella documentazione cosa succede al prezzo nel momento della graduazione.Il progetto ha già un appunto su questo. Lo rileggo insieme alla fonte sul contratto, per vedere se il prezzo del nuovo mercato continua la curva o salta.La nota interna dice che il pool apre allo stesso prezzo della curva. Verifico sulla documentazione ufficiale e, se serve, sul contratto.Il contratto calcola i due importi del pool con una formula precisa. La apro per vedere se quel rapporto è lo stesso prezzo di chiusura della curva.**Coincide.** Alla graduazione il pool Uniswap v4 apre al prezzo spot con cui la curva ha chiuso. Il salto non è previsto dal meccanismo.

Lo scrive il contratto della factory, non solo la documentazione. In `PonsV2LaunchFactory` la funzione che decide quanti gettoni entrano nel pool è commentata così: ricava la frazione di riserva che **conserva il prezzo terminale della curva** dopo aver tolto dal seme la riserva virtuale.

```1309:1321:contractsV2/src/v2/PonsV2LaunchFactory.sol
// Derives the reserve fraction that preserves the curve's terminal
// price after the virtual quote reserve is removed from the pool seed.
function _poolTokenAmount(...) returns (uint256 poolTokenAmount) {
    uint256 virtualQuote = sweptQuote + curve.phantomQuote();
    poolTokenAmount = totalTokenAmount * sweptQuote / virtualQuote;
}
```

Il prezzo del pool è il rapporto fra i due importi con cui viene inizializzato (`sqrtPriceX96FromAmounts`, poi `poolManager.initialize`). Quegli importi sono l'ETH davvero raccolto e solo una parte dei gettoni tenuti da parte. Il resto resta bloccato nel locker e non entra in circolazione. Con quei due numeri il rapporto è lo stesso del prezzo marginale di chiusura della curva, cioè riserva di quotazione (reale più fantasma) diviso gettoni ancora sulla curva.

Sulla config ETH standard (soglia 4,2 ETH, fantasma 1,68 ETH) i gettoni riservati sono 2/7 della supply. Nel pool ne entra la quota `4,2 / 5,88` di quei riservati. Se ci entrassero tutti, il pool aprirebbe circa al 71% del prezzo di chiusura, perché 1,68 ETH sono virtuali e non ci sono. Il lock dell'eccesso serve proprio a evitare quel ribasso.

Fonte, sul sorgente ufficiale, righe della factory:

- [quantità che conserva il prezzo terminale](https://github.com/ponsdotdev/ponsfamily/blob/main/contractsV2/src/v2/PonsV2LaunchFactory.sol#L1287-L1322)
- [inizializzazione del pool a quel rapporto](https://github.com/ponsdotdev/ponsfamily/blob/main/contractsV2/src/v2/PonsV2LaunchFactory.sol#L1362-L1370)

Factory deployata su Robinhood Chain (chain id 4663): [`0x7eD598BcEf8bd9Edd8C97A195C6d13f40801EC7e`](https://robinhoodchain.blockscout.com/address/0x7eD598BcEf8bd9Edd8C97A195C6d13f40801EC7e).

La [documentazione](https://docs.ponsfamily.com/v2#graduation) dice una cosa più stretta: a parità di config ogni lancio gradua in un pool della stessa dimensione e allo stesso prezzo, deciso in partenza. La frase che quel prezzo è quello di chiusura della curva sta nel contratto.

Due precisazioni, entrambe piccole. Il prezzo che coincide è lo spot dell'ultimo istante della curva, non la media pagata da chi ha fatto l'acquisto che l'ha chiusa: quell'acquisto ha camminato lungo la curva e ha pagato meno dello spot finale. E la divisione intera può lasciare un wei di arrotondamento. Non è un salto di mercato.
