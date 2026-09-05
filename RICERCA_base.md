# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (base)
*2026-09-05 06:51 UTC · 15 segnali nuovi messi alla prova su 768 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-11%**.

## 🎯 3 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `ampiezza (voto)` | quanto oscilla il prezzo prima di entrare | **-7%** | **+4 punti** |
| `quota_wallet_vincenti x ampiezza (voto)` | la quota di denaro da wallet con almeno un successo alle spalle MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | **-8%** | **+3 punti** |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-8%** | **+3 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `ampiezza (voto)` | quanto oscilla il prezzo prima di entrare | -7% (+4) |
| `quota_wallet_vincenti x ampiezza (voto)` | la quota di denaro da wallet con almeno un successo alle spalle MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -8% (+3) |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -8% (+3) |
| `trade_al_minuto x quota_wallet_reduci (voto)` | quanto è frenetico lo scambio MOLTIPLICATO per la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -9% (+2) |
| `trade_al_minuto x quota_wallet_reduci (filtro)` | quanto è frenetico lo scambio MOLTIPLICATO per la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -10% (+2) |
| `trade_al_minuto / quota_wallet_reduci (voto)` | quanto è frenetico lo scambio RAPPORTATO a la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -11% (+1) |
| `n_compratori / volume_ultima_su_media (voto)` | quante persone diverse hanno comprato RAPPORTATO a se il volume sta accelerando proprio adesso | -11% (+1) |
| `n_compratori x volume_ultima_su_media (voto)` | quante persone diverse hanno comprato MOLTIPLICATO per se il volume sta accelerando proprio adesso | -12% (-0) |
| `buy_grossi / usd_primi20 (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a quanto pesano i primissimi 20 acquisti sul totale | -12% (-0) |
| `buy_grossi x usd_primi20 (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -12% (-0) |
| `buy_grossi x usd_primi20 (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -19% (-7) |
| `n_compratori / volume_ultima_su_media (filtro)` | quante persone diverse hanno comprato RAPPORTATO a se il volume sta accelerando proprio adesso | -20% (-8) |
| `trade_al_minuto / quota_wallet_reduci (filtro)` | quanto è frenetico lo scambio RAPPORTATO a la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -20% (-8) |
| `buy_grossi / usd_primi20 (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a quanto pesano i primissimi 20 acquisti sul totale | -21% (-9) |
| `n_compratori x volume_ultima_su_media (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per se il volume sta accelerando proprio adesso | -31% (-20) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 13 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 13 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 13 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 13 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 13 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 5 volte 3h fa (si riprova fra 9h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 13 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 13 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 13 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 13 volte 1h fa (si riprova fra 11h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.