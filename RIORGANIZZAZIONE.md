# Ventiquattro ore sulla macchina, non sui dati

**Mandato di Nicolò, 10 ottobre:** *«ci sono troppe robe che non funzionano. Voglio un giorno in
fila in loop, mentre parallelamente accumuliamo. Vedere cosa non va a livello di macchina, cosa
va stoppato, cosa semplificato, magari una roba ne abbiamo troppi e la caliamo. Non ci siamo mai
focalizzati su questo.»*

Ha ragione sulla diagnosi: finora si è sempre ampliato il database e fatta l'analisi, mai guardata
la macchina. E la causa della confusione è precisa — **nessuno aveva mai dichiarato chi scrive
cosa, dove e quando.** Senza quel contratto non esiste la nozione di «sbagliato»: un file nato nel
posto sbagliato, una corsia che gira quando non serve, un dato riscritto da due corsie non violano
niente, quindi nessun controllo li può vedere.

Mentre questo va avanti, **la demo accumula**: robinhood, monete appena diplomate, regola congelata.
Non si guarda la matrix per 24 ore.

## Da dove partiamo (misurato oggi, non a impressione)

| cosa | prima | adesso |
|---|---|---|
| corsie accese | **34** | **14** |
| file scritti da più di una corsia accesa | **19** | **2** |
| chain lavorate | 2 (base + robinhood) | 1 (solo robinhood) |
| crescita del repository | 2,5 GB/giorno | **0,07** |
| peso / margine | 9,85 GB / 0,15 | 7,68 GB / **2,32** |
| difetti di struttura aperti | 18 | **8** |

## Fatto

1. **Ridotto.** 20 corsie delle fasi chiuse spente, ognuna con il motivo scritto e il comando per
   riaccenderla (`data/corsie_spente.json`). Restano le 14 che servono: la demo, i suoi guardiani,
   il deposito, il revisore.
2. **Base fermata**, come chiesto: togliuta dalla matrice di 11 corsie, non spente — robinhood
   continua senza interruzioni.
3. **La mappa esiste** (`ORGANIZZAZIONE.md`, generata da `agents/mappa_organizzazione.py`): per
   ogni corsia accesa, quando gira, cosa scrive, come consegna. Generata dalla **realtà**, non
   dalle intenzioni: legge i file di corsia e i sorgenti.
4. **La revisione della struttura esiste** (`agents/revisione_struttura.py`): sette controlli nati
   dai guasti veri del 10 ottobre — strade del Mac nel codice che gira sul runner, guardie puntate
   su file morti, limiti di silenzio più corti dell'orologio, corsie che scrivono e non consegnano,
   file di corsia non validi, sorgenti che non compilano, memoria scritta male *e che costa*.
5. **Quattro limiti di silenzio riallineati** all'orologio della loro corsia: erano allarmi
   garantiti ogni giorno, e un allarme che suona sempre si impara a ignorarlo.
6. **La memoria ha un custode** (`agents/custode_memoria.py`), cancello davanti a ogni
   pubblicazione: conosce i due depositi (GitHub 10 GB, R2 100 GB) e giudica per costo.
7. **Recuperate 30 consulenze** di Astra che morivano sul runner, e riparata la pubblicazione.

## Da fare nelle prossime 24 ore

- [ ] **Il contratto, e chi lo fa rispettare.** La mappa oggi *descrive*; deve *vincolare*: una
      corsia che scrive fuori da dove ha dichiarato va fermata dal controllo, non scoperta dopo.
- [ ] **I 7 file di memoria scritti male** che costano ancora: `curva_lanci.json.gz` (52 MB in un
      pezzo solo, lo leggono dieci script: va convertito a righe con un lettore condiviso),
      `coppie.json` (16,6 MB), `wallet_scores.json`, i tre `tenute_pezzo_*.jsonl.gz`,
      `serie_pool.jsonl` (12.820 byte per record, porta dentro le serie).
- [ ] **Dove la memoria si perde.** Tre strade già viste: un file che vive solo in locale; un
      output che non arriva mai al ramo (la classe del guasto di Astra); un allegato che scade
      dopo sette giorni. Serve un controllo che le copra tutte e tre.
- [ ] **Dove il sistema si ferma.** 25 giri falliti nel periodo: andare a leggerli uno per uno,
      perché «fallito» senza motivo non insegna niente.
- [ ] **Chiedere ad Astra** come organizzare memoria e database: è il revisore esterno, costa
      $0,17 e vede i punti ciechi per definizione.
- [ ] **Un database vero per i file di ricerca.** Oggi la ricerca scrive file sparsi; vanno sotto
      un posto dichiarato, con un indice.

## Come si misura se queste 24 ore sono servite

Non dal numero di cose fatte, ma dalla tabella in cima: corsie accese, file a doppia scrittura,
crescita, difetti aperti. Se quei numeri non scendono, ho lavorato senza risolvere.

---

# Come siamo messi dopo dodici ore (aggiornato l'11 ottobre, notte)

| cosa si misura | prima | adesso |
|---|---|---|
| corsie accese | 34 | **14** |
| file scritti da più di una corsia | 19 | **2** |
| chain lavorate | 2 | **1** |
| crescita del repository | 2,5 GB/giorno | **0,00** |
| peso / margine | 9,85 GB / 0,15 | **7,28 / 2,72** |
| difetti di struttura aperti | 18 | **6** |
| file senza un posto dichiarato | 230 | **0** |
| strade aperte per perdere memoria | 3 note, mai misurate | **misurate a ogni giro** |

## Cosa è stato costruito, e perché ognuno serviva

- **`MANIFESTO.json`** — 30 prodotti, ogni file del progetto con un proprietario, un deposito e
  un motivo. Prima «posto sbagliato» non esisteva come concetto, quindi nessun controllo poteva
  vederlo. La regola viene da Astra: codice e documenti nel ramo, risultati di esecuzione in R2,
  **quello che non è dichiarato non si scrive**.
- **`agents/consegna_verificata.py`** — carica, **rilegge**, confronta le impronte, e solo allora
  scrive la ricevuta. «Riuscito» non lo dice più il produttore: lo dice la consegna.
- **`agents/archivio.py`** — una sola libreria di lettura. Due monoliti (52 e 16,6 MB) convertiti
  a righe, verificati voce per voce: 675.145 e 69.697, tutte identiche.
- **`agents/custode_memoria.py`** — il cancello sulla memoria, che giudica per **costo** (peso ×
  riscritture) e non per bruttezza.
- **`agents/revisione_struttura.py`** — sette controlli nati dai guasti veri del 10 ottobre.
- **`agents/dove_si_perde.py`** — le tre strade per cui la memoria si perde, tutte e tre.
- **`agents/processi_a_mano.py`** — il punto cieco: le guardie guardavano solo GitHub, e un
  `while true` è girato 44 ore su questo Mac rubando il nodo RPC alla demo.
- **`agents/quanto_pesa.py` e `quanto_cresce.py`** — la quota misurata invece che stimata.
- **`ORGANIZZAZIONE.md`** — chi scrive cosa, dove e quando, generato dalla realtà.

## I tre guasti che hanno insegnato più di tutto

1. **Trenta consulenze pagate morte sul runner** mentre il registro diceva «riuscito». Il codice
   di pubblicazione cercava una cartella del Mac. Recuperate dagli allegati per un soffio.
2. **Il verso degli scambi invertito** in tutto il progetto: compra/vendi erano scambiati, e
   quattro misure sui venditori sono state ritirate. Scoperto confrontando con i trasferimenti
   del gettone, non rileggendo la convenzione.
3. **Una ribasatura di git interrotta** ha cancellato 575 file (203 agenti) e fermato l'accumulo
   per 4,6 ore — e **tre controlli hanno taciuto insieme**, tutti perché dipendevano da git. Uno
   di loro ha perfino dato un *falso via libera* («zero strade aperte per perdere memoria»)
   mentre mancavano 575 file.

**Il filo comune:** nessuno dei tre era un errore di calcolo. Erano tutti attrezzi che tacevano.
Per questo il lavoro di queste ore è stato quasi tutto sul **far rumore quando qualcosa non va**,
non sul fare cose nuove.

## Quello che resta, e che non faccio

- **Non completo la migrazione alla libreria** su tutti gli agenti: l'avevo fatta sulla copia
  mutilata e copre 13 file; completarla vorrebbe dire toccarne ~40 di fasi chiuse per poter
  cancellare due file che ora costano zero. Churn senza beneficio, e il churn è il posto da cui
  vengono gli errori — stanotte ne ho fatti tre, tutti su modifiche in blocco.
- **Il disco al 97%** è la causa probabile del guasto a git e può ripetersi: la decisione di
  liberare spazio riguarda cartelle di Nicolò e non la prendo da solo.
