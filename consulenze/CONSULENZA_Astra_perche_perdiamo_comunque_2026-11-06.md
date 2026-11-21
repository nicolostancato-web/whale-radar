# Astra (gpt-5) — perche_perdiamo_comunque — 2026-11-06

costo $0.1035, 222s, 10187 token di risposta

---

Ok, brutal.

Premessa falsa o incompleta n.1: “Paghiamo di più del vincitore, quindi dovremmo essere preferiti.”
Sbagliato. Il builder sceglie l’insieme di bundle/tx che massimizza il valore totale al proposer (coinbase) per quel blocco. Se il tuo bundle A paga 9,6% su UNA sola liquidazione, e il loro bundle B paga 5% ma contiene 3 liquidazioni + un unwind più efficiente + magari un backrun aggiuntivo, il bid totale del loro blocco è più alto. Il builder include B, punto. Percentuali non contano, conta il wei a coinbase nel blocco finale.

Premessa incompleta n.2: “333 pacchetti accettati su 333” significa “siamo in gara”.
Accettato != inclusione. “Accepted” vuol dire: relay lo ha simulato e forwardato. Il builder poi confronta con decine di bundle conflittuali. Se il tuo bundle non è il migliore in termini di valore totale di blocco, perdi. Zero misteri.

Premessa incompleta n.3: “Offriamo 9,6% al coinbase, con call on-chain: i builder lo vedono.”
Dipende dal builder. Alcuni builder/relays creditano solo ciò che risulta nel saldo del coinbase a fine simulazione (priority fee + transfer reali al coinbase effettivo). Altri scartano pattern strani. E alcuni privilegiano flussi con accordi out-of-band (fee al builder) o con reputazione (latency/quality). Non puoi dare per scontato che tutti contabilizzino allo stesso modo il tuo pagamento “calcolato in transazione”. Se stai perdendo contro chi paga meno “on-chain”, quasi sicuramente l’altro bundle ha più valore complessivo o c’è un pagamento/accordo invisibile a te.

La cosa che ti manca (risposta A):
- Latenza e pre-bundling aggressivo. I vincenti hanno precompilato i bundle multipli (tutte le posizioni potenzialmente liquidabili per feed) e spingono in <30–60 ms dalla vista dell’update OCR ai builder principali.
- Aggregazione. Mandare 7–13 bundle “uno per posizione” è losing by design contro chi manda UN bundle con tutte le liquidazioni che il feed sblocca. Il builder preferisce un blocco con più valore totale. Se tu spacchetti, perdi contro chi aggrega.
- Copertura builder/relay completa e peering. 4 destinazioni non basta. Nel 2024 i builder che contano erano ≥8 (Flashbots, beaverbuild, rsync, bloXroute (3–4 canali), Titan, Builder0x69, etc.). Nel 2026 è peggio. Se non mandi a tutti i builder rilevanti e non sei low-latency verso i relay giusti, vieni battuto anche quando “senti” l’update.
- Cutoff di slot e concurrency. L’update Chainlink arriva spesso 50–250 ms prima del sealing del blocco. Se costruisci e spedisci in secondi, sei fuori. “Accettato” può riferirsi al blocco +2/+3; intanto il +1 è già andato.

Latenza (risposta B, con numeri):
- Finestra reale tra apparizione dell’OCR in mempool e sealing: tipicamente 80–250 ms (ampia varianza, ho visto sia <50 ms sia >300 ms). Il “backrun immediato” che vince vive dentro questa finestra.
- Budget per chi vince:
  - Detection → decisione: 5–20 ms (precomputazione massiva, niente parsing/ABI runtime costoso).
  - Composizione bundle: 5–15 ms (niente subprocess; firmare già fatto, si patcha solo calldata/anchor).
  - Invio a TUTTI i relay/builder principali in parallelo: 10–40 ms intra-DC se sei colocalizzato o su link decente.
- Totale tipico vincente: 20–80 ms end-to-end. Oltre 150–200 ms inizi a perdere spesso.
- Il tuo pipeline: 338–545 ms per comporre 7–12 pacchetti + 2,5–3,5 s per inviarli a 4 porte (seriale!). È una condanna. Anche se “accettano”, arrivi troppo tardi per il blocco attuale. Devi:
  - Togliere completamente subprocess/call out a cast.
  - Pre-firmare TUTTE le transazioni e calldate; al tick cambi solo parametri già codificati nel contract (usa block.coinbase a runtime, niente ricalcoli).
  - Inviare in parallelo, non seriale. E ridurre drasticamente il numero di bundle (vedi sotto).
  - Scrivere in Go/Rust o almeno Python con librerie asincrone e zero shelling. Ma realisticamente: Go/Rust.

Conflitti e spam (risposta C):
- Mandare 12 bundle conflittuali per feed update è inferiore a:
  - 1 bundle con tutte le liquidazioni profittevoli (in ordine deterministico) + il tuo unwind interno più efficiente.
- I builder non “penalizzano” formalmente chi spamma, ma:
  - Alcuni deduplicano per searcher/pubkey e tengono solo il più alto valore. Se mandi conflitti, aumenti chance che prenda un bundle “sub-ottimo” o che arrivi tardivo.
  - Stai perdendo tempo prezioso a spedire roba inutile.
- Regola pratica: 1–2 bundle max per evento:
  - Bundle A: tutte le liq più profittevoli finché gas budget e rischio slippage/price impact sono accettabili.
  - Bundle B (fallback/minore) se A fallisce su alcuni builder (opzionale).
- Se il tuo gas “disponibile” è 0,041 ETH (lo hai scritto): è probabilmente troppo basso per includere più liq + unwind competitivo quando il basefee/tips schizza. A 30 gwei, 0,041 ETH sono ~1,36M gas; ma col basefee+tip reali e call a DEX, molte liq + swap bruciano 450–700k gas ciascuna. Con 2–3 liq dentro, potresti sforare. Devi dimensionare gas cap adeguatamente (o spacchettare in 2 bundle non conflittuali di set disgiunti se proprio).

Canale di pagamento (risposta D):
- Pagare coinbase via .call nella tua tx è accettato da alcuni builder, ma non tutti contano allo stesso modo. Ci sono builder che:
  - Contano solo priority tips + saldo coinbase a fine block sim.
  - Diffidano di pattern “weird” (selfdestruct o forwarding strani).
  - Hanno accordi out-of-band con searcher “trusted” (fee al builder), e preferiranno quei bundle a parità o quasi di coinbase per ridurre rischio/latency.
- Per essere visto al 100%:
  - Paga coinbase in modo banale (call con value in linea retta, no magie).
  - Aumenta l’assoluto in wei quando serve, non la percentuale.
  - Se puoi, usa anche i canali specifici dei builder (alcuni supportano headers/fields proprietari per fees o “bundle bid”). Ma con i tuoi vincoli probabilmente non puoi.
- Il tuo 9,6% non significa niente se il tuo bundle totale paga meno coinbase in assoluto del bundle aggregato concorrente. Se la liq rende 0,05 ETH e tu paghi 9,6% (=0,0048 ETH), ma l’altro bundle unisce tre liq per 0,12 ETH complessivi e paga 5% (=0,006 ETH), il builder preferisce l’altro.

Diagnosi post-mortem (risposta E):
- Flashbots v0/v2: c’è getBundleStats, logs di simulation, ma i motivi “perché non incluso” spesso non vengono resi pubblici. Ti dice simulated/accepted/not included, non “preferito altro perché +0,0023 ETH”.
- Beaverbuild/Titan/rsync/bloXroute: in generale niente motivi granulari pubblici. Alcuni relays forniscono metrics aggregate, ma non spiegazioni per bundle individuale.
- Come fare debugging:
  - Logga il valore netto che offri (priority fees + trasferimenti a coinbase) e confrontalo con quello del vincitore ricostruendo il loro bundle dal blocco (somma i coinbase credits e i transfer in-block).
  - Ricostruisci se il vincitore ha multipli liq in bundle, un unwind migliore (meno fee di LP), o ulteriori arbs all’interno.
  - Misura il delta temporale tra apparizione dell’OCR tx nella tua mempool e arrivo del tuo bundle “accepted” per block+1 su ogni relay (timestamp locale). Se la tua accettazione per +1 arriva dopo che il blocco è già stato sigillato… stai spedendo tardi.

Cosa fare subito (con i tuoi vincoli):

1) Riduci latenza di due ordini di grandezza:
- Niente subprocess, niente cast. Pre-firma tutto. Usa un contract che:
  - Legge block.coinbase a runtime.
  - Paga coinbase con una percentuale parametricamente fissata ma calcolata su base note già nel contract (o fissa un valore minimo in wei).
  - Esegue una lista di liq pre-calcolate su mapping di posizioni potenzialmente liquidabili per feed, fermandosi quando non più profittevoli.
- Patcha solo i parametri che devi (pochi bytes di calldata), non rigenerare tx. Firma già pronta.
- Invia a TUTTI i builder/relays principali in parallelo (asincrono). Niente invio sequenziale.

2) Aggrega:
- Costruisci un bundle per feed update con tutte le liquidazioni profittevoli (top k per EV) + un unwind interno che non si appoggia all’aggregatore retail (niente Quoter onchain nel blocco caldo).
- Se non puoi implementare unwind interno efficiente, considera route statiche a pool 0.05%/0.01% stabili e path pre-testati per quell’asset (il tuo “99,7% resa USDT->WETH” non basta; i vincenti spesso internalizzano o usano venue private con fee quasi zero). 0,3% di leakage ti ammazza il margine e la tua capacità di pagare coinbase.

3) Copertura builder:
- 4 endpoints non bastano. Nel 2024 servivano almeno: Flashbots, beaverbuild, rsync, bloXroute (light, private, s, etc.), Titan, builder0x69, relayoo, ecc. Nel 2026 ce ne sono altri/nuovi: devi coprirli tutti. “Accettato” su 4 non significa “competitivo”.
- Parallelizza. Con 2,5–3,5 s per 4, stai buttando via l’evento.

4) Budget gas reale:
- 0,041 ETH di budget gas è probabilmente insufficiente se vuoi includere 2–3 liq + swap + fee coinbase a gas price reali. Aumenta il budget o limita il bundle a 1–2 liq ad alto EV. Se non puoi aumentare, almeno assicurati di non andare out-of-gas e di non limitare il builder nell’includere altro valore attorno.

5) Misura latenza seriamente:
- Timestamp (ns) su:
  - Arrivo OCR tx (mempool).
  - “Bundle ready” localmente.
  - “Accepted” per block+1 su ogni relay (log di risposta).
- Obiettivo: <80 ms tra arrivo OCR e submit ai builder chiave. Se stai sopra 150–200 ms, perdi spesso.
- Evita Python blocking I/O; usa asyncio o passa a Go. Nessun server? Ok, ma allora almeno un client robusto localmente, senza shelling.

6) Scegli una sola offerta forte:
- Manda 1 (max 2) bundle per feed update, quello a massimo EV, non 7–13 conflittuali. Se vuoi fallback, rendilo disgiunto (altre posizioni/ordini), non conflittuale.

7) A pagamento (se vuoi davvero moltiplicare risultati):
- Colocation/latency: le soluzioni “pro” (colocazione in DC dei relays/builder, connessioni dedicate, peering privati) fanno la differenza. Prezzi 2024: bloXroute “MEV plans” partivano ~300–1500 USD/m per accesso avanzato/BDN con bassa latenza e protezioni; colocation/peering dedicati costano di più (4–5 cifre/anno). Non posso darti il “prezzo esatto di oggi” (cutoff 2024), ma la realtà è: chi vince investe in infra. Con 50€ e un Mac, devi compensare con precomputazione estrema, zero overhead, e aggregazione perfetta. Se paghi ~300–500 USD/m per un feed BDN low-latency/relays aggiuntivi, vedrai un miglioramento netto in inclusione entro giorni, a patto che il codice sia veloce e l’aggregazione buona.

Risposte secche alle tue domande:

A) Ti manca: velocità sub-100 ms end-to-end, aggregazione multi-liq per update, copertura completa dei builder, e un unwind migliore (meno leakage). Percentuale offerta > del concorrente non basta.

B) Budget di chi vince: 20–80 ms dal sighting al submit; 80–250 ms tipicamente tra sighting OCR e sealing. Il tuo Python + cast (338–545 ms build, 2,5–3,5 s invio) è fuori gara.

C) Sì, spedire 12 bundle conflittuali è peggio. Non c’è “penalità” ufficiale, ma vieni deduplicato e perdi tempo. Spedisci solo il bundle più ricco (o max 2), e fallo in parallelo a tutti i builder.

D) Il .call a block.coinbase è visto se semplice e reale, ma non tutti builder ponderano allo stesso modo. Conta il valore assoluto in wei all’interno del blocco finale. E molti builder favoriscono bundle con valore totale maggiore (multi-liq/miglior unwind) o con accordi reputazionali/out-of-band.

E) No, non c’è un “perché” ufficiale post-mortem dettagliato. Usa getBundleStats (Flashbots) e i log relay, ma il motivo vero lo deduci tu confrontando valore totale del blocco del vincitore con il tuo bundle. Se vuoi un motivo “ufficiale”, non c’è.

Conclusione cruda: con 82% di ascolto, 333 “accepted”, 9,6% di tip, e zero wins, il problema è 80% latenza/infra/codice e 20% strategia (aggregazione/unwind). Fissa la latenza sotto 100 ms, manda un solo bundle aggregato a tutti i builder principali, riduci leakage di swap, e smetti di serializzare invii. Finché resti a 300–500 ms di composizione e secondi di invio, resterai a 0.
