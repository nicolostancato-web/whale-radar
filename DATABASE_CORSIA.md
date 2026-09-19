# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 10:30 UTC · giro 1 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 1 con trade nuovi (mai 12741, giovani 2490) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 3 con trade nuovi (mai 12651, giovani 750) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 10 con trade nuovi (mai 10436, giovani 774) |
| battito | ok | PULSE | 47 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 167 pool nuovi, 46461 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 63 pool nuovi, 12237 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (158 da fare, 90s) | ok | COPPIE | robinhood: +36 nuove, 20133 note in totale, ne mancano 18 (100% mappato) |
| coppie token base (1732 da fare, 420s) | ok | COPPIE | base: +24 nuove, 11459 note in totale, ne mancano 148 (99% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 66973122 e 66999229,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51510342 e 51511599, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +1 nascite vere (1849 in tutto) | le candele sbagliavano di +13295.63 ore (mediana) | oltre la finestra di 6 ore:  |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1865/1865 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | ok | CANONICITA | robinhood: 1400 blocchi verificati, **0 ORFANI** (0.000%), 500 non letti | 170685 verificati in tutto |
| canonicita base | ok | CANONICITA | base: 2690 blocchi verificati, **0 ORFANI** (0.000%), 1790 non letti | 202690 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 9 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 25%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2467 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.