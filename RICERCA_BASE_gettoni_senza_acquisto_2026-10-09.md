# Da dove arrivano, su Base, i gettoni venduti senza un acquisto visibile

*9 ottobre 2026. Nodo pubblico, zero euro: `https://base.gateway.tenderly.co`. Nessuna chiave.*

## La chiusura

Su o1 — il launchpad che mette tutta la fornitura nel mercato — un gettone venduto da un indirizzo che non risulta averlo comprato non esce da una curva, da un pre-mine o da una lista. Esce dal PoolManager di Uniswap v4, in uno scambio già avvenuto, e arriva a chi vende passando da un altro firmatario.

La quota di questo fenomeno sul 32% del 5 ottobre non si può avere. Nessun launchpad pubblica «quante vendite sono di chi non ha mai comprato». L'unico nodo pubblico che il 9 ottobre ha accettato la ricerca rifiuta `eth_getLogs` oltre 1.000 blocchi. In questa cartella non c'è uno storico Base da riattraversare. L'API v1 di Basescan risponde che l'endpoint è deprecato; una chiave non è stata usata.

## 1. Su o1 il gettone nasce già nel pool

Documentazione o1, letta il 9 ottobre 2026 ([How it works](https://docs.o1.exchange/launchpad/how-it-works)): fornitura fissa di 1 miliardo, creata una volta sola. I contratti di lancio aprono il pool Uniswap v4 e ci mettono l'intera fornitura, in liquidità permanente. La posizione di lancio non si può togliere. I gettoni si muovono fra il pool e i portafogli con gli scambi.

Il Dev Buy, se il creatore lo accende, è un acquisto nella stessa transazione di lancio. Le fee Standard e le quote Tax (creatore, protocollo, integratore, dividendi) sono nell'asset di quotazione, non nel gettone lanciato. I gettoni raccolti per il burn si possono mandare all'indirizzo morto; chi li manda non viene pagato. Lo staking è un caveau a parte, e il lancio non lo crea.

Contratti su Base, chain id 8453, dalla [pagina dei contratti di produzione](https://docs.o1.exchange/launchpad/reference/production-contracts.md). Le quote della factory Standard sono state rilette al blocco 52.020.531 l'1 ottobre 2026.

| Contratto | Indirizzo |
|---|---|
| Factory Standard | `0x1176122eb77AD6a2339322Cda7C4D7ea9BfA63dC` |
| Hook di lancio | `0x1f91c998e7c2F4b690D75BDBf6502BDcD6e02AcC` |
| PoolManager v4 | `0x498581fF718922c3f8e6A244956aF099B2652b2b` |
| Universal Router | `0x6fF5693b99212Da76ad316178A184AB56D299b43` |

Gli stessi PoolManager e Universal Router sono nella tabella Base di Uniswap, chain 8453 ([deployments](https://developers.uniswap.org/docs/protocols/v4/deployments)). Il PoolManager di Robinhood, sulla pagina o1, è un altro contratto: `0x8366a39CC670B4001A1121B8F6A443A643e40951`, chain id 4663.

Su un gettone o1, chi vende senza aver comprato tiene gettoni che qualcun altro ha già tirati fuori da quel PoolManager.

## 2. Lo scambio non scrive chi tiene il gettone

Nell'interfaccia del PoolManager l'evento `Swap` indica come `sender` «l'indirizzo che ha iniziato la chiamata di swap e che ha ricevuto la callback» ([IPoolManager.sol](https://github.com/Uniswap/v4-core/blob/main/src/interfaces/IPoolManager.sol)). Il destinatario del gettone non è nell'evento. Lo paga `take(currency, to, amount)`: `to` lo sceglie chi ha sbloccato il manager, di solito il router.

Il conteggio del 5 ottobre attribuisce la posizione a `tx.from`, il firmatario della transazione esterna (`agents/iniziatori.py`, `eth_getTransactionByHash`). È un fatto del nostro codice, non della chain.

ERC-4337 funziona così: l'utente manda una UserOperation; un bundler la impacchetta in una transazione che chiama `handleOps` sull'EntryPoint. `tx.from` è il bundler. Il campo `sender` della UserOperation è lo smart account ([ERC-4337](https://eips.ethereum.org/EIPS/eip-4337)). L'EntryPoint v0.6 pubblicato da eth-infinitism, tag `v0.6.0`, è `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789` ([deployments/mainnet/EntryPoint.json](https://github.com/eth-infinitism/account-abstraction/blob/v0.6.0/deployments/mainnet/EntryPoint.json)). Il 9 ottobre, su Base, quell'indirizzo è il `to` delle vendite sotto.

## 3. Il 9 ottobre la vendita più frequente della finestra andava a quell'EntryPoint

Testa al blocco **52.355.376**. Ultimi 40 blocchi: 128 eventi Swap v4. Campione: **11 vendite** di gettoni non maggiori, su 11 coppie distinte.

In **5 di quelle 11 righe** `tx.to` è `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789` e `tx.from` non è l'indirizzo che ha mandato il gettone. Due righe sono la stessa transazione e lo stesso indirizzo, su due gettoni: **4 transazioni, 4 indirizzi**. Il bundler `0x1278c1e48e3c9548a5d9f2b16dc27ed311b0697c` firma tre righe, cioè due transazioni. Non gli ho dato un nome di prodotto: non l'ho cercato.

| Blocco | Vendita | Chi manda il gettone | Chi firma (`tx.from`) |
|---|---|---|---|
| 52.355.340 | [`0x80247410…c9dcf5d9`](https://basescan.org/tx/0x802474109380a06b4e2fd51af36b8119cf9cf75a8754179f07646799c9dcf5d9) | `0x58fb5894c01f54e33ba6534a759b18fd3fb7cb16` | `0x1278c1e4…b0697c` |
| 52.355.341 | [`0x5fe60859…b4a2f675`](https://basescan.org/tx/0x5fe60859ed095b17b84a7a74f67e7757b8ec79e3d767db472587d45fb4a2f675) | `0x4f6f91599858bf0d19fabcf2c5d591fe13f7c059` | `0xbdbebd58cc8153ce74530bb342427579315915b2` |
| 52.355.349 | [`0x4570d7fd…43bb1e82`](https://basescan.org/tx/0x4570d7fd6503add48e3cf3e7f0cfe3b761fefc9dd3bc89d85a20df9343bb1e82) | `0x5956bd24ee037533a284a2fc8a41a769301129dc` | `0x1278c1e4…b0697c` |
| 52.355.349 | [`0x5474ce85…d033dc2e6`](https://basescan.org/tx/0x5474ce85c303596e2c863bb8079122a72a0063f0bef96ffe7b2ed88d033dc2e6) | `0x7768a2778e882c6b443a51730b6eabd3b35652de` | `0x4b5c33c3c7a31bd108f5a99b64683b0056a62226` |

Questo 5 su 11 è la forma della vendita in 40 blocchi. Non è una quota del 32%.

Nella stessa finestra due vendite sono acquisti visibili, se si legge `tx.from`. Un gettone B20 (`0xb2000000000000000000008014aca6490df2fb59`) è uscito dal PoolManager in una transazione firmata dallo stesso indirizzo che lo ha rivenduto 153 blocchi dopo (`0x39f4e978…5758395f`, poi `0x0c4aa761…f7266cc3`). Un'altra vendita ha `tx.to` uguale all'AllowanceHolder di 0x, `0x0000000000001fF3684f28c67538d4D072C22734`, l'indirizzo pubblicato per le chain Cancun, Base inclusa ([Contracts](https://docs.0x.org/docs/core-concepts/contracts.md)); l'ingresso, 255 blocchi prima, è firmato dallo stesso venditore.

Il prefisso B20, da solo, non nasconde l'acquisto: quell'andata e ritorno è firmata dalla stessa persona.

## Da dove era arrivato il gettone, in un caso riletto

Su 6 delle 11 vendite non c'è nessun Transfer in entrata nei 4.000 blocchi precedenti.

Per `0x58fb5894c01f54e33ba6534a759b18fd3fb7cb16` e il gettone `0x486f662020286e17e7469df4e5f2cf2415f36662` ho riletto oggi il nodo. L'unico Transfer verso di lui, fra il blocco 52.345.090 e il 52.345.340, è al blocco **52.345.147**, cioè **10.193 blocchi** prima della vendita. Transazione [`0xd8dc726e…67fcdc5e`](https://basescan.org/tx/0xd8dc726ed7415382f2805b98ffb1b99f6c141aec7709234d2a07f4a567fcdc5e). Mittente e firmatario sono lo stesso indirizzo, `0x397d17bfcb8145e6bfbb4d1168c1b65de52c3445`, che chiama `0x008c62d5ac7218311d05587718066179c980b469`. Non è il PoolManager e non è il Universal Router. Quei due indirizzi restano senza nome: non ho una pagina che li identifichi.

Per `0x5956bd24ee037533a284a2fc8a41a769301129dc` e il gettone `0x36d6828942f6debca99f693b9858436353c76946`, la scansione dello stesso 9 ottobre non ha trovato un Transfer in entrata nei 20.000 blocchi prima della vendita. Quella seconda assenza non l'ho riletta blocco per blocco in questa stesura. Un mint verso quell'indirizzo, se fosse caduto in quei blocchi, sarebbe un Transfer da `0x0` e la scansione lo avrebbe visto.

La vendita via EntryPoint spiega perché il conteggio, che guarda `tx.from`, non vede l'acquisto su chi tiene il gettone. Nel caso riletto il gettone non è uscito dal pool in quella transazione: è arrivato con un trasferimento firmato da un altro indirizzo.

## Perché non è il 15% di Bankr, né il caveau di Clanker

Bankr, [Token Launching Overview](https://docs.bankr.bot/token-launching/overview), letto il 9 ottobre 2026. Sui lanci Doppler la fornitura è 100 miliardi: 85% nel pool v4, 15% pre-assegnato al fee recipient, cliff di 30 giorni, poi sblocco continuo fino a un anno. Prima del cliff non si ritira niente. `release()` paga `msg.sender`. Il destinatario è uno, fissato al lancio. Il vesting si può spegnere, e allora il 100% va nel pool; i lanci con Partner Key vendono già il 100%. Chat, social e API partono di default su Robinhood Chain; CLI e modulo web su Base. La quota di lanci con il vesting spento non è pubblicata. L'indirizzo dell'escrow di vesting non è in quella pagina: non lo invento.

Le fee di Bankr, di default, maturano nel gettone lanciato e nella quotazione. Un claim può consegnare il memecoin senza uno swap, a un beneficiario per gettone. Senza un conteggio, un beneficiario per gettone non è un terzo delle posizioni.

Clanker v4.0.0, [Token Deployments](https://clanker.gitbook.io/documentation/general/token-deployments), letto il 9 ottobre 2026: 100 miliardi, non mintabile dopo il deploy. Fino al 90% può andare a estensioni; senza estensioni, il 100% va nel pool v4. Il vault ha un minimo di 7 giorni e un amministratore. L'airdrop ha un minimo di 1 giorno. Il dev buy è uno swap dentro la transazione di deploy. La quota di deploy che usano un'estensione non è pubblicata.

Un cliff di giorni o di un mese, un solo destinatario, e una quota d'uso che nessuno pubblica, non reggono le vendite dei primi giorni.

## Il 32%

È il nostro conteggio del 5 ottobre 2026, dopo la correzione dei segni: su Base, 32% di posizioni con sole uscite e 46–48% comprate e mai vendute ([PRIMI_NUMERI_GIUSTI.md](PRIMI_NUMERI_GIUSTI.md)). Non è un dato di un esploratore. Le due fette sono vicine: chi risulta comprare e non vendere, e chi risulta vendere e non comprare. È la forma di un acquisto accreditato a un indirizzo e di una detenzione su un altro. Un pre-mine riempirebbe solo il secondo lato.

COSA USEREI DOMANI: su Base, una vendita senza acquisto dello stesso `tx.from` la leggo dal Transfer del gettone dentro la transazione. Se `tx.to` è l'EntryPoint `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789`, il titolare è lo smart account, non il bundler. Il gettone o1 è uscito comunque dal PoolManager `0x498581fF718922c3f8e6A244956aF099B2652b2b`.

COSA NON VALE LA PENA: cercare su o1 una curva alla Pons, un airdrop pubblico, o il 15% di Bankr per spiegare le vendite dei primi giorni. E non trasformare 5 vendite su 11 in una percentuale del 32%.
