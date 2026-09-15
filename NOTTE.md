# 🌙 LA NOTTE DELL'AUDIT — consuntivo

*13-14 settembre 2026 · leggi questo per primo, gli altri documenti sono gli allegati*

> **La domanda:** il sistema è capace di scoprire un edge che non abbiamo immaginato, o stiamo
> ottimizzando dentro una scatola costruita da noi?

> **La risposta: la seconda. Dimostrata con una misura, non con un'opinione sul codice.**

---

## 1. COSA REGGE

### Il sistema non scopre: ottimizza — e ciò che trova non batte il caso

Test di permutazione a blocchi: struttura temporale intatta, esiti scambiati **solo fra token nati
lo stesso giorno**, selezione rieseguita per intero, il migliore vero confrontato col **massimo** dei
mondi permutati.

| chain | vero | il caso, al suo massimo | batte il caso? |
|---|---|---|---|
| base | −23,9% | −23,4% | ❌ |
| solana | −29,7% | −28,4% | ❌ |
| robinhood | −13,5% | −11,7% | ❌ |

**Su nessuna chain.** E il controllo di potere conferma che il modello stava davvero discriminando
(a soglie diverse sceglieva 197/188/181 righe su Base): il test aveva il potere di dire «sì», e ha
detto no.

Aggiungi la scala: LOOP 1 ha fatto **1.958.455 tentativi** su uno spazio di **384.000** combinazioni.
Lo ha percorso cinque volte. Il mio placebo ne prova poche decine — quindi il premio della ricerca
vero è **più grande** di quello misurato, e il confronto reale è ancora più severo.

### I dati costruiti e mai usati (verificato)

`wallet_scores.json` — 3,2 MB, 9.743 wallet — è letto **solo dall'agente che lo scrive**. Nessun
modello lo consuma. Idem `insider_scores`. I first-buyers entrano come semplice conteggio.

---

## 2. COSA È STATO DEMOLITO — dal revisore avversariale

Ho chiesto a ChatGPT di distruggere le mie quattro tesi. Ne ha abbattute due, e aveva ragione.

| tesi | esito |
|---|---|
| 1 — ottimizzatore, non motore di scoperta | ✅ regge, ma **indebolita**: il limite è la classe di ipotesi, non l'additività del modello |
| 2 — il migliore è rumore selezionato | ❌ **non dimostrata** quando l'ho detta → poi **dimostrata** col test di permutazione |
| 3 — dati mai usati | ✅ **fatto verificato**, ❌ cade il salto «quindi lì c'è valore» |
| 4 — test del segnale iniettato | ❌ **invalido come proposto**, va rifatto a quattro bracci con un oracolo |

Ha anche preso un mio errore di fatto (avevo messo in tabella BSC, chain abbandonata) e la confusione
fra +8% operativo e +10% pre-registrato.

**La sua critica più utile**: come si distingue «cerchiamo nel posto sbagliato» da «non c'è niente da
trovare»? Serve un **limite superiore simultaneo** su una classe esplicita di strategie. Solo se il
tetto del migliore sta sotto il cancello si può dire «in questi dati, con questi costi, nessuna
strategia di questa classe ce la fa» — e **mai** «non esiste un segnale».

**La misura che manca, e che nessuno aveva chiesto**: la probabilità che l'uscita fosse *davvero
eseguibile* a quel prezzo, operazione per operazione. Senza, «+10% netto» può essere una proprietà
dei nostri OHLC e non di una strategia eseguibile.

---

## 3. COSA È RIMASTO NON GIUDICABILE

**La classe arricchita** (identità dei wallet, sequenza degli scambi, tempi, concentrazione, memoria
point-in-time) **non è stata bocciata: non è stata provabile.**

| chain | righe valutate | con scambi **prima dell'entrata** |
|---|---|---|
| base | 1.708 | 118 |
| solana | 754 | 87 |
| robinhood | 659 | **0** |

E sulle 118 di Base il test era **vuoto**: tutte le soglie selezionavano tutte le righe, il modello
non si attivava mai. Il mio codice aveva scritto «la classe ricca non batte il caso». Era falso.
Adesso entrambi i test verificano di **avere potere** prima di emettere un verdetto.

### Perché quei numeri sono così bassi — la scoperta più amara della notte

Gli scambi ci sono: 395 token su Base, 510 su Solana, 179 su Robinhood hanno un file. Ma **arrivano
troppo tardi**. La fonte gratuita conserva solo gli ultimi ~300 scambi: quando interroghiamo un token
già maturo, i primi acquisti — quelli che dicono **chi** è entrato per primo, in che ordine, con che
tempi — **sono già stati buttati via da chi li ospitava**.

> Abbiamo passato settimane a ottimizzare dentro una classe di ipotesi povera, mentre l'unico dato
> che avrebbe potuto arricchirla **evaporava ogni giorno**, e nessuno lo raccoglieva nel momento in
> cui era ancora raccoglibile.

---

## 4. COSA HO RIPARATO STANOTTE

1. Il collettore degli scambi ora dà **priorità ai pool già valutabili**: ogni file scaricato diventa
   subito una riga interrogabile, invece che peso morto.
2. La staffetta conta i **token COMPLETI** (prezzo **+** scambi): 685 Base, 739 Solana, 198
   Robinhood. È l'unico numero che dice se ci stiamo avvicinando alla domanda vera, e si può far
   crescere **solo in avanti**.
3. Entrambi i test di audit ora **si autocontrollano** prima di dare un verdetto.

---

## 5. I MIEI ERRORI, PER ONESTÀ

Tre conclusioni sbagliate in una notte, **due già pubblicate**, tutte dalla stessa causa: ho letto
una copia locale invece dei dati veri. La regola era scritta. L'ho violata lo stesso, e ogni volta
avevo *una ragione* — era più veloce, era lì, il clone era «recente». La ragione era sempre buona e
il risultato sempre sbagliato.

E due verdetti falsi prodotti dai miei stessi strumenti, che dichiaravano un fallimento ogni volta
che non riuscivano a distinguere. **La malattia che inseguo da giorni, dentro gli strumenti costruiti
per diagnosticarla.**

---

## 6. IL PROSSIMO ESPERIMENTO PIÙ INFORMATIVO

Non è una strategia. È: **accumulare in avanti i token COMPLETI**, e quando ce ne sono abbastanza
(servono almeno ~400 con scambi pre-entrata perché il modello si attivi) rifare **esattamente** la
prova di permutazione sulla classe arricchita.

- se **batte il massimo del caso** → sappiamo dove vive il segnale, per la prima volta;
- se **non lo batte** → due classi molto diverse hanno fallito la stessa prova, e il 3 ottobre si
  chiude **con una prova invece che con una resa**.

**Il vincolo vero non è più l'idea: è il tempo.** Quei dati si costruiscono solo in avanti, e il
3 ottobre è fra 19 giorni.
