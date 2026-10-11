# I due revisori sul piano — 6 ottobre 2026

Stessa domanda a entrambi: *«in che modo la ricerca di chi ripete molte X produrrà un'illusione, e
cosa non sto misurando?»*. Costo: Astra $0,09, Grok zero (abbonamento).

## Dove concordano, per strade diverse

**Contare le X ripetute non distingue tre cose opposte**: fortuna selezionata fra migliaia di
tentativi, vantaggio privilegiato (il lanciatore, i 32 indirizzi esentati dalla tassa) e vantaggio
davvero copiabile.

Astra: *«Un portafoglio può aver comprato dieci vincitori perché ha comprato diecimila monete.»*
Grok: *«K senza il numero di tentativi è la classifica dei bot.»*

**La correzione, identica:** non il conteggio delle X, ma **l'eccesso rispetto ai portafogli con
lo stesso numero di tentativi**, dopo aver tolto lanciatori ed esentati.

**La misura che uccide l'illusione, identica:** non il rendimento futuro di quei portafogli, ma
**il rendimento di chi li copia**. Lista congelata a una data, regole fissate prima, e poi si
conta *tutto*, comprese le monete che non graduano, con cassa finita e inventario valutato a
quello che davvero si incassa vendendolo.

Grok dà anche le soglie: con 5.169 graduazioni su 146.000 portafogli, **due volte è rumore di
fondo, quattro volte è dove il caso si esaurisce** — ma solo se i tentativi sono uguali, che non
è.

## Dove Grok ha visto una cosa che Astra non aveva visto

> «La colonna "solo chi ha venduto" non contiene un vantaggio. Contiene la formula della curva.»

Osservazione: 1,2063 / 0,9568 = 1,2608, e il vantaggio di gettoni del 1° sul 10° che avevo
misurato era 1,26. Scarto 0,001 — quindi zero residuo per l'abilità.

## Dove Grok sbaglia, verificato

Quel 1,26 veniva da **una mia misura vecchia e non appaiata**. Rifatta come confronto appaiato
sulla stessa curva (153.111 curve), il quadro cambia:

| confronto | vantaggio di prezzo | vantaggio di rendimento | residuo |
|---|---|---|---|
| 1° vs 2° | 1,054 | 1,137 | **1,079** |
| 1° vs 3° | 1,090 | 1,165 | 1,069 |
| 1° vs 5° | 1,176 | 1,199 | 1,020 |
| 1° vs 10° | 1,385 | 1,261 | **0,910** |
| 1° vs 20° | 1,714 | 1,336 | 0,779 |
| 1° vs 50° | 2,386 | 1,390 | **0,583** |

**Il residuo si rovescia, e questo è il fatto nuovo.** Fino al 5° posto il primo rende un po' più
di quanto spieghi il prezzo. Dal 10° in poi è il contrario: chi entra tardi paga i gettoni fino a
2,4 volte più cari e **ne recupera oltre la metà**.

Comprare tardi costa gettoni e compra informazione. Dal decimo posto in poi **l'informazione vale
più dei gettoni** — che è la direzione opposta a quella che stavamo seguendo.

L'intuizione di Grok era giusta (gran parte del gradiente è meccanica, non abilità); il suo numero
no, perché l'ho nutrito io con una misura sbagliata. **Un revisore vale quanto i dati che gli
dai.**

## E l'incongruenza che Astra ha trovato

1,2063 × (1 − 0,395) = 0,730, mentre il conto onesto è 0,854. Verificato: il numero era giusto,
l'esposizione incompleta. **Il 39,5% è quota di posizioni, il 29,2% è quota di capitale** — chi
non vende mette cifre più piccole. Da qui un fatto che nessuno dei due aveva chiesto:

| posto | capitale bloccato | posizioni bloccate | taglia del bloccato / taglia dell'uscito |
|---|---|---|---|
| 1 | **29%** | 39,5% | 0,63 |
| 2 | 12% | 20,3% | 0,51 |
| 3 | 8% | 23,1% | 0,31 |
| 10 | 4% | 19,4% | 0,16 |
| 50 | 2% | 19,5% | 0,08 |

In prima posizione il capitale che resta bloccato sono **soldi veri**; dal decimo in giù è
polvere. La quota di posizioni bloccate invece resta ferma intorno al 20%: guardare le posizioni
invece del capitale nascondeva proprio la differenza che conta.

## Cosa cambio nel piano (il goal resta quello del fondatore)

1. **Storia economica completa** di ogni portafoglio: tutti i suoi acquisti, non solo quelli
   andati bene. Senza il denominatore dei tentativi la classifica è la classifica dei bot.
2. **Togliere lanciatori ed esentati** prima di qualunque classifica: sono privilegio, non
   abilità, e sono leggibili dalla transazione di creazione.
3. **Non contare 32 indirizzi dello stesso operatore come 32 conferme.**
4. **Il test del copiatore**: lista congelata a una data, regole fissate prima, tutto incluso.
5. **Indagare il residuo che si rovescia** — è il filone più promettente emerso oggi, e non
   veniva da nessuno dei due revisori: viene dall'aver verificato uno dei due.
