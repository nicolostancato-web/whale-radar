# Grok (grok-4-1-fast-reasoning) — dopo_la_scoperta — 2026-11-04

costo $0.001, 21s, 1205 token di risposta

---

**1. Prima misura (48h post-ridistribuzione)**  
Conta solo gli eventi in cui (a) l’aggiornamento Chainlink muove il prezzo ≥0,45 % e (b) la posizione ha health factor ≤1,006 prima del pacchetto. Se su 40 di questi eventi validi (≈5-6 giorni a ritmo attuale) non hai almeno 1 esecuzione con profitto netto > gas + builder fee, la strategia è morta per te. Con 52 € e 0 prese non hai buffer per aspettare di più.

**2. Occasioni reali same-block**  
Movimento mediano 0,507 % → solo posizioni con HF <1,006 possono essere liquidate nello stesso blocco. Dati i 213 eventi/30 gg e la distribuzione dei vincitori (top-3 = 79,6 %), restano realisticamente 0,4-0,7 occasioni/giorno che un nuovo arrivato possa prendere. È lotteria, non strategia. Varianti migliori:  
- Non inseguire l’oracolo; monitora le transazioni di liquidazione già incluse nei blocchi dei builder dominanti (beaverbuild 75,5 %) e back-runna solo quelle che lasciano premio >300 $ dopo slippage misurato.  
- Parziale liquidazione solo su coppie con >2 M$ di liquidità profonda (osETH/rETH, stETH/WETH).  
- Saltare del tutto same-block e puntare a posizioni già underwater da >1 blocco (priorità fee + MEV-Share). Same-block con 52 € è quasi certamente negativo.

**3. Verifica pagamento builder senza tracing**  
Su un endpoint gratuito (etherscan o blockscout) prendi:  
- `block.coinbase` balance delta tra blocco N e N-1  
- somma di tutte le `priorityFeePerGas * gasUsed` del blocco  
- somma di tutti i transfer ETH espliciti verso `block.coinbase` nei log del blocco  
Se (delta balance - priority fees totali - transfer espliciti) > 0, quasi certamente c’è un pagamento interno o bundle privato. Ripeti su 10-15 blocchi con liquidazioni >500 $; se il delta è sistematicamente positivo e assente nei blocchi senza liquidazioni grosse, hai la prova indiretta. Non serve nodo pagato.

**4. Continuare o cambiare**  
Con 52 € e zero prese in sei settimane la probabilità di battere i tre vincitori che prendono il 79,6 % è <2 %. Rapporto sforzo/ritorno peggiore di altre nicchie misurabili con lo stesso stack (flashloan + mempool + multi-builder).  
Cambia verso: **arbitraggio di sandwich su Uniswap v3 pool con TVL 5-30 M$ e fee tier 0,3 %**, usando lo stesso contratto di vendita a catena. Misura in 7 giorni:  
- quante transazioni target con slippage atteso >0,8 % e profitto netto >0,015 ETH dopo builder fee;  
- se <3 al giorno con hit-rate >8 %, abbandona anche quella. Codice già pronto, solo cambio del trigger in mempool.

**5. Difetto strutturale non nominato**  
La verifica su fork locale distribuisce sempre un contratto nuovo, quindi non testa mai il bytecode reale su mainnet (esattamente il bug di stasera). Stesso problema esiste per:  
- slippage reale su Curve/Uniswap v3 quando la liquidità è su v4 (tu non la leggi);  
- gas usato reale delle sotto-chiamate Aave + router quando il contratto è già deployato (non quando viene creato nel test).  
Aggiungi una sola verifica periodica: chiama `eth_getCode` sull’indirizzo deployato e confronta lo sha256 del bytecode con quello del sorgente compilato; se differisce, blocca tutto.
