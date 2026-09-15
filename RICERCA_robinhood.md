# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-15 19:02 UTC · 21 segnali nuovi messi alla prova su 340 token*

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
| `concentrazione_top1 x drawdown_pre (voto)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -95% (+1) |
| `n_compratori x ampiezza (voto)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -96% (+0) |
| `n_compratori / ampiezza (voto)` | quante persone diverse hanno comprato RAPPORTATO a quanto oscilla il prezzo prima di entrare | -96% (+0) |
| `concentrazione_top1 x quota_wallet_nuovi (voto)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per la quota di denaro da wallet mai visti prima | -96% (+0) |
| `concentrazione_top1 / quota_wallet_nuovi (voto)` | quanto pesa il singolo compratore più grosso RAPPORTATO a la quota di denaro da wallet mai visti prima | -96% (+0) |
| `concentrazione_top1 / drawdown_pre (voto)` | quanto pesa il singolo compratore più grosso RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -96% (+0) |
| `quota_wallet_nuovi x accelerazione_denaro (voto)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per se i soldi stanno entrando più in fretta adesso che all'inizio | -96% (+0) |
| `quota_wallet_nuovi / accelerazione_denaro (voto)` | la quota di denaro da wallet mai visti prima RAPPORTATO a se i soldi stanno entrando più in fretta adesso che all'inizio | -96% (+0) |
| `n_compratori x ampiezza (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -97% (-1) |
| `n_compratori / ampiezza (filtro)` | quante persone diverse hanno comprato RAPPORTATO a quanto oscilla il prezzo prima di entrare | -97% (-1) |
| `concentrazione_top1 x quota_wallet_nuovi (filtro)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per la quota di denaro da wallet mai visti prima | -97% (-1) |
| `concentrazione_top1 / quota_wallet_nuovi (filtro)` | quanto pesa il singolo compratore più grosso RAPPORTATO a la quota di denaro da wallet mai visti prima | -97% (-1) |
| `concentrazione_top1 x drawdown_pre (filtro)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -97% (-1) |
| `concentrazione_top1 / drawdown_pre (filtro)` | quanto pesa il singolo compratore più grosso RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -97% (-1) |
| `quota_wallet_nuovi x accelerazione_denaro (filtro)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per se i soldi stanno entrando più in fretta adesso che all'inizio | -97% (-1) |
| `quota_wallet_nuovi / accelerazione_denaro (filtro)` | la quota di denaro da wallet mai visti prima RAPPORTATO a se i soldi stanno entrando più in fretta adesso che all'inizio | -97% (-1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 34 volte 10h fa (si riprova fra 2h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 34 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 34 volte 8h fa (si riprova fra 4h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.