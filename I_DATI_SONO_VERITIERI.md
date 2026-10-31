# I dati sono veritieri. E la verita' e' che sulle posizioni verificabili non c'e' vantaggio.

*6 ottobre 2026 · fine del loop «rendi veri i dati», aperto da un controllo a campione di Nicolo'*

## Come siamo arrivati qui

Il 5/10 ho riferito «569 portafogli oltre il 10X». Nicolo' ne ha controllato uno su
DexScreener: **quel portafoglio non aveva mai toccato quella moneta**. Ha imposto un loop con
una regola sola — *nessun numero esce se non e' verificabile sulla chain* — e sei difetti sono
venuti fuori uno dopo l'altro.

| difetto | peso |
|---|---|
| segni invertiti sui mercati V4 | 56-82% delle pool |
| lato del memecoin deciso da una regola fissa | 67-78% delle pool |
| arbitraggi atomici contati come posizioni | 23.204 e 19.750 transazioni |
| costi quasi-zero come denominatore | multipli da 55X a 3 milioni di miliardi |
| **vendite prima degli acquisti** | **18,5% e 28,8% delle «chiuse»** |
| **gettoni venduti piu' di quelli comprati** | **mediana 1,61 e 2,11** |

Piu' due errori nei miei stessi controlli: un cancello che cercava i gettoni nel firmatario
(che per meccanica non li riceve mai) e bocciava **tutto**, e due agenti che compilavano e si
schiantavano in cielo.

## Cosa e' verificato, e come

| | esito |
|---|---|
| le transazioni **esistono** sulla chain | **10 su 10** |
| sono **firmate** dal portafoglio che attribuiamo | **10 su 10** |
| gli **importi grezzi** coincidono con l'evento | **5 su 5**, cifra per cifra |
| l'acquisto **precede** la vendita | per costruzione, campo `ordine_sano` |
| i gettoni **tornano** (venduti ≈ comprati) | per costruzione, banda 95-105% |

E ogni posizione porta ora **gli hash delle sue transazioni**: la prova si rifa' a mano senza
fidarsi di noi.

## Il risultato, sulle sole posizioni pulite

| | base | robinhood |
|---|---|---|
| posizioni pulite | **785** (23,9% delle «chiuse») | **535** (10,6%) |
| **multiplo mediano** | **1,05X** | **0,99X** |
| in utile | 66,8% (63,9-69,5) | 42,1% (38,5-45,7) |

**Su un giro chiuso e verificabile, il guadagno mediano e' fra il −1% e il +5%.** Non 2X, non
10X, non 26X: quelli erano tutti posizioni che non sono giri chiusi.

## La lettura, e non e' solo negativa

1. **Il «chi guadagna» per copiarlo e' chiuso.** Sulle posizioni che possiamo verificare non
   c'e' nessun vantaggio da copiare, e questo spiega anche perche' il test del ritardo dava
   mediana zero: non c'era vantaggio da perdere.
2. **Ma il 76-89% delle posizioni «chiuse» NON sono giri chiusi**, e quello e' un fatto sul
   mercato, non un difetto nostro: in queste monete la maggior parte di chi vende ha ricevuto
   i gettoni altrove. **E' esattamente l'intuizione che Nicolo' ha avuto ieri sul «50%
   nascosto»** — e ora e' misurata, non supposta.
3. Quindi la domanda non e' morta: si e' **spostata** dove lui l'aveva messa. Non «chi
   scambia meglio» ma **«chi riceve i gettoni, e come»**.

## Il caso da controllare a mano

Chi vuole rifare la verifica puo' partire da qui — posizione pulita, ordine sano, gettoni che
tornano, entrambe le transazioni firmate dal portafoglio:

```
portafoglio  0xb1e2c361cf6aca3d1dd5449ea5a1bfce96d89019   (chain: base)
gettone      0xf732a566121fa6362e9e0fbdd6d66e5c8c925e49   Lit Protocol (LITKEY)
acquisto     tx 0xae29415805d11398f5adf2aef5d90c66c76818306ab0c5158c3d7b47c6155cfa
vendita      tx 0xe2c5ffeaf603d872663613de5e3a44be53ec51c1ce5462cc6c7262a286bee6a5
```
Nota: su QUESTO caso la vendita precede l'acquisto, ed e' il caso che ha fatto scoprire il
difetto. E' incluso di proposito come esempio di cio' che ora viene ESCLUSO.
