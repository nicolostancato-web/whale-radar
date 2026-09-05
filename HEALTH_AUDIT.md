# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-05 03:27Z · controllo automatico ogni 3h*

## 🔴 2 PROBLEMI RILEVATI

- 🟠 **solana**: dati FERMI da 3h (usable 797, trade 628) → collector forse bloccato
- 🔴 **bsc**: solo 22% dei token ha dati PRE-ENTRATA (156/714) → feature forti cieche, la MEDIA non e' affidabile

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 797 | 628 | **58%** (461) |
| bsc | 714 | 307 | **22%** (156) |
| base | 1016 | 679 | **46%** (466) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').