# Ricerca Grok — 2026-10-06 07:40 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 214s

---

Preparo un fascicolo con sole fonti primarie: prima verifico se Base e le chain EVM minori hanno programmi scritti per chi usa i ponti e per chi opera prima che esista una moneta.Le guide secondarie parlano di un token Base «in esplorazione» e di airdrop già chiusi. Cerco le pagine ufficiali: se le regole scritte non esistono, il fascicolo deve dirlo subito.Non esiste, al 6 ottobre 2026, un programma scritto con cui un indirizzo si qualifica per un gettone di Base, né per un gettone di Ink, di Soneium o di Arc, facendo ponti o altre operazioni. L’unico programma di ponte che ha regole scritte e ha già pagato un gettone è deBridge, e le due stagioni con regole pubblicate sono chiuse. Una stagione successiva, con data, percentuale e tasso di conversione, non risulta negli annunci della Foundation fino al 2 ottobre 2026.

## Base: esplorazione, zero regole

Base ha scritto, nel post di BaseCamp 2025, che sta iniziando a esplorare un gettone di rete e che non ha piani definitivi né dettagli su tempi, disegno o governance. Il post dice anche che non è un’offerta di vendita. I post più vecchi («no plans to issue a network token») sono precedenti a questo cambio di posizione.

- Testo: [The State of Base at BaseCamp 2025](https://blog.base.org/the-state-of-base-at-basecamp-2025)
- Versione precedente, superata da quel post: [Path to Base Mainnet](https://blog.base.org/path-to-base-mainnet) e [Base Mainnet is Open for Builders](https://blog.base.org/base-mainnet-is-open-for-builders)

Una ricerca sul blog ufficiale per post del 2026 che contengano «network token», «airdrop» o «eligibility» non ha restituito una pagina nuova con criteri. Il profilo di [@base](https://x.com/base), letto il 30 settembre 2026, ripete ancora la frase del 2025: «Base is beginning to explore a network token.»

Quello che non si può avere, perché non è stato pubblicato: quante operazioni contano, quale valore, per quanto tempo, e una pagina per controllare un indirizzo. Senza una lista di eleggibilità, un controllo è impossibile.

## Chain EVM minori: tre chiusure scritte

**Ink (Kraken).** La FAQ ufficiale risponde a «Wen TGE?» con «There is no information to share at this moment regarding any token from Ink» e a «Wen Airdrop» con «There is no information to share at this moment regarding any airdrop». Nessuna soglia, nessun checker. [FAQ](https://docs.inkonchain.com/faq).

**Arc (Circle).** Due testi ufficiali convivono e vanno letti insieme. La pagina del whitepaper, ancora online, scrive: «No ARC token has been launched» e «No decision has been made regarding whether a native token… will be developed, deployed, or made available.» [Pagina ARC](https://www.arc.io/arc-token-whitepaper). Il comunicato Circle del 16 settembre 2026 dice un’altra cosa sul piano tecnico: nella stessa settimana Circle ha completato negli Stati Uniti il mint di genesi dell’intera fornitura iniziale, 10 miliardi di ARC, e aggiunge che questo mint «is not a commitment to publicly launch ARC». Le fee restano in USDC; un passaggio a proof-of-stake è indicato come esplorazione per il 2027. [Comunicato](https://www.circle.com/pressroom/circle-launches-arc-mainnet-an-economic-operating-system-for-the-internet). Non c’è una regola pubblica che leghi ponti o uso della chain a una quota di quei 10 miliardi, e non c’è un checker.

I punti di Arc House sono un’altra cosa, e il contratto lo chiude. I termini del programma Architects, gestito da Circle Technology Services LLC, sezione 8, aggiornati al 25 marzo 2026 (la pagina risulta toccata il 21 luglio 2026), dicono che i punti sono promozionali, non hanno valore monetario, non si convertono in contanti, USDC o altra valuta virtuale, e «will not be converted into any form of legal tender or any future rewards». [Termini](https://community.arc.io/public/resources/architects-terms-and-conditions).

**Soneium (Sony Block Solutions Labs).** Il programma di attività è finito. Il 29 luglio 2026 Soneium ha scritto che la Season 12 è l’ultima: chi ha uno score di almeno 80 riceve un badge soulbound, non trasferibile. Sopra 84 si entra nel primo turno di mint; tra 80 e 83 nel secondo. Le date di mint non sono nel post: rimanda al portale. Il post non scrive che i badge diventano un gettone, né pubblica un tasso o un checker per una moneta. [Chiusura](https://soneium.org/en/blog/soneium-score-season-closure/). I termini, in vigore dal 28 agosto 2025, dicono che lo score è calcolato con una metodologia a sola discrezione di Sony Block Solutions Labs Pte. Ltd. e che la ricompensa scritta è il badge. [Termini dello Score](https://docs.soneium.org/docs/tos/tos-score).

La FAQ sviluppatori che dice «Currently, there are no plans for a native token» è la FAQ del testnet Minato e descrive ancora il mainnet come non uscito. Non la uso come politica attuale del mainnet. [FAQ Minato](https://docs.soneium.org/docs/builders/faq).

Robinhood Chain, nei documenti ufficiali, indica ETH come gas e non pubblica un programma di gettone della chain né un checker. [Gas e fee](https://docs.robinhood.com/chain/gas-and-fees/), [About](https://docs.robinhood.com/chain/). Non ho trovato una frase ufficiale del tipo «non ci sarà mai un gettone».

## L’unico ponte con regole scritte: deBridge, stagioni chiuse

Lo gestiscono due soggetti. Il conteggio dei punti è nel prodotto deBridge. Le distribuzioni del gettone DBR le fa la deBridge Foundation, foundation delle Cayman. DBR è un token Solana: [DBRiDgJAMsM95moTzJs7M9LnkGErpbv9v6CUR1DXnUu5](https://solscan.io/token/DBRiDgJAMsM95moTzJs7M9LnkGErpbv9v6CUR1DXnUu5).

La pagina punti, letta il 6 ottobre 2026, dice questo e non altro:

- 100 punti per ogni 1 dollaro di fee pagate al protocollo.
- Chi referenzia e chi integra prende il 25% dei punti generati dagli utenti portati. L’auto-referral non conta.
- A fine stagione i punti si convertono in DBR. Il tasso si annuncia quando la stagione chiude. La data di fine stagione si annuncia sui social, non è nella pagina.
- Non c’è un minimo di ponti, un minimo di valore trasferito, né una durata di detenzione. Conta la fee, non il numero di transazioni.

[Regole punti](https://docs.debridge.com/home/monetization/debridge-points).

Le due stagioni con numeri pubblicati sono finite.

| | Season 1 | Season 2 |
|---|---|---|
| Chi è dentro | Chi aveva punti prima dello snapshot | Chi aveva un saldo punti della Season 2 |
| Snapshot / finestra | 23 luglio 2024, 21:00 UTC | Claim dal 19 novembre 2025, 12:00 UTC, al 19 dicembre 2025, 12:00 UTC. Dopo quella data il claim è chiuso |
| Quanto DBR | 6% della supply; 1,5 miliardi di punti accumulati al momento dell’annuncio | 300 milioni di DBR, cioè il 3% di 10 miliardi, a più di 770.000 utenti |
| Fonte | [Eleggibilità S1](https://docs.debridge.foundation/faq-airdrop-season-1/eligibility-season-1), [overview](https://docs.debridge.foundation), [annuncio checker](https://debridge.foundation/blog/introducing-the-debridge-foundation-and-the-dbr-checker/) | [Claim S2](https://debridge.foundation/blog/debridge-points-season-2-claim-is-live/), conferma di chiusura nel [resoconto di gennaio 2026](https://debridge.foundation/blog/debridge-foundation-update-2025/) |

Per un indirizzo già usato: il checker storico è [debridge.foundation/checker](https://debridge.foundation/checker). I punti correnti, secondo la documentazione, si vedono collegando il wallet su [explorer.debridge.com/statistic](https://explorer.debridge.com/statistic). Non ho collegato un wallet a quelle due pagine, quindi non confermo che il 6 ottobre 2026 restituiscano ancora un saldo.

Quello che non si può avere: l’esistenza di una Season 3 con percentuale, tasso e data. Negli aggiornamenti della Foundation di luglio, settembre e del 2 ottobre 2026 che ho letto non c’è un annuncio di una nuova stagione. La pagina prodotto continua a descrivere il meccanismo «a fine stagione», senza nominare la stagione aperta.

## Il ponte più usato ha scritto che non ci sarà un altro airdrop

LayerZero, il 3 giugno 2026, scrive che i 183 milioni di ZRO della Foundation ancora bloccati fino al mainnet di Zero «will be used conservatively to grow the LayerZero ecosystem, and there are no plans for a future airdrop». [The ZRO Token](https://layerzero.network/blog/the-zro-token). Da aprile 2026 il 100% dei ricavi di Stargate va all’acquisto di ZRO, non a una nuova distribuzione a chi fa il ponte. Lo stesso post. Il fee switch del protocollo è rimasto spento: il referendum n. 4, 20–27 giugno 2026, non ha raggiunto il quorum. [Pagina del voto](https://layerzero.foundation/fee-switch), [esito](https://x.com/LayerZero_Fndn/status/2070680813910557120).

MegaETH non è più una finestra «prima che la moneta nasca»: $MEGA è stato lanciato il 30 aprile 2026, dopo una soglia di 10 app MegaMafia raggiunta il 23 aprile. [Annuncio](https://www.megaeth.com/blog-news/mega-is-live).

Orbiter pubblica ancora una pagina O-Points, «last updated 1 year ago»: i punti vanno all’indirizzo di partenza, le transazioni sulla stessa chain non contano, e l’importo è «calcolato in modo dinamico e mostrato in pagina». La pagina non dice che quei punti diventano un gettone, e non pubblica una cifra fissa per ponte o per dollaro. [O-Points](https://docs.orbiter.finance/faq/o-points).

**COSA USEREI DOMANI.** Per un indirizzo che ha già usato deBridge, aprirei solo [il checker](https://debridge.foundation/checker) e [la pagina punti](https://explorer.debridge.com/statistic). Non aprirei ponti nuovi in attesa di una stagione che non ha regole pubblicate.

**COSA NON VALE LA PENA.** Farmare Base, Ink, Soneium o i punti Arc House, e rifare ponti su LayerZero o Stargate per un secondo airdrop: i testi ufficiali non contengono una qualificazione, oppure dicono che i punti non si convertono, oppure che un altro airdrop non è previsto.
