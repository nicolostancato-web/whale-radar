# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-12 10:20 UTC · 15 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-96%**.

## 🎯 7 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `ampiezza x drawdown_pre (filtro)` | quanto oscilla il prezzo prima di entrare MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | **+15%** | **+111 punti** |
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | **-52%** | **+44 punti** |
| `buy_medio x volume_ultima_su_media (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per se il volume sta accelerando proprio adesso | **-66%** | **+30 punti** |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-68%** | **+28 punti** |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | **-79%** | **+17 punti** |
| `buy_medio / volume_ultima_su_media (filtro)` | quanto compra in media ciascuno RAPPORTATO a se il volume sta accelerando proprio adesso | **-88%** | **+8 punti** |
| `ampiezza / drawdown_pre (filtro)` | quanto oscilla il prezzo prima di entrare RAPPORTATO a quanto è già sceso dal massimo prima di entrare | **-91%** | **+5 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `ampiezza x drawdown_pre (filtro)` | quanto oscilla il prezzo prima di entrare MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | +15% (+111) |
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | -52% (+44) |
| `buy_medio x volume_ultima_su_media (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per se il volume sta accelerando proprio adesso | -66% (+30) |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -68% (+28) |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | -79% (+17) |
| `buy_medio / volume_ultima_su_media (filtro)` | quanto compra in media ciascuno RAPPORTATO a se il volume sta accelerando proprio adesso | -88% (+8) |
| `ampiezza / drawdown_pre (filtro)` | quanto oscilla il prezzo prima di entrare RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -91% (+5) |
| `usd_primi20 x sbilanciamento (voto)` | quanto pesano i primissimi 20 acquisti sul totale MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -96% (+0) |
| `usd_primi20 / sbilanciamento (voto)` | quanto pesano i primissimi 20 acquisti sul totale RAPPORTATO a quanto il denaro che entra supera quello che esce | -96% (+0) |
| `trade_al_minuto x quota_wallet_reduci (voto)` | quanto è frenetico lo scambio MOLTIPLICATO per la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -96% (+0) |
| `trade_al_minuto / quota_wallet_reduci (voto)` | quanto è frenetico lo scambio RAPPORTATO a la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -96% (+0) |
| `usd_primi20 x sbilanciamento (filtro)` | quanto pesano i primissimi 20 acquisti sul totale MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -97% (-1) |
| `usd_primi20 / sbilanciamento (filtro)` | quanto pesano i primissimi 20 acquisti sul totale RAPPORTATO a quanto il denaro che entra supera quello che esce | -97% (-1) |
| `trade_al_minuto x quota_wallet_reduci (filtro)` | quanto è frenetico lo scambio MOLTIPLICATO per la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -97% (-1) |
| `trade_al_minuto / quota_wallet_reduci (filtro)` | quanto è frenetico lo scambio RAPPORTATO a la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -97% (-1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 28 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 28 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 28 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 28 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 28 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 28 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 28 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 28 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 28 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 28 volte 1h fa (si riprova fra 11h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.