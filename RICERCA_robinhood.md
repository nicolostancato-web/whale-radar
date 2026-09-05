# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-05 18:32 UTC · 20 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-14%**.

## Nessun segnale nuovo ha superato la prova in questo giro

Nessuno dei 20 candidati alza la percentuale di almeno 3 punti.
Non è un fallimento: è la risposta onesta di oggi. Con più dati gli stessi segnali possono passare.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `buy_medio x drawdown_pre (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -12% (+2) |
| `buy_medio x wallet_ripetuti (voto)` | quanto compra in media ciascuno MOLTIPLICATO per quanti wallet comprano più di una volta | -13% (+0) |
| `buy_medio / wallet_ripetuti (voto)` | quanto compra in media ciascuno RAPPORTATO a quanti wallet comprano più di una volta | -13% (+0) |
| `buy_medio x drawdown_pre (voto)` | quanto compra in media ciascuno MOLTIPLICATO per quanto è già sceso dal massimo prima di entrare | -13% (+0) |
| `buy_grossi x usd_primi20 (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -13% (+0) |
| `buy_grossi / usd_primi20 (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a quanto pesano i primissimi 20 acquisti sul totale | -13% (+0) |
| `concentrazione_top1 x trade_al_minuto (voto)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per quanto è frenetico lo scambio | -13% (+0) |
| `concentrazione_top1 / trade_al_minuto (voto)` | quanto pesa il singolo compratore più grosso RAPPORTATO a quanto è frenetico lo scambio | -13% (+0) |
| `buy_medio / drawdown_pre (voto)` | quanto compra in media ciascuno RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -14% (+0) |
| `quota_wallet_vincenti x ampiezza (voto)` | la quota di denaro da wallet con almeno un successo alle spalle MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -14% (+0) |
| `quota_wallet_vincenti / ampiezza (voto)` | la quota di denaro da wallet con almeno un successo alle spalle RAPPORTATO a quanto oscilla il prezzo prima di entrare | -14% (+0) |
| `buy_medio / wallet_ripetuti (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanti wallet comprano più di una volta | -17% (-4) |
| `buy_medio x wallet_ripetuti (filtro)` | quanto compra in media ciascuno MOLTIPLICATO per quanti wallet comprano più di una volta | -18% (-4) |
| `buy_grossi x usd_primi20 (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -18% (-4) |
| `buy_grossi / usd_primi20 (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a quanto pesano i primissimi 20 acquisti sul totale | -18% (-4) |
| `quota_wallet_vincenti x ampiezza (filtro)` | la quota di denaro da wallet con almeno un successo alle spalle MOLTIPLICATO per quanto oscilla il prezzo prima di entrare | -18% (-4) |
| `quota_wallet_vincenti / ampiezza (filtro)` | la quota di denaro da wallet con almeno un successo alle spalle RAPPORTATO a quanto oscilla il prezzo prima di entrare | -18% (-4) |
| `concentrazione_top1 x trade_al_minuto (filtro)` | quanto pesa il singolo compratore più grosso MOLTIPLICATO per quanto è frenetico lo scambio | -18% (-4) |
| `concentrazione_top1 / trade_al_minuto (filtro)` | quanto pesa il singolo compratore più grosso RAPPORTATO a quanto è frenetico lo scambio | -18% (-4) |
| `buy_medio / drawdown_pre (filtro)` | quanto compra in media ciascuno RAPPORTATO a quanto è già sceso dal massimo prima di entrare | -34% (-21) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 14 volte 8h fa (si riprova fra 4h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.