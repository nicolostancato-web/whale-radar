# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-05 22:24Z · controllo automatico ogni 3h*

## 🔴 4 PROBLEMI RILEVATI

- 🟠 **solana**: dati FERMI da 3h (usable 811, trade 634) → collector forse bloccato
- 🔴 **bsc**: solo 22% dei token ha dati PRE-ENTRATA (156/715) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 715, trade 307) → collector forse bloccato
- 🟠 **base**: dati FERMI da 3h (usable 1049, trade 679) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 811 | 634 | **58%** (467) |
| bsc | 715 | 307 | **22%** (156) |
| base | 1049 | 679 | **44%** (466) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').