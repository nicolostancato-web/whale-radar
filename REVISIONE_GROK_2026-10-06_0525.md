# Revisione Grok — 2026-10-06 05:25 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 406s

---

La domanda è da dove arrivano i gettoni venduti senza un acquisto visibile. Cerco i meccanismi reali su Base e sulla chain robinhood, solo con fonti verificabili.Il dato batte con i lanci, non con un mercato parallelo. Apro la documentazione dei launchpad che su queste due chain mettono i gettoni nei portafogli prima dello swap pubblico.La direzione va chiusa. Quei gettoni non arrivano da una distribuzione pubblica a cui ci si iscrive: sulla chain dove il fenomeno è più forte si comprano su un altro contratto, e sulle due chain si spostano fra portafogli oppure restano l'allocazione del creatore. Quando acquisto e vendita sono entrambi nel vostro indice e i quantitativi tornano, il multiplo mediano è già 1,05X e 0,99X.

Il fatto che misurate è vero, e ha una forma precisa. Una fetta compra sul mercato che indicizzate e non vende. Una fetta comparabile vende senza un acquisto visibile lì. Fra le posizioni con entrambi i lati, la vendita precede l'acquisto nel 18,5% dei casi su Base e nel 28,8% su Robinhood, e i gettoni venduti superano quelli comprati di 1,61 e 2,11 volte. Il sottoinsieme pulito è piccolo, 785 e 535 posizioni, e non ha vantaggio.

Questa forma è quella di un costo pagato fuori dall'indice, non quella di un gruppo che riceve i gettoni gratis e sa quando venderli. Il divario fra le due chain indica dove guardare. Al 5 ottobre 2026, secondo MemeFees su dati DefiLlama, Pons raccoglieva il 92,9% delle fee dei launchpad di Robinhood Chain (116 milioni di dollari in 30 giorni, oltre 416.000 lanci). Su Base le fee sono spaccate fra o1 (39,1%), Bankr (29,0%) e Clanker (21,8%), e il launchpad più grande mette l'intera supply nel pool. Robinhood è peggio di Base perché lì il mercato precedente al pool è obbligatorio.

Ho scartato il resto dopo averlo aperto. o1, il launchpad più grande di Base e attivo anche su Robinhood, mette l'intero miliardo di supply nella liquidità permanente di Uniswap v4 e paga i dividendi nell'asset di quotazione, non nel gettone. La prevendita di Clanker esiste ed è precedente al mercato, ma la documentazione dice che non è permissionless e i gettoni restano bloccati almeno 7 giorni dopo la creazione del mercato. Non ho trovato un mercato fuori catena, un'asta o un secondario con una pagina propria che tratti queste monete nei minuti in cui nascono.

## 1. La curva di Pons, prima del pool

Documentazione: [pons v2](https://docs.ponsfamily.com/v2). Factory `0x7eD598BcEf8bd9Edd8C97A195C6d13f40801EC7e`, chain id 4663. La stessa forma, su pad minori, è quella di [Virtuals](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/virtuals-launch-mechanics) su Base e della [finestra a prezzo fisso di Flaunch](https://docs.flaunch.gg/features/fixed-price-fair-launch).

L'intera supply nasce nel contratto della curva. Si compra chiamando la curva e pagando l'asset di quotazione, ETH oppure un token approvato. I gettoni arrivano nel portafoglio con l'evento `CurveBuy(buyer, recipient, quoteIn, tokensOut, fee, tax)`. A graduazione la curva chiude, il ricavato e la quota tenuta da parte diventano un pool Uniswap v4 con liquidità bloccata, e i gettoni già in portafoglio restano gli stessi. Chi li vende dopo, sul pool, ha un acquisto vero che un indice di soli swap Uniswap non vede. La documentazione lo scrive: il lancio scambia in due posti, prima sulla curva e poi nel pool.

Non c'è un orologio. La fase dura dal blocco di creazione fino all'acquisto che esaurisce `sellableTokens()`. Può essere un blocco, o non arrivare mai. La soglia di ogni lancio è nel campo `graduationThreshold` dell'evento `TokenLaunched`; la guida Bitquery indica 4,2 ETH per i lanci quotati in ETH. I primi 5 secondi portano una tassa sull'acquisto che parte al 99% e va a zero. La vendita non è mai tassata da quella finestra.

Comprare è aperto a chiunque abbia l'asset di quotazione. Non serve invito né storia sulla chain. Lanciare è un'altra cosa: `canLaunch(address)` può essere chiuso e limitato a indirizzi in lista. Partecipare come acquirente significa pagare. È il ruolo che, nel vostro sottoinsieme pulito, rende circa 1X.

Il dato è pubblico prima di qualunque vendita sul pool. `TokenLaunched` sulla factory dà token, curva, deployer e soglia. `CurveBuy` e `CurveSell` sulla curva sono lo storico completo degli scambi, e la documentazione dice che bastano questi log per ricostruire il protocollo senza un servizio di Pons. L'esploratore della chain è [robinhoodchain.blockscout.com](https://robinhoodchain.blockscout.com).

C'è un privilegio, e non è un omaggio. All'indirizzo che lancia e al destinatario delle fee, più fino a 32 indirizzi passati nell'argomento `snipeTaxExemptions`, la tassa dei primi 5 secondi non si applica. La lista è fissata nella transazione di creazione e non si può allungare. Quei portafogli pagano comunque il prezzo della curva. Esserci richiede che il creatore vi nomini: è una scelta sua, non un requisito pubblico. Il router `launchAndBuy` esegue creazione e primo acquisto nella stessa transazione, così quell'acquisto non è front-runningabile; se il parser salta gli swap interni alla transazione di lancio, quell'unico portafoglio sembra aver ricevuto i gettoni.

Su Base la stessa cosa è più piccola. Virtuals fa scambiare sulla propria curva fino a 42.000 VIRTUAL e solo allora apre un pool Uniswap v2, senza prevendita né whitelist. Flaunch tiene una finestra, documentata a 30 minuti, in cui tutti pagano lo stesso prezzo fisso, e il creatore può comprare una parte prima che la finestra sia pubblica. Nessuno dei due è fra i primi launchpad di Base per fee.

## 2. L'allocazione del creatore, che si sblocca col mercato già aperto

Documentazione: [Bankr, supply e vesting](https://docs.bankr.bot/token-launching/overview). Bankr è il secondo launchpad di Base per fee e lancia, via Doppler, anche su Robinhood. Il contratto tiene da parte il 15% e mette l'85% nel pool Uniswap v4. Il 15% è preassegnato al destinatario delle fee, di default chi lancia, in un escrow: niente per 30 giorni, poi sblocco continuo fino a un anno. Il claim sposta i gettoni nel portafoglio senza uno swap. Da lì la vendita è un vendita senza acquisto, e il quantitativo può superare di molto qualunque acquisto successivo sullo stesso portafoglio.

Si ottiene solo essendo quel destinatario, scelto alla creazione e non riassegnabile. Disattivare il vesting è possibile, e in quel caso il 100% va nel pool. Non c'è una lista aperta, un capitale minimo che qualifichi, né una storia sulla chain che dia diritto alla quota. I primi 5 minuti un portafoglio non può superare il 2% della supply: è un tetto sugli acquisti, non un'assegnazione.

Il destinatario e le condizioni sono nella transazione di lancio, trenta giorni prima del primo gettone vendibile. Il trasferimento di claim è pubblico nel blocco in cui avviene.

Clanker, terzo su Base, può fare la stessa cosa in modo più largo e meno usato. Fino al 90% della supply può andare a estensioni invece che al pool ([deploy](https://clanker.gitbook.io/documentation/general/token-deployments)): un [vault](https://clanker.gitbook.io/documentation/references/core-contracts/v4/extensions/clankervault) per un solo admin, bloccato almeno 7 giorni; un [airdrop](https://clanker.gitbook.io/documentation/references/core-contracts/v4/extensions/clankerairdrop) con radice di Merkle di `(indirizzo, quantitativo)`, bloccato almeno 1 giorno. Senza estensioni, il 100% va nel pool. L'admin del vault è leggibile nella transazione di deploy. Dell'airdrop sulla chain c'è solo la radice: gli indirizzi non si ricostruiscono, compaiono al `claim()`, e la pagina di deploy diceva ancora che l'interfaccia non lo esponeva. Il dev buy di Clanker e quello di o1 sono acquisti veri, eseguiti dentro la transazione di lancio; sembrano un omaggio solo se quel passaggio non viene decodificato.

La [prevendita Clanker](https://clanker.gitbook.io/documentation/references/core-contracts/v4/extensions/clankerpresaleethtocreator) è l'unico meccanismo davvero precedente al mercato, e la sua stessa pagina dice di contattare il team: non è permissionless. L'ETH raccolto va al creatore, non nel pool. I gettoni dei compratori restano bloccati almeno 7 giorni dopo l'apertura del mercato. L'eventuale lista è una radice di Merkle, aggiornabile dal creatore, e non è pubblica.

Virtuals aggiunge un caso che tocca molti portafogli e pesa poco sul totale. Dopo la graduazione, [Hyperboost](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/virtuals-launch-mechanics) distribuisce per 14 giorni una quota residua a chi ha scambiato e a chi ha pubblicato contenuti sul gettone. Si reclama senza vincolo. È un gettone ricevuto senza comprarlo. Virtuals non è fra i pad che fanno il volume di Base, quindi non regge una fetta vicina alla metà delle posizioni.

Su Pons il creatore non riceve una borsa alla partenza. La documentazione dice che nessuno, creatore compreso, tiene gettoni messi da parte prima dell'apertura degli scambi. Le sue fee arrivano nell'asset di quotazione. I riacquisti opzionali sono gettoni bloccati e rilasciati lungo cinque anni, non un saldo vendibile al lancio.

## 3. Il trasferimento fra due portafogli

È il `Transfer` di [ERC-20](https://eips.ethereum.org/EIPS/eip-20), su entrambe le chain. Non c'è una piattaforma.

Un portafoglio compra sul mercato che indicizzate e manda i gettoni a un secondo portafoglio. Il primo resta «comprato e mai venduto». Il secondo vende senza alcun acquisto. Se il secondo vende e più tardi compra, la vendita precede l'acquisto. Se oltre al trasferimento compra anche un po' sul mercato indicizzato, i gettoni venduti superano quelli comprati. È l'unico meccanismo che produce, per costruzione, le due fette comparabili sullo stesso gettone. Può avvenire nel blocco successivo all'acquisto, o molto dopo. Non è precedente al mercato: sposta una posizione già pagata.

Ricevere non ha requisito, perché non c'è niente a cui iscriversi: decide il mittente. Inviare richiede di avere già i gettoni. Nessuna delle due cose crea un gettone non pagato da qualcuno.

Il `Transfer` è pubblico nel blocco in cui avviene, quindi prima della vendita del destinatario. Si vede chi ha ricevuto e da chi. Non esiste un campo «stesso proprietario». Due portafogli finanziati dallo stesso indirizzo sono un'inferenza, e la chain non la certifica.

## Cosa farne

Il test che separa i tre casi è uno solo, e i log ci sono già. Per ogni posizione venduta senza acquisto, la provenienza del saldo è un `CurveBuy` precedente, un `Transfer` da un indirizzo che non è pool né curva, oppure un claim dall'escrow di Bankr o dal vault di Clanker. La prima voce spiega il divario di Robinhood. La seconda spiega la simmetria comune alle due chain. La terza è poca e ha nome e cognome dal blocco di lancio.

Nessuna delle tre è una porta. La prima si compra, e il sottoinsieme in cui vedete entrambi i lati rende 1X. La seconda sposta un acquisto già fatto. La terza è di chi ha lanciato la moneta.
