# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (solana)
*2026-09-05 05:45 UTC · 11 segnali nuovi messi alla prova su 535 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-39%**.

## 🎯 10 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `n_compratori x sbilanciamento (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto il denaro che entra supera quello che esce | **-33%** | **+6 punti** |
| `trade_al_minuto / compra_e_rivende (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | **-35%** | **+4 punti** |
| `concentrazione_top1 / compra_e_rivende (filtro)` | quanto pesa il singolo compratore più grosso RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | **-35%** | **+4 punti** |
| `quota_wallet_nuovi / compra_e_rivende (filtro)` | la quota di denaro da wallet mai visti prima RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | **-35%** | **+4 punti** |
| `n_compratori x drawdown_pre (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | **-35%** | **+4 punti** |
| `sbilanciamento (filtro)` | quanto il denaro che entra supera quello che esce | **-35%** | **+4 punti** |
| `n_compratori x volume_ultima_su_media (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per se il volume sta accelerando proprio adesso | **-35%** | **+4 punti** |
| `quota_wallet_nuovi x drawdown_pre (filtro)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | **-35%** | **+4 punti** |
| `concentrazione_top5 x sbilanciamento (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanto il denaro che entra supera quello che esce | **-36%** | **+3 punti** |
| `trade_al_minuto / quota_wallet_vincenti (filtro)` | quanto è frenetico lo scambio RAPPORTATO a la quota di denaro da wallet con almeno un successo alle spalle | **-36%** | **+3 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `n_compratori x sbilanciamento (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -33% (+6) |
| `trade_al_minuto / compra_e_rivende (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -35% (+4) |
| `concentrazione_top1 / compra_e_rivende (filtro)` | quanto pesa il singolo compratore più grosso RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -35% (+4) |
| `quota_wallet_nuovi / compra_e_rivende (filtro)` | la quota di denaro da wallet mai visti prima RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -35% (+4) |
| `n_compratori x drawdown_pre (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -35% (+4) |
| `sbilanciamento (filtro)` | quanto il denaro che entra supera quello che esce | -35% (+4) |
| `n_compratori x volume_ultima_su_media (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per se il volume sta accelerando proprio adesso | -35% (+4) |
| `quota_wallet_nuovi x drawdown_pre (filtro)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -35% (+4) |
| `concentrazione_top5 x sbilanciamento (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -36% (+3) |
| `trade_al_minuto / quota_wallet_vincenti (filtro)` | quanto è frenetico lo scambio RAPPORTATO a la quota di denaro da wallet con almeno un successo alle spalle | -36% (+3) |
| `concentrazione_top5 x n_compratori (filtro)` | quanto del denaro iniziale arriva dai 5 compratori più grossi MOLTIPLICATO per quante persone diverse hanno comprato | -40% (-1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 3 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 3 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 3 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 12 volte 10h fa (si riprova fra 2h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.