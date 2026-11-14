# Revisione di Grok — 1 ottobre 2026

Revisore esterno, dall'abbonamento (costo zero). Domanda: dove si rompe il metodo con cui
sto cercando il vantaggio. Risposta ostile, come richiesto.

## I tre colpi che ho incassato subito

### 1. Il denominatore era quello che avevo scelto di scrivere

> «Il denominatore coincide con la riga che avete scelto di scrivere. Lo sguardo che poteva
> farvi cambiare idea sono i 10.700 confronti dentro ogni configurazione, e quella riga li
> cancella.»

Registravo **una riga per configurazione**. Gli sguardi veri sono 10.700 per giro.

| denominatore | soglia richiesta |
|---|---|
| 13 righe (quello che usavo) | 17,4% |
| 139.100 confronti (quello vero) | **44,2%** |
| 256.800 confronti (a rotazione finita) | 45,9% |

**Conseguenza immediata: il margine migliore mai misurato, +17,0% su base, non passa.**
Passava la vecchia soglia per un soffio. Non passa quella onesta. Niente di quello che ho
trovato finora sopravvive.

*Fatto:* `quanti_sguardi()` in `agents/ciclo_ipotesi.py`, e ogni riga del registro porta ora
`confronti` e `sguardi_totali`.

### 2. Il controllo sul rumore ha un punto cieco preciso

> «Mescolare gli esiti e tenere ferme le condizioni lascia in piedi il campione. Nel mazzo ci
> sono soltanto le righe con uno scambio successivo archiviato. Passa una regola correlata con
> "qui c'è un print archiviato": vera nel file, ineseguibile sul mercato.»

Il controllo distrugge il legame condizione→esito ma **non** la selezione del campione. Una
regola che in fondo dice «scegli le pool dove per caso esiste uno scambio successivo
registrato» supera il controllo ed è ineseguibile.

*Non ancora fatto.* È il prossimo lavoro: i pool senza scambio successivo devono entrare nel
denominatore come esito zero, non sparire.

### 3. La previsione sulle prossime 48 ore

> «Entro 48 ore il −12,1% diventa una condizione nuova — solo 25$, "taglia piccola rispetto al
> trade successivo", un quarto atomo — stimata sullo stesso campione, e il registro non cresce
> perché la riga di configurazione è la stessa.»

È la mossa che domani verrebbe naturale.

*Fatto:* i 33 atomi sono congelati con un'impronta (`data/atomi_congelati.json`) e un controllo
**grave** in `agents/decisioni.py`. Cambiarli resta possibile; cambiarli senza accorgersene no.

## Come distinguere capacità minuscola da rumore

Grok, sul −12,1% che compare passando da $25 a $100:

> «È coerente con una capacità minuscola e col massimo del rumore.»

Il modo di separarli, sulla sola fetta di giudizio:
- limite inferiore al 95% del rendimento a $25, al prezzo di chi arriva dopo di noi: **sotto
  zero → nessun vantaggio**;
- sopra zero, e il buco fino a $100 uguale all'impatto misurato dai tagli → **capacità piccola**;
- bello a $25 solo nella fetta di ricerca → **rumore**.

## I rilievi sul fascicolo che devo ancora verificare

1. L'audit del 01/10 stampa `0,0%` su un campione di **0 file**: un fallimento vestito da tasso
   pulito. Una percentuale va calcolata solo se il denominatore è maggiore di zero.
2. Due costi non possono descrivere lo stesso prezzo: +38% mediano sul trade successivo contro
   costo d'uscita sotto l'8% in 1.207 eventi su 1.207. Una soglia che non taglia nessun evento
   non ha misurato niente.
3. Il denominatore «congelato» del 20/09 ha 8.869 pool su base; l'estrazione corretta del 21/09
   ne ha 13.295. E nella stessa lista convivono indirizzi da 42 e da 66 caratteri.
4. La staffetta su cui deciderei è del 17/09: scaduta per la sua stessa regola, e l'ordine che
   contiene è «riaccendere il motore».
5. Due esperimenti dichiarati morti hanno la corsia ancora viva ogni 5 minuti: continueranno a
   produrre numeri che sembreranno misure nuove.

Ognuno di questi arriva con il modo di smentirlo. Sono il lavoro dei prossimi giorni.
