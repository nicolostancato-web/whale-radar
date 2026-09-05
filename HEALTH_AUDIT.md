# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-05 06:10Z · controllo automatico ogni 3h*

## 🔴 2 PROBLEMI RILEVATI

- 🔴 **bsc**: solo 22% dei token ha dati PRE-ENTRATA (156/714) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 714, trade 307) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 798 | 628 | **58%** (461) |
| bsc | 714 | 307 | **22%** (156) |
| base | 1028 | 679 | **45%** (466) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').