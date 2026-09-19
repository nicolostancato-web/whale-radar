# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-19 08:38 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 8 falliti · 6 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 6.9 | solo 133 righe su 1923 hanno scambi veri; le altre usano il valore di ripiego |
| base: freschezza | 🔴 **FALLISCE** | 38.7 | il dato piu' recente nel campione ha 38.7 ore (letto DENTRO i file, non dalla data del file) |
| finestra dell'embargo | 🔴 **FALLISCE** | -27.7 | entrata a +3h meno ritardo 30.7h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 797 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 73.3 | 4083 file su 5569 non si uniscono a nessuna serie di prezzo |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.4 | solo 129 righe su 787 hanno scambi veri; le altre usano il valore di ripiego |
| solana: freschezza | 🔴 **FALLISCE** | 38.7 | il dato piu' recente nel campione ha 38.7 ore (letto DENTRO i file, non dalla data del file) |
| solana: scambi orfani | 🔴 **FALLISCE** | 65.3 | 3093 file su 4734 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 31.0 | 663 file su 2136 non si uniscono a nessuna serie di prezzo |
| base: serie con scambi | 🟡 **ATTENZIONE** | 29.9 | 1473 su 4934 |
| base: timbro di acquisizione | 🟡 **ATTENZIONE** | 11.8 | 2 file su 17 fra i piu' recenti hanno il campo acq |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 39.7 | 1486 su 3741 |
| robinhood: timbro di acquisizione | 🟡 **ATTENZIONE** | 13.3 | 2 file su 15 fra i piu' recenti hanno il campo acq |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 16.7 | 4 file su 24 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1923 righe, 1923 pool distinti |
| base: storico dalla catena | 🟢 **PASSA** | 4597 | 4597 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 95.0 | sulle righe COPERTE: 285 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 97.1 | 1867 righe su 1923 hanno la storia dalla catena |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 797 righe, 797 pool distinti |
| robinhood: freschezza | 🟢 **PASSA** | 3.4 | il dato piu' recente nel campione ha 3.4 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: storico dalla catena | 🟢 **PASSA** | 865 | 865 pool con storia dalla catena |
| robinhood: storico utile | 🟢 **PASSA** | 86.3 | sulle righe COPERTE: 259 su 300 hanno almeno 6 scambi prima dell'entrata |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 72.5 | 578 righe su 797 hanno la storia dalla catena |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 787 righe, 787 pool distinti |
| solana: serie con scambi | 🟢 **PASSA** | 85.4 | 1641 su 1922 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 30.7h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.