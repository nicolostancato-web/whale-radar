# Ricerca Grok — 2026-10-08 12:24 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 610s

---

La domanda parla di «queste cose» senza nominarle. Prima cerco nel fascicolo e nel lavoro già fatto qual è l’oggetto, così le fonti che raccolgo sono quelle giuste.Il fascicolo è una serie di ricerche sul prelancio. Leggo le ultime e il brief, così «queste cose» ha un oggetto preciso.La domanda continua il fascicolo sui prelanci: dove un programma legge, da solo, che una prevendita o un lancio sta per aprire. Verifico le pagine ufficiali, non il riassunto di ieri.Il calendario di Flaunch e le API dei lanci sono postumi o chiusi. Adesso verifico i tre posti dove un orario potrebbe essere scritto prima dello scambio: prevendita Clanker, finestra di Flaunch, radar di Virtuals.Il campo che conta su Flaunch è `flaunchAt`: un orario futuro scritto nella transazione di creazione. Controllo se esiste un evento con quel nome, poi chiudo il fascicolo.Non esiste un bollettino, aperto a chiunque, che elenchi questi lanci prima della transazione che li crea. Un programma lo viene a sapere quando quella transazione è già accettata. L'unica cosa che la transazione può contenere, e che apre un intervallo vero prima dello scambio, è un orario futuro scritto dentro. Oggi è documentato in un solo posto, con un nome solo.

Lettura dell'8 ottobre 2026. Costo: zero.

## 1. Flaunch: `flaunchAt`

Il parametro di lancio si chiama `flaunchAt`. È un unix timestamp. Fino a quell'istante il token non si scambia. Se c'è una fair launch, la sua finestra parte da quel timestamp, non dalla transazione. Il valore non può superare `block.timestamp` più 30 giorni. [SDK, pagina pubblicata il 2026-06-01](https://docs.flaunch.gg/guides/flaunching-a-coin).

Lo stesso campo chiude Game Mode. Un acquisto prima dell'apertura revoca con `TokenNotFlaunched`, e la pagina dell'hook dice che quel revert esce dal `flaunchAt` del lancio, nel `PositionManager`. [Hook, 2026-09-10](https://docs.flaunch.gg/references/spend-gate/hook-path). La pagina di Game Mode, stessa data, dice che l'orario di apertura è scritto nella pool. [Game Mode](https://docs.flaunch.gg/game-mode/game-mode). Game Mode è documentato come attivo su Robinhood Chain e su Base.

La scadenza del gate è un secondo numero, `endsAt`, e deve stare entro `MAX_GATE_DURATION` (30 giorni) dal lancio. [Spend gate](https://docs.flaunch.gg/references/spend-gate). I due «30 giorni» sono tetti diversi. Non li ho sommati.

Non ho trovato un evento il cui solo scopo sia pubblicare i lanci futuri, né il nome di una funzione di lettura. Il programma lo vede decodificando la transazione di creazione, o leggendo lo stato dopo che è inclusa. Prima di quella transazione, la documentazione non dà nulla.

La strada HTTP è più stretta. `POST /api/v1/{{ base | base-sepolia | robinhood }}/launch-memecoin`, pagina del 2026-09-04, dice: «Launched immediately; fair launch and sniper protection are currently paused.» Un `fairLaunchDuration` diverso da zero torna 400. [API](https://docs.flaunch.gg/references/api). Quella pagina non dice se `flaunchAt` sia accettato. `GET /api/v1/launch-status/{{ jobId }}` è la coda del tuo job, non i lanci degli altri.

Due pagine del 2026-07-23 descrivono ancora l'orario futuro come opzione del prodotto, senza un endpoint: [Launch a Token](https://docs.flaunch.gg/getting-started/flaunch-a-coin) e [What Is Flaunch?](https://docs.flaunch.gg/getting-started/why-flaunch).

Il calendario di Game Mode non è un'interfaccia di programmazione. È il selettore di chi crea: passi di cinque minuti per le 24 ore successive, un hold di dieci minuti mentre il modulo è aperto. Nessun URL da chiamare. I lanci fatti fuori da flaunch.gg non ci entrano. [Launch calendar, 2026-09-15](https://docs.flaunch.gg/game-mode/launch-calendar).

`GET https://dev-api.flayerlabs.xyz/v1/:chain/tokens/new` elenca token già creati. Le chain scritte lì sono `base` e `base-sepolia`. Nessuna autenticazione. La pagina non fissa un tetto e raccomanda 100–200 ms fra le richieste. [REST Data API](https://docs.flaunch.gg/references/restful-data-api). Il subgraph nomina solo Base Mainnet, id `bbWLZuPrmoskDaU64xycxZFE6EvSkMQALKkDpsz5ifF`, e l'endpoint si interrompe a `https://gateway.thegraph.com/api/`. [Subgraph](https://docs.flaunch.gg/references/subgraph).

Sulla durata della fair launch le pagine non concordano, e la strada API dice che è spenta. [Fair launch, 2026-03-17](https://docs.flaunch.gg/features/fixed-price-fair-launch): «i primi 30 minuti». [Sniper, 2026-08-07](https://docs.flaunch.gg/features/sniper-protection): «5 minutes by default». Non scelgo quale sia viva.

## 2. Clanker: la prevendita, dopo che è partita e prima del token

`GET https://www.clanker.world/api/presales` è pubblico. Parametri: `sort`, `limit` (default 100), `offset`, `chainId`, `status`. La tabella di `status` è rotta: nel tipo compaiono un numero, `"all"` e `"successful"`. La risposta documentata è `{ "presales": [ ... ], "totalCount" }`. I campi dentro un elemento non sono pubblicati. [Presales](https://clanker.gitbook.io/documentation/api-reference/public/presales). L'indice che li dichiara pubblici è del 2026-07-02. [Public API](https://clanker.gitbook.io/documentation/api-reference/public).

L'8 ottobre una GET verso quel host non è partita da questa macchina: il certificato TLS non corrispondeva al nome. Non ho un record vivo, e non invento i campi.

Su catena, `PresaleStarted` porta `presaleId`, `presaleDuration`, `presaleOwner`, `lockupDuration`, `vestingDuration`, `clankerFeeBps`. `PresaleDeployed` porta il token ed è successivo. [SDK, 2026-07-08](https://clanker.gitbook.io/documentation/sdk-reference/extensions). L'unità di `presaleDuration` non è scritta. Non la converto. La pagina del contratto, 2025-12-03, dice che la prevendita non è permissionless. [ClankerPresaleEthToCreator](https://clanker.gitbook.io/documentation/references/core-contracts/v4/extensions/clankerpresaleethtocreator). Quelle pagine non stampano l'indirizzo del contratto: senza, i log non si filtrano per address. L'HTTP non ne ha bisogno.

Con un `presaleId` già noto, `GET /api/presales/allowlists` è pubblico e restituisce radice Merkle e allocazioni. È la lista di una prevendita già indicizzata.

`GET /api/preclank/pending` restituisce solo i preclank dell'utente autenticato (Farcaster o Privy), attivi 7 giorni. [Preclanks, 2026-06-30](https://clanker.gitbook.io/documentation/api-reference/user/preclanks). Il deploy scatta col cast su Farcaster che tagga @clanker. [Preclank Deployments, 2026-07-01](https://clanker.gitbook.io/documentation/general/token-deployments/preclank-deployments). `GET /api/tokens` elenca token già deployati. Nell'indice pubblico non c'è un websocket delle prevendite.

## 3. Il resto è il momento in cui succede

**Virtuals.** «Once the agent is created, trading opens automatically.» Niente prevendite né liste. [Launch mechanics](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/virtuals-launch-mechanics). La FAQ, «as of Aug 14, 2026», rimanda lì. [FAQ](https://whitepaper.virtuals.io/info-hub/virtuals-builder-and-agent-token-launch-faq). Launch Radar è ancora descritto come un feed nell'interfaccia, 100 $VIRTUAL, senza URL, senza schema, senza minuti di anticipo. [Launch Radar, 2026-04-09](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/launch-radar). L'indice del whitepaper non ha una pagina di API. [llms.txt](https://whitepaper.virtuals.io/llms.txt). Le curve da indicizzare, per vedere il lancio quando nasce: Base `0x1A540088125d00dD3990f9dA45CA0859af4d3B01`, Robinhood Chain `0xd4cCBFA37e2f35611b3042e4096Ad7a3459Bd007`. [Contract addresses](https://whitepaper.virtuals.io/info-hub/important-links-and-resources/virtuals-protocol-contract-addresses).

**Bankr.** «Your token is immediately tradeable.» [Overview](https://docs.bankr.bot/token-launching/overview). `GET https://api.bankr.bot/token-launches` è senza chiave e restituisce le 50 creazioni più recenti, già `deployed`. [List launches](https://docs.bankr.bot/token-launching/api-reference/list-token-launches). I webhook sono HTTP in entrata verso un agente tuo, non il flusso dei lanci altrui. [Webhooks](https://docs.bankr.bot/webhooks/overview/).

**o1.** «Trading begins immediately.» Sui lanci Standard di Base, Robinhood, Monad, BSC e X Layer la fee scende in 20 secondi e lo scambio resta aperto. Pagina del 2026-10-02. [How it works](https://docs.o1.exchange/launchpad/how-it-works). L'evento si chiama `Launched`. Gli annunci li posta il creatore del token già registrato. [Events, 2026-09-29](https://docs.o1.exchange/launchpad/reference/events-functions). `GET https://api.launch.o1.exchange/v1/tokens` richiede `x-api-key`; una chiave self-service è il piano Developer, due chiavi attive. [Authentication, 2026-09-25](https://docs.o1.exchange/launchpad/api/authentication). Tetti, 2026-09-29: 300 unità al minuto, 25.000 al giorno, 500.000 al mese. Una lista costa 2 unità. [Limits](https://docs.o1.exchange/launchpad/api/errors-and-limits). Su quelle pagine non c'è un prezzo in euro. Lo «Sniper Order» è un tipo di ordine nel terminale, senza un elenco di lanci futuri. [Trading](https://docs.o1.exchange/features/trading).

**Pons, chain id 4663.** «There is no pons API in the trust path. Index the factory and the curves.» L'evento è `TokenLaunched`. [v2](https://docs.ponsfamily.com/v2). Factory v2 `0x7eD598BcEf8bd9Edd8C97A195C6d13f40801EC7e`, factory v1 `0xA5aAb3F0c6EeadF30Ef1D3Eb997108E976351feB`. Il feed `https://www.ponsfamily.com/api/pons-launches` è un indice di lanci, non un calendario. [llms.txt](https://docs.ponsfamily.com/llms.txt). La tassa che parte dal 99% dura 5 secondi dal lancio.

**Robinhood Chain.** Il tubo più presto è il feed del sequencer, `wss://feed.mainnet.chain.robinhood.com`. Il backup sta circa 500 ms indietro. L'RPC pubblico non ha un tetto numerico su quella pagina. [Connecting](https://docs.robinhood.com/chain/connecting). I termini del 24 agosto 2026 dicono che può essere strozzato senza preavviso. [Terms](https://docs.robinhood.com/chain/terms-of-service/). È l'arrivo della transazione, in ordine di arrivo. [About](https://docs.robinhood.com/chain/). Non contiene un lancio che nessuno ha ancora inviato.

Il fascicolo è in `RICERCA_PRELANCIO_prima_che_succedano_2026-10-08.md`.

**COSA USEREI DOMANI.** Decodificare le creazioni Flaunch e leggere `flaunchAt`: è l'unico orario futuro, su catena, con un nome e un tetto. In parallelo, `GET https://www.clanker.world/api/presales` senza chiave, per le prevendite già partite e non ancora deployate.

**COSA NON VALE LA PENA.** Il calendario di flaunch.gg, Launch Radar, le liste di Bankr, o1 e Pons, i preclank altrui, e il feed del sequencer come se fosse un annuncio. Sono uno schermo senza URL, il lancio già avvenuto, o la transazione stessa.
