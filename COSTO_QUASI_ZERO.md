# Partire dall'outlier: ha speso zero e incassato 1.605 dollari

*5 ottobre 2026 · prescrizione di Astra: «riconciliate saldi iniziali, movimenti e saldi finali
dei vincitori, partendo dall'outlier»*

## L'outlier, aperto

```
chain       robinhood
pool        0xbbb207aa…
stato       chiuso
speso          0.00 $
incassato   1,604.98 $
multiplo   1,906,100 X
```

**Non ha fatto un milione e nove di volte: ha un costo d'acquisto sotto il centesimo, e io ci
ho diviso.** E' letteralmente la frase di Astra: «privo di credibilita' economica senza costo
iniziale e flussi verificabili». Una mediana resistente agli estremi non corregge un'unita'
contabile sbagliata — e qui l'unita' non era sbagliata, era **mancante**.

## Quanto pesava

| | base | robinhood |
|---|---|---|
| posizioni chiuse col multiplo | 1.656 | 2.741 |
| con costo **sotto 1$** | 284 (**17,1%**) | 217 (7,9%) |
| con costo sotto 10$ | 585 (35,3%) | 910 (33,2%) |
| multiplo mediano di quelle sotto 1$ | **56X** | **66X** |
| multiplo mediano — tutte | 1,35X | 2,75X |
| multiplo mediano — solo costo >=10$ | **1,11X** | **2,01X** |

Le posizioni di polvere portavano multipli mediani di 56 e 66 volte: erano **esattamente il
motore** dei numeri di stanotte. Un multiplo con denominatore sotto il dollaro non e' un
rendimento, e' una divisione per quasi-niente.

## Il test di persistenza, rifatto su posizioni con un costo vero

Soglia di «bravo» invariata (mediana >=2X sulla prima meta'), ma ogni posizione deve avere un
costo di almeno 10$. E ogni conteggio porta il suo intervallo, come impone l'altra correzione di
Astra — «zero su 54 non e' zero».

| | portafogli | prima | **DOPO** | >=2X in meta' delle posizioni successive |
|---|---|---|---|---|
| base, bravi | 10 | 2,53X | **1,81X** | 40,0% (al 95%: **15,0–69,6%**) |
| base, scarsi | 45 | 1,04X | **1,05X** | 11,1% (al 95%: **4,5–22,0%**) |
| robinhood, bravi | 42 | 3,05X | **3,48X** | 88,1% (al 95%: **76,6–95,2%**) |
| robinhood, scarsi | 26 | 1,03X | **1,07X** | 23,1% (al 95%: **10,6–40,5%**) |

**Su robinhood regge e gli intervalli non si toccano. Su base gli intervalli SI SOVRAPPONGONO**
(15,0% contro 22,0%): resta un indizio, non un risultato.

Ieri avrei dichiarato entrambe le chain. La differenza non e' prudenza: e' uno strumento che
ieri non avevo, costruito stanotte da una correzione esterna.

## La regola che ne esce, scritta dove serve

**Un rapporto richiede un denominatore con credibilita' economica.** Sotto una soglia dichiarata
di costo, la posizione non entra nella distribuzione dei multipli: va in uno **stato**
(«costo non credibile»), non in un numero. E' la stessa disciplina dei quattro stati di
posizione prescritti da Astra il 4/10 — qui applicata al costo invece che all'esito.

## Cosa resta aperto, dichiarato

Le altre tre obiezioni di Astra sulla persistenza non sono state affrontate: **quando** sarebbe
stata disponibile la selezione, se le posizioni della seconda meta' erano **gia' aperte** al
momento della selezione, e se gli stessi gettoni o finanziatori compaiono in **entrambe** le
meta'. Servono una data unica di selezione e coorti separate. Finche' non e' fatto, anche il
risultato di robinhood e' provvisorio.
