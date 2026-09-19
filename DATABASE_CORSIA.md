# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 14:29 UTC · giro 0 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 0 con trade nuovi (mai 12650, giovani 2436) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 0 con trade nuovi (mai 12570, giovani 750) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 12 con trade nuovi (mai 10436, giovani 754) |
| battito | ok | PULSE | 26 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 227 pool nuovi, 47529 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 62 pool nuovi, 12717 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (95 da fare, 308s) | ok | COPPIE | robinhood: +28 nuove, 20505 note in totale, ne mancano 11 (100% mappato) |
| coppie token base (62 da fare, 201s) | ok | COPPIE | base: +16 nuove, 11846 note in totale, ne mancano 28 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 67116237 e 67141096,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51517490 e 51518748, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1874 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1919/1919 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | codice -9 | ucciso: fuori tempo |
| canonicita base | ok | CANONICITA | base: 2640 blocchi verificati, **0 ORFANI** (0.000%), 1940 non letti | 202640 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 8 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 82%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok | SOPRAVVIVENZA | base: finestra al 26%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a pool att |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2498 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.