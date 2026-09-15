# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-15 21:38 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 7 falliti · 3 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 7.0 | solo 133 righe su 1906 hanno scambi veri; le altre usano il valore di ripiego |
| base: serie con scambi | 🔴 **FALLISCE** | 22.3 | 1013 su 4550 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 764 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 82.5 | 4083 file su 4952 non si uniscono a nessuna serie di prezzo |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.2 | solo 124 righe su 766 hanno scambi veri; le altre usano il valore di ripiego |
| solana: scambi orfani | 🔴 **FALLISCE** | 74.0 | 3093 file su 4177 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 39.6 | 663 file su 1676 non si uniscono a nessuna serie di prezzo |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 35.5 | 869 su 2446 |
| solana: freschezza | 🟡 **ATTENZIONE** | 23.6 | il dato piu' recente nel campione ha 23.6 ore (letto DENTRO i file, non dalla data del file) |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1906 righe, 1906 pool distinti |
| base: freschezza | 🟢 **PASSA** | 0.0 | il dato piu' recente nel campione ha 0.0 ore (letto DENTRO i file, non dalla data del file) |
| base: storico dalla catena | 🟢 **PASSA** | 4590 | 4590 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 90.7 | sulle righe COPERTE: 272 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 97.5 | 1858 righe su 1906 hanno la storia dalla catena |
| base: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 25 file su 25 fra i piu' recenti hanno il campo acq |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 764 righe, 764 pool distinti |
| robinhood: freschezza | 🟢 **PASSA** | 3.1 | il dato piu' recente nel campione ha 3.1 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: storico dalla catena | 🟢 **PASSA** | 809 | 809 pool con storia dalla catena |
| robinhood: storico utile | 🟢 **PASSA** | 74.3 | sulle righe COPERTE: 223 su 300 hanno almeno 6 scambi prima dell'entrata |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 68.7 | 525 righe su 764 hanno la storia dalla catena |
| robinhood: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 25 file su 25 fra i piu' recenti hanno il campo acq |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 766 righe, 766 pool distinti |
| solana: serie con scambi | 🟢 **PASSA** | 73.9 | 1084 su 1467 |
| solana: timbro di acquisizione | 🟢 **PASSA** | 54.2 | 13 file su 24 fra i piu' recenti hanno il campo acq |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.