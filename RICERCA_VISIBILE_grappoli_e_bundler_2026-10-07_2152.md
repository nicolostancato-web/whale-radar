# Ricerca Grok — grappoli_e_bundler

Modello grok-4.7. Costo: ZERO (abbonamento, nessuna chiave API). Tempo: 393s. 2/3 sotto-domande con risposta.

---

### Comprare per molti portafogli in UNA transazione sulle piattaforme di lancio memecoin: come si chiama questa pratica e quali strumenti pubblici la fanno? Nomi e link.

Cerco il nome preciso della pratica e gli strumenti pubblici che la offrono, con link verificati.Si chiama **bundling** (anche **bundle buy** o **bundle launch**). Su Solana il meccanismo è il **Jito bundle**: fino a 5 transazioni firmate, in ordine, tutto-o-niente, nello stesso blocco. Non è una sola istruzione on-chain; il mercato la chiama comunque “una transazione” perché nessuno può inserirsi in mezzo.

Su BNB (four.meme e simili) la stessa pratica si chiama ancora bundle: creazione e primi acquisti da più wallet nello stesso blocco.

| Strumento | Cosa fa | Link |
|---|---|---|
| **Jito** | Infrastruttura. `sendBundle`, max 5 tx atomiche. I tool sopra ci si appoggiano. | [docs.jito.wtf/lowlatencytxnsend](https://docs.jito.wtf/lowlatencytxnsend/) |
| **Smithii Solana Bundler** | Launch + buy da più wallet su pump.fun, LetsBonk, Raydium LaunchLab, Bags, Moonit, Jupiter Studio, Printr. Fino a 16 wallet su pump.fun, fee dichiarata 0.3 SOL + tip Jito. | [tools.smithii.io/solana-bundler](https://tools.smithii.io/solana-bundler) |
| **Smithii Four.meme Bundler** | Stessa cosa su four.meme (BNB). Fee dichiarata 0.05 BNB. | [tools.smithii.io/four-meme-bundler/binance](https://tools.smithii.io/four-meme-bundler/binance) |
| **J Tools** | Create & Bundle Buy su pump.fun, fino a 16 wallet in un Jito bundle. | [docs.j.tools — Pump.fun Create & Bundle Buy](https://docs.j.tools/tools/launch/pumpfun-create-and-bundle-buy) |
| **SolBundler** | Bundler web per pump.fun / Bonk / Bags. | [solbundler.app](https://solbundler.app) |
| **OpenLiquid Bundle Bot** | Bundle buy su pump.fun (e, a loro dire, anche ETH, BNB, Base). | [openliquid.io/tools/bundle-bot](https://openliquid.io/tools/bundle-bot/) |
| **Alphecca** | Launch pump.fun + buy, fino a 12 wallet extra. | [alphecca.io/en/pump-bundle-launch](https://alphecca.io/en/pump-bundle-launch) |
| **BumpOn** | Deployer pump.fun con bundle multi-wallet. | [bumpon.fun](https://bumpon.fun/) |
| **PumpDev** | API developer: create + più buyer via Jito. | [pumpdev.io/jito-bundles](https://pumpdev.io/jito-bundles) |

I numeri “fino a 500 wallet in una transazione” sono marketing. Il limite Jito è 5 transazioni per bundle; i tool con 12–20 wallet spezzano in più bundle o mettono più buy dove il programma della launchpad lo consente.

GMGN e Axiom etichettano questa supply come **Bundle %**. Non resta nascosta: [cos’è un bundle su GMGN](https://gmgn.ai/blog/what-is-a-meme-coin-bundle/).

### Quali metodi pubblicati esistono per riconoscere dalla blockchain che piu' portafogli sono controllati dallo stesso operatore? Elencali con una riga ciascuno e i link.

_(risposta troppo corta o assente: 145 caratteri — da riprovare)_

### Gli strumenti di bundling distribuiscono le vendite su piu' blocchi per non far crollare il prezzo? Con quali parametri tipici? Col link.

Verifico il contesto del progetto e le fonti sui bundler, così ti rispondo sui parametri di vendita spezzata e non su un’ipotesi.No. Il bundle di vendita fa il contrario: mette le vendite nello stesso blocco. La vendita spezzata su più blocchi è un’altra funzione, e il ritardo non ha un valore pubblicato.

Jito definisce il bundle come al massimo 5 transazioni, eseguite in ordine e nello stesso slot. Un bundle non può attraversare il confine di uno slot. Se una transazione fallisce, non ne passa nessuna. [Documentazione Jito](https://docs.jito.wtf/lowlatencytxnsend/).

Lo strumento di vendita, per esempio Smithii su PumpSwap, usa proprio questo: fino a 20 portafogli, tutti nello stesso blocco, e per ciascuno si sceglie il 100% oppure una percentuale libera. La commissione indicata è 0,1 SOL. [PumpSwap Bundle Sell](https://tools.smithii.io/pumpswap-bundle-sell/solana). Sulla chain Robinhood, lo stesso fornitore offre le percentuali fisse 25%, 50%, 75% e 100%, fino a 25 portafogli, con una commissione fissa di 0,004 ETH. [Flap Bundle Sell](https://tools.smithii.io/flap-bundle-sell/robinhood).

Dentro quel blocco le vendite sono in sequenza, quindi il prezzo scende comunque lungo la curva: l’intera quantità esce in un colpo solo. Quello che il bundle impedisce è che qualcun altro si infili tra un portafoglio e l’altro. La frase «tutti escono allo stesso prezzo» è claim del fornitore, non la regola di Jito.

La funzione che distribuisce nel tempo si chiama, negli strumenti aperti, Delay Sell: vende una percentuale da ogni portafoglio con un ritardo configurabile tra una transazione e l’altra, dichiarato come modo per ridurre l’impatto. Il file non pubblica né i secondi né il numero di blocchi di default. L’unico intervallo numerico in quella pagina riguarda gli acquisti scaglionati, 45–90 secondi, non le vendite. [README, modalità di vendita](https://github.com/cicere/pumpfun-bundler/blob/main/README.md).

Lì i parametri scritti della vendita reattiva, nel file di esempio, sono questi: vende il 30% del volume dell’acquisto in arrivo, e scatta solo se quell’acquisto vale almeno 0,05 SOL. Nel testo la stessa funzione è illustrata anche al 50%. Un blog di un altro fornitore consiglia «10% ogni 5 minuti»: è un consiglio, non un parametro dello strumento. [Come fermare il dump](https://solbundler.app/blog/how-to-stop-dump-after-launch).

Spezzare non riduce il calo totale se nel mezzo nessuno compra. Riduce il gradino singolo, e recupera prezzo solo se tra una fetta e l’altra entrano acquisti altrui.
