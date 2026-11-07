# 🔭 REVISIONE ESTERNA (Astra)
*2026-09-11 07:50 UTC · una volta al giorno · sola lettura · nessun accesso al sigillo*

> Serve contro l errore che non abbiamo ancora fatto: il revisore interno l ho scritto io,
> quindi controlla i modi di illudersi che avevo gia immaginato. Questo no.

1. ASSUNZIONE INVISIBILE

State trattando il ritardo reale di osservazione di **3–7 ore** come un costo uniforme, non come possibile cancellazione del segnale. Ma il metodo dichiara orizzonti di **5m/30m/2h/6h/24h** (sez. 6.8): per 5m, 30m e 2h il bot può arrivare dopo che l’orizzonte è già finito. Verificate, sui **349 trade Base**, rendimento e squilibrio buy/sell fra timestamp dell’evento e prima entrata realmente eleggibile; confrontateli con il rendimento dopo l’entrata, appaiando età e liquidità. Se il movimento sta prima dell’entrata, LOOP 1 sta valutando segnali che il vostro ritardo rende economicamente morti.

2. VERDETTO DI TRAIETTORIA

**NO.** Base è la migliore: **+4% media, +1% robusta**, cioè **7 punti** sotto il +8% netto; nella metà recente è **-21%** (PERCENTUALE.md). Dal 9 settembre al 3 ottobre restano **24 giorni**, ma Base raggiunge 25 giornate solo il **29 settembre**: restano quattro giorni. Il verdetto cambia solo con una configurazione congelata che passi il suo holdout e tutti i criteri già scritti; non con altro screening.

3. MOSSE IN ORDINE

1. Congelate oggi una sola configurazione Base e applicate congiuntamente i cancelli già scritti: **≥10% netto, t≥2, 25 gruppi, 250 righe, costi condizionati all’uscita e trappole -100%** (VERDETTO.md), più il cancello dichiarato di **+40% robusta su 150+ token** (PERCENTUALE.md). I due documenti oggi prescrivono soglie incompatibili: lasciarle alternative significa scegliere il traguardo dopo il risultato.  
   Dati: holdout sigillato, 349 trade Base, dati sicurezza e costi.  
   Morte: il candidato è morto il 29 settembre se fallisce anche un solo cancello, oppure se il costo Base all’uscita non è identificabile.  
   Costo: 20 giorni. È prima perché produce un sì verificabile o una chiusura pulita.

2. In un giorno, fate il test di decadimento da ritardo sui dati di ricerca, separato dal candidato congelato: per ogni segnale Base calcolate rendimento pre-entrata durante le **3–7 ore** e rendimento netto post-entrata a 2h/6h, contro controlli appaiati.  
   Dati: candele minuto, trade wallet/importo, ritardo registrato, liquidità. Non è copy-trading, flusso-cluster o uno dei quattro segnali di domanda morti (sez. 4): non cerca un nuovo ingresso, verifica se il vostro ingresso esiste ancora.  
   Morte: l’ipotesi “il segnale sopravvive al ritardo” è morta se, su **25 gruppi** giorno-creator, l’extra-rendimento netto post-entrata è ≤0.  
   Costo: 1 giorno. Viene dopo il congelamento: non deve contaminare l’holdout.

4. ANGOLO DEL GIORNO

Nei **34 casi** del gemello, i risultati a 5m e 30m sono riportati nonostante il ritardo reale sia 3–7 ore (SPERIMENTALE.md; sez. 6.8). Non riaprite l’idea morta: verificate invece chi si muove per primo ricostruendo il timestamp in cui il bot avrebbe potuto conoscere l’esplosione sull’altra chain. Se l’entrata eleggibile cade dopo 2h nella maggioranza dei 34 casi, quei primi tre orizzonti non erano osservabili, non evidenza economica.

5. RICHIAMO

Il controllo richiesto il 4 settembre non è stato fatto: allora c’erano **zero misure durante lo stop**; ora COSTO_MODELLO.md dice ancora quotazioni Jupiter su token vivi “in calma”. Finché non fissate taglia $25, timestamp e regime di vendita, Base e Robinhood non hanno un costo di fuga dimostrato.
