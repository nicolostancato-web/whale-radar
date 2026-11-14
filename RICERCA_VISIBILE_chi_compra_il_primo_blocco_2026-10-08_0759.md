# Ricerca Grok — chi_compra_il_primo_blocco

Modello grok-4.7. Costo: ZERO (abbonamento, nessuna chiave API). Tempo: 153s. 2/2 sotto-domande con risposta.

---

### Robinhood Chain ha un mempool pubblico o le transazioni passano da un sequencer privato? Col link alla documentazione.

Cerco nella documentazione ufficiale di Robinhood Chain come vengono ordinate le transazioni: mempool pubblico o sequencer privato.La documentazione ufficiale parla di sequencer e di ordering first-come-first-served. Verifico se dice esplicitamente che non esiste un mempool pubblico.Le transazioni passano da un sequencer gestito da Robinhood. Non c’è un mempool pubblico di transazioni in attesa, come su Ethereum.

L’ordine è first-come, first-served: conta l’arrivo al sequencer, e una priority fee più alta non scavalca nessuno. Lo scrive la documentazione ufficiale nella sezione *Predictable Transaction Ordering*: [About Robinhood Chain](https://docs.robinhood.com/chain/).

Chi gestisce quel nodo è Robinhood (RHDA, LLC). Nei Terms of Service, sezione 2.1, il sequencer è il servizio che riceve, registra e riporta le transazioni: [Robinhood Chain Terms of Service](https://docs.robinhood.com/chain/terms-of-service/).

Due precisazioni utili:

* **L’endpoint di invio è pubblico.** Chiunque può mandare una transazione a `https://sequencer.mainnet.chain.robinhood.com`, oppure via RPC pubblico. “Privato” vale per la coda prima dell’ordine, non per il permesso di inviare. Endpoint: [Connecting to Robinhood Chain](https://docs.robinhood.com/chain/connecting).
* **Dopo l’ordine c’è un feed pubblico**, `wss://feed.mainnet.chain.robinhood.com`. Pubblica transazioni già sequenziate, non un mempool di tx ancora in coda. I nodi ci si agganciano da qui: [Run a full node](https://docs.robinhood.com/chain/run-a-full-node/).

La soft confirmation arriva dal sequencer in meno di un secondo; l’ordine diventa fisso solo quando il batch è pubblicato su Ethereum: [Transaction Finality](https://docs.robinhood.com/chain/transaction-finality/).

La frase “no public mempool” non compare testualmente nei docs di Robinhood. È il modello Arbitrum Nitro / Orbit su cui la chain è costruita, e lo ripetono gli operatori di infrastruttura (bloXroute, Chainstack).

### Come si riesce tecnicamente a comprare nel blocco stesso del lancio di una moneta su una chain EVM? Elenca i modi documentati, con i link.

Ti elenco i modi documentati per finire nello stesso blocco del lancio su una chain EVM. Prima verifico i link ufficiali aggiornati, così non ti passo documentazione vecchia.Nello stesso blocco ci entri solo se il builder o il sequencer inserisce la tua swap **dopo** che la liquidità esiste già. Il blocco è una lista ordinata: stessa altezza senza quell’ordine fa revertire lo swap, perché la pool non c’è ancora o ha riserve a zero.

Ci sono quattro modi documentati. I primi due fissano anche la posizione. Gli altri due ti fanno solo entrare nel blocco.

## 1. Sei tu che lanci: tutto in una transazione

Una transazione EVM esegue le chiamate interne in ordine, e o va a buon fine tutta o non lascia nulla. È l’unico modo in cui l’acquisto è nello stesso blocco **e** attaccato alla creazione della pool, senza dipendere dal builder.

Su Uniswap v4 il Universal Router esegue in sequenza, nella stessa `execute`:

- `V4_INITIALIZE_POOL` (0x13)
- `V4_POSITION_MANAGER_CALL` (0x14), la liquidità iniziale
- `V4_SWAP` (0x10), l’acquisto

Documentazione: [comandi del Universal Router](https://developers.uniswap.org/docs/protocols/universal-router/concepts/commands), [creare pool e liquidità in una `multicall`](https://docs.uniswap.org/contracts/v4/quickstart/create-pool), [atomicità di una transazione](https://ethereum.org/en/developers/docs/transactions/).

Su v2 non esiste un comando unico nel router ufficiale. Il pattern documentato è un contratto tuo che, nella stessa chiamata, fa `createPair`, `addLiquidity` e `swap`. Riferimenti: [Router02](https://docs.uniswap.org/contracts/v2/reference/smart-contracts/router-02).

## 2. Bundle atomico verso un block builder

Un bundle è una lista di transazioni firmate che il builder esegue nell’ordine indicato, senza infilarci transazioni estranee in mezzo. O entra tutto il bundle, o non entra niente. È il meccanismo con cui, su Ethereum e su BNB Chain, si compra nel blocco del lancio anche se il lancio non è tuo.

Due usi:

- **Lancio tuo, tenuto privato.** Mandi `[crea pool / aggiungi liquidità, tuo buy]`. Finché quel bundle non è nel blocco, la transazione non sta nel mempool pubblico.
- **Lancio altrui, già visibile.** Mandi `[tx di lancio già firmata, tua swap]`. La tua swap sta subito dopo la liquidità. Se la tx di lancio non entra, il bundle intero viene scartato e non paghi il gas della swap fallita.

Il builder sceglie il bundle che gli rende di più (priority fee più pagamento diretto). Se più searcher puntano la stessa tx di lancio, nel blocco ne entra uno solo.

Documentazione Ethereum:

- [Cos’è un bundle e perché l’ordine è quello della lista](https://docs.flashbots.net/flashbots-auction/advanced/understanding-bundles)
- [eth_sendBundle e mev_sendBundle](https://docs.flashbots.net/guide-send-tx-bundle)
- [Come si prezza un bundle](https://docs.flashbots.net/flashbots-auction/advanced/bundle-pricing)
- [Asta Flashbots, il motivo per cui il bundle ha sostituito la guerra di gas](https://docs.flashbots.net/flashbots-auction/overview)
- [Builder API / MEV-Boost, chi costruisce davvero il blocco](https://github.com/ethereum/builder-specs)

Stesso `eth_sendBundle`, endpoint dei builder:

- [beaverbuild](https://beaverbuild.org/docs.html) — `https://rpc.beaverbuild.org/`
- [Titan](https://docs.titanbuilder.xyz/api/eth_sendbundle) — `https://rpc.titanbuilder.xyz`
- [bloXroute su Ethereum](https://docs.bloxroute.com/eth/submit-bundles/bundle-submission) — `blxr_submit_bundle`

Su BNB Chain il builder dominante documentato è 48 Club Puissant. `eth_sendBundle` accetta `backrunTarget`: il builder prepende lui la tx bersaglio. L’asta è descritta nell’auction feed (ti arrivano hash, log e state diff, e tu rispondi col bundle).

- [Send Bundle](https://docs.48.club/puissant-builder/send-bundle)
- [Auction Transaction Feed](https://docs.48.club/puissant-builder/auction-transaction-feed)
- [bloXroute su BSC](https://docs.bloxroute.com/bsc/submit-bundles/bsc-bundle-submission), inoltra a `48club`, `blockrazor`, `jetbldr`, `nodereal`
- [Come viene ordinato e pagato il bundle su BSC](https://docs.bloxroute.com/bsc/submit-bundles/bundle-mechanics-and-fees)

## 3. Backrun su ordine privato (MEV-Share / BackRunMe)

Se chi lancia manda la transazione a un RPC privato che condivide degli hint, un searcher può agganciare un buy **solo dopo** quella transazione. Il protocollo rifiuta i frontrun.

- [MEV-Share: il nodo accetta solo backrun](https://docs.flashbots.net/flashbots-mev-share/introduction)
- [Quali campi della tx vengono mostrati](https://docs.flashbots.net/flashbots-protect/settings-guide)
- [Invio del bundle di backrun](https://docs.flashbots.net/flashbots-mev-share/searchers/sending-bundles)
- [Esempio guidato di backrun](https://docs.flashbots.net/flashbots-mev-share/searchers/tutorials/limit-order/introduction)
- [bloXroute BackRunMe](https://docs.bloxroute.com/backrunme-program/overview): stesso schema, tx privata → stream anonimizzato → bundle di solo backrun

Se il lancio è un bundle privato che non pubblica hint, dall’esterno quella transazione non è agganciabile. Il primo acquisto possibile è nel blocco successivo.

## 4. Stesso blocco senza posizione garantita

Qui finisci nel blocco, ma la posizione rispetto alla tx di lancio la decide la fee o l’ordine di arrivo, non tu.

**Mempool pubblico e priority fee.** Il builder ordina per quanto viene pagato. Una fee più alta della tx di lancio può metterti prima della liquidità: lo swap revertisce. Flashbots descrive questo limite come il motivo dell’asta sui bundle: [overview](https://docs.flashbots.net/flashbots-auction/overview).

**Base.** Il sequencer chiude un flashblock ogni 200 ms e ordina per priority fee al momento in cui seleziona le transazioni. Due transazioni possono stare nello stesso blocco da 2 secondi. Non esiste, nella spec, un modo per dire “subito dopo questa tx”.

- [Flashblocks](https://docs.base.org/base-chain/flashblocks/overview)
- [Transaction ordering](https://docs.base.org/specifications/transactions/transaction-ordering)

**Arbitrum (Timeboost).** Il mempool è privato fino al sequencing. L’express lane dà 200 ms di vantaggio a chi ha vinto l’asta del round, ma non dà il diritto di riordinare né di leggere le tx altrui. Non è un backrun: al massimo coincidi col lancio se la mandi nello stesso intervallo.

- [Come funziona Timeboost](https://docs.arbitrum.io/how-arbitrum-works/timeboost/gentle-introduction)
- [Come vengono ordinate le tx express nel blocco](https://docs.arbitrum.io/how-arbitrum-works/timeboost/troubleshoot-timeboost)

In sintesi: su Ethereum e BNB Chain la posizione “subito dopo il lancio” è un bundle. Sulle L2 con sequencer il blocco condiviso è una corsa di fee o di latenza, e l’ordine interno non lo scegli tu.
