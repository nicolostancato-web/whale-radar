# Le squadre ricorrenti vanno PEGGIO. Il livello che conta è un altro.

*2 ottobre 2026 · 23.070 pool su robinhood e 5.934 su base, coi primi compratori veri*

## L'ipotesi, nelle parole di Nicolò

> «Se noi scopriamo che ci sono degli insider che vengono finanziati da grossi wallet e questi
> si mettono insieme — magari sono le persone ricche nei gruppi, ognuno ha il suo wallet, viene
> finanziato, e poi casualmente in modo incrociato entrano sempre in modo combinato in
> qualcosa — quello vince sull'analisi del pattern, della pressione. Perché c'è qualcosa che noi
> sappiamo in più.»

Il principio è giusto, e il nostro stesso metro lo conferma senza volerlo: **tutte** le
combinazioni di pressione, volume e concentrazione non superano il caso, perché cercano di
*indovinare* una cosa che qualcuno *sa*.

## Primo pezzo provato: le squadre si ripetono?

Nell'insieme, **no**. Coppie di persone viste insieme 3+ volte: 12.742 sul vero contro 8.909
mescolando le persone fra le pool — compatibile col caso. Su base il vero è perfino **sotto** il
mescolato (4.414 contro 6.034).

Il conto è dominato dalle **fabbriche**: un portafoglio compare con altri in **153 pool** su
robinhood e **301** su base. Non sono insider, sono bot, e affogano qualunque segnale.

## Secondo pezzo: togliendo le fabbriche, le squadre ricorrenti vanno meglio?

Escluse le persone che compaiono in 20+ pool, e contando solo le coppie viste nel **passato**:

| la squadra era già stata vista insieme | robinhood | base |
|---|---|---|
| mai | **−0,5%** | −30,5% |
| 1 volta | −0,2% | −37,0% |
| 2-3 volte | −12,8% | −27,2% |
| 4-9 volte | −15,0% | −23,9% |
| 10+ volte | **−19,8%** | — |

**Su robinhood la direzione è OPPOSTA all'ipotesi: più la squadra è ricorrente, peggio va.**
Diciannove punti. Su base è incoerente, quindi nemmeno un segnale al rovescio regge la regola
di ripetizione.

Lettura: le squadre ricorrenti che non sono fabbriche sembrano **sciami che estraggono** — chi
entra accanto a loro paga il conto, non lo incassa.

## Perché questo NON smentisce l'ipotesi di Nicolò

Ho misurato portafogli che **compaiono insieme**. Lui parla di portafogli **finanziati dalla
stessa mano**. Sono due cose diverse, e la differenza è il cuore della faccenda:

> chi coordina davvero **non si fa vedere sempre con gli stessi compagni**. Cambia portafoglio.

Un'entità che usa dieci indirizzi nuovi per dieci monete diverse ha co-occorrenza **zero** — e il
test qui sopra la dichiarerebbe inesistente. È il falso negativo peggiore possibile: ho cercato
l'ombra del fenomeno invece del fenomeno.

Il legame che NON si può cambiare a costo zero è **chi ha pagato le prime commissioni** di quel
portafoglio. Un indirizzo nuovo non ha fondi: qualcuno gliene manda. Quel qualcuno è l'entità.

## Il prossimo passo, e quanto costa

Per ogni primo compratore, la **prima transazione in entrata**: chi l'ha finanziato. Poi si
raggruppano i portafogli per finanziatore e si rifà esattamente questa tabella sulle ENTITÀ
invece che sui portafogli.

- **Costo: €0.** Gli endpoint sono pubblici (`mainnet.base.org`,
  `rpc.mainnet.chain.robinhood.com`), senza chiave e senza fatturazione — gli stessi che già
  usiamo per risolvere chi firma.
- **Chiamate:** una per portafoglio, non per transazione. Sono ~23.000 persone su robinhood e
  ~10.000 su base: due ordini di grandezza meno del lavoro che stiamo già facendo.
- **Il vincolo vero** non è il costo ma l'ordine: serve prima che la copertura delle persone
  salga (oggi mediana 0%, la catena è al secondo passo di quattro).

## Cosa resta in piedi, dopo questa misura

Il **passato chiuso del singolo portafoglio**: 16-20 punti, su entrambe le chain, sopravvissuto
a due attacchi. Quello regge. Quello che cade è la versione «squadra visibile» del
coordinamento — e cade in modo utile, perché dice dove NON guardare.
