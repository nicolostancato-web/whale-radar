# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-15 15:24 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 8 falliti · 5 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 7.0 | solo 133 righe su 1912 hanno scambi veri; le altre usano il valore di ripiego |
| base: serie con scambi | 🔴 **FALLISCE** | 21.6 | 972 su 4493 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 756 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 84.5 | 4083 file su 4832 non si uniscono a nessuna serie di prezzo |
| robinhood: storico utile | 🔴 **FALLISCE** | 16.3 | sulle righe COPERTE: 49 su 300 hanno almeno 6 scambi prima dell'entrata |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.3 | solo 124 righe su 762 hanno scambi veri; le altre usano il valore di ripiego |
| solana: scambi orfani | 🔴 **FALLISCE** | 76.3 | 3093 file su 4054 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 40.6 | 663 file su 1635 non si uniscono a nessuna serie di prezzo |
| robinhood: freschezza | 🟡 **ATTENZIONE** | 7.1 | il dato piu' recente nel campione ha 7.1 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 33.7 | 749 su 2221 |
| solana: freschezza | 🟡 **ATTENZIONE** | 10.2 | il dato piu' recente nel campione ha 10.2 ore (letto DENTRO i file, non dalla data del file) |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 0.0 | 0 file su 18 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1912 righe, 1912 pool distinti |
| base: freschezza | 🟢 **PASSA** | 0.0 | il dato piu' recente nel campione ha 0.0 ore (letto DENTRO i file, non dalla data del file) |
| base: storico dalla catena | 🟢 **PASSA** | 4493 | 4493 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 84.0 | sulle righe COPERTE: 252 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 92.3 | 1765 righe su 1912 hanno la storia dalla catena |
| base: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 25 file su 25 fra i piu' recenti hanno il campo acq |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 756 righe, 756 pool distinti |
| robinhood: storico dalla catena | 🟢 **PASSA** | 806 | 806 pool con storia dalla catena |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 69.0 | 522 righe su 756 hanno la storia dalla catena |
| robinhood: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 11 file su 11 fra i piu' recenti hanno il campo acq |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 762 righe, 762 pool distinti |
| solana: serie con scambi | 🟢 **PASSA** | 69.4 | 961 su 1384 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.