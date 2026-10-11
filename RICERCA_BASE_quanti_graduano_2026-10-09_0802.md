# Ricerca Grok — Base — quanti_graduano

Modello grok-4.7. Costo: ZERO (abbonamento). Tempo: 175s. 2/2 con risposta.

---

### Che percentuale delle monete lanciate sulla principale piattaforma di Base arriva alla graduazione? Dammi il numero e come e' stato calcolato.

Cerco il dato aggiornato sulla piattaforma principale di lancio token su Base e come viene calcolata la quota che arriva alla graduazione.Le fee indicano o1, Bankr e Clanker come piattaforme più grandi su Base. Controllo quale ha davvero una graduazione e se esiste un tasso pubblicato.

### Esistono misure pubblicate su quanto sale in mediana una moneta di Base dopo la graduazione? Col metodo dichiarato e il link.

Cerco studi e dashboard pubblicati sul rendimento mediano dei token su Base dopo la graduazione, con metodo e fonte.I dati trovati finora misurano soprattutto il tasso di graduazione, non il rialzo mediano dopo. Cerco studi e dashboard che riportino il multiplo di prezzo post-graduazione, in particolare su Base.No. Non esiste una misura pubblicata della **salita mediana dopo la graduazione** per le monete su Base, con un campione e un metodo dichiarati. I numeri che circolano misurano altro.

**Quello che c’è, e non è una salita su Base**

Lo studio con metodo esplicito è di MemeFees, e il risultato è una **discesa**, su Solana. La mediana di pump.fun a 24 ore è **0,04×** la market cap di graduazione: resta il **3,8%**, cioè **−96,2%** (n = 28.960, graduazioni dal 3 settembre all’8 ottobre 2026). A 1 ora la mediana è **0,17×** (n = 30.072); a 7 giorni **0,05×** (n = 7.407).

Metodo, dalla pagina dello studio e dal catalogo metriche:

- Graduazione = la bonding curve si riempie e la liquidità passa a una pool.
- Per ogni token si registra la market cap alla graduazione, poi di nuovo a +1 h, +24 h e +7 giorni, da DexScreener.
- Entrambe le osservazioni devono arrivare entro 10 minuti dall’evento o dalla scadenza. Quelle in ritardo e i tempi stimati sono esclusi.
- Il multiplo mediano è la mediana di (market cap all’orizzonte ÷ market cap alla graduazione).
- Escluse le market cap di graduazione sotto 1.000 $. Un check senza pool non conta né come successo né come fallimento.

Virtuals, l’unico launchpad su Base con una curva che loro seguono, in quella finestra ha **0 graduazioni** (almeno 343 lanci in 7 giorni), quindi nessuna mediana. Clanker, Zora e Flaunch sono fuori dal calcolo: partono già in pool, senza graduazione.

- Studio: https://memefees.com/research/memecoin-survival-2026
- Tabella viva: https://memefees.com/stats/survival
- Metodo: https://memefees.com/methodology

**Il 64× su Base è il percorso fino alla graduazione, non dopo, e non è una mediana**

Blokz (15 giugno 2026) legge il contratto Bonding di Virtuals su Base (`assetRate = 5000`, `gradThreshold = 125.000.000` token, `k = 6e12`). Riserva virtuale iniziale 6.000 VIRTUAL su 1 miliardo di token. Alla soglia la riserva virtuale è 48.000 VIRTUAL, di cui **42.000 raccolti davvero**. Lo spot sulla curva è **64×** il prezzo di apertura. La pool Uniswap si apre a 42.000 / 125.000.000, cioè **12,5% sotto** l’ultimo prezzo della curva, perché i 6.000 VIRTUAL virtuali non entrano nella pool. È aritmetica del contratto, uguale per ogni token, non la mediana di cosa fa il prezzo dopo.

https://blokz.dev/articles/agent-token-bonding-curve/

**Il +54% mediano non è la graduazione della curva**

Fundstrat (PDF del 27 ottobre 2025, fonti dichiarate «Virtuals, Dune, Fundstrat») scrive un rendimento mediano del **+54%** e medio del **+646%** «from launch price» per i **Genesis launch** (pledge a punti, non bonding curve). Nella stessa tabella: partecipazione mediana 2.187 wallet, oversubscription mediana 310%, 0,002 $ per punto. Il PDF non pubblica la data del prezzo né il numero di lanci nel campione.

https://fundstrat.com/wp-content/uploads/2025/10/Virtuals_FSGA_10.27.25_Final.pdf
