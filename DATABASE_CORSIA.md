# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 11:49 UTC · giro 3 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 1 con trade nuovi (mai 12711, giovani 2486) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 6 con trade nuovi (mai 12624, giovani 750) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 9 con trade nuovi (mai 10436, giovani 774) |
| battito | ok | PULSE | 67 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 160 pool nuovi, 46765 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 65 pool nuovi, 12392 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (68 da fare, 232s) | ok | COPPIE | robinhood: +32 nuove, 20254 note in totale, ne mancano 8 (100% mappato) |
| coppie token base (81 da fare, 277s) | ok | COPPIE | base: +17 nuove, 11677 note in totale, ne mancano 26 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 67021144 e 67045807,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51512700 e 51513945, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1857 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1880/1880 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | codice -9 | ucciso: fuori tempo |
| canonicita base | ok | CANONICITA | base: 2660 blocchi verificati, **0 ORFANI** (0.000%), 1930 non letti | 202660 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 7 | attenzione 7 | non misurabili 0 |
| sopravvivenza robinhood | ok |    il piu' scambiato che ci e' sfuggito: 19349 scambi nelle prime 6 ore |
| sopravvivenza base | ok | SOPRAVVIVENZA | base: finestra al 28%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a pool att |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2493 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.