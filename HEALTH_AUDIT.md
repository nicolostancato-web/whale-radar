# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-15 20:01Z · controllo automatico ogni 3h*

## 🔴 2 PROBLEMI RILEVATI

- 🔴 **bsc**: solo 21% dei token ha dati PRE-ENTRATA (156/733) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 733, trade 307) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 939 | 771 | **61%** (569) |
| bsc | 733 | 307 | **21%** (156) |
| base | 1176 | 698 | **42%** (490) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').