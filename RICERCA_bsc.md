# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (bsc)
*2026-09-05 11:46 UTC · 14 segnali nuovi messi alla prova su 536 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-27%**.

## 🎯 5 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | **-18%** | **+10 punti** |
| `buy_medio / buy_grossi (filtro)` | quanto compra in media ciascuno RAPPORTATO a la quota di denaro che arriva da acquisti sopra i 500 dollari | **-18%** | **+9 punti** |
| `sbilanciamento / drawdown_pre (filtro)` | quanto il denaro che entra supera quello che esce RAPPORTATO a quanto è già sceso dal massimo prima di entrare | **-23%** | **+4 punti** |
| `usd_primi20 x sbilanciamento (filtro)` | quanto pesano i primissimi 20 acquisti sul totale MOLTIPLICATO per quanto il denaro che entra supera quello che esce | **-23%** | **+4 punti** |
| `sbilanciamento x drawdown_pre (filtro)` | quanto il denaro che entra supera quello che esce MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | **-24%** | **+4 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | -18% (+10) |
| `buy_medio / buy_grossi (filtro)` | quanto compra in media ciascuno RAPPORTATO a la quota di denaro che arriva da acquisti sopra i 500 dollari | -18% (+9) |
| `sbilanciamento / drawdown_pre (filtro)` | quanto il denaro che entra supera quello che esce RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -23% (+4) |
| `usd_primi20 x sbilanciamento (filtro)` | quanto pesano i primissimi 20 acquisti sul totale MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -23% (+4) |
| `sbilanciamento x drawdown_pre (filtro)` | quanto il denaro che entra supera quello che esce MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -24% (+4) |
| `concentrazione_top1 x compra_e_rivende (filtro)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -26% (+1) |
| `concentrazione_top1 / compra_e_rivende (filtro)` | quanto pesa il singolo compratore più grosso RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -26% (+1) |
| `concentrazione_top5 x buy_grossi (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per la quota di denaro che arriva da acquisti sopra i 500 dollari | -26% (+1) |
| `concentrazione_top5 / buy_grossi (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a la quota di denaro che arriva da acquisti sopra i 500 dollari | -26% (+1) |
| `buy_grossi x quota_wallet_reduci (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -26% (+1) |
| `buy_grossi / quota_wallet_reduci (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -26% (+1) |
| `usd_primi20 / sbilanciamento (filtro)` | quanto pesano i primissimi 20 acquisti sul totale RAPPORTATO a quanto il denaro che entra supera quello che esce | -26% (+1) |
| `quota_wallet_vincenti x drawdown_pre (filtro)` | la quota di denaro da wallet con almeno un successo alle spalle MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -26% (+1) |
| `quota_wallet_vincenti / drawdown_pre (filtro)` | la quota di denaro da wallet con almeno un successo alle spalle RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -26% (+1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 13 volte 5h fa (si riprova fra 7h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.