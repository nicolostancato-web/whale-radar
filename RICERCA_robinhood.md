# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-12 14:25 UTC · 8 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-95%**.

## 🎯 4 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | **-51%** | **+45 punti** |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-67%** | **+28 punti** |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | **-78%** | **+17 punti** |
| `buy_medio x ampiezza (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | **-88%** | **+8 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | -51% (+45) |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -67% (+28) |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | -78% (+17) |
| `buy_medio x ampiezza (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -88% (+8) |
| `sbilanciamento x drawdown_pre (voto)` | quanto il denaro che entra supera quello che esce MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -95% (+0) |
| `sbilanciamento / drawdown_pre (voto)` | quanto il denaro che entra supera quello che esce RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -95% (+0) |
| `sbilanciamento / drawdown_pre (filtro)` | quanto il denaro che entra supera quello che esce RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -97% (-1) |
| `sbilanciamento x drawdown_pre (filtro)` | quanto il denaro che entra supera quello che esce MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -97% (-1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 28 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 28 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 28 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 28 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 28 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 28 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 28 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 28 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.