# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-12 01:46Z · controllo automatico ogni 3h*

## 🔴 4 PROBLEMI RILEVATI

- 🟠 **solana**: dati FERMI da 3h (usable 893, trade 660) → collector forse bloccato
- 🔴 **bsc**: solo 21% dei token ha dati PRE-ENTRATA (156/729) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 729, trade 307) → collector forse bloccato
- 🟠 **base**: dati FERMI da 3h (usable 1141, trade 685) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 893 | 660 | **55%** (493) |
| bsc | 729 | 307 | **21%** (156) |
| base | 1141 | 685 | **42%** (474) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').