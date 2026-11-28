# Ricerca Grok — 2026-10-08 09:01 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 225s

---

Preparo un fascicolo solo su fonti primarie: per ogni launchpad verifico se prevendita e lista bianca esistono, chi può entrarci, e — solo dove è aperto a chiunque — procedura, capitale minimo e canale di annuncio. Parto dalle pagine ufficiali.Le pagine ufficiali esistono: Clanker ha prevendite con allowlist opzionale, Virtuals documenta sia un modello senza gate sia un Genesis a punti. Ora leggo i contratti e le guide, non i blog.Nessuna di queste piattaforme pubblica una lista bianca a cui ci si iscrive. La prevendita esiste solo su Clanker, e aprirla non è permesso a un wallet qualunque. Sugli altri il token è già in mercato nel momento in cui nasce: si compra, non si viene ammessi.

Lettura delle pagine il 8 ottobre 2026. Dove la pagina non stampa una data di revisione, la data è quella della lettura.

## Chi è su quale catena

| Piattaforma | Dove la documentazione la mette |
|---|---|
| Pons | Solo Robinhood Chain, chain id 4663. [docs.ponsfamily.com](https://docs.ponsfamily.com/) |
| Virtuals | Base e Solana. Nessuna pagina letta cita Robinhood Chain. [FAQ builder, «as of Aug 14, 2026»](https://whitepaper.virtuals.io/info-hub/virtuals-builder-and-agent-token-launch-faq) |
| Clanker | Base, Arbitrum, Monad e «altre EVM». [About](https://clanker.world/about), [introduzione](https://clanker.gitbook.io/documentation) |
| Flaunch | Base (8453) e Robinhood (4663). [API](https://docs.flaunch.gg/references/api) |
| Bankr | Robinhood Chain di default da chat, social e API; Base di default da CLI e form web. Anche Arbitrum e Arc. [Overview](https://docs.bankr.bot/token-launching/overview) |
| o1 | Base (8453) e Robinhood (4663), più Monad, Arc, BSC, X Layer. [Introduction](https://docs.o1.exchange/launchpad/introduction) |
| Robinhood stessa | Non è un launchpad. La chain è permissionless e il gas è ETH. [About](https://docs.robinhood.com/chain/), [articolo chain](https://robinhood.com/us/en/support/articles/robinhood-chain-mainnet/) |

## Chiuse, o non aperte a chiunque

**Clanker, prevendita.** Il contratto `ClankerPresaleEthToCreator` esiste, e la pagina dice testualmente: «This presale is not permissionless. If your team is interested in using this presale, please reach out to the Clanker team.» `startPresale()` è `onlyAdmin`. [Pagina del contratto](https://clanker.gitbook.io/documentation/references/core-contracts/v4/extensions/clankerpresaleethtocreator), aggiornata 3 mesi prima della lettura, pubblicata il 2026-07-01.

Se un prevendita esiste già, l’ingresso dipende dal creatore, non da una domanda pubblica:

- senza modulo allowlist, `buyIntoPresale()` con ETH in `msg.value`;
- con allowlist attiva, `buyIntoPresaleWithProof()` e una prova Merkle della foglia `(address buyer, uint256 allowedEthAmount)`;
- se alla creazione non viene messa una radice Merkle, nessuno può comprare finché il proprietario non fa un’azione;
- il proprietario può spegnere l’allowlist e riaccenderla. Spenta, compra chiunque.

[Allowlist](https://clanker.gitbook.io/documentation/references/core-contracts/v4/extensions/clankerpresaleallowlist). L’elenco delle prevendite è pubblico: `GET https://www.clanker.world/api/presales` ([API presales](https://clanker.gitbook.io/documentation/api-reference/public/presales), base `https://www.clanker.world/api` dalla [introduzione](https://clanker.gitbook.io/documentation)). Non ho trovato un modulo di iscrizione.

Capitale minimo del compratore: la pagina non lo fissa. Il tetto, se c’è, è l’ETH consentito a quell’indirizzo nella foglia, oppure il `maxEthGoal` della singola prevendita. Fee di ingresso e uscita: 0%, stessa pagina. I token della prevendita restano bloccati almeno 7 giorni dopo la creazione del token.

Il lancio normale di Clanker è un’altra cosa: pool subito, descritto come permissionless su [clanker.world/about](https://clanker.world/about). L’airdrop è una Merkle che compila il creatore, non una lista aperta. Il Preclank è un deploy ritardato: si salva una frase e si lancia citando @clanker su Farcaster; dura 7 giorni e richiede login Farcaster o Privy. [Preclank](https://clanker.gitbook.io/documentation/general/token-deployments/preclank-deployments), [API preclank](https://clanker.gitbook.io/documentation/api-reference/user/preclanks). Non è una vendita anticipata per chi compra.

**Pons v2, creare un token.** Il 8 ottobre 2026 la pagina builder dice: «Public launches are closed, so only whitelisted addresses can create a token for now. Check canLaunch(address).» L’errore `NotWhitelisted` significa «Launching is currently restricted to approved addresses.» [docs.ponsfamily.com/v2](https://docs.ponsfamily.com/v2). La stessa pagina dice che v1 continua a operare. Il contatto indicato è contact@ponsfamily.com, per partnership e per l’accesso anticipato agli indirizzi di test, non per farsi mettere in una lista di compratori.

Una volta che un token v2 esiste, la pagina dice «Anyone can buy and sell» sulla curva. Il creatore può esentare dalla tassa di apertura al massimo 32 indirizzi, fissati alla creazione (`ExemptionListTooLong` oltre quel numero). Non è una domanda pubblica: o il creatore ti ha nominato, o paghi la tassa. [Stessa pagina, sezione snipe protection ed exemption](https://docs.ponsfamily.com/v2).

**Robinhood Stock Tokens, mercato primario.** Non è uno dei sei launchpad. L’unica sottoscrizione primaria che Robinhood documenta è questa: solo gli Authorised Participants possono sottoscrivere direttamente da Robinhood Assets (Jersey) Limited, e all’emissione l’unico è BBVI, dopo KYB. [Stock Tokens](https://docs.robinhood.com/chain/stock-tokens/). Sul secondario, dove il prodotto è offerto, è escluso negli Stati Uniti e per le US persons, e la FAQ nomina anche Canada, Regno Unito e Svizzera. L’elenco completo delle giurisdizioni è rinviato a [docs.robinhood.com/rhj](https://docs.robinhood.com/rhj/). [FAQ RHJ](https://docs.robinhood.com/rhj/faq/). Non ho trovato, sulle pagine della chain, una prevendita di un token nativo di Robinhood Chain.

**Virtuals Genesis.** Le pagine Genesis sono ancora online e descrivono un impegno a punti, con tetto 566 $VIRTUAL a wallet e soglia 21.000 $VIRTUAL, finestra di 24 ore. [Meccanica di allocazione](https://whitepaper.virtuals.io/builders-hub/genesis-launch/genesis-allocation-mechanics). Quelle pagine non portano un «vale a ottobre 2026». La FAQ punti è datata 25 agosto 2025 in una copia e 27 maggio 2025 nell’altra. La meccanica che la FAQ builder del 14 agosto 2026 indica come corrente dice altro: vedi sotto. Non ho trovato un avviso che nuovi round Genesis siano in calendario.

## Aperte: si compra, non si viene elencati

In tutte e quattro il capitale minimo del compratore non è pubblicato. C’è il gas della transazione e l’importo che decidi di spendere. I numeri qui sotto sono costi del creatore o tetti della pool, non un biglietto minimo.

**o1, Base e Robinhood.** Il contratto crea il token e la pool Uniswap v4 nella stessa transazione. «Trading begins immediately.» Non c’è prevendita né lista di compratori. [How it works](https://docs.o1.exchange/launchpad/how-it-works), pubblicata il 2026-09-29.

Procedimento: il token compare, si sceglie quanto spendere, si firma lo swap. Sui lanci Standard di Base e Robinhood la fee parte dal 99% e scende all’1% in 20 secondi. Su Arc Standard non c’è quel sovrapprezzo. Il Dev Buy è un acquisto del solo creatore, nella stessa transazione, spento di default. [Introduction](https://docs.o1.exchange/launchpad/introduction).

Fee di creazione, che paga chi lancia: 0,001 ETH su Base e su Robinhood, gas a parte. Verificata il 1 ottobre 2026 sulle factory correnti di tutte e sei le chain. [Live configuration](https://docs.o1.exchange/launchpad/reference/live-configuration). Offerta iniziale documentata: supply fissa 1 miliardo, FDV di apertura vicina a 4.000 USD.

Dove si vede: la home di o1, viste All / Crypto / Stocks, ordinabile per newest. [Pagine dell’interfaccia](https://docs.o1.exchange/launchpad/architecture/frontend-indexer). Gli annunci del registro sono postumi: li pubblica il creatore del token già lanciato, non una vendita in anticipo. [Funzioni dell’AnnouncementRegistry](https://docs.o1.exchange/launchpad/reference/events-functions). Il token di piattaforma $O, nel whitepaper datato giugno 2026, è distribuito senza public sale: è un altro oggetto, e il TGE indicato è giugno 2026. [Whitepaper $O](https://docs.o1.exchange/token/whitepaper).

**Bankr, Robinhood Chain e Base.** «Liquidity pool is created — Your token is immediately tradeable.» [Overview](https://docs.bankr.bot/token-launching/overview), pagina senza data di revisione, letta l’8 ottobre 2026.

Procedimento: pool già aperta, si compra. Per i primi 5 minuti dopo un lancio Doppler non-partner, un wallet non può arrivare a detenere più del 2% della supply: un buy o un transfer che sfora fallisce. I lanci partner sono esenti. A parte c’è una fee anti-snipe che decade in 14 secondi. Il 15% di default in vesting al creatore (1 anno, cliff 30 giorni) non è un’allocazione pubblica.

Dove si vede, dopo il fatto: [bankr.bot/launches](https://bankr.bot/launches) e `GET https://api.bankr.bot/token-launches`, le 50 più recenti, senza autenticazione. [List launches](https://docs.bankr.bot/token-launching/api-reference/list-token-launches). Su X il post di deploy a @bankrbot è l’annuncio, e il trading è già aperto. [Social deployment](https://docs.bankr.bot/guides/social-deployment/). Non c’è una finestra «prima».

Le restrizioni di regione, l’età minima del wallet Bankr (24 ore, interruttore runtime) e l’attesa di 72 ore per chi entra solo con email riguardano chi lancia, non chi compra. Stessa overview.

**Virtuals, percorso corrente.** «Anyone can trade directly through the Virtuals Protocol platform. There are no presales, whitelists, or gated allocations.» [Launch mechanics](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/virtuals-launch-mechanics), pubblicata il 2026-08-25. La FAQ builder del 14 agosto 2026 rimanda a quella pagina.

Procedimento: si apre [app.virtuals.io](https://app.virtuals.io), il token è sulla bonding curve in $VIRTUAL appena l’agente è creato. Se il fondatore ha acceso l’anti-sniper, la tassa parte dal 99% e scende all’1% in una finestra scelta fra 0 secondi, 60 secondi, 10 minuti e 98 minuti; di default solo sugli acquisti. La pool Uniswap nasce quando la liquidità totale raggiunge 42.000 $VIRTUAL. Quel numero è la soglia della curva, non il minimo di un wallet. [Stessa pagina](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/virtuals-launch-mechanics).

In anticipo esiste solo Launch Radar: il fondatore paga 100 $VIRTUAL e il progetto compare nel feed Launch Radar della piattaforma prima che si scambi. Non impegna capitale e non assegna un posto. [Launch Radar](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/launch-radar), pubblicata il 2026-04-09; la fee di 100 $VIRTUAL è ripetuta nella meccanica del 2026-08-25. Il Pre-buy è del solo fondatore, fino al 100% della supply, in creazione, con vesting. [Pre-buy](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/pre-buy-token).

**Pons v1, Robinhood Chain.** Creare il token apre subito la pool WETH, liquidità bloccata, supply 1 miliardo, fee di pool 1%. Fee di lancio del creatore: 0,0005 ETH. Soglia di graduation, che non sposta la pool: 4,2 ETH di default. [docs.ponsfamily.com](https://docs.ponsfamily.com/).

Procedimento del compratore, stessa pagina: nel blocco di lancio può eseguire solo l’acquisto iniziale del creatore. Per il resto della finestra di due blocchi ogni wallet può detenere al massimo il 5% della supply e comprare al massimo il 5,5%. Vendite e trasferimenti non sono limitati. Finita la finestra, il limite cade. Non è una lista: è un tetto uguale per ogni wallet, per due blocchi. La pagina non converte i due blocchi in secondi, e non lo faccio io.

Feed dei lanci già avvenuti, nell’indice ufficiale: `https://www.ponsfamily.com/api/pons-launches`. [llms.txt](https://docs.ponsfamily.com/llms.txt). Non c’è un calendario di prevendite.

**Flaunch.** Due stati diversi, entrambe le pagine sono ufficiali.

Il lancio via API nasce subito. La pagina dice: «Launched immediately; fair launch and sniper protection are currently paused.» Mandare `sniperProtection: true` restituisce 400. Market cap iniziale di default scritta in quella pagina: 10.000 USD in un punto, e nel campo `marketCap` «default: 4,000». Non scelgo io quale dei due sia quello vivo. [API](https://docs.flaunch.gg/references/api). La pagina del fair launch a prezzo fisso, aggiornata 6 mesi prima della lettura, dice ancora «for everyone» e «the first 30 minutes». [Fixed Price Fair Launch](https://docs.flaunch.gg/features/fixed-price-fair-launch). Per un lancio fatto oggi via API, la frase operativa è quella che dice che il fair launch è in pausa: si compra sulla pool, senza finestra e senza captcha.

Game Mode è documentato come attivo su Base e su Robinhood Chain. Durante la finestra si entra solo giocando: il punteggio diventa un’autorizzazione firmata a spendere fino a un massimo, nel token di quotazione, e un tetto per wallet fissato a quel lancio. Prima dell’orario di apertura ogni swap fallisce. Scaduta la finestra, il trading è permissionless. [Game Mode](https://docs.flaunch.gg/game-mode/game-mode), aggiornata 27 giorni prima della lettura. Il minimo spendibile non è un numero di protocollo: è ciò che il punteggio autorizza, sotto il `walletCapWei` di quel lancio. [Spend gate](https://docs.flaunch.gg/references/spend-gate).

Il calendario del creatore, su flaunch.gg, mostra orari a passi di 5 minuti per le 24 ore successive. Serve a non sovrapporre le partite, non a raccogliere nomi. [Launch calendar](https://docs.flaunch.gg/game-mode/launch-calendar). Lo stesso meccanismo di firma può essere pilotato da una allowlist se qualcuno costruisce un signer con quella regola: la pagina del signer elenca «were you on the allowlist» come regola possibile, accanto al punteggio di gioco. [Trusted signer](https://docs.flaunch.gg/references/spend-gate/signer). Game Mode, come descritto, usa il punteggio.

## Cosa sembra una lista e non lo è

La «allowlist» di Bankr è l’elenco dei token con cui si può quotare la pool (BNKR, azioni tokenizzate, e altri), non dei compratori. [List quote tokens](https://docs.bankr.bot/token-launching/api-reference/list-launch-quote-tokens). Le 32 esenzioni di Pons v2 e il Dev Buy di o1 sono indirizzi scelti dal creatore prima del primo blocco. Il tetto del 2% di Bankr e i due blocchi di Pons v1 valgono per ogni wallet.

---

**COSA USEREI DOMANI.** Per comprare da subito, senza domanda: o1 e Bankr (pool già viva; su Bankr il 2% per 5 minuti), Virtuals sulla curva in $VIRTUAL, Pons v1 dopo i due blocchi, Flaunch sulla pool. Per vedere un progetto prima dello scambio, l’unico feed documentato è Launch Radar di Virtuals, e non assegna un posto.

**COSA NON VALE LA PENA.** Cercare un form di whitelist su questi sei, chiedere l’accesso creator di Pons v2 per comprare, o pianificare due settimane su Genesis o su una prevendita Clanker: la prima non è il percorso che la FAQ del 14 agosto 2026 indica come corrente, la seconda si apre solo se il team Clanker te la abilita.
