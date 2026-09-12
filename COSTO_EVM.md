# ⛓️💸 IL COSTO SU BASE E ROBINHOOD — letto dalla catena, non prestato da un altro mercato
*2026-09-12 14:38 UTC · taglia $25 · RPC pubblici · €0*

> Su Robinhood non esiste un Jupiter a cui chiedere un preventivo. Ma la catena non va
> interrogata da un servizio: **si legge**. Chiediamo alla coppia le sue riserve; se risponde,
> è un pool a prodotto costante — e il conto con la commissione dello 0,3% **non è una stima**,
> è esattamente ciò che il contratto calcola quando esegue lo scambio.

> *(Ieri la stima dalla riserva è stata bocciata contro Jupiter: là erano curve di lancio e
> percorsi multipli, dove la riserva non spiega il prezzo. Qui rifacciamo il calcolo del
> contratto, non indoviniamo il suo risultato.)*

| chain | pool provati | a prodotto costante | non leggibili | costo mediano | il 25% peggiore |
|---|---|---|---|---|---|
| **base** | 60 | 2 | 58 | **0.34%** | 0.60% |
| **robinhood** | 21 | 21 | 0 | **0.10%** | 0.59% |

> I pool **non leggibili** sono quelli in stile Uniswap V4, che non vivono in un contratto
> proprio: lì il conto non si può rifare da fuori e **non lo inventiamo**. Compaiono nel
> conteggio apposta: un buco dichiarato non è un buco nascosto.

*Misure conservate finora: **base** 203, **robinhood** 92.*