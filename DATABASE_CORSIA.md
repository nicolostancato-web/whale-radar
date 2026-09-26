# 🧱 CORSIA DATABASE — il terreno
*2026-09-26 09:42 UTC · giro 1 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 20 con trade nuovi (mai 12611, giovani 0) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 15 con trade nuovi (mai 11434, giovani 0) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 21 con trade nuovi (mai 10436, giovani 0) |
| battito | ok | PULSE | 0 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 292 pool nuovi, 117459 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 66 pool nuovi, 40841 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (62 da fare, 180s) | ok | COPPIE | robinhood: +14 nuove, 41945 note in totale, ne mancano 17 (100% mappato) |
| coppie token base (113 da fare, 329s) | ok | COPPIE | base: +15 nuove, 21678 note in totale, ne mancano 74 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | codice -9 | ucciso: fuori tempo |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 72947610 e 72971917,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51811361 e 51812589, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +59 nascite vere (24787 in tutto) | le candele sbagliavano di -0.43 ore (mediana) | oltre la finestra di 6 or |
| nascita vera base | ok | NASCITA | base: +4 nascite vere (9742 in tutto) |
| ripara orario robinhood | ok | RIPARA | robinhood: 0 pool in questo giro, 52990/52990 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrec |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 29639/29639 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecupera |
| canonicita robinhood | ok | CANONICITA | robinhood: 1700 blocchi verificati, **0 ORFANI** (0.000%), 0 non letti | 201700 verificati in tutto |
| canonicita base | ok | CANONICITA | base: 2550 blocchi verificati, **0 ORFANI** (0.000%), 1460 non letti | 202550 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 9 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 84%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2423 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.