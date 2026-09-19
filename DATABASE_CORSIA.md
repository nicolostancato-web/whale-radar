# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 13:47 UTC · giro 6 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 0 con trade nuovi (mai 12665, giovani 2421) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 2 con trade nuovi (mai 12583, giovani 750) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 11 con trade nuovi (mai 10436, giovani 754) |
| battito | ok | PULSE | 25 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 275 pool nuovi, 47302 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 88 pool nuovi, 12655 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (80 da fare, 264s) | ok | COPPIE | robinhood: +11 nuove, 20420 note in totale, ne mancano 20 (100% mappato) |
| coppie token base (74 da fare, 245s) | ok | COPPIE | base: +13 nuove, 11812 note in totale, ne mancano 27 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 67093709 e 67116236,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51516356 e 51517489, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1870 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1912/1912 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | ok | CANONICITA | robinhood: 1700 blocchi verificati, **0 ORFANI** (0.000%), 200 non letti | 177385 verificati in tutto |
| canonicita base | ok | CANONICITA | base: 2700 blocchi verificati, **0 ORFANI** (0.000%), 1960 non letti | 202700 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 8 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 95%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2233 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.