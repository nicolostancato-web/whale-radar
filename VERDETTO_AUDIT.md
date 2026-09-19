# ⚖️ VERDETTO DELL'AUDIT

*13-14/09/2026 · la domanda della notte, e la risposta*

> **«Il nostro sistema è capace di scoprire un edge che non abbiamo immaginato, o stiamo facendo
> ottimizzazione su un piccolo spazio di idee costruito da noi?»**

## La risposta: la seconda, e adesso è dimostrata

Non per ragionamento sul codice — per **un fatto misurato**.

Test di permutazione a blocchi: stessa struttura temporale, esiti scambiati **solo fra token nati lo
stesso giorno**, selezione rieseguita **per intero**, il migliore vero confrontato con il **massimo**
dei mondi permutati.

| chain | vero | il caso, al suo massimo | batte il caso? |
|---|---|---|---|
| base | −23,9% | −23,4% | ❌ |
| solana | −29,7% | −28,4% | ❌ |
| robinhood | −13,5% | −11,7% | ❌ |

**Su nessuna chain.** E il nostro placebo prova poche decine di configurazioni, mentre LOOP 1 ne ha
provate **1.958.455** su Base: il premio della ricerca vero è **più grande** di quello misurato qui.
Il confronto reale è ancora più severo.

---

## 1. COSA STIAMO FACENDO OGGI

Una griglia fissa di 9 parametri (384.000 combinazioni) più una regressione logistica su 10 feature
scritte a mano. Quattro corsie che girano 24 ore su 24 a costo zero.

## 2. COSA FUNZIONA

L'apparato di misura: controlli appaiati, placebo all'indietro, prove indipendenti per gruppi,
cassaforte divisa per **tempo**, criteri di morte scritti prima (10 idee provate, 8 morte, nessuna
soglia spostata dopo il risultato). **Il laboratorio è serio.**

## 3. COSA NON FUNZIONA

Lo spazio di ricerca. Esaurito cinque volte su Base, e ciò che ne esce è indistinguibile dal rumore.

## 4. DOVE SIAMO LIMITATI

Dalla **classe di ipotesi**, non dall'additività del modello: strategia = «entra a un'ora fissa se
il volume basta, esci a multipli o allo stop». Fuori da quella forma il sistema non può nemmeno
formulare una domanda.

## 5. DATI SFRUTTATI MALE

Gli scambi: 13.000 file con wallet, importo e istante, ridotti a **quattro aggregati**. `sell_ratio`
è identico se le vendite arrivano prima o dopo gli acquisti.

## 6. DATI NON SFRUTTATI

`wallet_scores.json` (3,2 MB, 9.743 wallet) letto **solo da chi lo scrive**; `insider_scores` idem;
i first-buyers entrano come semplice conteggio; la liquidità non è mai una feature; l'ora del giorno
e l'età al segnale non esistono.

## 7. DOMANDE MAI FATTE

Conta il livello o il cambiamento? La sequenza? I tempi fra un'operazione e l'altra? **Chi** compra,
non quanti? Esistono interazioni? Esistono segnali validi solo in certe condizioni?

## 8. NUOVE DIREZIONI

Una sola, e precisa: **arricchire la classe di ipotesi** con identità e relazioni fra wallet,
sequenze e tempi degli scambi, liquidità, interazioni — e **rifare esattamente questo stesso test**.

## 9. TEST PRIMA DI IMPLEMENTARE

Per ogni nuova variabile, tre controlli obbligatori prima di crederle:
1. **disponibilità al momento**: ricostruita come istantanea storica, mai con dati successivi
   (altrimenti è fuga di informazione, non miglioramento);
2. **stratificazione**: testata dentro blocchi di chain, giorno, età e liquidità, perché «wallet
   ricorrente» può voler dire solo «bot» o «periodo di euforia»;
3. **la stessa permutazione a blocchi**: se la classe arricchita non batte il massimo del caso, è
   morta come questa.

## 10. LOOP 1 È UN MOTORE DI SCOPERTA?

**No.** È un ottimizzatore su una classe di ipotesi scritta a mano, e su quella classe non c'è nulla
da trovare.

## 11. COME ANDREBBE CAMBIATO

Il pezzo mancante non è in fondo alla catena, è **all'inizio**: manca la generazione automatica delle
domande.

```
DATI GREZZI
   ↓  costruzione automatica di feature   ← NON ESISTE
   ↓  scoperta sulla metà VECCHIA          ← esiste da oggi, minuscola
   ↓  registrazione dell'ipotesi (criterio di morte scritto prima)
   ↓  prova sulla metà RECENTE, mai vista
   ↓  permutazione a blocchi                ← esiste da stanotte
   ↓  cassaforte (una lettura sola)
   ↓  giudice
```

## 12. IL PROSSIMO ESPERIMENTO PIÙ INFORMATIVO

**Costruire la classe di ipotesi arricchita e sottoporla a questo stesso test di permutazione.**

- se **batte il massimo del caso** → il segnale vive lì, e sappiamo dove guardare;
- se **non lo batte** → due classi molto diverse hanno fallito lo stesso test, e l'ipotesi «in questi
  dati non c'è un vantaggio raggiungibile» diventa la spiegazione più semplice. Il 3 ottobre si
  chiude, con una prova invece che con una resa.

In entrambi i casi **si impara qualcosa di decisivo**, ed è la definizione di esperimento più
informativo.

---

## STATO DELLE AFFERMAZIONI

| affermazione | tipo |
|---|---|
| il vero non batte il massimo dei permutati su tre chain | **MISURATO** |
| la classe di ipotesi non contiene wallet, sequenze, interazioni | **MISURATO** (lettura del codice) |
| continuare a ottimizzare questa classe è tempo perso | **INFERITO**, con prova forte |
| un segnale vive nelle variabili non rappresentate | **IPOTIZZATO** — non ancora giudicabile |
| nei dati disponibili non esiste alcun vantaggio | **NON GIUDICABILE**: servirebbe un limite superiore su una classe molto più ricca |
