# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-12 03:23 UTC · 14 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-96%**.

## 🎯 10 segnali NUOVI che alzano la percentuale

| il segnale | cosa guarda | porta a | guadagno |
|---|---|---|---|
| `ampiezza x drawdown_pre (filtro)` | quanto oscilla il prezzo prima di entrare MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | **+15%** | **+111 punti** |
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | **-52%** | **+44 punti** |
| `buy_medio x volume_ultima_su_media (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per se il volume sta accelerando proprio adesso | **-67%** | **+29 punti** |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | **-69%** | **+27 punti** |
| `drawdown_pre x volume_ultima_su_media (filtro)` | quanto è già sceso dal massimo prima di entrare MOLTIPLICATO per se il volume sta accelerando proprio adesso | **-78%** | **+18 punti** |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | **-79%** | **+17 punti** |
| `drawdown_pre / volume_ultima_su_media (filtro)` | quanto è già sceso dal massimo prima di entrare RAPPORTATO a se il volume sta accelerando proprio adesso | **-84%** | **+12 punti** |
| `buy_medio / volume_ultima_su_media (filtro)` | quanto compra in media ciascuno RAPPORTATO a se il volume sta accelerando proprio adesso | **-88%** | **+9 punti** |
| `buy_medio x ampiezza (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | **-88%** | **+8 punti** |
| `ampiezza / drawdown_pre (filtro)` | quanto oscilla il prezzo prima di entrare RAPPORTATO a quanto è già sceso dal massimo prima di entrare | **-91%** | **+5 punti** |

> Questi segnali non erano nella lista di partenza: li ha costruiti e verificati il sistema.
> Vanno aggiunti al cervello — è una DECISIONE, quindi passa da DECISIONS.md.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `ampiezza x drawdown_pre (filtro)` | quanto oscilla il prezzo prima di entrare MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | +15% (+111) |
| `drawdown_pre (filtro)` | quanto è già sceso dal massimo prima di entrare | -52% (+44) |
| `buy_medio x volume_ultima_su_media (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per se il volume sta accelerando proprio adesso | -67% (+29) |
| `volume_ultima_su_media (filtro)` | se il volume sta accelerando proprio adesso | -69% (+27) |
| `drawdown_pre x volume_ultima_su_media (filtro)` | quanto è già sceso dal massimo prima di entrare MOLTIPLICATO per se il volume sta accelerando proprio adesso | -78% (+18) |
| `ampiezza (filtro)` | quanto oscilla il prezzo prima di entrare | -79% (+17) |
| `drawdown_pre / volume_ultima_su_media (filtro)` | quanto è già sceso dal massimo prima di entrare RAPPORTATO a se il volume sta accelerando proprio adesso | -84% (+12) |
| `buy_medio / volume_ultima_su_media (filtro)` | quanto compra in media ciascuno RAPPORTATO a se il volume sta accelerando proprio adesso | -88% (+9) |
| `buy_medio x ampiezza (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -88% (+8) |
| `ampiezza / drawdown_pre (filtro)` | quanto oscilla il prezzo prima di entrare RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -91% (+5) |
| `quota_wallet_vincenti x wallet_ripetuti (voto)` | la quota di denaro da wallet con almeno un successo alle spalle MOLTIPLICATO per quanti wallet comprano più di una volta | -96% (+0) |
| `quota_wallet_vincenti / wallet_ripetuti (voto)` | la quota di denaro da wallet con almeno un successo alle spalle RAPPORTATO a quanti wallet comprano più di una volta | -96% (+0) |
| `quota_wallet_vincenti x wallet_ripetuti (filtro)` | la quota di denaro da wallet con almeno un successo alle spalle MOLTIPLICATO per quanti wallet comprano più di una volta | -97% (-1) |
| `quota_wallet_vincenti / wallet_ripetuti (filtro)` | la quota di denaro da wallet con almeno un successo alle spalle RAPPORTATO a quanti wallet comprano più di una volta | -97% (-1) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 27 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 27 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 27 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 27 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 27 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 27 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 27 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 27 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 27 volte 6h fa (si riprova fra 6h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 27 volte 6h fa (si riprova fra 6h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.