# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-15 11:02 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 8 falliti · 4 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 7.8 | solo 133 righe su 1712 hanno scambi veri; le altre usano il valore di ripiego |
| base: serie con scambi | 🔴 **FALLISCE** | 20.1 | 944 su 4703 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 680 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 85.3 | 4083 file su 4787 non si uniscono a nessuna serie di prezzo |
| robinhood: serie con scambi | 🔴 **FALLISCE** | 15.2 | 704 su 4638 |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.3 | solo 124 righe su 762 hanno scambi veri; le altre usano il valore di ripiego |
| solana: scambi orfani | 🔴 **FALLISCE** | 74.5 | 3093 file su 4150 non si uniscono a nessuna serie di prezzo |
| base: freschezza | 🟡 **ATTENZIONE** | 10.2 | il dato piu' recente nel campione ha 10.2 ore (letto DENTRO i file, non dalla data del file) |
| base: scambi orfani | 🟡 **ATTENZIONE** | 41.3 | 663 file su 1607 non si uniscono a nessuna serie di prezzo |
| solana: freschezza | 🟡 **ATTENZIONE** | 16.7 | il dato piu' recente nel campione ha 16.7 ore (letto DENTRO i file, non dalla data del file) |
| solana: serie con scambi | 🟡 **ATTENZIONE** | 53.7 | 1057 su 1970 |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1712 righe, 1712 pool distinti |
| base: storico dalla catena | 🟢 **PASSA** | 4374 | 4374 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 83.0 | sulle righe COPERTE: 249 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 96.1 | 1646 righe su 1712 hanno la storia dalla catena |
| base: timbro di acquisizione | 🟢 **PASSA** | 85.0 | 17 file su 20 fra i piu' recenti hanno il campo acq |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 680 righe, 680 pool distinti |
| robinhood: freschezza | 🟢 **PASSA** | 0.0 | il dato piu' recente nel campione ha 0.0 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: storico dalla catena | 🟢 **PASSA** | 689 | 689 pool con storia dalla catena |
| robinhood: storico utile | 🟢 **PASSA** | 66.7 | sulle righe COPERTE: 200 su 300 hanno almeno 6 scambi prima dell'entrata |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 59.6 | 405 righe su 680 hanno la storia dalla catena |
| robinhood: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 20 file su 20 fra i piu' recenti hanno il campo acq |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 762 righe, 762 pool distinti |
| solana: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 18 file su 18 fra i piu' recenti hanno il campo acq |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.