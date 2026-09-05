# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-05 18:34Z · controllo automatico ogni 3h*

## 🔴 3 PROBLEMI RILEVATI

- 🟠 **solana**: dati FERMI da 3h (usable 809, trade 633) → collector forse bloccato
- 🔴 **bsc**: solo 22% dei token ha dati PRE-ENTRATA (156/715) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 715, trade 307) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 809 | 633 | **58%** (466) |
| bsc | 715 | 307 | **22%** (156) |
| base | 1042 | 679 | **45%** (466) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').