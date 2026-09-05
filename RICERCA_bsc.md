# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (bsc)
*2026-09-05 05:55 UTC · 18 segnali nuovi messi alla prova su 524 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-27%**.

## 🎯 5 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `buy_medio / compra_e_rivende (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | **-17%** | **+10 punti** |
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | **-18%** | **+9 punti** |
| `buy_medio / sbilanciamento (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto il denaro che entra supera quello che esce | **-18%** | **+9 punti** |
| `buy_medio / trade_al_minuto (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto è frenetico lo scambio | **-18%** | **+9 punti** |
| `buy_medio / quota_wallet_nuovi (filtro)` | quanto compra in media ciascuno RAPPORTATO a la quota di denaro da wallet mai visti prima | **-18%** | **+9 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `buy_medio / compra_e_rivende (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -17% (+10) |
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | -18% (+9) |
| `buy_medio / sbilanciamento (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto il denaro che entra supera quello che esce | -18% (+9) |
| `buy_medio / trade_al_minuto (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto è frenetico lo scambio | -18% (+9) |
| `buy_medio / quota_wallet_nuovi (filtro)` | quanto compra in media ciascuno RAPPORTATO a la quota di denaro da wallet mai visti prima | -18% (+9) |
| `concentrazione_top5 x sbilanciamento (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -24% (+3) |
| `quota_wallet_reduci x volume_ultima_su_media (filtro)` | la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) MOLTIPLICATO per se il volume sta accelerando proprio adesso | -25% (+2) |
| `quota_wallet_reduci / volume_ultima_su_media (filtro)` | la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) RAPPORTATO a se il volume sta accelerando proprio adesso | -25% (+2) |
| `n_compratori x drawdown_pre (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -25% (+2) |
| `n_compratori / drawdown_pre (filtro)` | quante persone diverse hanno comprato RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -25% (+2) |
| `wallet_ripetuti x ampiezza (filtro)` | quanti wallet comprano più di una volta MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -25% (+2) |
| `wallet_ripetuti / ampiezza (filtro)` | quanti wallet comprano più di una volta RAPPORTATO a quanto oscilla il prezzo prima di entrare | -25% (+2) |
| `wallet_ripetuti x ampiezza (voto)` | quanti wallet comprano più di una volta MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -25% (+2) |
| `n_compratori x drawdown_pre (voto)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -26% (+0) |
| `quota_wallet_reduci x volume_ultima_su_media (voto)` | la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) MOLTIPLICATO per se il volume sta accelerando proprio adesso | -27% (+0) |
| `quota_wallet_reduci / volume_ultima_su_media (voto)` | la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) RAPPORTATO a se il volume sta accelerando proprio adesso | -27% (+0) |
| `n_compratori / drawdown_pre (voto)` | quante persone diverse hanno comprato RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -27% (+0) |
| `wallet_ripetuti / ampiezza (voto)` | quanti wallet comprano più di una volta RAPPORTATO a quanto oscilla il prezzo prima di entrare | -27% (+0) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 12 volte 11h fa (si riprova fra 1h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.