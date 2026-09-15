# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-15 15:32 UTC · 19 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-96%**.

## 🎯 4 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | **-52%** | **+44 punti** |
| `buy_medio x drawdown_pre (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | **-58%** | **+38 punti** |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-68%** | **+28 punti** |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | **-79%** | **+17 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | -52% (+44) |
| `buy_medio x drawdown_pre (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -58% (+38) |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -68% (+28) |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | -79% (+17) |
| `quota_wallet_nuovi x compra_e_rivende (voto)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -95% (+1) |
| `buy_medio / drawdown_pre (voto)` | quanto compra in media ciascuno RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -96% (+0) |
| `quota_wallet_nuovi / compra_e_rivende (voto)` | la quota di denaro da wallet mai visti prima RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -96% (+0) |
| `trade_al_minuto x sbilanciamento (voto)` | quanto è frenetico lo scambio MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -96% (+0) |
| `trade_al_minuto / sbilanciamento (voto)` | quanto è frenetico lo scambio RAPPORTATO a quanto il denaro che entra supera quello che esce | -96% (+0) |
| `concentrazione_top1 x ampiezza (voto)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -96% (+0) |
| `concentrazione_top1 / ampiezza (voto)` | quanto pesa il singolo compratore più grosso RAPPORTATO a quanto oscilla il prezzo prima di entrare | -96% (+0) |
| `buy_medio x drawdown_pre (voto)` | quanto compra in media ciascuno MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -96% (+0) |
| `trade_al_minuto x sbilanciamento (filtro)` | quanto è frenetico lo scambio MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -97% (-1) |
| `buy_medio / drawdown_pre (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -97% (-1) |
| `quota_wallet_nuovi x compra_e_rivende (filtro)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -97% (-1) |
| `quota_wallet_nuovi / compra_e_rivende (filtro)` | la quota di denaro da wallet mai visti prima RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -97% (-1) |
| `trade_al_minuto / sbilanciamento (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanto il denaro che entra supera quello che esce | -97% (-1) |
| `concentrazione_top1 x ampiezza (filtro)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -97% (-1) |
| `concentrazione_top1 / ampiezza (filtro)` | quanto pesa il singolo compratore più grosso RAPPORTATO a quanto oscilla il prezzo prima di entrare | -97% (-1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 34 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 34 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 34 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 34 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 34 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 34 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 34 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 34 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 34 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 34 volte 5h fa (si riprova fra 7h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.