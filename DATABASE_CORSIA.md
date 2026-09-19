# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 08:45 UTC · giro 5 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 1 con trade nuovi (mai 12771, giovani 2445) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 2 con trade nuovi (mai 12677, giovani 750) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 12 con trade nuovi (mai 10436, giovani 774) |
| battito | ok | PULSE | 48 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 214 pool nuovi, 46070 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 80 pool nuovi, 12068 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (94 da fare, 90s) | ok | COPPIE | robinhood: +16 nuove, 19921 note in totale, ne mancano 41 (100% mappato) |
| coppie token base (2607 da fare, 420s) | ok | COPPIE | base: +22 nuove, 9456 note in totale, ne mancano 2046 (82% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 66883598 e 66908938,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51507136 e 51508385, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1840 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1846/1846 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | codice -9 | ucciso: fuori tempo |
| canonicita base | ok | CANONICITA | base: 2610 blocchi verificati, **0 ORFANI** (0.000%), 960 non letti | 202610 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 8 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 79%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok | SOPRAVVIVENZA | base: finestra al 72%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a pool att |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2643 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.