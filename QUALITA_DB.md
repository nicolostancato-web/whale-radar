# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?
*2026-09-26 19:16 UTC · controllo continuo · €0*

> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta
> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non
> si uniscono a niente, qui è un **fallimento**.

## 9 falliti · 6 da guardare · 0 non misurabili

| controllo | esito | numero | perché |
|---|---|---|---|
| base: feature scambi vive | 🔴 **FALLISCE** | 6.9 | solo 133 righe su 1923 hanno scambi veri; le altre usano il valore di ripiego |
| base: freschezza | 🔴 **FALLISCE** | 114.9 | il dato piu' recente nel campione ha 114.9 ore (letto DENTRO i file, non dalla data del file) |
| finestra dell'embargo | 🔴 **FALLISCE** | -27.7 | entrata a +3h meno ritardo 30.7h → NESSUNO scambio puo' mai entrare |
| robinhood: feature scambi vive | 🔴 **FALLISCE** | 0.0 | solo 0 righe su 797 hanno scambi veri; le altre usano il valore di ripiego |
| robinhood: freschezza | 🔴 **FALLISCE** | 135.0 | il dato piu' recente nel campione ha 135.0 ore (letto DENTRO i file, non dalla data del file) |
| robinhood: scambi orfani | 🔴 **FALLISCE** | 73.2 | 4083 file su 5577 non si uniscono a nessuna serie di prezzo |
| solana: feature scambi vive | 🔴 **FALLISCE** | 16.4 | solo 129 righe su 787 hanno scambi veri; le altre usano il valore di ripiego |
| solana: freschezza | 🔴 **FALLISCE** | 222.9 | il dato piu' recente nel campione ha 222.9 ore (letto DENTRO i file, non dalla data del file) |
| solana: scambi orfani | 🔴 **FALLISCE** | 65.3 | 3093 file su 4734 non si uniscono a nessuna serie di prezzo |
| base: scambi orfani | 🟡 **ATTENZIONE** | 29.7 | 663 file su 2232 non si uniscono a nessuna serie di prezzo |
| base: serie con scambi | 🟡 **ATTENZIONE** | 31.8 | 1569 su 4934 |
| base: timbro di acquisizione | 🟡 **ATTENZIONE** | 27.3 | 6 file su 22 fra i piu' recenti hanno il campo acq |
| robinhood: serie con scambi | 🟡 **ATTENZIONE** | 39.9 | 1494 su 3741 |
| robinhood: timbro di acquisizione | 🟡 **ATTENZIONE** | 20.0 | 2 file su 10 fra i piu' recenti hanno il campo acq |
| solana: timbro di acquisizione | 🟡 **ATTENZIONE** | 8.3 | 2 file su 24 fra i piu' recenti hanno il campo acq |
| base: entita' duplicate | 🟢 **PASSA** | 0 | 1923 righe, 1923 pool distinti |
| base: storico dalla catena | 🟢 **PASSA** | 18218 | 18218 pool con storia dalla catena |
| base: storico utile | 🟢 **PASSA** | 96.0 | sulle righe COPERTE: 288 su 300 hanno almeno 6 scambi prima dell'entrata |
| base: storico, quante righe copre | 🟢 **PASSA** | 97.1 | 1867 righe su 1923 hanno la storia dalla catena |
| robinhood: entita' duplicate | 🟢 **PASSA** | 0 | 797 righe, 797 pool distinti |
| robinhood: storico dalla catena | 🟢 **PASSA** | 27870 | 27870 pool con storia dalla catena |
| robinhood: storico utile | 🟢 **PASSA** | 83.7 | sulle righe COPERTE: 251 su 300 hanno almeno 6 scambi prima dell'entrata |
| robinhood: storico, quante righe copre | 🟢 **PASSA** | 72.5 | 578 righe su 797 hanno la storia dalla catena |
| solana: entita' duplicate | 🟢 **PASSA** | 0 | 787 righe, 787 pool distinti |
| solana: serie con scambi | 🟢 **PASSA** | 85.4 | 1641 su 1922 |

> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha
> assolto niente: ha solo taciuto.

## Il primo da riparare

> 🔴 **finestra dell'embargo** — entrata a +3h meno ritardo 30.7h → NESSUNO scambio puo' mai entrare

> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello
> che sembra significare.