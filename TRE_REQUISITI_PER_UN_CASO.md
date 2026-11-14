# I tre requisiti perché un caso possa essere mostrato — 7 ottobre 2026, pomeriggio

Stamattina ho chiuso due cause dei numeri sbagliati (righe di due generazioni mescolate, fette
assegnate per posizione). Nel pomeriggio ne ho trovata una **terza, indipendente dalle prime due e
non risolta da quelle**.

## La terza causa: una posizione può essere una fetta della storia

Ho preso tre posizioni vere dai nostri file e le ho **ricalcolate da zero dalla chain**, senza
passare dalla nostra pipeline. Risultato su una di esse:

| | pipeline | chain |
|---|---|---|
| speso | 0,00912022417 | 0,2372853304 |
| incassato | 0,0019561339 | 0,0795572219 |

Ventisei volte di differenza. La spiegazione comoda era «copertura parziale» — ed è la prima che
viene in mente, quindi andava sospettata. Verificata con un numero: la somma delle sole operazioni
dentro la finestra che leggiamo vale **0,0110763581**, e la nostra riga diceva **0,0110763581**.

**Identico fino alla decima cifra: i conti della pipeline sono esatti.** Quello che non è esatto è
*quale pezzo di mondo* legge: di 57 operazioni di quel portafoglio su quella moneta, **5 sono
dentro la finestra e 52 fuori**.

Il nostro «coperto 100%» significa 100% della finestra dichiarata, **non** 100% della storia di un
portafoglio. Su un campione di 25 posizioni (13 verificabili, 12 con la moneta non presente
nell'elenco lanci locale):

- **8 posizioni intere**, tutte le operazioni dentro la finestra;
- **5 posizioni parziali** — il 38% — e quando è parziale ne vediamo in mediana il **25%**
  (minimo 3%, massimo 54%).

**Di un portafoglio di cui si vedono le vendite ma non gli acquisti si dice che è bravissimo.**
È il modo più semplice di inventarsi una X, e non lo risolvono né le versioni né i duplicati.

## Perché la verifica non può dipendere dalle nostre prove

`prima_la_prova.py` controlla gli hash che le nostre righe si portano dietro: un passo avanti, ma
le prove le scrive **la stessa pipeline che potrebbe sbagliare**, e sulla curva esistono solo per i
candidati (99,5% delle posizioni non ne ha, per una scelta di peso: con le prove per tutti il file
pesava 290 MB a giro). Il caso in cima a una classifica *nuova* è quindi quasi sempre non
verificabile.

`riprova_dalla_chain.py` fa un'altra cosa: parte dall'indirizzo del portafoglio e da quello della
moneta, rilegge gli eventi della curva dalla chain, e **rifà il conto da capo**. È la differenza
fra chiedere a qualcuno di ricontrollare il proprio compito e rifarlo.

## I tre requisiti, tutti e tre o niente

1. i numeri della pipeline **combaciano** con quelli ricalcolati dalla chain (tolleranza 2%);
2. i **gettoni venduti sono quelli comprati** (90-110%) — altrimenti è un rapporto fra merci
   diverse, ed è così che era nato il «157x»;
3. la posizione è **intera**: nessuna operazione fuori dalla finestra letta.

Provato sui due casi veri: uno bocciato con cinque motivi scritti, uno promosso.

## Cosa comporta

Un caso che non supera tutti e tre **non arriva a Nicolò**, nemmeno come «indizio». E la copertura
utile è più piccola di quanto sembrava: le finestre da 90.000 blocchi vanno allargate per moneta,
perché la storia di un portafoglio su una moneta non sta dentro una finestra scelta da noi.
