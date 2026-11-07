# Ricerca Grok — 2026-10-06 08:20 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 377s

---

Preparo un fascicolo solo con fonti primarie: prima verifico se Base ha una distribuzione ufficiale, poi quali protocolli pubblicano requisiti prima dello snapshot e quali li decidono dopo.La posizione ufficiale di Base è cambiata nel 2025: da «niente token» a «esplorazione, senza criteri». Ora verifico i programmi con numeri scritti prima, e quelli decisi solo a consuntivo.Al 6 ottobre 2026 un indirizzo su Base non ha una checklist ufficiale per una distribuzione gratuita. Base e Coinbase non hanno pubblicato numero di operazioni, valore mosso, età del portafoglio, gettoni da tenere o protocolli da usare per un token di rete. L'unica rubrica numerica che ha contato l'attività su Base è un airdrop di OP già chiuso, con le soglie uscite a finestra scaduta. L'unica soglia ancora scritta prima dell'azione chiede capitale bloccato, e non è gratuita.

Fonti lette il 6 ottobre 2026. Solo testi di chi organizza la distribuzione.

## Il token di rete non ha requisiti, perché non ha un programma

Tre testi, in ordine.

Nel post di lancio per i builder, [Base Mainnet is Open for Builders](https://blog.base.org/base-mainnet-is-open-for-builders), la frase è: «Base has no plans to issue a network token.» Il blog lo colloca al 13 luglio, subito prima del post del 9 agosto sull'apertura pubblica (2023). La stessa frase è in [Path to Base Mainnet](https://blog.base.org/path-to-base-mainnet).

Il 15 settembre 2025 il testo cambia e si ferma. [The State of Base at BaseCamp 2025](https://blog.base.org/the-state-of-base-at-basecamp-2025): «Base is beginning to explore a network token. […] we have no definitive plans to share at this time. […] don’t have any specifics to share around timing, design, or governance.» Lo stesso giorno Brian Armstrong: [«there are no definitive plans»](https://x.com/brian_armstrong/status/1967602534601875734). Il post avvisa che non è un'offerta di vendita di un token.

[Base 2026 Mission, Vision, and Strategy](https://blog.base.org/2026-mission-vision-and-strategy) elenca mercati, pagamenti e builder. Non nomina un token di rete e non pubblica una soglia. Il corpo della pagina non mostra una data. Il 14 gennaio 2026 Armstrong scrive della Base App e non aggiunge criteri: [post](https://x.com/brian_armstrong/status/2011521034394976690).

Nel Form 10-K di Coinbase per l'esercizio chiuso il 31 dicembre 2025, file SEC del 12 febbraio 2026, Base è la chain da cui Coinbase «generates revenue from sequencer fees paid each time a transaction is processed on the Base blockchain.» [Filing](https://www.sec.gov/Archives/edgar/data/1679788/000167978826000015/0001679788-26-000015.txt). In quella descrizione non ci sono un token di rete e un elenco di idoneità.

Quello che queste fonti non contengono: data di snapshot, formula, minimo di transazioni, minimo in dollari, età del wallet, elenco di protocolli. Non si può avere, e non lo stimo.

I fondi gratuiti nella documentazione di Base sono faucet di testnet. Il faucet del Coinbase Developer Platform dà fino a 0,1 ETH ogni 24 ore su Base Sepolia. [Pagina](https://docs.base.org/base-chain/network-information/network-faucets). È ether di prova.

I premi per chi costruisce (verifica di un'app, Base Batches) sono domande di team. Il post di strategia 2026 cita builder code, incentivi di liquidità e programmi per chi porta utenti e volume. Non pubblica una checklist sull'indirizzo di un utente. [Rewards](https://docs.base.org/apps/growth/rewards).

## L'unica rubrica che ha contato Base è chiusa, e i numeri sono usciti dopo

È un airdrop di OP, non un token di Base. Base c'era perché era nella lista delle chain.

Criteri: [Airdrop 5](https://community.optimism.io/op-token/airdrops/airdrop-5). Data di chiusura e claim: [app.optimism.io/airdrops/5](https://app.optimism.io/airdrops/5). Discussione sul forum ufficiale, 10 ottobre 2024: [thread](https://gov.optimism.io/t/airdrop-5-feedback-thread/9008).

| Regola | Soglia | Quando |
| --- | --- | --- |
| Contratti distinti toccati da un EOA (campo `to`) | almeno 20 | 15 marzo 2024 00:00 UTC – 15 settembre 2024 00:00 UTC |
| Rapporto contratti / transazioni | almeno 10%. Esempio ufficiale: 25 contratti e 100 transazioni-app = 25% | stessa finestra |
| Premio calcolato | sotto 50 OP l'indirizzo è escluso | — |
| Transazione-app | transazione con un log, escluse le approval ERC-20/721/1155 e il wrap/unwrap di WETH | stessa finestra |
| Tipo di indirizzo | solo EOA | — |
| Chain contate | OP Mainnet, Base, Zora, Mode, Metal, Fraxtal, Cyber, Mint, Swan, Redstone, Lisk, Derive, BOB, Xterio, Polynomial, Race, Orderly | — |
| Esito pubblicato | 10.368.678 OP a 54.723 indirizzi | insieme ai criteri |

Il premio base «scale in proportion to network usage». La pagina non pubblica il coefficiente (OP per transazione, o per contratto). Quel numero non è nel testo.

Bonus, stessa finestra, stesse due pagine:

- almeno 9.000 di (OP delegati × giorni)
- almeno 10 transazioni-app a settimana in almeno 20 settimane
- almeno 1 transazione-app su almeno 7 chain
- almeno 1 transazione-app su almeno 3 chain nella prima settimana dopo il mainnet pubblico di ciascuna
- almeno 1 Optimism quest tra il 20 settembre 2022 e il 17 gennaio 2023
- almeno 5 missioni SuperFest tra il 9 luglio 2024 e il 3 settembre 2024
- mint da almeno 3 contratti registrati ai SUNNYs

L'app scrive: «Eligibility details for Airdrop #5 were locked in on 2024-09-15». I numeri, nelle fonti ufficiali, descrivono un periodo già chiuso. Non ho trovato un documento Optimism anteriore al 15 settembre 2024 che indicasse «20 contratti» come obiettivo. Il claim sull'app scadeva l'8 ottobre 2025. La pagina docs dice ancora «needs to be claimed»: è indietro rispetto alla data sull'app.

Quella rubrica non chiedeva età del wallet, né un saldo minimo in dollari, né un gettone specifico. L'eccezione è il bonus delegator, che chiede OP già delegati.

Caso più stretto, stessa famiglia: [Airdrop 4](https://community.optimism.io/op-token/airdrops/airdrop-4). Aver pubblicato un contratto NFT (ERC-721 o ERC-1155) su Base, OP Mainnet o Zora prima del 10 gennaio 2024 00:00 UTC. Sulla Superchain: 5.000 OP per 1 ETH di gas speso, nei 365 giorni prima del cutoff, nelle transazioni che trasferivano quegli NFT. 9.294 indirizzi per quella riga. Anche qui i criteri descrivono una finestra già chiusa.

## Dal 23 agosto 2026 quel serbatoio non è più un airdrop agli utenti

Proposta della Optimism Foundation, 6 agosto 2026: [Re-designating the User Airdrop Allocation as the Strategic Ecosystem Fund](https://gov.optimism.io/t/re-designating-the-user-airdrop-allocation-as-the-strategic-ecosystem-fund/10797).

Nel testo: cinque airdrop già fatti e 269,1 milioni di OP distribuiti; saldo non speso, 546,9 milioni di OP. Frase della Foundation: «no airdrops currently planned». Aggiunge che non è un verdetto permanente: se uscisse un disegno nuovo, rivaluterebbe. Chiede di togliere i token da «a purpose the Collective no longer pursues».

Voto eseguito il 23 agosto 2026 alle 7:30: [proposta](https://vote.optimism.io/proposals/71046981157786379776549698790429169615693449771144448151464817786433292182423). FOR 17.973.915, AGAINST 10.930.696, quorum 16.540.389, soglia 51%, stato EXECUTED. La pagina dice «No substantive onchain transactions»: è una riassegnazione dell'allocazione, non un trasferimento in quella proposta.

Uso scritto del fondo nuovo: accordi con chain, protocolli, istituzioni e infrastruttura; incentivi su attività e liquidità di OP Mainnet; accordi con istituzioni e marchi. Nessuna soglia per un indirizzo su Base. La rendicontazione prevista è il rapporto annuale di budget, non una formula pubblicata prima.

Non esiste un documento «Airdrop 6» con criteri. La pagina [OP Token Overview](https://community.optimism.io/op-token/op-token-overview) parla ancora di airdrop futuri «#5, 6, …» e di un 14% in riserva: elenca l'Airdrop 5 come futuro, quindi è anteriore al voto del 23 agosto 2026.

La cittadinanza nel Citizens' House non paga. FAQ della Season 8: «No, being a Citizen is no longer associated with any financial rewards, airdrops, points, or retroactive voter rewards.» [FAQ](https://community.optimism.io/citizens-house/faq-citizenship).

## Regole scritte prima: una finestra è chiusa, l'altra chiede capitale

### SuperStacks. Formula pubblica all'apertura, conversione in OP dopo. Chiuso.

Annuncio del 16 aprile 2025: [SuperStacks](https://optimism.io/blog/superstacks-a-new-approach-to-rewards-on-the-superchain). Finestra scritta quel giorno: 16 aprile – 30 giugno 2025. Frase dello stesso post: «Earning points does not guarantee earning OP tokens or any other reward. The program’s design, eligibility criteria and rewards structure will likely evolve over time.»

Formula, sulla pagina del programma: [SuperStacks](https://community.optimism.io/op-token/superstacks). 10 XP per ogni dollaro che resta 24 ore in una pool qualificata, per ogni pool. Gli XP partono dopo le prime 24 ore. L'elenco delle pool poteva allungarsi durante il programma. Il tasso OP per XP sarebbe stato annunciato alla fine.

Consuntivo, dopo: [SuperStacks Allocation](https://community.optimism.io/op-token/superstacks-allocation). 2.500.000 OP a 6.387 indirizzi, per attività dal 16 aprile 2025 16:00 UTC al 30 giugno 2025 23:59 UTC su Base, Unichain, Ink, World, Soneium e OP Mainnet. Sotto 20 OP l'indirizzo è escluso. Esempi su Base, dalla tabella: liquidità Uniswap v4 ETH/USD₮0 (0,05%) e USD₮0/USDC (0,01%), almeno 0,01 dollari per almeno un'ora. La FAQ dice che gli OP non ritirati entro un anno tornano al tesoro. Non ho una data ufficiale di apertura del claim, quindi al 6 ottobre 2026 non affermo che il claim sia ancora aperto.

Il requisito leggibile prima era la liquidità in una pool della lista, tenuta nel tempo. Non c'erano età del wallet né un conteggio di transazioni. Il valore era in dollari depositati, non in volume scambiato. La conversione in gettoni, il 16 aprile 2025, era esplicitamente non garantita.

### Aerodrome Flight School. Soglia ancora descritta come attiva. Non è gratuita.

Testo della pagina, al presente, il 6 ottobre 2026: [Flight School](https://aerodrome.finance/flight-school).

- Ogni quattro settimane, un bonus in veAERO.
- Serve un lock nuovo di almeno 2.500 veAERO dentro la classe di quattro settimane.
- Il bonus della classe si divide in proporzione al veAERO che qualifica. La pagina scrive «up to 15%» e l'esempio è una quota del monte: chi ha il 5% del veAERO qualificante riceve il 5% del bonus. Mi fermo a quella frase.
- I lock di un membro Coinbase One pesano 1,3 volte. La stessa pagina lo chiama anche un boost del 30% e chiede un wallet verificato. L'abbonamento non si legge dall'indirizzo su Base.

veAERO non equivale ad AERO. Dalla documentazione: 100 AERO bloccati 4 anni diventano 100 veAERO; 100 AERO bloccati 1 anno diventano 25 veAERO. [Docs](https://aerodrome.finance/docs), file [tokenomics.mdx](https://github.com/aerodrome-finance/docs/blob/main/content/tokenomics.mdx). Per 2.500 veAERO servono 2.500 AERO se il lock dura quattro anni, e 10.000 AERO se dura un anno. È la curva pubblicata.

Nello stesso documento l'allocazione iniziale di Flight School è 50 milioni di veAERO, il 10% della supply iniziale. È il budget di genesi, non il residuo di oggi. La pagina cita anche «over 42.6 million AERO» distribuiti dal 2023, senza data: non la uso.

Le emissioni ordinarie vanno a chi deposita liquidità e la mette in gauge, in proporzione ai voti veAERO dell'epoca. Un'epoca va dal giovedì 00:00 UTC al mercoledì 23:59 UTC. [Docs](https://aerodrome.finance/docs). Non c'è una soglia di transazioni, di età o di volume. C'è un deposito. Lo schedule di lancio (10 milioni di AERO la prima settimana, poi +3% per 14 epoche, poi −1% a epoca) è in quel documento: non è la quantità dell'epoca in corso, che la pagina non data, e quindi non riporto.

L'airdrop iniziale a chi aveva veVELO (200 milioni, 40%) è una riga della genesi 2023, nello stesso file. È chiuso.

Non ho passato in rassegna i programmi punti delle singole app su Base. Sono un altro oggetto: quasi sempre un saldo interno, con il diritto di conversione tenuto da chi li emette. L'unico di cui ho, nelle pagine di chi pagava, formula, diniego scritto e consuntivo in OP è SuperStacks, ed è chiuso.

## Prima o dopo

Pubblico prima, e ancora descritto come aperto: il lock da 2.500 veAERO, il peso 1,3× per Coinbase One verificato, e le emissioni Aerodrome a chi mette liquidità in gauge. Pagano chi impegna capitale.

Pubblico prima, finestra chiusa: SuperStacks, 10 XP per dollaro ogni 24 ore, dal 16 aprile 2025, con il diniego che gli XP diventassero OP.

Pubblicato a finestra già chiusa: le soglie dell'Airdrop 5 (20 contratti, rapporto 10%, minimo 50 OP) e dell'Airdrop 4 (contratto NFT prima del 10 gennaio 2024). Il coefficiente in OP dell'Airdrop 5 non è nel testo dei criteri.

Discrezionale, o noto solo a consuntivo: il tasso OP per XP di SuperStacks; l'uso del Strategic Ecosystem Fund, che si legge nel rapporto annuale; un token di rete Base, di cui non ci sono tempi, disegno, governance, né criteri.

Nessuna di queste fonti fissa un'età minima del portafoglio su Base.

COSA USEREI DOMANI: niente, sull'indirizzo, per qualificarmi. L'unica soglia numerica ancora scritta prima dell'azione è un lock nuovo di almeno 2.500 veAERO su Aerodrome, e il bonus va a chi blocca capitale suo.
COSA NON VALE LA PENA: transazioni, volume o anzianità del wallet su Base in attesa di un airdrop. La checklist del token di rete non esiste; l'unica rubrica che ha contato l'attività su Base è l'Airdrop 5 di OP, chiusa il 15 settembre 2024, e il 23 agosto 2026 i 546,9 milioni di OP rimasti in quel serbatoio sono stati riassegnati.
