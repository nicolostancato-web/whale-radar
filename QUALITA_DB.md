# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-15 13:55 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 7 falliti · 3 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 7.0 | solo 133 righe su 1905 hanno scambi veri; le altre usano il valore di ripiego |
| base: serie con scambi | 🔴 **FALLISCE** | 21.5 | 963 su 4489 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 756 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 84.7 | 4083 file su 4823 non si uniscono a nessuna serie di prezzo |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.3 | solo 124 righe su 763 hanno scambi veri; le altre usano il valore di ripiego |
| solana: scambi orfani | 🔴 **FALLISCE** | 76.4 | 3093 file su 4049 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 40.8 | 663 file su 1626 non si uniscono a nessuna serie di prezzo |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 33.7 | 740 su 2197 |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 0.0 | 0 file su 8 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1905 righe, 1905 pool distinti |
| base: freschezza | 🟢 **PASSA** | 5.5 | il dato piu' recente nel campione ha 5.5 ore (letto DENTRO i file, non dalla data del file) |
| base: storico dalla catena | 🟢 **PASSA** | 4374 | 4374 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 83.0 | sulle righe COPERTE: 249 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 86.4 | 1646 righe su 1905 hanno la storia dalla catena |
| base: timbro di acquisizione | 🟢 **PASSA** | 91.7 | 22 file su 24 fra i piu' recenti hanno il campo acq |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 756 righe, 756 pool distinti |
| robinhood: freschezza | 🟢 **PASSA** | 0.3 | il dato piu' recente nel campione ha 0.3 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: storico dalla catena | 🟢 **PASSA** | 786 | 786 pool con storia dalla catena |
| robinhood: storico utile | 🟢 **PASSA** | 68.0 | sulle righe COPERTE: 204 su 300 hanno almeno 6 scambi prima dell'entrata |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 66.4 | 502 righe su 756 hanno la storia dalla catena |
| robinhood: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 5 file su 5 fra i piu' recenti hanno il campo acq |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 763 righe, 763 pool distinti |
| solana: freschezza | 🟢 **PASSA** | 4.8 | il dato piu' recente nel campione ha 4.8 ore (letto DENTRO i file, non dalla data del file) |
| solana: serie con scambi | 🟢 **PASSA** | 69.1 | 956 su 1384 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.