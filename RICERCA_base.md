# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (base)
*2026-09-05 16:34 UTC · 15 segnali nuovi messi alla prova su 775 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-12%**.

## 🎯 3 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-4%** | **+8 punti** |
| `ampiezza (voto)` | quanto oscilla il prezzo prima di entrare | **-6%** | **+7 punti** |
| `wallet_ripetuti x sbilanciamento (filtro)` | quanti wallet comprano più di una volta MOLTIPLICATO per quanto il denaro che entra supera quello che esce | **-8%** | **+4 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -4% (+8) |
| `ampiezza (voto)` | quanto oscilla il prezzo prima di entrare | -6% (+7) |
| `wallet_ripetuti x sbilanciamento (filtro)` | quanti wallet comprano più di una volta MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -8% (+4) |
| `concentrazione_top5 x quota_wallet_nuovi (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per la quota di denaro da wallet mai visti prima | -11% (+1) |
| `concentrazione_top5 / quota_wallet_nuovi (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a la quota di denaro da wallet mai visti prima | -12% (+0) |
| `trade_al_minuto x quota_wallet_vincenti (voto)` | quanto è frenetico lo scambio MOLTIPLICATO per la quota di denaro da wallet con almeno un successo alle spalle | -12% (+0) |
| `trade_al_minuto x quota_wallet_vincenti (filtro)` | quanto è frenetico lo scambio MOLTIPLICATO per la quota di denaro da wallet con almeno un successo alle spalle | -12% (+0) |
| `trade_al_minuto / quota_wallet_vincenti (voto)` | quanto è frenetico lo scambio RAPPORTATO a la quota di denaro da wallet con almeno un successo alle spalle | -12% (-0) |
| `trade_al_minuto / usd_primi20 (voto)` | quanto è frenetico lo scambio RAPPORTATO a quanto pesano i primissimi 20 acquisti sul totale | -12% (-0) |
| `trade_al_minuto x usd_primi20 (voto)` | quanto è frenetico lo scambio MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -14% (-2) |
| `trade_al_minuto / quota_wallet_vincenti (filtro)` | quanto è frenetico lo scambio RAPPORTATO a la quota di denaro da wallet con almeno un successo alle spalle | -23% (-10) |
| `trade_al_minuto x usd_primi20 (filtro)` | quanto è frenetico lo scambio MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -25% (-13) |
| `trade_al_minuto / usd_primi20 (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanto pesano i primissimi 20 acquisti sul totale | -28% (-16) |
| `concentrazione_top5 x quota_wallet_nuovi (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per la quota di denaro da wallet mai visti prima | -30% (-17) |
| `concentrazione_top5 / quota_wallet_nuovi (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a la quota di denaro da wallet mai visti prima | -30% (-18) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 13 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 13 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 13 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 13 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 13 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 6 volte 1h fa (si riprova fra 11h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 13 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 13 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 13 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 13 volte 11h fa (si riprova fra 1h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.