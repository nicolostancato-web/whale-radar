# Astra (gpt-5) — stato — 2026-11-05

costo $0.0655, 62s, 6380 token di risposta

---

1) Regge solo in parte: falsificala con un bundle “bribe-only” (coinbaseDiff alto, nessun conflitto) inviato a beaverbuild+BuilderNet; se non entra, il problema non è la porta. 
Perché: “accettato dal relay” non implica che il builder includa; i builder competono sul block value e filtrano per reputazione/allowlist; senza bribe interno puoi essere sempre sotto al vincitore anche consegnando alla porta giusta. 
Cosa misurare: per builder, tasso accettato→incluso dei tuoi bundle; inclusione di bundle bribe-only a varie percentuali del premio; tempo di risposta relay vs builder; differenza di inclusion rate tra porte per bundle identici.

2) Sì: misura indirettamente il bribe con delta saldo del feeRecipient del blocco meno la somma dei priority fees dai receipts (e meno i withdrawals nel payload); il residuo è la mancia interna. 
Perché: i trasferimenti a block.coinbase aumentano il saldo EL del feeRecipient e non compaiono nei gas fees; sottraendo fees e withdrawals ottieni i trasferimenti interni senza tracce. 
Cosa misurare: per ogni blocco con liquidazione, residual = Δbalance(coinbase, block) − Σ(gasUsed·(effectiveGasPrice−baseFee)) − Σ(withdrawals to coinbase); quota di liquidazioni con residual>0; distribuzione residual/% premio; builder che più spesso mostrano residual.

3) Prossima cosa: implementa subito pagamento a block.coinbase dentro la transazione (percentuale dinamica del premio) e invia bundle con replacement aggressivo a beaverbuild+BuilderNet; NON aumentare la priority fee dal wallet e NON aggiungere nuove porte/mercati ora. 
Perché: il tetto del wallet ti rende non competitivo; il bribe interno allinea il tuo bundle al criterio di selezione dei builder (block value) usando i ricavati della stessa tx; frammentare su più porte o alzare tip on-chain diluisce senza sbloccare inclusione. 
Cosa misurare: inclusion rate per builder prima/dopo bribe; coinbaseDiff offerto vs coinbaseDiff del vincitore (via metodo del punto 2); net profit dopo bribe; tempo alla prima presa; percentuale di bundle sostituiti (replacement) e conflitti sullo stesso target.

4) Cecità: allowlist/score del searcher lato builder (origine/signing key/relay reputation) che penalizza i tuoi bundle anche quando “accettati”. 
Perché: molti builder adottano filtri/priority per mittenti noti; 12k accettati e 0 inclusi è compatibile con gating reputazionale; senza misurare l’effetto dell’origine non vedi la causa. 
Cosa misurare: inclusione del tuo bundle bribe-only cambiando chiave/signer e relay; confronto inclusion rate della stessa payload inviata via un forwarder terzo; latenza di accettazione vs inclusione per origine; differenze di outcome per identico coinbaseDiff a parità di builder.
