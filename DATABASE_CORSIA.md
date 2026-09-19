# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 16:21 UTC · giro 3 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 1 con trade nuovi (mai 12611, giovani 2423) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 0 con trade nuovi (mai 12537, giovani 730) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 11 con trade nuovi (mai 10436, giovani 754) |
| battito | ok | PULSE | 25 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 493 pool nuovi, 48734 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 105 pool nuovi, 12987 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (118 da fare, 285s) | ok | COPPIE | robinhood: +21 nuove, 20752 note in totale, ne mancano 25 (100% mappato) |
| coppie token base (93 da fare, 224s) | ok | COPPIE | base: +20 nuove, 11982 note in totale, ne mancano 45 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 67188586 e 67209762,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51521140 e 51522211, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1874 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1942/1942 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | ok | CANONICITA | robinhood: 1800 blocchi verificati, **0 ORFANI** (0.000%), 100 non letti | 184085 verificati in tutto |
| canonicita base | ok | CANONICITA | base: 2560 blocchi verificati, **0 ORFANI** (0.000%), 1900 non letti | 202560 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 8 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 89%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2114 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.