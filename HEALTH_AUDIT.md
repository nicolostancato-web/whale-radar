# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-17 16:25Z · controllo automatico ogni 3h*

## 🔴 2 PROBLEMI RILEVATI

- 🔴 **bsc**: solo 21% dei token ha dati PRE-ENTRATA (156/734) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 734, trade 307) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 957 | 901 | **73%** (699) |
| bsc | 734 | 307 | **21%** (156) |
| base | 1203 | 730 | **43%** (514) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').