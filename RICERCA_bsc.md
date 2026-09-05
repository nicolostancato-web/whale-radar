# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (bsc)
*2026-09-05 12:56 UTC · 13 segnali nuovi messi alla prova su 540 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-27%**.

## 🎯 6 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | **-18%** | **+10 punti** |
| `buy_medio / trade_al_minuto (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto è frenetico lo scambio | **-18%** | **+10 punti** |
| `buy_medio / buy_grossi (filtro)` | quanto compra in media ciascuno RAPPORTATO a la quota di denaro che arriva da acquisti sopra i 500 dollari | **-18%** | **+9 punti** |
| `buy_medio / ampiezza (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto oscilla il prezzo prima di entrare | **-22%** | **+5 punti** |
| `quota_wallet_nuovi x sbilanciamento (filtro)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per quanto il denaro che entra supera quello che esce | **-23%** | **+4 punti** |
| `compra_e_rivende x sbilanciamento (filtro)` | quanti di quelli che hanno comprato stanno già rivendendo MOLTIPLICATO per quanto il denaro che entra supera quello che esce | **-24%** | **+3 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | -18% (+10) |
| `buy_medio / trade_al_minuto (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto è frenetico lo scambio | -18% (+10) |
| `buy_medio / buy_grossi (filtro)` | quanto compra in media ciascuno RAPPORTATO a la quota di denaro che arriva da acquisti sopra i 500 dollari | -18% (+9) |
| `buy_medio / ampiezza (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto oscilla il prezzo prima di entrare | -22% (+5) |
| `quota_wallet_nuovi x sbilanciamento (filtro)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -23% (+4) |
| `compra_e_rivende x sbilanciamento (filtro)` | quanti di quelli che hanno comprato stanno già rivendendo MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -24% (+3) |
| `usd_primi20 x drawdown_pre (filtro)` | quanto pesano i primissimi 20 acquisti sul totale MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -26% (+1) |
| `usd_primi20 / drawdown_pre (filtro)` | quanto pesano i primissimi 20 acquisti sul totale RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -26% (+1) |
| `n_compratori x wallet_ripetuti (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanti wallet comprano più di una volta | -26% (+1) |
| `n_compratori / wallet_ripetuti (filtro)` | quante persone diverse hanno comprato RAPPORTATO a quanti wallet comprano più di una volta | -26% (+1) |
| `quota_wallet_nuovi / sbilanciamento (filtro)` | la quota di denaro da wallet mai visti prima RAPPORTATO a quanto il denaro che entra supera quello che esce | -26% (+1) |
| `n_compratori x buy_medio (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto compra in media ciascuno | -26% (+1) |
| `n_compratori / buy_medio (filtro)` | quante persone diverse hanno comprato RAPPORTATO a quanto compra in media ciascuno | -26% (+1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 13 volte 6h fa (si riprova fra 6h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.