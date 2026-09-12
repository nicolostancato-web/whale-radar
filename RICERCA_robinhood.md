# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-12 13:35 UTC · 17 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-95%**.

## 🎯 5 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | **-51%** | **+45 punti** |
| `buy_medio x volume_ultima_su_media (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per se il volume sta accelerando proprio adesso | **-65%** | **+30 punti** |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-67%** | **+28 punti** |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | **-78%** | **+17 punti** |
| `buy_medio / volume_ultima_su_media (filtro)` | quanto compra in media ciascuno RAPPORTATO a se il volume sta accelerando proprio adesso | **-87%** | **+8 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | -51% (+45) |
| `buy_medio x volume_ultima_su_media (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per se il volume sta accelerando proprio adesso | -65% (+30) |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -67% (+28) |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | -78% (+17) |
| `buy_medio / volume_ultima_su_media (filtro)` | quanto compra in media ciascuno RAPPORTATO a se il volume sta accelerando proprio adesso | -87% (+8) |
| `quota_wallet_nuovi (voto)` | la quota di denaro da wallet mai visti prima | -95% (+1) |
| `eta_al_primo_trade (voto)` | quanto tempo passa dalla nascita al primo scambio | -95% (+1) |
| `quota_wallet_nuovi / ampiezza (voto)` | la quota di denaro da wallet mai visti prima RAPPORTATO a quanto oscilla il prezzo prima di entrare | -95% (+1) |
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | -95% (+0) |
| `quota_wallet_nuovi x ampiezza (voto)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -95% (+0) |
| `buy_grossi x volume_ultima_su_media (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per se il volume sta accelerando proprio adesso | -95% (+0) |
| `buy_grossi / volume_ultima_su_media (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a se il volume sta accelerando proprio adesso | -95% (+0) |
| `quota_wallet_nuovi (filtro)` | la quota di denaro da wallet mai visti prima | -97% (-2) |
| `quota_wallet_nuovi x ampiezza (filtro)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -97% (-2) |
| `quota_wallet_nuovi / ampiezza (filtro)` | la quota di denaro da wallet mai visti prima RAPPORTATO a quanto oscilla il prezzo prima di entrare | -97% (-2) |
| `buy_grossi x volume_ultima_su_media (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per se il volume sta accelerando proprio adesso | -97% (-2) |
| `buy_grossi / volume_ultima_su_media (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a se il volume sta accelerando proprio adesso | -97% (-2) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 28 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 28 volte 4h fa (si riprova fra 8h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 28 volte 4h fa (si riprova fra 8h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.