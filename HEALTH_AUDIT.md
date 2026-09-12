# 🛡️ HEALTH AUDIT — watchdog dati/logica
*2026-09-12 12:41Z · controllo automatico ogni 3h*

## 🔴 4 PROBLEMI RILEVATI

- 🟠 **solana**: dati FERMI da 3h (usable 895, trade 659) → collector forse bloccato
- 🔴 **bsc**: solo 21% dei token ha dati PRE-ENTRATA (156/729) → feature forti cieche, la MEDIA non e' affidabile
- 🟠 **bsc**: dati FERMI da 3h (usable 729, trade 307) → collector forse bloccato
- 🟠 **base**: dati FERMI da 3h (usable 1146, trade 684) → collector forse bloccato

## Copertura dati per chain
| chain | token usabili | con trade | con dati PRE-ENTRATA |
|---|---|---|---|
| solana | 895 | 659 | **55%** (493) |
| bsc | 729 | 307 | **21%** (156) |
| base | 1146 | 684 | **42%** (477) |

> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?').