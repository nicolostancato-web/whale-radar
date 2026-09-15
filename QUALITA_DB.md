# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-15 17:32 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 8 falliti · 5 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 7.0 | solo 133 righe su 1905 hanno scambi veri; le altre usano il valore di ripiego |
| base: serie con scambi | 🔴 **FALLISCE** | 21.7 | 983 su 4530 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 759 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 83.9 | 4083 file su 4865 non si uniscono a nessuna serie di prezzo |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.2 | solo 124 righe su 764 hanno scambi veri; le altre usano il valore di ripiego |
| solana: freschezza | 🔴 **FALLISCE** | 38.5 | il dato piu' recente nel campione ha 38.5 ore (letto DENTRO i file, non dalla data del file) |
| solana: scambi orfani | 🔴 **FALLISCE** | 74.7 | 3093 file su 4143 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 40.3 | 663 file su 1646 non si uniscono a nessuna serie di prezzo |
| base: timbro di acquisizione | 🟡 **ATTENZIONE** | 13.0 | 3 file su 23 fra i piu' recenti hanno il campo acq |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 33.7 | 782 su 2318 |
| robinhood: timbro di acquisizione | 🟡 **ATTENZIONE** | 40.0 | 8 file su 20 fra i piu' recenti hanno il campo acq |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 8.3 | 2 file su 24 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1905 righe, 1905 pool distinti |
| base: freschezza | 🟢 **PASSA** | 0.0 | il dato piu' recente nel campione ha 0.0 ore (letto DENTRO i file, non dalla data del file) |
| base: storico dalla catena | 🟢 **PASSA** | 4581 | 4581 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 88.0 | sulle righe COPERTE: 264 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 97.1 | 1849 righe su 1905 hanno la storia dalla catena |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 759 righe, 759 pool distinti |
| robinhood: freschezza | 🟢 **PASSA** | 0.9 | il dato piu' recente nel campione ha 0.9 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: storico dalla catena | 🟢 **PASSA** | 806 | 806 pool con storia dalla catena |
| robinhood: storico utile | 🟢 **PASSA** | 74.0 | sulle righe COPERTE: 222 su 300 hanno almeno 6 scambi prima dell'entrata |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 68.8 | 522 righe su 759 hanno la storia dalla catena |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 764 righe, 764 pool distinti |
| solana: serie con scambi | 🟢 **PASSA** | 72.7 | 1050 su 1444 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.