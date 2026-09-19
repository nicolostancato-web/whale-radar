# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 11:07 UTC · giro 2 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 1 con trade nuovi (mai 12726, giovani 2486) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 4 con trade nuovi (mai 12638, giovani 750) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 11 con trade nuovi (mai 10436, giovani 774) |
| battito | ok | PULSE | 49 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 144 pool nuovi, 46605 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 90 pool nuovi, 12327 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (86 da fare, 154s) | ok | COPPIE | robinhood: +7 nuove, 20193 note in totale, ne mancano 27 (100% mappato) |
| coppie token base (198 da fare, 355s) | ok | COPPIE | base: +12 nuove, 11622 note in totale, ne mancano 35 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 66999230 e 67021143,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51511600 e 51512699, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1853 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1875/1875 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | ok | CANONICITA | robinhood: 1600 blocchi verificati, **0 ORFANI** (0.000%), 300 non letti | 172285 verificati in tutto |
| canonicita base | ok | CANONICITA | base: 2700 blocchi verificati, **0 ORFANI** (0.000%), 2000 non letti | 202700 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 8 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 88%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2247 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.