# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-05 07:18Z · controllo automatico ogni 3h*

## 🔴 3 PROBLEMI RILEVATI

- 🟠 **solana**: dati FERMI da 3h (usable 798, trade 628) → collector forse bloccato
- 🔴 **bsc**: solo 22% dei token ha dati PRE-ENTRATA (156/714) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 714, trade 307) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 798 | 628 | **58%** (461) |
| bsc | 714 | 307 | **22%** (156) |
| base | 1029 | 679 | **45%** (466) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').