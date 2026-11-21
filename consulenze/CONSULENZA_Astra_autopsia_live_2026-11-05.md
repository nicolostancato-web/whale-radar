# Astra (gpt-5) — autopsia_live — 2026-11-05

costo $0.0815, 90s, 7993 token di risposta

---

Ok, lettura: sì, il collo di bottiglia è la selezione. Lo provano i tuoi numeri: 82% del premio perso è DISTANZA 2, cioè non avete neanche spedito la posizione che poi è caduta. E i 30 slot se li mangiano posizioni giganti con premio “capato” e hazard bassissimo che non cadono mai. Ma misuriamolo bene, e sistemiamo il ranking.

1) La tesi “il collo è la selezione” regge? Cosa falsificare
- Misura immediata per falsificarla:
  - Coverage dei vincenti: per ogni liquidazione vincente nel mondo, ricalcola se con un ranking alternativo (vedi punto 2) entrava nei vostri 30. Se >70% dei vincenti finirebbero nei vostri 30 con ranking nuovo, la tesi è vera; se restano fuori comunque, allora è latenza/builder coverage.
  - Hazard gap: per ogni blocco, prendi le 30 candidate spedite e confronta la distribuzione di “distanza a cadere” (in bp di movimento prezzo necessari) con quella dei vincenti. Se i vincenti hanno distanze sistematicamente più piccole delle vostre candidate, è selezione sbagliata.
  - Slot hogging: quante delle 30 sono occupate da quelle 31 posizioni osETH/WETH “capate” e quasi statiche? Se >30-40% medio, state soffocando la coda utile.
  - Latency budget vs builder: misurate T_total dal log di update Chainlink visto al primo invio bundle a ciascun builder. Se T_total mediana >250-300 ms, siete lenti rispetto ai migliori (che precompilano e sparano in <100 ms). Se siete lenti e i vostri candidate sono giusti, potete ancora perdere per arrivo tardivo.

2) Come assegnare i 30 slot (e che metrica usare al posto del “premio capato”)
- Niente split 50/50 “premio vs vicine a cadere”. Va tutto su EV attesa per bundle.
- Ranking per EV attesa:
  - P_liq: probabilità che la posizione diventi liquidabile con questo update. Calcolatela come funzione della distanza in bp al threshold rispetto alla distribuzione empirica di Δprezzo dell’asset specifico su aggiornamenti Chainlink (non la mediana 0,507% globale; serve per-asset, per feed). Usate la coda delle ultime N finestre reali per quell’asset.
  - Net profit stimato: min(premio teorico, sellcap dinamico) − gas − tip al builder. Qui il “sellcap” non è un numero fisso: stimatelo con un modello di slippage per route attuale, aggiornato ogni X secondi su orderflow reale, e con un range (pessimista/mediano). Usate il pessimistico per il tip.
  - Tip target: se il mercato paga 12,3% mediano, usate 15% come base solo se la vostra stima di profit è conservativa. Se la vostra stima sottovaluta rispetto al realizzato di chi vince, voi pagate meno tip a parità di realtà. Agganciate il tip a un percentile del realized builder cut per quell’asset e size (es. P75), non a un fisso 15%.
  - EV = P_liq × Net profit. Rankate solo su EV.
- Collateral constraints per evitare hogging:
  - Hard cap per asset/cluster: massimo X slot per asset/categoria (es. osETH-WETH max 4-6 per update). Così non vi intasate.
  - Penalità di persistenza: se una posizione è in HR 1,0006–1,012 da 48h e non cade mai, decay esponenziale al suo punteggio. Chi sta sempre al filo senza cadere ha hazard reale basso.
  - Deduplicate per debt/collateral route capacity: se 5 posizioni competono per la stessa route con stesso sellcap identico, prendete solo le top 1-2 per EV.
- Sostituire il “premio capato” identico:
  - Usate Expected Realizable Premium: minimo tra teorico e sellcap “mid” ma con penalità per conflitto di liquidità intra-blocco (se più posizioni toccano lo stesso pool, riduci sellcap previsto).
  - Introducete “bp to liquidation” come feature primaria: distanza in bp al threshold post-update simulato. Se servono >50 bp e la distribuzione storica per quell’asset dà P<5% in una singola tick, EV crolla, non va nei 30.
  - Considerate hazard per cluster di update multipli: a volte in un blocco arrivano 2-3 feed correlati; la kombinazione aumenta P_liq. Se avete storico, annotate i “burst” e pesate P_liq di conseguenza.

3) Perché limitarsi a 30? Qual è il vero vincolo
- 600 ms per 30 pacchetti è troppo. Il vincolo reale è la latenza totale prezzo→bundle→builder. Non è “rifiuto del relay”. I builder accettano spam se simulabile; il costo è solo vostro.
- Aumentate i bundle a 100-200 per update, ma:
  - Precompute continuo: mantenete una heap delle top 1000 per asset/hazard aggiornata ogni pochi secondi. Al tick Chainlink fate solo stitch e tip, non ricalcolo pesante. Obiettivo: tempo di composizione <100-150 ms per 100 bundle.
  - Parallelizzate simulazioni di route e sellcap; cache per asset/liquidity bins.
  - Ampiate la copertura builder: 4 è poco. Aggiungete rsync, builder0x69, Titan, Flashbots, Aestus, eth-builder, etc. Se non entrate nel builder vincente, la mancia è irrilevante.
  - Evitate duplicati identici agli stessi builder: variate leggermente tip e ordering per ridurre collisioni interne.
- Nota: i builder non vi “rifiutano” per numero, ma:
  - Rate limit/DoS guard per searcher esiste in alcuni builder; monitorate acceptance ratio per builder e adattate. Se crolla, riducete per quel builder ma non globalmente.
  - Rischio di conflitto tra i vostri bundle: assicurate mutual exclusion per target uguali per non farvi scavalcare da un vostro bundle meno redditizio.

4) DISTANZA 1: eravamo nel pacchetto ma abbiamo perso. Perché?
- Spiegazioni probabili:
  - Tip inferiore netto: il vincitore ha valutato un profit maggiore (miglior route/slippage) e quindi ha potuto pagare un tip più alto. Con 12,3% mediana, è normale vedere 20-30% in spike.
  - Route migliore: il vincitore ha liquidato con meno slippage (private liquidity, RFQ, concentrazione migliore su Uniswap v3, internalizzazione nel builder). Quindi EV reale > vostra, quindi anche tip più alto a parità di rischio.
  - Bundle combinato: il builder ha ricevuto un pacchetto che combinava più opportunità (es. 2-3 liquidazioni + un arb), quindi valore totale superiore al vostro singolo. I builder massimizzano coinbase, non “per tx”.
  - Arrivo/compatibilità: la vostra coppia [update Chainlink + liquidazione] può essere arrivata dopo un’altra coppia equivalente con tip più alto o con vincoli più facili per il builder (gas più basso, meno conflitti).
- Cosa misurare nel blocco vincente:
  - Coinbase delta per quel blocco: stimate la mancia totale e attribuite quella parte alla liquidazione (approssimate via confronto prezzi realizzati e gas). Confrontatela con la vostra tip offerta.
  - Slippage realizzato del vincitore: reconstruct dei trade della loro route; confrontate con la vostra stima di sellcap. Se loro hanno venduto meglio, siete “ciechi” sulla liquidità.
  - Gas e struttura: confrontate gas usato, close factor, numero di subcalls. Se loro spendono meno gas/msm, il builder preferisce.
  - Builder che ha vinto: il vostro bundle è arrivato a quel builder? Se no, coverage problema. Se sì, guardate timestamp di accettazione vs latenza vostra (se loggate gli ack).
  - Conflitti: c’erano altri bundle vostri confliggenti? Se sì, il builder può scartarvi per instabilità.

5) Punti ciechi che non hai nominato
- Coverage builder/relay: 4 builder non bastano. Se non siete nelle pipeline di chi ha vinto, non esistete. Loggate per builder acceptance/ack e correlate con share di mercato di ciascun builder nel periodo.
- Hazard per-asset e combinazioni: usare 0,507% mediana globale nasconde che alcuni feed hanno distribuzioni di update molto diverse. Serve P_liq per feed specifico. E attenzione ai burst multi-feed: la vostra “asset filter” potrebbe saltare posizioni che cadono per combinazioni collateral/debt su due feed nella stessa manciata di secondi.
- Bias del sellcap “identico”: state tagliando 31 posizioni gigantesche allo stesso cap e lasciando che dominino il ranking. Senza una tie-break di hazard vero e una penalità per persistenza, vi auto-sabotate.
- Latenza: 600 ms per 30 è alto. I migliori precomputano liste e composizione è istantanea. Ogni 200 ms in più aumenta la probabilità che i builder abbiano già lockato bundle con valore più alto.
- Stima profit → tip: se la vostra stima è conservativa o usa un sellcap più basso del realizzato, il 15% che pagate è in realtà inferiore al 12,3% “reale” dei vincitori. Outcome: perdete tie-break anche a parità di prezzo.
- Private liquidity/RFQ: se non avete canali RFQ o linee private (OTC, aggregatori con protezione), siete condannati a slippage peggiore e quindi EV inferiore. Misurate la differenza tra vostri realized e quelli dei vincitori.
- Diversificazione per route capacity: se più delle vostre candidate scaricano lo stesso pool/slot di liquidità, vi cannibalizzate. Serve scheduling/quotas per pool.
- eMode/close factor specifici Aave: controllate che la vostra simulazione consideri eMode category, LT specifiche, close factor corrente e possibili modifiche intra-blocco. Errori qui falsano P_liq e profit.
- Trigger non-Chainlink: ci sono liquidazioni innescate da accrued interest o variazioni su borrow APY senza update di prezzo immediato. Se i vostri trigger sono solo OCR, perdete qualche coda. Tenete un watcher per drift di salute dovuto a interessi su posizioni borderline.
- Copertura asset “debt side”: assicuratevi che il filtro asset includa anche movimenti del prezzo dell’asset di debito; spesso chi cade è perché sale il borrow asset.

Azioni pratiche immediate
- Passate da 30 a 150 bundle per update, con precompute continuo; hard cap 4-6 per asset/cluster; penalità di persistenza alle “balene immortali”.
- Ranking su EV attesa con P_liq per-asset; eliminate il 50/50. Agganciate il tip a P75 del builder cut locale per size/asset.
- Aumentate i builder a 8-10; misurate acceptance e share. Se non siete nel builder vincente, aggiungetelo.
- Strumenti di autopsia: per ogni DISTANZA 1, estrarre tip effettivo del vincitore, slippage realizzata e builder usato. Se la differenza è di tip/route, correggete modello di profit e tip schedule.
- Riduzione latenza: precompilazione candidate e route, simulazioni parallele, caching sellcap per asset, obiettivo <150 ms end-to-end per 100 bundle.
- RFQ/private: integrate almeno un canale RFQ per i collateral/debt più comuni; aumenterà EV e quindi tip competitiva.

Conclusione: i dati dicono che perdete soprattutto perché non spedite le giuste posizioni (DISTANZA 2) per colpa di ranking/slot hogging. Il resto è tip/route/coverage. Correggete ranking su EV con P_liq per asset, aumentate slots e builder coverage, e riducete latenza. Se dopo queste mosse DISTANZA 1 rimane alta, alzate il tip target in eventi di cluster (burst) e investite in route migliori.
