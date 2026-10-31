# La regola da provare in avanti — registrata il 29/09, RISCRITTA l'1/10

> ## ⚠ RISCRITTURA DELL'1/10: la misura era sbagliata, non la regola
>
> Tutto quello che segue misurava l'esito **comprando al prezzo dello scambio a cui entriamo**.
> Quel prezzo **non si puo' avere**: per comprare si manda una transazione, eseguita DOPO quelle
> davanti. Si paga il prezzo successivo, e sui pool veloci costa il **38% in piu' in mediana**.
>
> Effetto: il primo numero positivo del progetto (+17,6%) diventa **−11,4%** con UN solo scambio
> di latenza. Il giudice stava per emettere un verdetto preciso su un prezzo che non esiste.
>
> **Cosa cambia:** il campo su cui si giudica e' `_uscita_25_ritardo`, non `_uscita_25`.
> **Il conteggio riparte da zero** — i pool registrati con la vecchia misura non valgono, e
> mescolarli darebbe un verdetto su due cose diverse. Il codice lo dichiara da solo quando
> accade.
>
> **La data del verdetto slitta** di conseguenza: serviranno di nuovo 5.000 pool nuovi per chain.
>
> Dettagli: `LATENZA_LA_SCOPERTA.md`.

---

# La regola da provare in avanti — registrata il 29/09, prima di avere i dati

**Questo documento e' il contratto. Ogni parola vale come scritta: se domani il risultato non
piace, si cambia il verdetto, non la regola.**

## La regola, per intero e senza parametri da scegliere dopo

1. Si compra **$25** in **ogni** pool nuovo. Nessuna selezione: si copre tutto.
2. Si compra al **5° scambio** del pool.
3. Il prezzo di riferimento e' **il prezzo dello scambio a cui entriamo**, non la mediana dei
   precedenti. *(Clausola corretta il 30/09, poche ore dopo averla scritta: avevo messo la
   mediana degli ultimi cinque per togliere l'impatto del singolo scambio, ed e' PEGGIO. Alla
   nascita il prezzo sale a scatti — +8-9% nei primi cinque scambi — quindi la mediana sta sotto
   il prezzo che pagherei davvero, nel 67% dei pool su robinhood e nell'80% su base. Gonfiava il
   guadagno di 5 punti su robinhood e di 7 su base, e mi aveva fatto annunciare base come
   positiva quando e' piatta. **Una correzione che migliora il risultato va sospettata prima di
   essere celebrata.**)*
4. Si liquida dentro **168 ore** vendendo dentro il flusso reale; cio' che non si riesce a
   vendere vale zero.
5. **Non si entra se il gas costa piu' dell'1% della posizione** (cioe' piu' di $0,25 andata e
   ritorno su $25). Il gas si conosce PRIMA di comprare, quindi e' una condizione d'ingresso,
   non un rischio nascosto.
6. Costo di giro contato: **1,8%**.

## Cosa dicono i dati passati (e perche' non bastano)

| | robinhood | base |
|---|---|---|
| media | **+19,4%** | +1,6% |
| mediana | +1,1% | +0,2% |
| in pari | 53% | 51% |
| togliendo l'1% migliore | +12,0% | −2,2% |
| pool | 20.789 | 14.007 |

*(Numeri corretti il 30/09 col prezzo d'ingresso giusto. La versione precedente diceva +24,8% e
+8,3% ed era gonfiata dalla clausola 3 sbagliata.)*

**Su base NON funziona**: +1,6% di media, mediana +0,2%, e togliendo l'1% migliore va sotto zero.
La condizione «serve su tutte e due le chain» **non e' soddisfatta oggi**. Robinhood regge su
tutti i periodi misurati; base no.

## Aggiornamento del 30/09 sera — campione cresciuto di quattromila pool

L'insieme e' passato da 20.789 a 24.647 pool su robinhood (da 14.007 a 16.761 su base). Stessa
regola, stesso metro:

| | ieri | oggi |
|---|---|---|
| robinhood | +19,4% | **+17,6%** (intervallo 90%: +16,7% / +18,7%) |
| robinhood senza l'1% migliore | +12,0% | +10,4% |
| robinhood, periodi positivi | 5 su 5 | **5 su 5** |
| base | +1,6% | **−2,3%** |
| base, ultimi due periodi | −3,1% e −5,8% | −10% e −14% |

**Robinhood tiene. Base e' passata sotto zero**, e non per rumore: peggiora man mano che
arrivano dati. La condizione «serve su tutte e due le chain» resta non soddisfatta, e adesso lo
e' in modo piu' netto di ieri.

## Le tre prove superate oggi

1. **Non e' il rientro dall'impatto di una vendita.** Il sospetto era che il modello scegliesse
   i pool col prezzo d'ingresso depresso. Misurato: il decile scelto ha il prezzo d'ingresso
   SOPRA la media recente (+0,086 contro +0,021) e il legame fra ingresso depresso e guadagno e'
   positivo, non negativo. Il modello cerca **slancio**, non prezzi schiacciati.
2. **Non e' un rimbalzo immediato.** Il guadagno misurato sul prezzo mediano dell'intera
   finestra e' piu' grande di quello preso vendendo subito.
3. **Non lo fanno pochi fortunati.** Togliendo l'1% migliore resta +16,8%, e la mediana e'
   positiva in cinque periodi su sei.

## La forma del mestiere — chi fa quel guadagno

Non e' un mercato che sale: e' un mercato dove **si perde poco quasi sempre e si guadagna molto
raramente**.

| robinhood | quota dei pool | contributo alla media |
|---|---|---|
| sotto +100% | 90,1% | **−4,5%** |
| sopra +100% | 9,9% (2.062 pool) | **+23,5%** |
| di cui sopra +500% | 0,8% (170 pool) | +6,7% |
| al tetto del calcolo (+1900%) | 2 pool | +0,2% |

**Non lo fanno due fortunati**: duemila pool sopra il raddoppio sono una popolazione, non un
aneddoto. E il tetto del calcolo non conta nulla (due pool), quindi il numero non e' un
artefatto del troncamento.

**Perche' base non funziona, detto bene:** sul lato perdite e' identica (−4,8% sul 97% dei pool).
La differenza e' che i vincitori sopra +100% sono il **3,0%** invece del 9,9%. Base non perde di
piu': **produce meno vincitori grossi**.

### Cosa impone questa forma

Con un tasso di successo del 10%, **servono decine di posizioni** perche' la statistica si
realizzi. Dieci scommesse non sono una prova di niente: potrebbero facilmente essere dieci
perdite del 4,5% con zero vincitori, e sarebbe **coerente con una strategia che funziona**.

E' anche il motivo per cui la taglia deve restare piccola: il capitale si divide su molte
posizioni, non si concentra.

## Le quattro cose che possono ucciderla, e che i dati passati NON possono dire

1. **Il gas — misurato, e meno grave di come l'avevo raccontato.**

   | robinhood, 5° scambio | lordo | gas ($0,05/scambio) | **netto** |
   |---|---|---|---|
   | $25 | +19,4% | 0,40% | **+19,0%** |
   | $100 | +13,6% | 0,10% | +13,5% |
   | $500 | +4,8% | 0,02% | +4,7% |

   Anche col gas dell'impennata di inizio settembre — **$1 per scambio**, venti volte il normale —
   il netto resta **+11,4%** a $25 e +11,6% a $100: il vantaggio lordo lo assorbe.

   Resta vero che il **picco estremo** ($64 per transazione, durato minuti) azzera tutto. Ma si
   vede prima di entrare, ed e' la regola 5.

   *Nota pratica:* a $100 si perdono sei punti di vantaggio ma servono **un quarto delle
   posizioni** per lo stesso capitale — un quarto delle transazioni e un quarto delle occasioni
   di sbagliare. La regola registrata resta $25 perche' e' dove il vantaggio e' massimo; $100 e'
   la variante per quando conta la capienza.
2. **La velocita' di reazione.** Bisogna accorgersi del pool ed essere dentro al 5° scambio.
   Nessun numero qui misura quel tempo.
3. **La capienza.** A $500 il vantaggio sparisce. Un portafoglio vero significa MOLTE posizioni
   piccole, non una grande — e quindi molte transazioni, e quindi di nuovo il gas.
4. **L'epoca.** Quattro dei sei periodi buoni sono di settembre.

## Il secondo candidato: la selezione, col modello CONGELATO oggi

Il contratto sopra misura il fondale «compra tutto». Ma la selezione — bocciata quindici volte,
e che sul dato corretto batte il fondale in **undici finestre su dodici, di +24,6 punti** — e' un
candidato a se', e senza registrarlo adesso non si potrebbe giudicare sul futuro.

**Il modello e' stato congelato il 30/09** su 25.233 pool (robinhood) e 17.399 (base), 33
caratteristiche, tutte note PRIMA di comprare. Da questo momento si **applica**, non si
riaddestra: `data/loop1/modello_congelato.json`.

> **Un modello che impara ogni giorno non si puo' giudicare sul futuro: quando arriva il
> verdetto, ha gia' visto i dati su cui lo stai giudicando.**

Il giudice registra, per ogni pool nuovo, l'esito **e** il punteggio del modello congelato. Al
traguardo dira' due numeri: il fondale, e il decimo migliore secondo il modello.

- Se il decimo migliore **batte** il fondale: la selezione e' un vantaggio vero.
- Se lo batte solo quando il modello si riaddestra: era memoria del passato.

## Come si giudica — deciso adesso

- Su pool **nati dopo il 30/09/2026**, che oggi non esistono.
- **Almeno 5.000 pool nuovi per chain** prima di guardare. *(Alzata da 1.500 il 30/09, prima di
  vedere un solo esito: il ritmo misurato e' ~2.000 pool giudicabili al giorno su robinhood e
  ~1.100 su base, quindi 1.500 si chiudevano in un giorno. Con code grasse — il 10% dei vincitori
  porta tutto — pochi casi li decide la fortuna. **Alzare l'asta prima di guardare e' lecito;
  abbassarla dopo aver visto, no.**)*
- **Tempi attesi:** i pool nati oggi diventano giudicabili fra sette giorni (la finestra e' 168
  ore). Con 5.000 richiesti, il verdetto arriva intorno al **10 ottobre 2026**.
- **Si guarda una volta sola**, a fine finestra. Guardare presto e fermarsi quando piace e' il
  modo classico di comprare rumore.
- **Soglia: media sopra +3%** al netto dei costi. Sotto, non si procede.
- Se passa su robinhood e non su base, **non e' bocciata**: si annota che vale dove il mercato
  regge, e si continua solo li'.

**Nessun euro rischiato prima che questa prova sia chiusa.**
