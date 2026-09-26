# 🧱 CORSIA DATABASE — il terreno
*2026-09-26 12:35 UTC · giro 5 · fetta 0*

| passo | esito | ultima cosa detta |
|---|---|---|
| scambi robinhood | ok | MULTICHAIN_TRADES | robinhood: 90 pool interrogati, 19 con trade nuovi (mai 12611, giovani 0) |
| scambi base | ok | MULTICHAIN_TRADES | base: 90 pool interrogati, 10 con trade nuovi (mai 11434, giovani 0) |
| scambi solana | ok | MULTICHAIN_TRADES | solana: 90 pool interrogati, 19 con trade nuovi (mai 10436, giovani 0) |
| battito | ok | PULSE | 0 punti scritti |
| scopritore robinhood | ok | SCOPRITORE | robinhood: 6 chiamate, 296 pool nuovi, 119065 nell'universo | sono indietro di 0 minuti dalla punta |
| scopritore base | ok | SCOPRITORE | base: 3 chiamate, 142 pool nuovi, 41258 nell'universo | sono indietro di 0 minuti dalla punta |
| coppie token robinhood (66 da fare, 176s) | ok | COPPIE | robinhood: +11 nuove, 42148 note in totale, ne mancano 17 (100% mappato) |
| coppie token base (125 da fare, 333s) | ok | COPPIE | base: +14 nuove, 21819 note in totale, ne mancano 92 (100% mappato) |
| elenco righe | ok | ELENCO_RIGHE | solana: 757 pool che diventano righe |
| integrita | codice -9 | ucciso: fuori tempo |
| censimento robinhood | ok | CENSIMENTO | robinhood: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 73048319 e 73075078,  |
| censimento base | ok | CENSIMENTO | base: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno scambiato fra i blocchi 51816450 e 51817799, e nie |
| nascita vera robinhood | ok | NASCITA | robinhood: +51 nascite vere (25125 in tutto) | le candele sbagliavano di +7.11 ore (mediana) | oltre la finestra di 6 or |
| nascita vera base | ok | NASCITA | base: +5 nascite vere (9779 in tutto) |
| ripara orario robinhood | ok | RIPARA | robinhood: 0 pool in questo giro, 53453/53453 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrec |
| ripara orario base | ok | RIPARA | base: 0 pool in questo giro, 29803/29803 in tutto | corretti 0 record (scarto mediano 0.0 min), gia' giusti 0, irrecupera |
| canonicita robinhood | ok | CANONICITA | robinhood: 1700 blocchi verificati, **0 ORFANI** (0.000%), 0 non letti | 201700 verificati in tutto |
| canonicita base | ok | CANONICITA | base: 2550 blocchi verificati, **0 ORFANI** (0.000%), 1420 non letti | 202550 verificati in tutto |
| qualita del terreno | ok | QUALITA_DB | falliti 9 | attenzione 6 | non misurabili 0 |
| sopravvivenza robinhood | ok | SOPRAVVIVENZA | robinhood: finestra al 95%, segnalibro salvato. Non classifico: un conteggio parziale direbbe «sotto soglia» a poo |
| sopravvivenza base | ok |    il piu' scambiato che ci e' sfuggito: 32384 scambi nelle prime 6 ore |
| coorte | ok | COORTE | 0 nuove, 1952 totali |

*Durata del giro: **2485 secondi**.*

> Questa corsia non costruisce strategie. Raccoglie cio' che evapora e controlla che
> serva a qualcosa. Un collettore che funziona e produce dati che non si uniscono a
> niente, qui e' un fallimento.