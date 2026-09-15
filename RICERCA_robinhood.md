# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-15 19:34 UTC · 13 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-96%**.

## 🎯 5 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | **-53%** | **+43 punti** |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-68%** | **+28 punti** |
| `drawdown_pre x volume_ultima_su_media (filtro)` | quanto è già sceso dal massimo prima di entrare MOLTIPLICATO per se il volume sta accelerando proprio adesso | **-78%** | **+18 punti** |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | **-79%** | **+17 punti** |
| `drawdown_pre / volume_ultima_su_media (filtro)` | quanto è già sceso dal massimo prima di entrare RAPPORTATO a se il volume sta accelerando proprio adesso | **-85%** | **+11 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | -53% (+43) |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -68% (+28) |
| `drawdown_pre x volume_ultima_su_media (filtro)` | quanto è già sceso dal massimo prima di entrare MOLTIPLICATO per se il volume sta accelerando proprio adesso | -78% (+18) |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | -79% (+17) |
| `drawdown_pre / volume_ultima_su_media (filtro)` | quanto è già sceso dal massimo prima di entrare RAPPORTATO a se il volume sta accelerando proprio adesso | -85% (+11) |
| `trade_al_minuto x wallet_ripetuti (voto)` | quanto è frenetico lo scambio MOLTIPLICATO per quanti wallet comprano più di una volta | -96% (+0) |
| `trade_al_minuto / wallet_ripetuti (voto)` | quanto è frenetico lo scambio RAPPORTATO a quanti wallet comprano più di una volta | -96% (+0) |
| `buy_grossi x ampiezza (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -96% (+0) |
| `buy_grossi / ampiezza (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a quanto oscilla il prezzo prima di entrare | -96% (+0) |
| `trade_al_minuto x wallet_ripetuti (filtro)` | quanto è frenetico lo scambio MOLTIPLICATO per quanti wallet comprano più di una volta | -97% (-1) |
| `trade_al_minuto / wallet_ripetuti (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanti wallet comprano più di una volta | -97% (-1) |
| `buy_grossi x ampiezza (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -97% (-1) |
| `buy_grossi / ampiezza (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a quanto oscilla il prezzo prima di entrare | -97% (-1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 34 volte 9h fa (si riprova fra 3h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 34 volte 9h fa (si riprova fra 3h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.