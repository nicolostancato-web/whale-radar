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
