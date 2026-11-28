# Cosa stiamo facendo — la versione da riferire a un investitore

*Scritto il 27 settembre 2026 su dettatura di Nicolò, perché possa essere ripetuto parola per parola
a chi sta sopra di lui. Nessun gergo tecnico: se una frase qui dentro non si capisce ad alta voce,
è scritta male.*

---

## Il goal, in una riga

**Costruire uno strumento che fa soldi.** Punto.

Tutto il resto è il metodo per arrivarci.

## Come ci arriviamo: una fabbrica di strategie

Non cerchiamo *la* buona idea. Costruiamo una **macchina che sforna un'idea dopo l'altra** e le
uccide in fretta, finché una non sopravvive.

**Loop 1 — sforna le strategie.** Formula un'ipotesi su come guadagnare, la mette alla prova sul
nostro database di scambi reali, ci lavora ore. Quando arriva a una conclusione che sembra
positiva, **non la si crede**: si passa ai revisori.

**Loop 0 — tiene in piedi la fabbrica.** Decine di agenti automatici raccolgono dati ventiquattro
ore su ventiquattro. Loop 0 controlla che girino, che non muoiano in silenzio, che non perdano
niente. Senza di lui il Loop 1 lavorerebbe su dati marci senza saperlo.

## I due revisori esterni, e perché sono due

Ogni conclusione importante passa da **due intelligenze diverse dalla mia**: **Astra** e **Grok**.

Servono in due perché ragionano in modo diverso. Il 24 settembre Grok ha trovato un errore logico
che Astra non aveva visto. Quando concordano per strade diverse, il risultato vale molto di più;
quando si contraddicono, abbiamo imparato dove scavare.

**Astra si chiama sempre, nel suo budget giornaliero** — costa pochi centesimi e dà una visione che
non abbiamo. Solo per le verifiche semplici si usa Grok da solo, che è incluso nell'abbonamento.

**Se dicono no, spiegano perché.** E quel "perché" non è una porta chiusa: è il materiale da cui
nasce l'ipotesi successiva. **La demolizione è produttiva.** Otto strategie morte finora, zero euro
rischiati, e ognuna ha lasciato uno strumento che non avevamo.

## La cosa che ci rende diversi: la fabbrica si ferma per ripararsi

Questa è la parte che vale la pena raccontare per intera.

Se durante l'analisi ci accorgiamo che **manca un dato**, ci fermiamo e **lo aggiungiamo al
database** — anche andando a riprenderlo dalla catena. Se ci accorgiamo che **un dato è sbagliato o
veniva perso**, ci fermiamo, ripariamo, e solo dopo ripartiamo.

Non è tempo perso: è l'unico modo di non produrre scarti. Una fabbrica che sa di avere un buco e
continua a produrre, produce difetti più in fretta.

**È successo questa settimana, due volte.**

Una strategia sembrava viva — dava l'11% — ed è morta quando abbiamo misurato **quanti soldi
passavano davvero** a quei prezzi: trentadue dollari. Un guadagno vero sulla carta, impossibile da
incassare. Quel dato — quanto un mercato può contenere — **c'era nei messaggi della catena e lo
buttavamo via da un mese**. Ora lo registriamo, e fra due giorni ne avremo abbastanza per usarlo.

E abbiamo scoperto che stavamo **perdendo dati**: quattro volte ogni sei ore, quando un raccoglitore
non riusciva a salvare, il suo lavoro moriva. Ora c'è una rete che lo mette in salvo e un percorso
che lo rimette dentro. Ha già recuperato migliaia di righe che sarebbero sparite.

**Il punto da sottolineare:** non ce ne siamo accorti per caso. Ce ne siamo accorti **perché siamo
diventati più bravi a guardare**. Un mese fa quegli stessi errori sarebbero passati inosservati.

## Il motore vero: diventare più intelligenti ogni giorno

**Una volta al giorno il sistema si ferma e si chiede: «come posso essere più forte, più sveglio,
più preciso di ieri?»** Poi mette in pratica la risposta.

Non è una frase motivazionale: è una procedura, e produce modifiche al codice.

Funziona perché ogni miglioramento **rende visibili errori che prima non si vedevano**, e ogni
errore visto produce il miglioramento successivo. L'anello si chiude su se stesso e gira sempre più
in fretta.

### La chiave, e non è sugli errori

Quasi tutti i sistemi che «imparano» imparano **dagli sbagli**. È metà del lavoro, e la metà facile:
**un errore si fa notare da solo.**

L'altra metà è quella che fa la differenza. **Ogni volta che produciamo qualcosa di buono — una
strategia, un'analisi, un giro di ricerca — ci chiediamo: come deve essere fatta domani perché sia
migliore di questa?**

Perché è più forte di quanto sembri: **nessuno critica una proposta che non è sbagliata.** Una buona
idea passa, viene approvata, e resta identica per sempre. Se non le si fa la domanda apposta, il
livello si ferma dov'è — e si continua a produrre per anni allo stesso livello, convinti di
migliorare solo perché non si sbaglia.

L'esempio più concreto: **le istruzioni che diamo a Grok per cercare.** Non cambiamo Grok. Miglioriamo
ogni giorno cosa gli chiediamo e come. Dopo un mese la stessa intelligenza produce risultati che il
primo giorno non avrebbe mai trovato — **senza che sia cambiato niente tranne la domanda.**

Questo vale per ogni cosa che facciamo: la strategia di domani non deve essere diversa da quella di
oggi, deve essere **migliore di come oggi sapevamo farla**.

**Si misura.** Non dai risultati — quelli vanno e vengono — ma da **quanto in fretta riconosciamo
lo stesso tipo di errore**:

| quando | quanto ci abbiamo messo |
|---|---|
| 22 settembre | un piano intero costruito storto |
| 23 settembre | sei ore |
| 24 settembre | trenta minuti, poi dieci |
| 27 settembre | pochi minuti, da solo, mentre facevo altro |

**Se quel tempo scende, stiamo imparando. Se resta uguale, stiamo solo lavorando.**

## Dove prendiamo il sapere che non abbiamo

**Grok cerca in continuazione su X e su GitHub**, e non "cosa sta per esplodere" — quello è rumore.
Cerca due cose:

1. **conoscenza di trading**: chi discute strategie, chi pubblica analisi con numeri veri, chi mette
   il link al codice;
2. **conoscenza di costruzione**: come si costruiscono sistemi di agenti che non cadono, che
   flussi usano, che architetture reggono.

Il secondo punto vale quanto il primo: **non serve solo sapere cosa cercare, serve saper costruire
meglio la macchina che cerca.**

Ha già dato risultati concreti: un meccanismo di truffa costruito apposta contro il metodo che
usavamo, con gli indirizzi verificabili. Quel tipo di cosa non si trova in un archivio di codice —
si trova dove la gente la smonta in pubblico.

## Perché ci aspettiamo di arrivarci

Non perché abbiamo un'idea geniale in canna. **Perché la macchina migliora da sola.**

Ogni giro produce un'ipotesi più informata del giro prima, perché ha più dati, strumenti più
affilati e meno modi di ingannarsi. Gli attributi del database si possono aggiungere in qualunque
momento: il giorno in cui capiremo che ne serve uno nuovo, lo andiamo a prendere e rifacciamo
l'analisi con quello dentro.

**La scommessa è statistica, non fortunata:** se ogni settimana siamo più intelligenti, più veloci
a scartare il falso e più ricchi di dati, la probabilità che una delle ipotesi sia quella giusta
cresce ad ogni giro. E il costo di sbagliare resta zero, perché non rischiamo un euro finché una
strategia non ha passato tutti e due i revisori.

## Lo stato oggi, senza abbellimenti

- **otto strategie provate, otto morte, zero euro rischiati**
- database di **12.300 mercati** e decine di milioni di scambi, su due chain
- **quattro strumenti di misura riparati** questa settimana: erano rotti, e con loro avevamo ucciso
  strategie che forse non meritavano di morire
- i dati hanno una **seconda casa** indipendente da GitHub, verificata copia per copia
- il dato che mancava si accumula: **330 mercati su 600** che servono per fidarsi del risultato
- la prossima prova è **già scritta e congelata**, prima di aver visto i dati, così non possiamo
  adattarla al risultato

**Non abbiamo ancora una strategia che funziona. Abbiamo una fabbrica che ne prova una dopo l'altra
e che ogni giorno sbaglia meno.**
