# Il primo candidato che sopravvive a tutti i controlli — 6 ottobre 2026, notte

## Il portafoglio

```
0x6a96de27d21bcac2cc71a76a9cc8714653c2a02f
```

**323 posizioni pulite** sulla curva di Pons (robinhood).

| misura | valore |
|---|---|
| ritorno sul capitale, dentro la nostra taglia (0,01-0,2 nativo) | **1,470x** |
| ritorno su tutte le sue posizioni | 1,249x |
| posizioni chiuse / totali | 221 / 226 nella taglia |
| prima metà della sua storia | **1,085x** |
| seconda metà | **1,764x** |
| in cassa adesso | 0,5597 nativo |

## I controlli che ha superato, in ordine

1. **I gettoni tornano.** Comprati = venduti, alla cifra esatta. È il controllo che ha ucciso il
   «157x» di qualche ora prima (quello vendeva cento volte quello che comprava).
2. **Stessa valuta** su entrambi i lati (nativo), nessuna conversione, nessun prezzo inventato.
3. **Non è un lanciatore**: nessuna delle monete è sua.
4. **Dentro la nostra taglia**: mette 0,01-0,2, cifre che possiamo mettere anche noi.
5. **Il meglio di 852** portafogli con ≥100 operazioni pulite, dove la **mediana è 0,879x** — il
   portafoglio tipico perde il 12%.
6. **Regge fuori campione**: spezzando le sue operazioni in due metà cronologiche, guadagna in
   **entrambe**. Degli altri tre candidati, due hanno il vantaggio tutto nella seconda metà: li
   ho scartati.

## Le prove da riaprire a mano

| moneta `0x6f57fc6b0ff4cf0bf348bb55766994a70034bb46` | |
|---|---|
| messo | 0,105378 |
| incassato | **0,515689** → **4,89x** |
| gettoni | 55.569.284 comprati = 55.569.284 venduti |
| acquisto, 21/09 22:19 UTC | `0x7c6bc5b09796d64cfe7ca9827b76246aaf22a2e0c2e99410736b137e994c8ce0` |
| vendita, 21/09 22:19 UTC | `0x2c15a83da759f52657fe11333317daa8a334dd4318f605366a55d9a9421e582c` |

| moneta `0x5b4e9f55e3981e4ff159d00906e50eb938787cb5` | |
|---|---|
| messo | 0,242397 |
| incassato | **1,100189** → **4,54x** |
| gettoni | 124.849.722 comprati = 124.849.722 venduti |
| acquisto | `0x6cb7f7fc2e3d09eae77ed01965123fcaa137aef3438dc348471f9e9e93bd748e` |
| vendita | `0x5aef24c696baed8e73d460910a510f39933f7f849dc4911c26c8d3eef88ebbe9` |

Verificate tutte e quattro sulla chain: esistono, sono riuscite. **Si aprono su
`robinhoodchain.blockscout.com`, non su DexScreener** — gli acquisti sono sulla curva, che
DexScreener non mostra.

## Che cosa è, tecnicamente

Non è una persona e non è un contratto creato da qualcuno: è un **account con codice attaccato**
(l'esploratore dà `creator_address_hash: None` ma `eth_getCode` torna codice). Quindi un
portafoglio che firma da sé ma esegue un programma.

**E qui un dettaglio che Nicolò aveva previsto.** Le sue vendite le firma lui. Ma campionando 14
dei suoi acquisti di settembre, erano stati **sottomessi da 14 indirizzi diversi, ognuno una volta
sola**. Le sue ultime 50 transazioni invece sono tutte sue: **ha cambiato modo di operare**.

Parole di Nicolò, di stasera: *«magari sto qua ha già mosso i soldi in un altro wallet che l'ha
finanziato.»* Esattamente il punto.

## Cosa NON è ancora dimostrato

- **Non sappiamo se è copiabile.** Sopravvivere ai controlli vuol dire che i soldi sono veri, non
  che possiamo rifarli noi. Se il suo vantaggio è la velocità di esecuzione o un'informazione che
  non vediamo, copiarlo non serve.
- **I 14 firmatari usa-e-getta** vanno capiti: sono la sua infrastruttura, o un servizio condiviso?
  E chi li finanzia? È la domanda che Nicolò ha posto mesi fa e che resta la più promettente.
- **L'ho scelto perché ha vinto.** Il controllo a metà è il primo vero test fuori campione, ma non
  basta: serve la **regola congelata**, applicata in avanti, comprando anche le monete che vanno a
  zero.
- 1,47x su 226 operazioni non è «da 50 euro a 500». È un margine del 47%, reale ma modesto, e va
  pesato contro lo slittamento quando siamo noi a comprare.

## Perché lo pubblico comunque

Perché è **il primo oggetto della giornata che non si è sbriciolato**. Oggi ne ho uccisi tre: il
«+21% per chi entra primo» (era sopravvivenza), il «157x» (vendeva gettoni che non aveva
comprato), e la firma d'ingresso dei sette (erano tutti artefatti).

Questo ha superato sei controlli di fila, incluso quello che ha ucciso gli altri.
