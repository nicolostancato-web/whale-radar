# 🧪 TEAM · RICERCA — segnali nuovi, inventati dal sistema (robinhood)
*2026-09-05 12:26 UTC · 20 segnali nuovi messi alla prova su 340 token*

**Punto di partenza:** con i segnali attuali la percentuale robusta è **-15%**.

## Nessun segnale nuovo ha superato la prova in questo giro

Nessuno dei 20 candidati alza la percentuale di almeno 3 punti.
Non è un fallimento: è la risposta onesta di oggi. Con più dati gli stessi segnali possono passare.

## Tutti i segnali provati, dal migliore al peggiore

| il segnale | cosa guarda | risultato |
|---|---|---|
| `n_compratori / compra_e_rivende (voto)` | quante persone diverse hanno comprato RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -15% (+0) |
| `wallet_ripetuti (voto)` | quanti wallet comprano più di una volta | -15% (+0) |
| `n_compratori x compra_e_rivende (voto)` | quante persone diverse hanno comprato MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -15% (+0) |
| `usd_primi20 (voto)` | quanto pesano i primissimi 20 acquisti sul totale | -15% (+0) |
| `quota_wallet_reduci (voto)` | la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -15% (+0) |
| `quota_wallet_vincenti (voto)` | la quota di denaro da wallet con almeno un successo alle spalle | -15% (+0) |
| `quota_wallet_nuovi x volume_ultima_su_media (voto)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per se il volume sta accelerando proprio adesso | -15% (-0) |
| `quota_wallet_nuovi (voto)` | la quota di denaro da wallet mai visti prima | -15% (-0) |
| `eta_al_primo_trade (voto)` | quanto tempo passa dalla nascita al primo scambio | -15% (-0) |
| `quota_wallet_nuovi / volume_ultima_su_media (voto)` | la quota di denaro da wallet mai visti prima RAPPORTATO a se il volume sta accelerando proprio adesso | -16% (-0) |
| `quota_wallet_reduci (filtro)` | la quota di denaro che arriva da wallet già visti in ALTRI token andati bene (insider) | -18% (-3) |
| `quota_wallet_vincenti (filtro)` | la quota di denaro da wallet con almeno un successo alle spalle | -18% (-3) |
| `quota_wallet_nuovi (filtro)` | la quota di denaro da wallet mai visti prima | -18% (-3) |
| `usd_primi20 (filtro)` | quanto pesano i primissimi 20 acquisti sul totale | -18% (-3) |
| `wallet_ripetuti (filtro)` | quanti wallet comprano più di una volta | -18% (-3) |
| `quota_wallet_nuovi x volume_ultima_su_media (filtro)` | la quota di denaro da wallet mai visti prima MOLTIPLICATO per se il volume sta accelerando proprio adesso | -18% (-3) |
| `quota_wallet_nuovi / volume_ultima_su_media (filtro)` | la quota di denaro da wallet mai visti prima RAPPORTATO a se il volume sta accelerando proprio adesso | -18% (-3) |
| `n_compratori x compra_e_rivende (filtro)` | quante persone diverse hanno comprato MOLTIPLICATO per quanti di quelli che hanno comprato stanno già rivendendo | -18% (-3) |
| `n_compratori / compra_e_rivende (filtro)` | quante persone diverse hanno comprato RAPPORTATO a quanti di quelli che hanno comprato stanno già rivendendo | -18% (-3) |
| `eta_al_primo_trade (filtro)` | quanto tempo passa dalla nascita al primo scambio | -18% (-3) |

## Non riprovati (la memoria del team dice che è inutile)

- `concentrazione_top5 (voto)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `concentrazione_top5 (filtro)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `concentrazione_top1 (voto)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `concentrazione_top1 (filtro)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `n_compratori (voto)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `n_compratori (filtro)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_medio (voto)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_medio (filtro)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_grossi (voto)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)
- `buy_grossi (filtro)` — già bocciato 14 volte 2h fa (si riprova fra 10h o quando i dati crescono)

> **Perché questo ruolo esiste:** l'insider su Solana l'ha inventato un umano. Qui il sistema
> costruisce da sé segnali nuovi dai dati grezzi e li mette alla prova. Uno dei mattoni è proprio
> *la quota di denaro che arriva da wallet già visti in altri token andati bene*: se l'insider conta,
> il sistema lo riscopre da solo — e su ogni chain, non solo dove ci è venuto in mente di guardare.