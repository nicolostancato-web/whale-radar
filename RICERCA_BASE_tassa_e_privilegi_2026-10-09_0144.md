# Ricerca Grok — Base — tassa_e_privilegi

Modello grok-4.7. Costo: ZERO (abbonamento). Tempo: 412s. 2/2 con risposta.

---

### Sulle piattaforme di lancio di Base esiste una tassa sui primi secondi dopo il lancio (anti-sniper)? Percentuale e durata, col link.

Cerco sulle piattaforme di lancio di Base se esiste una tassa anti-sniper nei primi secondi, con percentuale, durata e fonte ufficiale.La documentazione di Clanker parla di una fee discendente. Verifico i numeri ufficiali e se le altre launchpad di Base usano lo stesso meccanismo.Sì. Sulle launchpad principali di Base c’è una fee anti-sniper che parte altissima e scende da sola. Non è una regola della chain: ogni piattaforma ha numeri diversi.

**Clanker** (è il motore dietro Bankr e la maggior parte dei token lanciati su Base). La configurazione raccomandata parte da una fee effettiva dell’**80%** e scende in modo parabolico al **5% in 30 secondi**. Poi vale la fee normale della pool. Chi lancia può accorciare o allungare la discesa, al massimo fino a **2 minuti**, con una fee LP iniziale fino all’80%. Su Base la discesa parte dopo l’asta anti-sniper: gli swap dell’asta pagano già la fee iniziale.

- Docs: [ClankerMevDescendingFees](https://clanker.gitbook.io/documentation/references/core-contracts/v4/mev-modules/clankermevdescendingfees)
- Annuncio: [Clanker v4.1 sniper tech](https://paragraph.com/@clankerworld/clanker-v4_1-sniper-tech)

In pratica molti deploy (compresi quelli Bankr) usano **15 secondi** invece di 30. È una scelta di chi lancia, non il default dei docs.

**Zora Coins** (creator, content e trend, su Base). Fee al **99%** che scende in modo lineare fino alla fee base in **10 secondi**. Creator e content arrivano all’**1%**. I trend coin arrivano allo **0,01%**.

- [Protocol rewards / Sniper Tax](https://docs.zora.co/coins/contracts/rewards)

**Virtuals** (lancio di agent). Tassa d’acquisto al **99%** che scende all’**1%**. Il founder sceglie la finestra: **60 secondi**, **10 minuti** o **98 minuti** (circa −1% al minuto). Di default è solo sul buy. Si può spegnere (0 secondi).

- [Anti-Sniper Protection](https://whitepaper.virtuals.io/about-virtuals/capital-formation-layer/anti-sniper-protection)

**Flaunch** non usa questa tassa. Ha un fair launch a prezzo fisso di 30 minuti, con tetto per wallet e verifica anti-bot.

### Esistono indirizzi esentati da quella tassa, o posizioni privilegiate concesse al creatore? Col link.

Cerco nel contesto della sessione a quale tassa ti riferisci e se risultano esenzioni o privilegi per il creatore.Il filo è la tassa anti-sniper e gli indirizzi esentati. Leggo i documenti già scritti e la fonte ufficiale.La domanda è sulla tassa anti-sniper dei launchpad di Base. Verifico sulla documentazione ufficiale se esistono esenzioni o privilegi per il creatore.Sì. Sulle tre piattaforme che si dividono i lanci su Base l’esenzione dalla tassa dei primi secondi, quando c’è, è una sola operazione del creatore. La posizione privilegiata vera è un’assegnazione di gettoni che non passa dal mercato.

**o1, su Base.** La tassa parte dal 99% e scende all’1% in 20 secondi. L’unica esenzione documentata è il Dev Buy: un acquisto del creatore, spento di default, eseguito dentro la transazione di lancio. Paga l’1% ordinario e non paga il sovrapprezzo anti-sniper. Vale solo per quell’acquisto. Gli acquisti successivi seguono il calendario del pool. Non c’è un elenco di indirizzi esentati. Tutta la fornitura (1 miliardo) entra nel pool: il creatore non riceve gettoni a parte. Incassa il 50% della fee ordinaria dell’1%, cioè lo 0,5% del volume. Il sovrapprezzo sopra l’1% va alla piattaforma.

Fonte: [Fees, anti-snipe, and referrals](https://docs.o1.exchange/launchpad/trading/fees-referrals). Il Dev Buy è nello stesso paragrafo e in [How it works](https://docs.o1.exchange/launchpad/how-it-works).

**Bankr (Doppler), su Base.** La fee di scambio parte dall’80% e torna alla fee normale in 14 secondi. La documentazione non pubblica indirizzi esentati da quella fee: al creatore dice di aspettare almeno 15 secondi e poi comprare. A parte c’è un tetto, non una tassa: nei primi 5 minuti un portafoglio non può superare il 2% della fornitura. I lanci partner, inclusi i portafogli provisioned, sono esenti da quel tetto.

La posizione del creatore è un pre-assegnato: il 15% della fornitura (100 miliardi) va al destinatario delle fee e si sblocca in un anno, con i primi 30 giorni bloccati. Non è uno scambio, quindi non paga la fee dell’80%. Si può spegnere al lancio (`disableVesting: true`): allora il 100% entra nel pool. I lanci con Partner Key vendono già il 100% e non hanno questo vesting.

Fonte: [FAQ, anti-snipe e tetto del 2%](https://docs.bankr.bot/faq/token-launching) e [Creator vesting](https://docs.bankr.bot/token-launching/overview).

**Clanker.** Non c’è una tassa percentuale che scende. C’è un’asta: al massimo 5 round, uno ogni 2 blocchi, e lo scambio ordinario apre dopo circa 22 secondi oppure appena un round resta senza offerte. Nessuna lista di indirizzi esentati da quell’asta. Il creatore può, dentro la transazione di deploy, comprare per primo dal pool (Dev Buy). Può anche tenere fino al 90% della fornitura fuori dal pool: un caveau con minimo 7 giorni, oppure un airdrop a una lista che compila lui, con minimo 1 giorno.

Fonte: [Token Deployments](https://clanker.gitbook.io/documentation/general/token-deployments) e [ClankerSniperAuctionV0](https://clanker.gitbook.io/documentation/references/core-contracts/v4/mev-modules/clankersniperauctionv0).
