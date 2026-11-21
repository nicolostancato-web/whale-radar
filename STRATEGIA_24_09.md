# 24 settembre — una strategia costruita e demolita in tre ore

*Con metodo nuovo: prima la stabilita', poi la soglia. Nessun euro a rischio.*


> **⚠️ Metro corretto il 25/09.** I tassi di trappola citati qui sono **ottimistici**: col metro
> giusto (pool giudicati per eta', non per ore osservate) le trappole sono il **43% su robinhood**
> e il **53% su base**, con media −41% / −52%. Vedi la correzione in testa a `DIREZIONE_CHIUSA.md`.

## Il metodo, cambiato apposta

Ieri quattro risultati promettenti sono caduti, e li produceva sempre lo stesso gesto: **cercare fra
molte combinazioni e tenere la vincente**. Con abbastanza tentativi si trova sempre qualcosa che ha
funzionato nel passato esaminato.

Oggi il criterio e' un altro: non cosa ha funzionato **meglio**, ma cosa ha funzionato **allo stesso
modo in ogni periodo**. Campione diviso in tre, e passa solo chi tiene direzione e forza in tutti e
tre. Severo apposta: meglio scartare un segnale vero che accettarne uno falso.

## Primo giro: 17 caratteristiche su 33 passano. E sono una trappola.

Il punteggio costruito su quelle mostrava quinti che salivano in fila e capacita' **0,731 e 0,730**
in due periodi mai visti — piu' stabile di qualunque cosa di ieri.

Ma i decimi rivelavano **uno scalino, non una salita**: tutto piatto fra il 2% e il 9%, poi un solo
decimo all'**85,3%** con mediana **+77,5%**, poi giu'. Un salto del genere non esiste in finanza.

**Cosa erano quei pool:**

| | decimo dello scalino | decimo normale |
|---|---|---|
| compratori distinti | **1** | 7 |
| quota di acquisti | **100%** | 42% |
| chi ha anche venduto | **0%** | 25% |
| disuguaglianza degli importi | 0,026 | 0,469 |

**Un solo portafoglio che fa 19 acquisti identici e non vende mai.** Rendimenti incollati: quartili
+70% / +78% / +80% su 319 pool diversi — l'aritmetica di una curva, non un mercato.

**La prova definitiva:** nelle 24 ore dopo l'ingresso quei pool hanno **166 scambi e ZERO vendite**;
l'**86%** non ha una singola vendita. Ci si entra e non si esce. Quel +77% non e' incassabile.

## La scoperta che vale piu' della strategia

Quei pool sono il **26% del nostro mondo**, e i «vincenti» sono quattro volte piu' concentrati li':

| robinhood | quota | fanno +50% |
|---|---|---|
| **invendibili** | 26% | **26,6%** |
| vendibili | 74% | **6,4%** |

**Ogni misura fatta finora era contaminata.** La vera probabilita' di un colpo grosso non e' l'11,7%
usato tutta la notte: e' **6,4%**.

E c'e' di piu'. Prima di togliere le trappole il fondale variava fra i periodi — 6,3%, 12,7%, 16,0%
— e ieri ne avevo concluso che **il mercato avesse cambiato regime**. Tolte le trappole: **7,1%,
6,6%, 5,6%**. Quasi piatto. **Quel cambio di regime non e' mai esistito**: era la quota variabile di
pool-trappola.

## Secondo giro, sui soli pool vendibili

Sopravvivono **5 caratteristiche su 33**, e tre sono misure di prezzo agganciate al prezzo
d'ingresso. Restano due, che dicono la stessa cosa: **vincono i pool con importi uniformi**, non
dominati da pochi scambi giganti. E stavolta i vincenti sono veri: 5 compratori, meta' acquisti e
meta' vendite, **33 vendite** nelle 24 ore dopo, rendimenti sparsi (+61% / +88% / +148%).

**Ma il conto economico la uccide:**

| gruppo | rendimento medio | in utile |
|---|---|---|
| quinto a importi uniformi | **+0,4%** | 41% |
| tutti i vendibili | −0,4% | 35% |
| quinto sbilanciato | −0,9% | 31% |

Tutto il vantaggio e' **0,8 punti**. Muore togliendo **un solo pool** su 1.414 (−0,7%) e muore con
un costo del 4% invece dell'1,8% (−1,8%).

## Verdetto

**Nessun vantaggio sfruttabile** in queste 33 caratteristiche, su robinhood, entrando a mezz'ora e
tenendo un giorno, sui pool da cui si puo' davvero uscire.

**Ma e' un no motivato, non un'illusione caduta.** Sappiamo che il mondo reale rende circa zero, che
le trappole erano un quarto del campione e inquinavano tutto, e che il «cambio di regime» era un
artefatto. Tre cose che ieri non sapevamo.

## Cosa cambia da adesso

`agents/insieme.py` registra per ogni pool **quante vendite** avvengono dopo l'ingresso. Non si
scartano — toglierli sarebbe una selezione che premia i casi buoni — ma ogni analisi futura puo'
separare il vendibile dall'illusorio. Senza quel campo, qualunque ricerca ritrova sempre e solo le
trappole, perche' sono le piu' redditizie sulla carta.

---

# Il numero che nessuno aveva mai misurato: −32,7%

*24 settembre, pomeriggio. Nato da un rilievo di Grok alla sua prima revisione.*

## Il rilievo

> *«L'esito e' la mediana di TUTTI gli swap. Con una frazione di acquisti sopra il 50%, la mediana
> e' un order statistic degli acquisti: una vendita sola non la sposta. Misura quanto pagano gli
> altri per entrare, non quanto incassi tu per uscire.»*

Mi ero difeso coi numeri: la quota mediana di vendite fra gli scambi e' **52%**, e solo il 2,8% dei
pool sta sotto il 20%. Sembrava chiuderla.

**Avevo torto, e il motivo e' nella coda.** La mediana descrive il pool tipico; il danno lo fanno i
pool dove le vendite sono quasi zero. Misurato: **il 26% dei pool che l'etichetta chiamava
«vendibili» non ha abbastanza vendite per misurare un'uscita.** Bastava UNA vendita in 24 ore per
prendere l'etichetta.

## Il numero

Esito misurato sul prezzo mediano dei **soli scambi di vendita** (chi non ne ha almeno 5 vale
perdita totale: non e' un caso da scartare, e' il caso peggiore):

| chain | media coi prezzi di TUTTI | media coi prezzi di USCITA |
|---|---|---|
| **robinhood** | +0,9% | **−32,7%** |
| **base** | −32,7% | **−43,9%** |

La quota di colpi grossi **incassabili** scende dall'11,7% al **3,9%**.

## Cosa questo cancella

**Tutto quello inseguito in tre giorni.** Il «+63% di portafoglio», il «4,2x meglio del caso», il
modello a «0,92», il «+0,4% del quinto migliore»: erano tutti misurati su prezzi che nessuno ha mai
pagato per USCIRE.

**Comprare memecoin nuovi e rivenderli perde circa un terzo del capitale.** Questo e' il fondale, e
da adesso ogni strategia si misura contro questo numero, non contro lo zero.

## Un errore mio, nel mezzo, che vale la pena raccontare

Nel verificare il rilievo ho prima ottenuto **+4,5%** con i prezzi di vendita, e stavo per
riportarlo come buona notizia. Poi ho controllato l'universo: avevo **saltato 1.419 pool su 7.073**
— quelli dove l'uscita non e' misurabile, che nell'insieme valgono −98%. Toglierli portava la media
da +0,4% a +9%.

**La stessa selezione che premia i casi buoni, rifatta da me, poche ore dopo averla denunciata.**
Non e' bastato saperlo: serviva controllare il conteggio dell'universo prima di guardare il
risultato. Da adesso e' la prima cosa che stampo.

## Perche' e' una buona notizia

- il metro misura **i soldi**, non i prezzi di vetrina;
- qualunque cosa sembri funzionare deve battere un **−33%**: le illusioni piccole spariscono da sole;
- **nessun euro rischiato** su nessuna delle quattro strategie che sembravano buone.

---

# Il bersaglio era sbagliato, e con esso tre giorni di ricerca

*24 settembre, pomeriggio. La scoperta metodologica piu' importante finora.*

## Cosa e' successo

Rifatta la ricerca contro il metro onesto (esito misurato sui prezzi di VENDITA), sopravvivevano 4
caratteristiche su 33, tutte misure di prezzo. Sospettavo fossero artefatti del denominatore — il
prezzo d'ingresso sta sotto la frazione dell'esito. **Verificato cambiando denominatore: non lo
erano.** Anzi si rafforzavano (volatilita' da 8,0x a 13,2x).

Poi ho guardato l'economia per quinti, e il quadro si e' ribaltato:

| quinto per volatilita' | fanno +50% | media | mediana |
|---|---|---|---|
| 1° (i piu' calmi) | 1,4% | −9,8% | −1,8% |
| **5° (i piu' volatili)** | **9,9%** | **−15,0%** | **−22,7%** |

**Il quinto piu' volatile becca il TRIPLO dei colpi grossi e ha la media PEGGIORE.**

## La lezione

**Misurare «quante volte fa +50%» premia la volatilita', non il vantaggio.** Cio' che oscilla di
piu' supera qualunque soglia piu' spesso — in entrambe le direzioni. I colpi grossi in piu' non
pagano le perdite in piu'.

Per tre giorni ho cercato «cosa alza la frequenza dei colpi grossi». Era la domanda sbagliata: la
risposta e' sempre «la volatilita'», e la volatilita' non e' un vantaggio, e' un rischio.

Il bersaglio giusto e' il **rendimento atteso**. Rifatto con quello, passano 12 caratteristiche su
33, e le quattro piu' forti raccontano una storia sola.

## Il segnale «la folla sta arrivando adesso»

| caratteristica | verso | cosa dice |
|---|---|---|
| ritmo in accelerazione | alto | gli scambi stanno aumentando |
| eta' del pool | basso | e' appena nato |
| portafogli nuovi nella seconda meta' | alto | arriva gente mai vista |
| scambi per portafoglio | basso | tanti partecipanti, non pochi che ripetono |

E' **l'opposto esatto** della regola del 23/09, che sceglieva i pool dove la folla era GIA' arrivata
— e che infatti ha fallito.

**Su due periodi mai visti, i numeri coincidono al decimale:**

| | periodo 2 | periodo 3 |
|---|---|---|
| quinto peggiore | −20,5% | −27,4% |
| quinto migliore | −7,6% | −8,8% |
| decimo migliore | **−4,4%** | **−4,2%** |

Il segnale e' vero e si ripete. **Ma resta negativo.**

## E poi cade anche quello: le uscite vere

Il −4,2% era misurato col prezzo MEDIANO delle 24 ore, che nessuno puo' scegliere. Rifatto
percorrendo la sequenza dei prezzi a cui qualcuno ha davvero venduto, uscendo con una regola:

| regola di uscita | tutti | decimo migliore |
|---|---|---|
| fine giornata | −26,3% | **−38,0%** |
| al primo +25% | −37,5% | −47,4% |
| al primo +50% | −35,9% | −46,0% |
| al primo +100% | −34,4% | −44,0% |
| se cala del 30% dal massimo | −29,6% | −46,8% |

**La classifica si ROVESCIA.** Il decimo migliore diventa il peggiore.

Perche': la regola identifica i pool che **si gonfiano durante il giorno e si sgonfiano entro
sera**. Il prezzo mediano delle 24 ore e' alto proprio per questo. Tenere fino alla fine e' un
disastro; uscire a bersaglio fisso tronca i guadagni e lascia intere le perdite.

E il picco lo conferma: **il decimo migliore ha lo stesso picco mediano di tutti gli altri (+7%)**,
e tocca +25% nel 33% dei casi contro il 31% della popolazione. Due punti. Il picco arriva dopo 1,2
ore mediane e poi svanisce.

## Verdetto

**Nessun vantaggio sfruttabile**, nemmeno con uscite intelligenti: provate sette regole diverse,
tutte peggiorano. Il segnale c'e' ma non produce piu' occasioni — produce solo percorsi di prezzo
piu' alti a meta' giornata, che non si possono incassare senza sapere quando uscire.

## Cosa resta di oggi

1. **Il fondale vero: −32,7%** su robinhood, −43,9% su base. Prima lo credevamo zero.
2. **Il bersaglio era sbagliato** — e questo invalida il metodo dei tre giorni precedenti, non solo
   i risultati.
3. **La liquidita' dei pool V4 si legge** (85% del nostro mondo, prima dichiarato irraggiungibile).
4. **Il 43% dei pool ha un hook** che puo' toccare l'uscita.
5. **Due revisori invece di uno**, e Grok ha trovato al primo colpo l'errore che ha sbloccato tutto.

Zero euro rischiati.
