# Revisione Grok — 2026-09-25 20:43 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 831s

---

Il pareggio sul medio dei “sani” va verificato sui dati, non solo sull’algebra. Cerco il calcolo vero (distribuzione dei rendimenti, non solo le due medie) prima di dire se chiude la direzione.Il +0,9% non è un premio. È la media di un secchio il cui centro è negativo, e il −41% non è un prezzo: è il peso della regola «meno di 5 vendite = −98%».

Ricalcolato su `data/loop1/insieme_*.jsonl.gz`, pool giudicabili (robinhood 10.429, base 4.728). Stesso metro della tua tabella, scarto di qualche decimo.

## 1. Il pareggio è fatto sul numero sbagliato

La formula, come algebra del valore atteso, è giusta: un classificatore che toglie solo gli esiti ≤ −90% e tiene tutto il resto incassa la media di quel resto. Su robinhood quella media è +0,91%. Il conto «serve p < 0,9%» descrive quella media, e nient'altro.

Quella media non è il rendimento dei pool sani.

| | robinhood | base |
|---|---|---|
| media dei sani | +0,91% | +0,11% |
| mediana degli stessi | **−2,30%** | **−1,80%** |
| quota dei sani in perdita | 70% | 82% |
| media, tagliando il rendimento a p99 | **−1,08%** | **−1,56%** |
| errore standard della media | 0,63 punti | 0,77 punti |
| intervallo bootstrap 5–95% della media | −0,08% … +1,94% | −1,04% … +1,39% |

Su robinhood 107 pool (quelli a ≥ +100%) contribuiscono **+4,57 punti** alla media dei sani. Gli altri 5.861 stanno a **−3,7%**. Togli quei 107 e il «premio» cambia segno. Su base la media dei sani è 0,14 errori standard sopra zero: rumore.

Con la media tagliata a p99 il soffitto del rilevatore perfetto è una perdita, e non esiste un tasso di trappole che lo porti in pari:

\[
(1-p)\times 0{,}9892 + p\times 0{,}02 = 1 \implies p < 0
\]

Il +0,9% campionario, anche preso per buono, ha un intervallo che arriva a zero. All'estremo ottimistico di quell'intervallo (+1,9%) il pareggio sta ancora sotto il 2% di trappole. Il decile migliore che hai già misurato è al 10%. La direzione resta chiusa. La frase «il premio esiste e vale +0,9%» no.

Il soffitto di un rilevatore di *vincenti* è un altro numero, e non riapre niente: su robinhood il 17% dei pool chiude sopra zero, media +30%, mediana di quei vincenti **+9,6%**. È un conto sull'esito, dopo aver visto chi ha vinto.

## 2. Il numero del primo giorno

Il portafoglio robinhood si spezza in due pezzi, e torna al centesimo:

\[
0{,}4253\times(-0{,}98) + 0{,}5747\times(+0{,}0050) = -0{,}4139
\]

Il primo pezzo contribuisce **−41,7 punti**. Il secondo, i pool dove il prezzo di vendita è davvero misurato, contribuisce **+0,3 punti**. Base è lo stesso oggetto: fra i pool con almeno 5 vendite, la quota con prezzo ≤ −90% è **zero**; le «trappole» al 53% sono tutte l'assegnazione −98%.

Dentro i prezzi misurati, robinhood: media +0,50%, mediana −2,32%, il 70% sotto zero, solo il 2,6% sotto −50%. Un memecoin a 24 ore non ha questa forma. La forma è quella della definizione. La mediana delle stampe cade dove è avvenuta l'attività, di solito prima della morte; la morte non sposta la mediana finché non produce metà delle stampe. A quel punto le stampe finiscono, scatta la soglia delle 5 vendite, e il pool diventa −98% per decreto. I «sani a +0,9%» sono i pool ancora vivi al centro della finestra. Il −41% è il decreto, pesato per il 43%.

Il numero da leggere il primo giorno era la mediana di `_uscita` sui pool con almeno 5 vendite, accanto alla media, e la scomposizione del −41% in «etichetta» e «prezzo». Due binari, trappole contro sani, mettono il decreto e la coda nello stesso sacco e chiamano premio il residuo.

## 3. Lo strumento

Manca il prezzo del pool a un'ora di orologio, nel verso della valuta di base. Oggi `_uscita` è la mediana di `abs(a0)/abs(a1)` sugli swap con `a0 > 0`. Quel rapporto è token0 per token1, e `a0 > 0` vuol dire «è entrato token0 nel pool». Il memecoin è token0 solo quando il suo indirizzo è minore della valuta. Nell'altra metà dei pool conti i buy come vendite e il rendimento ha il verso invertito: un +900% vero diventa circa −90%, un −95% vero diventa superiore a +2000% e il codice lo butta (`rend` fuori da (−0,99, +20) fa `continue`). `impatto_reale.py` usa il rapporto inverso, `a1/a0`. L'orientamento giusto c'è già in `multichain_rpc.py` (`quote_is_t0`) e non entra in `insieme.py`. I file grezzi non sono in questa copia: l'effetto sul −41% non l'ho rimisurato. Il difetto nel codice c'è.

Si costruisce così, dagli swap che hai già.

1. Valuta di base: `data/valute_base.json`. Token0 = il minore dei due indirizzi. Vendita del memecoin = il delta del memecoin verso il pool è positivo. Prezzo = valuta incassata / memecoin venduto. I decimali si annullano nel rendimento.

2. Per i pool V3 e V4 il log che già decodifichi e poi butti contiene `sqrtPriceX96` e `liquidity` (terza e quarta parola del data, dopo amount0 e amount1). `firma()` tiene solo le due quantità. Lo sqrtPrice è il prezzo del pool dopo lo swap, unico, indipendente da chi ha colpito:

\[
\frac{\text{token1}}{\text{token0}} = \left(\frac{\text{sqrtPriceX96}}{2^{96}}\right)^{2}
\]

Poi lo giri in valuta-per-memecoin con la stessa regola del punto 1. Hai detto che i V4 sono l'85% del campione: il dato è nel log, non in una raccolta nuova.

3. Entrata a \(t_0+2\text{h}\): ultimo sqrtPrice con `ts` ≤ entrata. Uscita a orologio, non a mediana di stampa: ultimo sqrtPrice con `ts` ≤ entrata + Δ, per Δ = 5 min, 30 min, 2 h, 6 h, 24 h. Se l'ultimo swap è molto prima di Δ, il prezzo è stantio: si dichiara il buco, non si tratta come un incasso. La curva è la media e la mediana di \(P(t_0+\Delta)/P(t_0)-1\), costo a parte. È la mappa che dice se un orizzonte qualsiasi ha il centro sopra zero.

4. Due controlli sullo stesso giro, sempre dai log. I pool con 1–4 vendite (robinhood: 17%) oggi valgono −98% pur avendo un prezzo: riporta la mediana di quelle poche vendite, orientate. E `liquidity` nello stesso evento, convertita in valuta nel range: è la taglia che quel prezzo poteva assorbire. I 107 pool che fabbricano il +0,9% vanno letti con quella taglia accanto. Una mediana di cinque stampe da polvere a +300% non è un'uscita.

I Mint/Burn non li hai: senza quelli non distingui «prezzo fermo, riserve integre» da «pool svuotato». È l'unico pezzo che richiede eventi nuovi. Lo sqrtPrice, il verso e la curva a orologio no.
