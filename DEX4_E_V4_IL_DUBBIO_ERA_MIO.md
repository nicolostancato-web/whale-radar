# La famiglia 4 è Uniswap v4 — e il dubbio era mio — 7 ottobre 2026

## Risoluzione

| | |
|---|---|
| chi emette gli scambi della famiglia 4 | **`0x8366a39cc670b4001a1121b8f6a443a643e40951`** (un solo contratto: il gestore dei pool Uniswap v4) |
| scambi v4 trovati | da **960 a 4.321 ogni mille blocchi**, in tutta la storia della chain |
| gli identificativi da 64 cifre | sono veri **poolId** di v4, presi da `topics[1]` dello Swap |
| monete nate sulla curva che hanno un pool | **5.268 su 675.145 = 0,78%** |

**Lo 0,8% regge. «Graduata» significa graduata. Il registro dei pool è giusto.**

## Perché avevo misurato «zero scambi v4»

Avevo scritto, in uno script a mano:

```python
lg = log_di_finestra(SWAP4, bl, bl + 200000)
print(f"{len(lg) if lg else 0} scambi v4")
```

Una finestra di 200.000 blocchi supera il tetto di 10.000 risultati, la chiamata viene **rifiutata**
e torna `None` — e `len(lg) if lg else 0` stampa **`0`**.

**Un rifiuto mostrato come «zero eventi».** Nona volta in due giorni che un'assenza diventa un
fatto, e questa volta la lezione era già scritta da me, ieri, dentro `agents/curva_pons.py`:

> «Uno zero che arriva senza errore e' il piu' pericoloso di tutti.»

L'avevo messa nell'agente e poi violata nei miei script usa-e-getta. **Una lezione scritta
nell'agente non protegge chi lavora a mano accanto all'agente.**

## E il numero che «ballava»

5.169 → 11.489 → 12.970 «monete graduate». Spiegazione banale e tutta mia: in un punto contavo
**monete**, nell'altro **pool**, e una moneta ne può avere più di uno.

| | |
|---|---|
| monete nate su Pons con almeno un pool | **5.268** |
| pool che le riguardano | **12.939** |
| pool per moneta | 2,46 |

Il 12.970 che riportavo erano **pool**. Stessa realtà, due unità, un'etichetta sbagliata.

Ieri avevo scritto che «un numero fondamentale che raddoppia merita una domanda, non una
spiegazione». La domanda era giusta. **La risposta non era un dato sbagliato: era un nome
sbagliato.**

## Cosa torna in piedi

Tutto quello che avevo sospeso ieri notte:

- la separazione fra «morta sulla curva» (99,2%) e «graduata» (0,78%);
- il **77,5% di chi risultava «mai venduto» che ha mosso gettoni dopo la graduazione**;
- e quindi la strada del mercato pubblico, che resta la più promettente perché lì i tempi sono di
  ore e non di decimi di secondo.

## Cosa aggiungo per non ripeterlo

Nei conti a mano, mai `len(x) if x else 0` su qualcosa che può essere `None` per un rifiuto: `None`
e «vuoto» sono due fatti opposti e vanno stampati diversi. Lo scrivo qui perché la prossima volta
rileggerò questo file, non il commento dentro l'agente.
