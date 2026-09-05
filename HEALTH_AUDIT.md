# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-04 22:23Z · controllo automatico ogni 3h*

## 🔴 4 PROBLEMI RILEVATI

- 🟠 **solana**: dati FERMI da 3h (usable 797, trade 628) → collector forse bloccato
- 🔴 **bsc**: solo 22% dei token ha dati PRE-ENTRATA (156/713) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 713, trade 307) → collector forse bloccato
- 🟠 **base**: dati FERMI da 3h (usable 1013, trade 679) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 797 | 628 | **58%** (461) |
| bsc | 713 | 307 | **22%** (156) |
| base | 1013 | 679 | **46%** (466) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').