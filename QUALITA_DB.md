# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-16 01:02 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 7 falliti · 4 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 7.0 | solo 133 righe su 1906 hanno scambi veri; le altre usano il valore di ripiego |
| base: serie con scambi | 🔴 **FALLISCE** | 22.4 | 1022 su 4559 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 770 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 81.4 | 4083 file su 5016 non si uniscono a nessuna serie di prezzo |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.1 | solo 124 righe su 769 hanno scambi veri; le altre usano il valore di ripiego |
| solana: scambi orfani | 🔴 **FALLISCE** | 73.6 | 3093 file su 4200 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 39.3 | 663 file su 1685 non si uniscono a nessuna serie di prezzo |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 37.2 | 933 su 2507 |
| solana: freschezza | 🟡 **ATTENZIONE** | 19.8 | il dato piu' recente nel campione ha 19.8 ore (letto DENTRO i file, non dalla data del file) |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 4.0 | 1 file su 25 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1906 righe, 1906 pool distinti |
| base: freschezza | 🟢 **PASSA** | 0.1 | il dato piu' recente nel campione ha 0.1 ore (letto DENTRO i file, non dalla data del file) |
| base: storico dalla catena | 🟢 **PASSA** | 4597 | 4597 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 92.7 | sulle righe COPERTE: 278 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 97.8 | 1865 righe su 1906 hanno la storia dalla catena |
| base: timbro di acquisizione | 🟢 **PASSA** | 52.2 | 12 file su 23 fra i piu' recenti hanno il campo acq |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 770 righe, 770 pool distinti |
| robinhood: freschezza | 🟢 **PASSA** | 0.9 | il dato piu' recente nel campione ha 0.9 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: storico dalla catena | 🟢 **PASSA** | 809 | 809 pool con storia dalla catena |
| robinhood: storico utile | 🟢 **PASSA** | 75.3 | sulle righe COPERTE: 226 su 300 hanno almeno 6 scambi prima dell'entrata |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 68.2 | 525 righe su 770 hanno la storia dalla catena |
| robinhood: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 25 file su 25 fra i piu' recenti hanno il campo acq |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 769 righe, 769 pool distinti |
| solana: serie con scambi | 🟢 **PASSA** | 75.5 | 1107 su 1467 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.