# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-05 16:42 UTC · 8 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-14%**.

## Nessun segnale nuovo ha superato la prova in questo giro

Nessuno dei 8 candidati alza la percentuale di almeno 3 punti.
Non è un fallimento: è la risposta onesta di oggi. Con più dati gli stessi segnali possono passare.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `trade_al_minuto x usd_primi20 (voto)` | quanto è frenetico lo scambio MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -14% (+0) |
| `trade_al_minuto / usd_primi20 (voto)` | quanto è frenetico lo scambio RAPPORTATO a quanto pesano i primissimi 20 acquisti sul totale | -14% (+0) |
| `buy_grossi x sbilanciamento (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -14% (+0) |
| `buy_grossi / sbilanciamento (voto)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a quanto il denaro che entra supera quello che esce | -14% (+0) |
| `trade_al_minuto x usd_primi20 (filtro)` | quanto è frenetico lo scambio MOLTIPLICATO per quanto pesano i primissimi 20 acquisti sul totale | -18% (-4) |
| `trade_al_minuto / usd_primi20 (filtro)` | quanto è frenetico lo scambio RAPPORTATO a quanto pesano i primissimi 20 acquisti sul totale | -18% (-4) |
| `buy_grossi / sbilanciamento (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari RAPPORTATO a quanto il denaro che entra supera quello che esce | -18% (-4) |
| `buy_grossi x sbilanciamento (filtro)` | la quota di denaro che arriva da acquisti sopra i 500 dollari MOLTIPLICATO per quanto il denaro che entra supera quello che esce | -19% (-5) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 14 volte 7h fa (si riprova fra 5h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.