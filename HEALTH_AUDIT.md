# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-11 19:09Z · controllo automatico ogni 3h*

## 🔴 3 PROBLEMI RILEVATI

- 🟠 **solana**: dati FERMI da 3h (usable 891, trade 659) → collector forse bloccato
- 🔴 **bsc**: solo 21% dei token ha dati PRE-ENTRATA (156/728) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 728, trade 307) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 891 | 659 | **55%** (492) |
| bsc | 728 | 307 | **21%** (156) |
| base | 1140 | 685 | **41%** (472) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').