# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-15 15:51 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 8 falliti · 3 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 7.0 | solo 133 righe su 1913 hanno scambi veri; le altre usano il valore di ripiego |
| base: serie con scambi | 🔴 **FALLISCE** | 21.6 | 972 su 4503 |
| finestra dell'embargo | 🔴 **FALLISCE** | -32.4 | entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 758 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 84.4 | 4083 file su 4836 non si uniscono a nessuna serie di prezzo |
| robinhood: storico utile | 🔴 **FALLISCE** | 17.7 | sulle righe COPERTE: 53 su 300 hanno almeno 6 scambi prima dell'entrata |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.3 | solo 124 righe su 762 hanno scambi veri; le altre usano il valore di ripiego |
| solana: scambi orfani | 🔴 **FALLISCE** | 75.4 | 3093 file su 4103 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 40.6 | 663 file su 1635 non si uniscono a nessuna serie di prezzo |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 33.4 | 753 su 2255 |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 28.0 | 7 file su 25 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1913 righe, 1913 pool distinti |
| base: freschezza | 🟢 **PASSA** | 0.0 | il dato piu' recente nel campione ha 0.0 ore (letto DENTRO i file, non dalla data del file) |
| base: storico dalla catena | 🟢 **PASSA** | 4493 | 4493 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 85.3 | sulle righe COPERTE: 256 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 92.1 | 1761 righe su 1913 hanno la storia dalla catena |
| base: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 25 file su 25 fra i piu' recenti hanno il campo acq |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 758 righe, 758 pool distinti |
| robinhood: freschezza | 🟢 **PASSA** | 1.7 | il dato piu' recente nel campione ha 1.7 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: storico dalla catena | 🟢 **PASSA** | 806 | 806 pool con storia dalla catena |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 68.9 | 522 righe su 758 hanno la storia dalla catena |
| robinhood: timbro di acquisizione | 🟢 **PASSA** | 100.0 | 8 file su 8 fra i piu' recenti hanno il campo acq |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 762 righe, 762 pool distinti |
| solana: freschezza | 🟢 **PASSA** | 0.5 | il dato piu' recente nel campione ha 0.5 ore (letto DENTRO i file, non dalla data del file) |
| solana: serie con scambi | 🟢 **PASSA** | 71.9 | 1010 su 1404 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 35.4h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.