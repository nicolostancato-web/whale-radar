# Grok (grok-4-1-fast-reasoning) — autopsia_live — 2026-11-05

costo $0.0008, 22s, 1088 token di risposta

---

1. Sì, la lettura regge.  
I filtri “salute <1.06” + “asset che si muove” + “metà premio” fanno sì che le 31 osETH/WETH identiche (tetto di vendita) occupino stabilmente 15 slot. Quelle che cadono davvero hanno premio 130-2.700 $ e non entrano.  
Per falsificarla misura:  
- quante delle 30 candidate hanno premio = tetto (se >12-15 slot continui, è il problema);  
- rank di salute delle 5 liquidate vere vs le 30 mandate (se sistematicamente fuori dalle prime 40, il filtro salute è troppo lasco).

2. Usa Expected Value = (premio reale stimato) × (probabilità di liquidazione entro N blocchi).  
Il premio dichiarato è inquinato; la probabilità la stimi con:  
- distanza da 1.0 di salute normalizzata per la volatilità dell’asset (misurata su 40 cadute);  
- tempo da ultimo aggiornamento Chainlink che ha mosso il prezzo >0.4 %.  
Metà slot al top EV, metà ai top EV tra quelli con salute <1.03 (per catturare le code). Il tetto di vendita sparisce dal calcolo.

3. Il vincolo reale è il tempo di composizione + la larghezza di banda verso i 4 builder.  
600 ms per 30 pacchetti vuol dire che a 31-40 inizi a perdere interi slot di aggiornamento Chainlink (che arrivano ogni ~12-15 s). I relay non rifiutano per numero, ma i builder hanno limiti pratici di tx per bundle (tipicamente 200-300) e tu sei in competizione con chi manda 80-100 tx. Mandare 60-70 pacchetti è tecnicamente possibile solo se riduci il tempo di composizione sotto 250 ms.

4. Offerta identica o superiore in % non basta.  
Misura nel blocco vincente:  
- effective bribe totale (priority fee + coinbase transfer + eventuale private orderflow);  
- se il vincitore ha incluso anche la tx dell’oracolo o l’ha ricevuta privata;  
- posizione esatta nel bundle (sei stato 6/927, ma forse loro erano 2-3).  
Con 15 % vs 12.3 % mediana dovresti vincere a parità di tutto; se perdi, o il vincitore ha pagato di più sul ricavato reale o ha un canale più veloce.

5. Punto cieco: la latenza end-to-end dal momento in cui ricevi l’aggiornamento Chainlink fino all’arrivo del bundle al builder.  
Non stai misurando quanto tempo perdi tra “prezzo pubblicato” e “pacchetto firmato e spedito”. Se perdi 800-1200 ms su quel percorso, anche con EV perfetto arrivi sistematicamente dopo chi ha co-location o connessione privata.
