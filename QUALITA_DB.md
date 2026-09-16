# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-16 02:37 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 7 falliti · 5 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 7.0 | solo 133 righe su 1912 hanno scambi veri; le altre usano il valore di ripiego |
| base: serie con scambi | 🔴 **FALLISCE** | 22.7 | 1034 su 4559 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 768 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 80.8 | 4083 file su 5052 non si uniscono a nessuna serie di prezzo |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.4 | solo 126 righe su 769 hanno scambi veri; le altre usano il valore di ripiego |
| solana: scambi orfani | 🔴 **FALLISCE** | 73.1 | 3093 file su 4231 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 39.1 | 663 file su 1697 non si uniscono a nessuna serie di prezzo |
| robinhood: freschezza | 🟡 **ATTENZIONE** | 8.2 | il dato piu' recente nel campione ha 8.2 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 38.0 | 969 su 2547 |
| solana: freschezza | 🟡 **ATTENZIONE** | 11.3 | il dato piu' recente nel campione ha 11.3 ore (letto DENTRO i file, non dalla data del file) |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 9.1 | 2 file su 22 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1912 righe, 1912 pool distinti |
| base: freschezza | 🟢 **PASSA** | 0.6 | il dato piu' recente nel campione ha 0.6 ore (letto DENTRO i file, non dalla data del file) |
| base: storico dalla catena | 🟢 **PASSA** | 4597 | 4597 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 94.0 | sulle righe COPERTE: 282 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 97.6 | 1866 righe su 1912 hanno la storia dalla catena |
| base: timbro di acquisizione | 🟢 **PASSA** | 60.9 | 14 file su 23 fra i piu' recenti hanno il campo acq |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 768 righe, 768 pool distinti |
| robinhood: storico dalla catena | 🟢 **PASSA** | 811 | 811 pool con storia dalla catena |
| robinhood: storico utile | 🟢 **PASSA** | 75.3 | sulle righe COPERTE: 226 su 300 hanno almeno 6 scambi prima dell'entrata |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 68.6 | 527 righe su 768 hanno la storia dalla catena |
| robinhood: timbro di acquisizione | 🟢 **PASSA** | 59.1 | 13 file su 22 fra i piu' recenti hanno il campo acq |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 769 righe, 769 pool distinti |
| solana: serie con scambi | 🟢 **PASSA** | 77.6 | 1138 su 1467 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.