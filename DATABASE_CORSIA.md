# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 15:07 UTC · giro 1 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 1 con trade nuovi (mai 12634, giovani 2433) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 0 con trade nuovi (mai 12558, giovani 730) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 8 con trade nuovi (mai 10436, giovani 754) |
| battito | ok | PULSE | 26 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 422 pool nuovi, 47951 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 84 pool nuovi, 12801 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (93 da fare, 289s) | ok | COPPIE | robinhood: +18 nuove, 20591 note in totale, ne mancano 8 (100% mappato) |
| coppie token base (71 da fare, 220s) | ok | COPPIE | base: +17 nuove, 11891 note in totale, ne mancano 26 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 67141097 e 67165719,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51518749 e 51519988, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1874 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1927/1927 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | codice -9 | ucciso: fuori tempo |
| canonicita base | ok | CANONICITA | base: 2600 blocchi verificati, **0 ORFANI** (0.000%), 1880 non letti | 202600 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 8 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 82%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2261 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.