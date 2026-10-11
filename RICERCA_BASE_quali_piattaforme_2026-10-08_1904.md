# Ricerca Grok — Base — quali_piattaforme

Modello grok-4.7. Costo: ZERO (abbonamento). Tempo: 169s. 2/2 con risposta.

---

### Su Base (chain id 8453), quali sono le piattaforme di lancio di memecoin piu' usate nel 2026? Dammi i nomi e il link alla documentazione di ognuna.

Cerco le piattaforme di lancio memecoin più usate su Base nel 2026 e i link alla documentazione ufficiale.I dati di fee su Base (7 ottobre 2026) mettono in testa o1, Bankr e Clanker. Recupero la classifica completa e i link alla documentazione ufficiale.Su Base (chain id 8453), a inizio ottobre 2026 l’attività si concentra su cinque piattaforme. Insieme raccolgono quasi tutte le fee dei launchpad della chain: circa **3,05 milioni di dollari in 30 giorni**, fino al 7 ottobre 2026 (UTC), secondo DefiLlama via [MemeFees](https://memefees.com/chains/base). Altre 16 piattaforme stanno sotto i 10.000 dollari in 30 giorni (22.900 dollari in tutto).

La classifica è per **fee incassate su Base**, non per numero di token creati: per queste piattaforme il conteggio dei lanci non è completo.

| Piattaforma | Fee 30g su Base | Quota | Documentazione |
|---|---:|---:|---|
| **o1 Launchpad** | 1,08 M$ | 35,3% | [docs.o1.exchange/launchpad/introduction](https://docs.o1.exchange/launchpad/introduction) |
| **Bankr** | 1,01 M$ | 33,1% | [docs.bankr.bot — token launching](https://docs.bankr.bot/token-launching/overview) |
| **Clanker** | 708 k$ | 23,3% | [clanker.gitbook.io/documentation](https://clanker.gitbook.io/documentation) |
| **BaseStonk** | 169 k$ | 5,6% | [docs.basestonk.io](https://docs.basestonk.io/) |
| **Umia** | 61 k$ | 2,0% | [umia.finance/docs](https://umia.finance/docs) |

Il giorno 7 ottobre la classifica giornaliera era diversa: Bankr al 45,3%, Clanker al 31,1%, o1 al 19,6%. o1 guida il mese, Bankr la giornata più recente.

Cosa fa ciascuna:

- **o1 Launchpad** apre subito un pool Uniswap v4 con liquidità bloccata. Su Base ha due prodotti, Standard (token B20) e Tax (ERC-20 con tasse di buy/sell). Supply fissa di 1 miliardo. API: `https://api.launch.o1.exchange/v1`.
- **Bankr** è il launchpad per agenti e per lanci da X (`@bankrbot`). Su Base il deploy passa da **Doppler** (pool Uniswap v4, gas sponsorizzato). Gira anche su Robinhood Chain, Arbitrum e Arc; solo circa il 30% delle sue fee arriva da Base.
- **Clanker** è il launcher storico di Base (Farcaster e clanker.world), ora anche su altre EVM. Il 94,6% delle sue fee resta su Base. Deploy v4: [clanker.world/deploy](https://www.clanker.world/deploy).
- **BaseStonk** crea token e pool Uniswap v4 in una transazione, senza bonding curve né graduation. Su Base la coppia può essere USDC, WETH, cbBTC, azioni tokenizzate o $BSTONK.
- **Umia** è un quinto posto per fee, ma non è un memepad classico: aste onchain (Uniswap v4 Continuous Clearing Auction), tesoreria e governance. I primi quattro sono i launchpad memecoin veri e propri.

Zora, Flaunch e Virtuals Protocol, citati ancora nella documentazione di Base, a ottobre 2026 sono marginali sulle fee: Zora circa 9.300 dollari in 30 giorni su tutte le chain, Flaunch circa 6.700 dollari tutti su Base. Docs: [docs.flaunch.gg](https://docs.flaunch.gg/), [docs.zora.co](https://docs.zora.co/), [whitepaper.virtuals.io](https://whitepaper.virtuals.io/).

### Qual e' la piattaforma di lancio con piu' volume su Base oggi? Dammi il dato e la fonte.

Cerco i dati di volume delle piattaforme di lancio su Base aggiornati a oggi e la fonte ufficiale.Le fee di ieri indicano Bankr in testa, ma cerco il volume di trading vero, non solo le commissioni.La query Dune di Bankr è aggiornata da poche ore. Recupero il volume del giorno più recente, non solo la settimana.**Bankr**, con **$33,2 milioni** di volume di trading negli ultimi 7 giorni su Base.

È la finestra più stretta pubblicata oggi. Il giorno UTC dell’8 ottobre è ancora aperto e non c’è un totale giornaliero chiuso.

| Piattaforma | Volume 7 giorni | Volume 30 giorni |
|---|---:|---:|
| **Bankr** | **$33,2M** | $133,7M |
| o1 | $14,3M | **$146,9M** |
| Virtuals | $10,8M | $27,1M |
| Clanker | $4,9M | $28,4M |
| Flaunch | $111K | $2,6M |
| Liquid | $27K | $312K |

Sui 30 giorni è ancora **o1** avanti ($146,9M contro $133,7M di Bankr). Sulla settimana Bankr è tornato primo.

**Fonte:** query Dune di Bankr, [Launchpad Volume by Timeframe](https://dune.com/queries/7448936), ultima esecuzione indicata a circa 17 ore fa (8 ottobre 2026). Dashboard: [Bankr Metrics](https://dune.com/bankrofficial/bankr-metrics).

Il volume è quello dei token lanciati da ciascuna piattaforma, solo su Base. Clanker è contato al netto del wash (pool USDC e pool ETH nativi su Uniswap v4). Bankr e o1 sono contati grezzi: lo stesso filtro, applicato a o1, taglierebbe circa l’85% del suo volume, quindi i numeri di Clanker non sono sullo stesso metro degli altri.
