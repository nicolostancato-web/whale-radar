# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-16 00:09 UTC · 20 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-96%**.

## 🎯 4 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | **-54%** | **+42 punti** |
| `buy_medio x drawdown_pre (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | **-59%** | **+37 punti** |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-69%** | **+27 punti** |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | **-80%** | **+17 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | -54% (+42) |
| `buy_medio x drawdown_pre (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -59% (+37) |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -69% (+27) |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | -80% (+17) |
| `concentrazione_top5 x compra_e_rivende (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -96% (+1) |
| `concentrazione_top5 / wallet_ripetuti (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a quanti wallet comprano più di una volta | -96% (+1) |
| `concentrazione_top5 / compra_e_rivende (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -96% (+0) |
| `concentrazione_top5 x wallet_ripetuti (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanti wallet comprano più di una volta | -96% (+0) |
| `concentrazione_top5 x trade_al_minuto (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanto è frenetico lo scambio | -96% (+0) |
| `concentrazione_top5 / trade_al_minuto (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a quanto è frenetico lo scambio | -96% (+0) |
| `sbilanciamento x ampiezza (voto)` | quanto il denaro che entra supera quello che esce MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -96% (+0) |
| `sbilanciamento / ampiezza (voto)` | quanto il denaro che entra supera quello che esce RAPPORTATO a quanto oscilla il prezzo prima di entrare | -96% (+0) |
| `sbilanciamento x ampiezza (filtro)` | quanto il denaro che entra supera quello che esce MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -97% (-1) |
| `sbilanciamento / ampiezza (filtro)` | quanto il denaro che entra supera quello che esce RAPPORTATO a quanto oscilla il prezzo prima di entrare | -97% (-1) |
| `concentrazione_top5 x compra_e_rivende (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -98% (-1) |
| `concentrazione_top5 / compra_e_rivende (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -98% (-1) |
| `concentrazione_top5 x wallet_ripetuti (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanti wallet comprano più di una volta | -98% (-1) |
| `concentrazione_top5 / wallet_ripetuti (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a quanti wallet comprano più di una volta | -98% (-1) |
| `concentrazione_top5 x trade_al_minuto (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanto è frenetico lo scambio | -98% (-1) |
| `concentrazione_top5 / trade_al_minuto (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a quanto è frenetico lo scambio | -98% (-1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 35 volte 3h fa (si riprova fra 9h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 35 volte 3h fa (si riprova fra 9h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 35 volte 3h fa (si riprova fra 9h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 35 volte 3h fa (si riprova fra 9h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 35 volte 3h fa (si riprova fra 9h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 35 volte 3h fa (si riprova fra 9h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 35 volte 3h fa (si riprova fra 9h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 35 volte 3h fa (si riprova fra 9h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 35 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 35 volte 1h fa (si riprova fra 11h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.