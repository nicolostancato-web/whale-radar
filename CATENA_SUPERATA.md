# La catena completa passa sui dati corretti: 14 date su 14, due chain

*5 ottobre 2026 · prima volta che tutti e tre i controlli reggono su dati sani*

## I tre anelli, nello stesso ordine di ieri

**Anello 1 — attivi contro controllo preso a caso.**

| | attivi | controllo (300 a caso) |
|---|---|---|
| base | 1,80X · 46,1% (39,8-52,5) | 1,09X · 18,7% (11,7-27,6) |
| robinhood | 1,98X · 55,4% (49,5-61,2) | 1,00X · 15,6% (6,4-30,1) |

Intervalli separati su entrambe. E il portafoglio giudicabile preso a caso sta **a pari**:
i multipli ripetuti non sono come funziona il mercato.

**Anello 2 — persistenza fuori campione** (scelta sulle posizioni vecchie, misura sulle nuove).

| | bravi dopo | scarsi dopo | intervalli |
|---|---|---|---|
| base | 2,02X · 62,8% (49,1-75,1) | 1,60X · 31,7% (21,8-42,9) | **separati** |
| robinhood | 2,42X · 67,1% (56,8-76,4) | 1,95X · 48,1% (36,0-60,3) | **si sovrappongono** |

Ieri separava robinhood e non base; oggi l'opposto. E i divari sono **molto piu' piccoli** di
ieri (+0,4 contro +2,4): quello di ieri era gonfiato dai costi quasi-zero.

**Anello 3 — molte date, con il controllo dello STESSO periodo a ogni data.**

| | date giudicabili | i bravi vincono | divari |
|---|---|---|---|
| base | 6 | **6 su 6** | da +0,12 a +0,83 |
| robinhood | 8 | **8 su 8** | da +0,20 a +0,79 |

**14 su 14.** Con il controllo contemporaneo, quindi il periodo e' escluso: non e' il mercato
che andava bene, perche' a ogni data i mediocri dello stesso periodo stanno sotto.

## Cosa questo e', detto con precisione

**Esiste un gruppo di portafogli che fa sistematicamente meglio del caso, e la cosa persiste.**
E' modesto — mediana intorno a **2,0-2,4X** contro **1,5-1,9X** dei mediocri — ma e' presente
a ogni data e su entrambe le chain.

## Cosa NON e'

1. **E' il loro rendimento, non il nostro.** Il nostro va calcolato con le riserve e il
   ritardo, e quel lavoro va rifatto da zero sui dati corretti: la versione di ieri diceva
   mediana zero, ma era costruita sui segni sbagliati.
2. **E' misurato sulle sole posizioni chiuse**, e il **45-48%** non e' mai stato venduto. Chi
   chiude i vincenti e tiene i perdenti appare meglio di quello che e'. L'effetto gonfia il
   livello di tutti e due i gruppi, non il divario — ma il livello non va creduto.
3. **I numeri sono piccoli**: 103 e 122 portafogli con almeno sei posizioni chiuse.

## L'errore di metodo di questo stesso giro, e vale piu' del risultato

Il terzo anello, al primo tentativo, ha stampato i numeri di **ieri, cifra per cifra**
(3,10/2,12 · 3,51/1,97 · 3,68/2,02…). Causa: `main` **non leggeva la riga di comando**, quindi
la cartella che gli passavo era ignorata e leggeva sempre le consegne vecchie.

Me ne sono accorto **solo perche' erano identici a due decimali su sei coppie**. Se fossero
stati *simili ma diversi*, avrei pubblicato «regge anche sui dati corretti» misurando i dati
sbagliati — la conferma piu' pericolosa possibile, perche' confermava cio' che speravo.

E' la «dimensione fantasma» del 2 ottobre (dodici prove indipendenti con margini identici,
perche' il codice ignorava una dimensione dichiarata). **Seconda volta la stessa trappola, e
stavolta l'ho scavata io.**
La cura e' scritta nel codice: l'agente ora **stampa da quale cartella ha letto e quanti
portafogli**. Un agente che non dichiara la sua sorgente puo' misurare ieri credendo di
misurare oggi.
