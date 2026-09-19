# 🧱 CORSIA DATABASE — il terreno
*2026-09-19 13:10 UTC · giro 5 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 0 con trade nuovi (mai 12681, giovani 2424) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 4 con trade nuovi (mai 12597, giovani 750) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 10 con trade nuovi (mai 10436, giovani 774) |
| battito | ok | PULSE | 46 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 126 pool nuovi, 47027 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 95 pool nuovi, 12567 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (70 da fare, 244s) | ok | COPPIE | robinhood: +10 nuove, 20359 note in totale, ne mancano 14 (100% mappato) |
| coppie token base (76 da fare, 265s) | ok | COPPIE | base: +18 nuove, 11765 note in totale, ne mancano 34 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | ok | INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, e in quel caso la copertura scende. Solo raccog |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 67069782 e 67093708,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51515197 e 51516355, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +0 nascite vere (603 in tutto) |
| nascita vera base | ok | NASCITA | base: +1 nascite vere (1866 in tutto) | le candele sbagliavano di +14182.90 ore (mediana) | oltre la finestra di 6 ore:  |
| ripara orario robinhood | codice -9 | ucciso: fuori tempo |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 1900/1900 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecuperabi |
| canonicita robinhood | codice -9 | ucciso: fuori tempo |
| canonicita base | ok | CANONICITA | base: 2600 blocchi verificati, **0 ORFANI** (0.000%), 1970 non letti | 202600 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 8 | attenzione 5 | non misurabili 1 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 88%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok | SOPRAVVIVENZA | base: finestra al 6%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a pool atti |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2485 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.