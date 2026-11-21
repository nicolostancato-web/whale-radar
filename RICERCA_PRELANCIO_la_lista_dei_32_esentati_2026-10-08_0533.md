# Ricerca Grok — 2026-10-08 05:33 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 571s

---

Il privilegio è scritto in chiaro prima dello scambio: parto dalla documentazione ufficiale di Pons e verifico se la lista dei 32 indirizzi si legge davvero on-chain, e se qualcuno l’ha già studiata.La lista nasce dentro la transazione di creazione. Prima di quella transazione non c’è un registro da leggere. Un elenco pubblico degli indirizzi che ricorrono su molti lanci non è stato pubblicato, e il database di chi ha studiato il caso più grosso non è stato rilasciato.

## Come si legge

L’argomento `snipeTaxExemptions` è un `address[]` sull’overload di `launchToken`, al massimo 32 voci: oltre, la factory reverte con `ExemptionListTooLong`. La lista è fissata in creazione. Fonte: [docs v2, «Exempting addresses»](https://docs.ponsfamily.com/v2) e la factory su GitHub, costante e controllo alle righe 623–627 e 713–750, file letto l’8 ottobre 2026: [PonsV2LaunchFactory.sol](https://github.com/ponsdotdev/pons-labs/blob/main/contractsV2/src/v2/PonsV2LaunchFactory.sol).

Quell’array non è la lista intera. La factory esenta da sola, prima dell’array, chi lancia e il destinatario delle fee se è un indirizzo diverso ([righe 841–847](https://github.com/ponsdotdev/pons-labs/blob/main/contractsV2/src/v2/PonsV2LaunchFactory.sol)). La documentazione del router `launchAndBuy` dice che anche il destinatario del primo acquisto viene esentato, e che l’array sono solo i portafogli in più ([stessa pagina](https://docs.ponsfamily.com/v2)).

La lista intera sta nei log `SnipeTaxExempted(address)` della transazione di creazione, emessi dalla curva. Il topic0 è `0xe4b7e48fbd47c2f602bacadee76ad33b16542ddb4997cfc0de04c311adcfa8c7` (keccak della firma, collima con i log). L’indirizzo è il topic1. Si tiene l’insieme unico: lo stesso indirizzo può comparire due volte.

Verifica su una transazione vera, letta l’8 ottobre 2026 dal RPC pubblico [rpc.mainnet.chain.robinhood.com](https://docs.robinhood.com/chain/connecting/):

- Transazione [0xc1947bc6…d453b8](https://robinhoodchain.blockscout.com/tx/0xc1947bc6afce3780c45829f54aaf38cb4a1e01ecb11b0d486efc073167d453b8), blocco 64.710.959, timestamp del blocco 2026-09-16 18:08:09 UTC. È un `launchAndBuy` (selettore `0xf85f8e41`) verso il router `0xe33E9E479dF8802cb0866d5d05258bEc4cF62948`. Curva: `0x59b118d176469366f15bc4afffe58ddcb98cb9d3`.
- Nell’argomento ci sono 15 indirizzi.
- Nei log ci sono 17 eventi e 16 indirizzi unici: prima chi lancia (`0x5d93d37141ef8d567c4b947c949f9304481769e6`, che è anche il destinatario delle fee), poi i 15 dell’argomento nello stesso ordine, poi di nuovo chi lancia, che è il destinatario dell’acquisto e non era fra i 15.

Dopo la finestra la lista resta interrogabile a uno a uno, non in blocco. L’8 ottobre 2026, sulla stessa curva: `snipeTaxExempt` restituisce vero per `0xe6896d1b92ece44f06e52e33e94de83dcf251b3a` e per chi ha lanciato, falso per `0x000…0000`, per `0x…dEaD` e per `0x1111…1111`. `currentSnipeTaxBps` sugli esenti restituisce 0. Quel getter non elenca nessuno: risponde solo se l’indirizzo lo hai già. La documentazione pubblica solo `currentSnipeTaxBps(recipient)`, e dice che a finestra chiusa vale zero ([docs, snipe protection](https://docs.ponsfamily.com/v2#snipe-protection)).

Il sorgente pubblicato della curva non contiene questa funzione. L’issue aperta il 14 settembre 2026, ancora aperta all’8 ottobre, mostra che `PonsV2BondingCurve.sol` non ha `exemptFromSnipeTax` né `currentSnipeTaxBps`, e che la factory non compila contro quel file: [issue #10](https://github.com/ponsdotdev/pons-labs/issues/10). Il comportamento sopra è quello del bytecode deployato, letto dai log e dalle chiamate, non dal file della curva su GitHub.

Due numeri di contorno, perché la domanda dice «5 secondi». La prosa dei docs dice 99% che decade nei primi 5 secondi, circa 25% a un secondo e circa 3% a due ([stessa sezione](https://docs.ponsfamily.com/v2#snipe-protection)). Il sorgente della factory ha default 15 secondi, modificabile dal proprietario, tetto 60 ([righe 312–320 e 66–70](https://github.com/ponsdotdev/pons-labs/blob/main/contractsV2/src/v2/PonsV2LaunchFactory.sol)). Lettura dell’8 ottobre 2026 sulla factory `0x7eD598BcEf8bd9Edd8C97A195C6d13f40801EC7e`: `snipeTaxStartBps()` = 9900, `snipeTaxSeconds()` = 3. Ogni curva copia i termini alla nascita, quindi il 3 di oggi non è la finestra dei lanci già aperti. La tabella secondo-per-secondo del bytecode non è nel sorgente pubblicato della curva: non la riporto.

## Indirizzi che tornano su molti lanci

Quel conteggio non è ottenibile da qui, e non va stimato. L’evento lo emette la curva, un contratto nuovo per ogni lancio: la factory non tiene un registro unico. Il getter risponde per un indirizzo che conosci già. La storia della chain, dal lancio del 1° luglio 2026, è decine di milioni di blocchi; il RPC pubblico è a rate limit ([docs Robinhood](https://docs.robinhood.com/chain/connecting/)) e in questa sessione ha risposto 429 a una scansione. Non ho fatto il censimento.

## Chi l’ha già studiato

Sì, un caso. No, non come tabella di indirizzi ricorrenti.

Il 27 settembre 2026 Wazz ha pubblicato un thread: 53 lanci in due mesi, 18,43 milioni di dollari estratti «per quanto sono riuscito a collegare direttamente», quasi tutti snipati sopra il 70% della supply, bundle da 70 a 200 portafogli (92, 77 e 125 nei tre casi che mostra). Il legame che descrive è il denaro: il ricavo di un lancio paga la chiave che finanzia il successivo; 45 lanci così, 4 per la stessa chiave, 4 per lo stesso indirizzo di incasso. Non nomina `snipeTaxExemptions`. I suoi bundle da 70–200 non possono essere la lista dei 32. Scrive che ha etichettato i portafogli nel suo database e che quel database non è ancora pubblicato. Thread: [27 settembre 2026](https://x.com/WazzCrypto/status/2104194307628621976).

Lo stesso giorno The Block ha ricontato 10 lanci Pons V2 di quell’elenco. In 9, da fine agosto in poi, la transazione di creazione ha esentato da 15 a 25 portafogli, e uno o tre blocchi dopo una sola transazione ha comprato per ciascuno di loro, svuotando la curva. The Block attribuisce a Wazz la cifra di almeno 18,43 milioni su 53 lanci fra il 10 luglio e il 21 settembre 2026; è la sua cifra, riportata da loro. Articolo: [The Block, 27 settembre 2026](https://www.theblock.co/news/defi/2026-09-27-onchain-analyst-links-18-4-million-in-robinhood-chain-memecoin-extractions-to-single-rug-pull-operation-416960).

Uno strumento legge la lista di un lancio alla volta e la usa come punteggio, senza pubblicare chi si ripete: bodkin decodifica solo l’array dentro `launchAndBuy`, quindi perde le esenzioni automatiche ([enrich.ts](https://github.com/Phosphenq/bodkin/blob/main/src/pons/enrich.ts)).

COSA USEREI DOMANI: per ogni lancio, l’insieme unico dei log `SnipeTaxExempted` nella transazione di creazione. Per un indirizzo già in mano, `snipeTaxExempt(address)` sulla curva, che resta vero a finestra chiusa.

COSA NON VALE LA PENA: cercare la lista prima della transazione di creazione; usare `currentSnipeTaxBps` a finestra chiusa per scoprire gli esenti; contare solo l’argomento `snipeTaxExemptions`; aspettare il database di Wazz, che il 27 settembre 2026 non era pubblico.
