# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (bsc)
*2026-09-05 04:37 UTC · 16 segnali nuovi messi alla prova su 524 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-27%**.

## 🎯 4 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | **-18%** | **+9 punti** |
| `buy_medio / sbilanciamento (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto il denaro che entra supera quello che esce | **-18%** | **+9 punti** |
| `buy_medio / trade_al_minuto (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto è frenetico lo scambio | **-18%** | **+9 punti** |
| `buy_medio / quota_wallet_nuovi (filtro)` | quanto compra in media ciascuno RAPPORTATO a la quota di denaro da wallet mai visti prima | **-18%** | **+9 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | -18% (+9) |
| `buy_medio / sbilanciamento (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto il denaro che entra supera quello che esce | -18% (+9) |
| `buy_medio / trade_al_minuto (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto è frenetico lo scambio | -18% (+9) |
| `buy_medio / quota_wallet_nuovi (filtro)` | quanto compra in media ciascuno RAPPORTATO a la quota di denaro da wallet mai visti prima | -18% (+9) |
| `buy_medio x sbilanciamento (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -24% (+3) |
| `sbilanciamento / accelerazione_denaro (filtro)` | quanto il denaro che entra supera quello che esce RAPPORTATO a se i soldi stanno entrando più in fretta adesso che all'inizio | -24% (+3) |
| `concentrazione_top1 x sbilanciamento (filtro)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -24% (+3) |
| `sbilanciamento x accelerazione_denaro (filtro)` | quanto il denaro che entra supera quello che esce MOLTIPLICATO per se i soldi stanno entrando più in fretta adesso che all'inizio | -24% (+3) |
| `n_compratori x sbilanciamento (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -24% (+3) |
| `buy_medio / quota_wallet_nuovi (voto)` | quanto compra in media ciascuno RAPPORTATO a la quota di denaro da wallet mai visti prima | -24% (+2) |
| `buy_medio x quota_wallet_nuovi (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per la quota di denaro da wallet mai visti prima | -25% (+2) |
| `trade_al_minuto x volume_ultima_su_media (filtro)` | quanto è frenetico lo scambio MOLTIPLICATO per se il volume sta accelerando proprio adesso | -25% (+2) |
| `trade_al_minuto / volume_ultima_su_media (filtro)` | quanto è frenetico lo scambio RAPPORTATO a se il volume sta accelerando proprio adesso | -25% (+2) |
| `trade_al_minuto / volume_ultima_su_media (voto)` | quanto è frenetico lo scambio RAPPORTATO a se il volume sta accelerando proprio adesso | -27% (+0) |
| `buy_medio x quota_wallet_nuovi (voto)` | quanto compra in media ciascuno MOLTIPLICATO per la quota di denaro da wallet mai visti prima | -27% (-0) |
| `trade_al_minuto x volume_ultima_su_media (voto)` | quanto è frenetico lo scambio MOLTIPLICATO per se il volume sta accelerando proprio adesso | -27% (-0) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.