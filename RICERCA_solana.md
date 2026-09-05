# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (solana)
*2026-09-05 03:31 UTC · 16 segnali nuovi messi alla prova su 533 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-39%**.

## 🎯 6 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `trade_al_minuto / compra_e_rivende (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | **-35%** | **+4 punti** |
| `buy_medio x usd_primi20 (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | **-35%** | **+4 punti** |
| `sbilanciamento (filtro)` | quanto il denaro che entra supera quello che esce | **-35%** | **+4 punti** |
| `sbilanciamento / ampiezza (filtro)` | quanto il denaro che entra supera quello che esce RAPPORTATO a quanto oscilla il prezzo prima di entrare | **-35%** | **+4 punti** |
| `n_compratori x volume_ultima_su_media (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per se il volume sta accelerando proprio adesso | **-35%** | **+4 punti** |
| `trade_al_minuto / ampiezza (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanto oscilla il prezzo prima di entrare | **-36%** | **+3 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `trade_al_minuto / compra_e_rivende (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -35% (+4) |
| `buy_medio x usd_primi20 (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -35% (+4) |
| `sbilanciamento (filtro)` | quanto il denaro che entra supera quello che esce | -35% (+4) |
| `sbilanciamento / ampiezza (filtro)` | quanto il denaro che entra supera quello che esce RAPPORTATO a quanto oscilla il prezzo prima di entrare | -35% (+4) |
| `n_compratori x volume_ultima_su_media (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per se il volume sta accelerando proprio adesso | -35% (+4) |
| `trade_al_minuto / ampiezza (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanto oscilla il prezzo prima di entrare | -36% (+3) |
| `n_compratori x usd_primi20 (voto)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -38% (+1) |
| `concentrazione_top5 x wallet_ripetuti (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanti wallet comprano più di una volta | -38% (+1) |
| `buy_medio / compra_e_rivende (voto)` | quanto compra in media ciascuno RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -39% (+0) |
| `concentrazione_top5 / wallet_ripetuti (voto)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a quanti wallet comprano più di una volta | -39% (+0) |
| `n_compratori / usd_primi20 (voto)` | quante persone diverse hanno comprato RAPPORTATO a quanto pesano i primissimi 20 acquisti sul totale | -39% (+0) |
| `buy_medio x compra_e_rivende (voto)` | quanto compra in media ciascuno MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -39% (-0) |
| `concentrazione_top5 x wallet_ripetuti (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanti wallet comprano più di una volta | -44% (-5) |
| `concentrazione_top5 / wallet_ripetuti (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi RAPPORTATO a quanti wallet comprano più di una volta | -44% (-5) |
| `buy_medio / wallet_ripetuti (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanti wallet comprano più di una volta | -45% (-6) |
| `buy_medio / compra_e_rivende (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -48% (-9) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 12 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 3 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 12 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 12 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 12 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 3 volte 5h fa (si riprova fra 7h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 12 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 3 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 12 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 12 volte 8h fa (si riprova fra 4h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.