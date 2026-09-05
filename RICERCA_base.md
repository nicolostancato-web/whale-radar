# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (base)
*2026-09-05 07:13 UTC · 15 segnali nuovi messi alla prova su 769 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-11%**.

## 🎯 3 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `ampiezza (voto)` | quanto oscilla il prezzo prima di entrare | **-7%** | **+4 punti** |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-8%** | **+3 punti** |
| `ampiezza / drawdown_pre (voto)` | quanto oscilla il prezzo prima di entrare RAPPORTATO a quanto è già sceso dal massimo prima di entrare | **-8%** | **+3 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `ampiezza (voto)` | quanto oscilla il prezzo prima di entrare | -7% (+4) |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -8% (+3) |
| `ampiezza / drawdown_pre (voto)` | quanto oscilla il prezzo prima di entrare RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -8% (+3) |
| `wallet_ripetuti x ampiezza (filtro)` | quanti wallet comprano più di una volta MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -10% (+2) |
| `wallet_ripetuti / ampiezza (filtro)` | quanti wallet comprano più di una volta RAPPORTATO a quanto oscilla il prezzo prima di entrare | -10% (+2) |
| `wallet_ripetuti / ampiezza (voto)` | quanti wallet comprano più di una volta RAPPORTATO a quanto oscilla il prezzo prima di entrare | -11% (+0) |
| `trade_al_minuto x compra_e_rivende (voto)` | quanto è frenetico lo scambio MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -11% (+0) |
| `trade_al_minuto / compra_e_rivende (voto)` | quanto è frenetico lo scambio RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -11% (-0) |
| `usd_primi20 x compra_e_rivende (voto)` | quanto pesano i primissimi 20 acquisti sul totale MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -12% (-0) |
| `usd_primi20 / compra_e_rivende (voto)` | quanto pesano i primissimi 20 acquisti sul totale RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -12% (-0) |
| `trade_al_minuto / compra_e_rivende (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -24% (-13) |
| `usd_primi20 / compra_e_rivende (filtro)` | quanto pesano i primissimi 20 acquisti sul totale RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -25% (-13) |
| `concentrazione_top5 x n_compratori (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quante persone diverse hanno comprato | -29% (-18) |
| `usd_primi20 x compra_e_rivende (filtro)` | quanto pesano i primissimi 20 acquisti sul totale MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -38% (-26) |
| `trade_al_minuto x compra_e_rivende (filtro)` | quanto è frenetico lo scambio MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -38% (-27) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 13 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 13 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 13 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 13 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 13 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 5 volte 4h fa (si riprova fra 8h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 13 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 13 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 13 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 13 volte 2h fa (si riprova fra 10h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.