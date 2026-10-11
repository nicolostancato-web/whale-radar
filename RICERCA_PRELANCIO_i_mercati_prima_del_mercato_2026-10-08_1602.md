# Ricerca Grok — 2026-10-08 16:02 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 409s

---

Il fascicolo deve chiudere o confermare, con fonti primarie, se nel 2026 esistono mercati di pretese, aste o scambi fuori catena per i gettoni di Base e Robinhood prima del mercato principale. Prima verifico il contesto del fascicolo e le fonti ufficiali.Per questi gettoni non esiste un mercato di pretese future, né un libro fuori catena. L'unica asta documentata su entrambe le chain è un prodotto a parte: ci si entra se un team ci mette la supply, non perché il gettone è nato su un launchpad. Sui launchpad il gettone nasce già scambiabile.

Oggetto: i gettoni che nascono sui launchpad di Base e di Robinhood Chain (Pons, Clanker, Flaunch, Bankr, o1, Virtuals). «Mercato principale» è la pool in cui quel gettone si scambia appena esiste. Lettura dell'8 ottobre 2026. Costo: zero.

## 1. Pretese future: il prodotto esiste, non per questi gettoni

Una pretesa futura ha bisogno di un gettone che qualcuno possa consegnare dopo un TGE, e di un mercato che qualcuno abbia aperto prima. I launchpad di queste due chain fanno il contrario: la transazione che crea il gettone apre lo scambio.

**Whales Market.** Scambio peer-to-peer di allocazioni pre-TGE. Il venditore mette in lista l'allocazione, il compratore accetta, entrambi bloccano collaterale, la consegna è on-chain dopo il TGE. [About Pre-Market](https://docs.whales.market/pre-market/about-pre-market). Prima del TGE nessuno regola e nessuno cancella. La finestra ideale dura 4 ore dall'attivazione; il venditore può consegnare oppure andare in default e perdere il collaterale. [Settlement Rules](https://docs.whales.market/pre-market/settlement-rules).

Il contratto è distribuito su Base: `0xdf02eeaB3CdF6eFE6B7cf2EB3a354dCA92A23092`. [Supported Networks](https://docs.whales.market/additional-document/supported-networks). Nella stessa tabella non c'è Robinhood Chain, chain id 4663. L'indice della documentazione non ha una pagina per aprire un mercato su un gettone qualunque: l'ordine di vendita si crea su un gettone già in lista. [Create Your Own Sell Order](https://docs.whales.market/pre-market/how-to-sell-token-allocation/create-your-own-sell-order). Quante monete dei launchpad di Base siano in quella lista non si può sapere da queste pagine: non pubblicano l'elenco filtrato per chain.

**Aevo, Pre-Launch Token Futures.** Future su un gettone non ancora lanciato. Quando il gettone scambia su un mercato esterno, il contratto diventa un perpetual. Margine iniziale 50% (leva massima 2×), margine di mantenimento 48%, posizione massima 50.000 USD «subject to change», niente prezzo indice, niente funding, settlement in USDC, taker 25 bps, maker −10 bps, liquidazione 5%. [Pre-Launch Token Futures](https://docs.aevo.xyz/aevo-products/aevo-exchange/trading-on-aevo/pre-launch-token-futures). All'8 ottobre 2026 la pagina dice «last updated 5 months ago». La conversione scatta quando Aevo aggancia «a reliable source for the index price, typically a tier 1 CEX or a deep DEX LP». La pagina non nomina Base né Robinhood Chain, e non descrive una funzione con cui un utente apre il mercato.

**Binance Pre-Market.** Finestra spot, sui libri di Binance, per gettoni che Binance ha selezionato, in genere legati a Launchpool. Finisce almeno 4 ore prima dello spot ufficiale. [FAQ](https://www.binance.com/en/support/faq/detail/d4c5afbf4b804c63908a63d760be97f9), data in pagina 2024-09-25. [Academy](https://www.binance.com/en/academy/articles/what-is-binance-pre-market), «Updated Jun 26, 2026». Non è una chain, e la pagina non dice che un gettone entra perché è nato su Base o su Robinhood Chain.

La documentazione corrente di Hyperliquid descrive i mercati di esito HIP-4, non un mercato di gettoni ancora da emettere su queste due chain. [HIP-4](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-4-outcome-markets).

## 2. Aste: un protocollo sì, il percorso dei launchpad no

**Uniswap Continuous Clearing Auction.** Asta on-chain a prezzo uniforme continuo; a fine asta i proventi seminano una pool Uniswap v4. [Overview](https://docs.uniswap.org/contracts/liquidity-launchpad/Overview). La pagina dei deployment corrente dice che la factory CCA è allo stesso indirizzo su Ethereum, Unichain, Base, Arbitrum, Robinhood Chain e Sepolia, e che le versioni prima della v2.0.0 non vanno più integrate. Factory v2.1.0: `0x000000001F26a0044BaA66024e7b6599c61963F8`. LBPStrategy v3.3.0: Base `0xf10124B01E9fa88b0a2eF3fA95a53B3310446000`, Robinhood Chain `0xbf1aB81f7d534b2CC0Da76fcf4d541322bB0e000`. [Deployments](https://developers.uniswap.org/docs/liquidity/liquidity-launchpad/deployments).

Sulla stessa pagina, InstantLaunchStrategy fa l'opposto dell'asta: mette il gettone subito in una pool v4. Su Robinhood Chain, v3.3.0 con fee al creatore: `0x7c48DDe3B447381F4d986334679b3Afc7F2D35C2`. Un indirizzo Uniswap su queste chain non è, da solo, un'asta.

Quante aste CCA siano aperte oggi su Base o su Robinhood Chain non è scritto in quella pagina. Non lo stimo. L'asta parte quando un team ci impegna supply. Nessuna pagina dei launchpad letti (Pons, o1, Clanker nel lancio normale, Virtuals, Bankr) dice che il gettone passa di lì.

Una pagina più vecchia dello stesso prodotto elenca la factory su Ethereum, Unichain, Base, Arbitrum e Sepolia, e non nomina Robinhood Chain. [docs.uniswap.org Deployments](https://docs.uniswap.org/contracts/liquidity-launchpad/Deployments). Per le chain vale la pagina developers citata sopra, che è quella con la riga Robinhood Chain e con l'indirizzo v2.1.0.

**Doppler.** Il protocollo documenta un'asta on-chain e, dopo, la migrazione della liquidità verso un AMM. [Price discovery auctions](https://docs.doppler.lol/core-concepts/price-discovery-auctions). All'8 ottobre 2026 la pagina dice «last updated 7 months ago». I contratti canonici sono su Base (8453) e su Robinhood Mainnet (4663). Airlock Base: `0x660eAaEdEBc968f8f3694354FA8EC0b4c5Ba8D12`. Airlock Robinhood: `0xeb7c034704ef8dcd2d32324c1545f62fb4ad0862`. [Contract addresses](https://docs.doppler.lol/reference/contract-addresses).

Bankr, che su Base e su Robinhood Chain lancia tramite Doppler, descrive un'altra sequenza: la pool nasce nella stessa operazione e il gettone è subito scambiabile. L'85% della supply va nella pool Uniswap v4; il 15% resta in vesting al creatore. [Overview](https://docs.bankr.bot/token-launching/overview). Non c'è, in quella pagina, una finestra d'asta prima della pool. Quanti lanci Doppler su queste due chain usino invece il percorso «asta, poi migrazione» non si ricava: l'indice pubblico di esempio è su Base Sepolia, e gli endpoint di produzione si chiedono. [Indexer API](https://docs.doppler.lol/reference/api-usage).

## 3. Fuori catena

Whales scrive che, prima del suo contratto, questi scambi passavano da gruppi e messaggi privati, senza impegno di consegna. [About Pre-Market](https://docs.whales.market/pre-market/about-pre-market). Quella pagina non dà un indirizzo, una chain, un libro ordini, né un volume datato di quegli scambi, e non nomina Base né Robinhood Chain. Non è un mercato che si può leggere.

Aevo accoppia ordini fuori dal libro on-chain e regola on-chain, sulla propria L2, per i mercati che apre lei. [Welcome](https://www.aevo.xyz/docs). È il suo mercato, non un OTC dei gettoni di queste due chain.

Non ho trovato una pagina primaria di un libro fuori catena per i gettoni di Pons, Clanker, Flaunch, Bankr, o1 o Virtuals.

La curva di Pons, su Robinhood Chain, è lo scambio prima della pool Uniswap. È on-chain, non è una pretesa e non è un'asta di questo tipo. [v2](https://docs.ponsfamily.com/v2). La prevendita Clanker esiste e non è permissionless: `startPresale()` è `onlyAdmin`. [ClankerPresaleEthToCreator](https://clanker.gitbook.io/documentation/references/core-contracts/v4/extensions/clankerpresaleethtocreator).

---

**COSA USEREI DOMANI.** Niente. Per questi gettoni il primo scambio è la transazione di nascita, sulla curva o sulla pool. Un'asta CCA si guarda solo se un team ha pubblicato l'indirizzo dell'asta: la factory è `0x000000001F26a0044BaA66024e7b6599c61963F8` su Base e su Robinhood Chain.

**COSA NON VALE LA PENA.** Due settimane su Whales, Aevo o Binance Pre-Market in attesa dei gettoni dei launchpad, e due settimane a cercare un libro fuori catena. Whales non ha Robinhood Chain nella tabella delle reti; gli altri aprono loro il mercato, su progetti con un TGE ancora da fare.

Il fascicolo è in `RICERCA_PRELANCIO_mercati_di_pretese_2026-10-08_1600.md`.
