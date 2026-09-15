# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-15 15:33 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 8 falliti · 4 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 6.9 | solo 133 righe su 1914 hanno scambi veri; le altre usano il valore di ripiego |
| base: serie con scambi | 🔴 **FALLISCE** | 21.6 | 972 su 4493 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 758 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 84.5 | 4083 file su 4833 non si uniscono a nessuna serie di prezzo |
| robinhood: storico utile | 🔴 **FALLISCE** | 16.3 | sulle righe COPERTE: 49 su 300 hanno almeno 6 scambi prima dell'entrata |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.3 | solo 124 righe su 762 hanno scambi veri; le altre usano il valore di ripiego |
| solana: scambi orfani | 🔴 **FALLISCE** | 76.3 | 3093 file su 4054 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 40.6 | 663 file su 1635 non si uniscono a nessuna serie di prezzo |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 33.8 | 750 su 2221 |
| solana: freschezza | 🟡 **ATTENZIONE** | 10.3 | il dato piu' recente nel campione ha 10.3 ore (letto DENTRO i file, non dalla data del file) |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 0.0 | 0 file su 19 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1914 righe, 1914 pool distinti |
| base: freschezza | 🟢 **PASSA** | 0.0 | il dato piu' recente nel campione ha 0.0 ore (letto DENTRO i file, non dalla data del file) |
| base: storico dalla catena | 🟢 **PASSA** | 4493 | 4493 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 84.0 | sulle righe COPERTE: 252 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 92.2 | 1765 righe su 1914 hanno la storia dalla catena |
| base: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 25 file su 25 fra i piu' recenti hanno il campo acq |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 758 righe, 758 pool distinti |
| robinhood: freschezza | 🟢 **PASSA** | 4.5 | il dato piu' recente nel campione ha 4.5 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: storico dalla catena | 🟢 **PASSA** | 806 | 806 pool con storia dalla catena |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 68.9 | 522 righe su 758 hanno la storia dalla catena |
| robinhood: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 10 file su 10 fra i piu' recenti hanno il campo acq |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 762 righe, 762 pool distinti |
| solana: serie con scambi | 🟢 **PASSA** | 69.4 | 961 su 1384 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.