# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 15:46 UTC · giro 2 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 2 con trade nuovi (mai 12620, giovani 2428) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 0 con trade nuovi (mai 12551, giovani 730) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 9 con trade nuovi (mai 10436, giovani 754) |
| battito | ok | PULSE | 25 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 290 pool nuovi, 48241 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 81 pool nuovi, 12882 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (86 da fare, 267s) | ok | COPPIE | robinhood: +5 nuove, 20658 note in totale, ne mancano 20 (100% mappato) |
| coppie token base (78 da fare, 242s) | ok | COPPIE | base: +19 nuove, 11934 note in totale, ne mancano 35 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 67165720 e 67188585,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51519989 e 51521139, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +0 nascite vere (1874 in tutto) |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1935/1935 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | ok | CANONICITA | robinhood: 1900 blocchi verificati, **0 ORFANI** (0.000%), 0 non letti | 182285 verificati in tutto |
| canonicita base | ok | CANONICITA | base: 2640 blocchi verificati, **0 ORFANI** (0.000%), 1860 non letti | 202640 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 8 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 100%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a po |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2310 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.