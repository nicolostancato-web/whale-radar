# Imparare a leggere Uniswap v4 — un gradino per giro

**Perché, misurato il 4/11 sera.** Leggiamo solo la v3, e la liquidità delle
monete che ci servono sta in gran parte sulla **v4**:

| moneta | gestore v4 | vasche v3 | quota su v4 |
|---|---|---|---|
| cbBTC | $18,2 M | $115 mila | **99%** |
| LBTC | $2,7 M | zero | **100%** |
| sUSDe | $728 mila | zero | **100%** |
| tBTC | $125 mila | $6 mila | 95% |
| rETH | $89 mila | $7 mila | 93% |
| wstETH | $7,4 M | $1,8 M | 81% |
| WBTC | $45,9 M | $14,2 M | 76% |
| USDT | $81,7 M | $44,0 M | 65% |

**Tre conseguenze, tutte costose:**

1. **I tetti sono troppo bassi.** Li misuriamo sulla profondità v3: dove la v4
   ha quattro volte tanto, stiamo chiudendo una frazione del debito che il
   mercato regge — cioè prendendo premi più piccoli del dovuto.
2. **Alcuni verdetti "senza strada" sono sbagliati.** sUSDe l'avevo dichiarato
   chiuso per costruzione: ha 728 mila dollari sulla v4.
3. **È una cecità che non si annuncia.** Una vasca v4 ci risponde «zero», e
   noi lo leggiamo come «il mercato non c'è» invece di «non so leggere».

**La lezione che l'ha permessa, e me l'ero già scritta:** non si deduce il
limite della realtà dal limite del proprio strumento. Tre registri Curve che
dicevano no non erano una prova; due piazze che dicono zero non sono il
mercato.

## I gradini

| # | gradino | stato |
|---|---|---|
| 1 | leggere un preventivo dalla v4 (il Quoter) e confrontarlo con l'oracolo | da fare |
| 2 | capire se una coppia ha una vasca v4 e con quali parametri (fee, tickSpacing, hook) | da fare |
| 3 | costruire la calldata di scambio (UniversalRouter + Permit2) | da fare |
| 4 | verificare che l'importo compaia **una volta sola** | da fare |
| 5 | capire chi preleva i gettoni (su v4 passa da Permit2) | da fare |
| 6 | **eseguire su una copia del blocco corrente** — il gradino che decide | da fare |
| 7 | collegarla come piazza nella scelta della rotta (si prende la migliore) | da fare |
| 8 | rifare la taratura dei tetti con la v4 dentro | da fare |

## Regole che valgono su tutta la scaletta

- **Il minimo in uscita a zero**, come sulle altre piazze: difende il
  contratto, non la calldata.
- **Il destinatario non si scrive fisso** — su v3 ho usato «chi mi ha
  chiamato», su Curve era implicito; sulla v4 va verificato.
- **La rotta si scegli per quanto rende**, e ora il confronto è a tre piazze.
- **Un no misurato è informazione**: se una coppia non si vende nemmeno sulla
  v4, si registra col motivo.
- **Attenzione agli hook.** Le vasche v4 possono avere codice attaccato che
  cambia il comportamento dello scambio. Una vasca con un hook sconosciuto
  non si usa prima di aver capito cosa fa.
