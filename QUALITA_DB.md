# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-15 13:27 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 8 falliti · 3 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 7.0 | solo 133 righe su 1905 hanno scambi veri; le altre usano il valore di ripiego |
| base: freschezza | 🔴 **FALLISCE** | 47.4 | il dato piu' recente nel campione ha 47.4 ore (letto DENTRO i file, non dalla data del file) |
| base: serie con scambi | 🔴 **FALLISCE** | 21.5 | 963 su 4481 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 755 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 84.8 | 4083 file su 4815 non si uniscono a nessuna serie di prezzo |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.3 | solo 124 righe su 762 hanno scambi veri; le altre usano il valore di ripiego |
| solana: scambi orfani | 🔴 **FALLISCE** | 76.7 | 3093 file su 4035 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 40.8 | 663 file su 1626 non si uniscono a nessuna serie di prezzo |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 33.6 | 732 su 2176 |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 0.0 | 0 file su 11 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1905 righe, 1905 pool distinti |
| base: storico dalla catena | 🟢 **PASSA** | 4374 | 4374 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 83.0 | sulle righe COPERTE: 249 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 86.4 | 1646 righe su 1905 hanno la storia dalla catena |
| base: timbro di acquisizione | 🟢 **PASSA** | 91.7 | 22 file su 24 fra i piu' recenti hanno il campo acq |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 755 righe, 755 pool distinti |
| robinhood: freschezza | 🟢 **PASSA** | 4.2 | il dato piu' recente nel campione ha 4.2 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: storico dalla catena | 🟢 **PASSA** | 779 | 779 pool con storia dalla catena |
| robinhood: storico utile | 🟢 **PASSA** | 68.0 | sulle righe COPERTE: 204 su 300 hanno almeno 6 scambi prima dell'entrata |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 65.6 | 495 righe su 755 hanno la storia dalla catena |
| robinhood: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 6 file su 6 fra i piu' recenti hanno il campo acq |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 762 righe, 762 pool distinti |
| solana: freschezza | 🟢 **PASSA** | 3.7 | il dato piu' recente nel campione ha 3.7 ore (letto DENTRO i file, non dalla data del file) |
| solana: serie con scambi | 🟢 **PASSA** | 68.3 | 942 su 1380 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.