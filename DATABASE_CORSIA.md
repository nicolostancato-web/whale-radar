# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 12:28 UTC · giro 4 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 0 con trade nuovi (mai 12696, giovani 2482) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 7 con trade nuovi (mai 12611, giovani 750) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 11 con trade nuovi (mai 10436, giovani 774) |
| battito | ok | PULSE | 25 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 136 pool nuovi, 46901 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 80 pool nuovi, 12472 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (56 da fare, 224s) | ok | COPPIE | robinhood: +13 nuove, 20302 note in totale, ne mancano 9 (100% mappato) |
| coppie token base (71 da fare, 285s) | ok | COPPIE | base: +25 nuove, 11723 note in totale, ne mancano 25 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 67045808 e 67069781,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51513946 e 51515196, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1861 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1888/1888 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | ok | CANONICITA | robinhood: 1200 blocchi verificati, **0 ORFANI** (0.000%), 700 non letti | 174585 verificati in tutto |
| canonicita base | ok | CANONICITA | base: 2580 blocchi verificati, **0 ORFANI** (0.000%), 1940 non letti | 202580 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 8 | attenzione 6 | non misurabili 1 |
| sopravvivenza robinhood | ok |    il piu' scambiato che ci e' sfuggito: 19349 scambi nelle prime 6 ore |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2342 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.