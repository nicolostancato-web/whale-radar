# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 09:49 UTC · giro 0 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 3 con trade nuovi (mai 12757, giovani 2475) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 5 con trade nuovi (mai 12664, giovani 750) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 12 con trade nuovi (mai 10436, giovani 774) |
| battito | ok | PULSE | 27 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 224 pool nuovi, 46294 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 106 pool nuovi, 12174 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (79 da fare, 90s) | ok | COPPIE | robinhood: +41 nuove, 19992 note in totale, ne mancano 9 (100% mappato) |
| coppie token base (1715 da fare, 420s) | ok | COPPIE | base: +24 nuove, 9875 note in totale, ne mancano 1674 (86% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 66908939 e 66973121,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51508386 e 51510341, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1844 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1859/1859 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | codice -9 | ucciso: fuori tempo |
| canonicita base | ok | CANONICITA | base: 2620 blocchi verificati, **0 ORFANI** (0.000%), 1940 non letti | 202620 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 7 | attenzione 7 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 87%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2693 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.