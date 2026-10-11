# ☀️ LA NOTTE SUL DATABASE — cosa è successo e le domande

*15 settembre 2026, ore 3 · focus database come da direttiva*

---

## 1. LA SCOPERTA CHE SBLOCCA MESI DI STALLO

Il limite delle ~300 transazioni — quello su cui ci arenavamo da mesi — **è della fonte gratuita,
non della catena.** Sulla catena c'è tutto, per sempre.

Sbagliavamo la domanda: chiedevamo **un pool alla volta**, e il nodo rifiutava perché doveva cercare
in milioni di blocchi. Chiedendo **una fascia di blocchi per tutti i pool insieme**, risponde subito.

Prima prova: **108.092 scambi da 4.382 pool in 50 secondi.** Tutto il nostro archivio storico,
accumulato in settimane, era di ~30.000.

**Costo: €0.** Nodi pubblici gratuiti, minuti GitHub gratuiti su repo pubblico. Per Base e Robinhood
**non serve pagare niente**. (Solana è un'altra tecnologia: là l'API a pagamento potrebbe servire
davvero, e te la proporrò coi numeri quando ci arriveremo.)

---

## 2. DOVE SIAMO ADESSO

| | |
|---|---|
| pool con storia dalla catena | base **2.393**, robinhood **399** |
| copertura delle righe valutabili | base **13,9%**, robinhood **21,4%** |
| pool scoperti raggiungibili continuando | **100%** — sono tutti dentro la fascia che le fette scavano |
| qualità del dato nuovo | wallet 100%, istanti 100%, date impossibili 0, **duplicati 0** |
| peso del repo | 322 MB (tetto e potatura attivi) |

**Le sei variabili nuove, calcolate sul dato dalla catena, sono sane su Base**: 99-129 valori
distinti ciascuna, nessuna degenere. Non è una promessa: è misurato.

| variabile | mediana | valori distinti |
|---|---|---|
| ordine vendite/acquisti | 0,002 | 124 |
| tempo fra le operazioni | 0,70 | 38 |
| raffiche | 18,7 | 129 |
| concentrazione del più grosso | 0,39 | 127 |
| quanti ricomprano | 0,55 | 99 |
| wallet già visti | 0,47 | 105 |

---

## 3. LA QUINTA CORSIA, COME AVEVI PROPOSTO

Esiste e gira: **`database`**. Non conta i file — giudica se servono. Al primo giro ha segnalato
**nove fallimenti**, tutti quelli che avevo trovato a mano in 48 ore. Se fosse esistita due mesi fa,
li avrebbe urlati il primo giorno.

Più **dodici fette in parallelo** che scavano la storia (0, 6, 12, 18, 24, 30 giorni indietro).

---

## 4. LA DOMANDA CHE TI LASCIO, E NON DECIDO DA SOLO

**Il dato dalla catena deve sottostare allo stesso ritardo di quello delle API?**

Oggi il sistema impone un **embargo di 35,4 ore**: per decidere può usare solo dati vecchi di almeno
35 ore. Nasce da una misura vera — le API gratuite ci consegnano i dati con quel ritardo — ed è una
prudenza giusta *per quelle fonti*.

Ma la catena **la leggiamo noi**, direttamente, senza intermediari. Un blocco è nostro nel momento in
cui esiste.

**Le due letture, e le conseguenze:**

| | |
|---|---|
| **A) stesso embargo per tutti** | prudente, coerente col passato, ma **azzera quasi tutto** il valore della raccolta di stanotte |
| **B) embargo per fonte** | la catena ha ritardo ~zero, le API 35 ore. Sblocca le variabili nuove, **ma cambia il metro** rispetto a tutti i confronti storici |

Io propendo per **B**, perché è più vicina alla verità: fingere di ricevere in ritardo un dato che
abbiamo subito è prudenza che costa e non protegge da niente. **Ma non la applico senza il tuo OK e
senza passarla dal consulente esterno**, perché cambia retroattivamente il significato di ogni numero
passato — ed è esattamente il tipo di scelta che, fatta di notte e da soli, diventa un errore che
nessuno ricorda di aver preso.

---

## 5. ONESTÀ SULLA NOTTE

Sette guasti trovati e riparati, **cinque erano miei**:

1. le fette si arrendevano al primo rifiuto del nodo invece di rallentare
2. il salvataggio riportava "riuscito" senza aver salvato niente
3. una funzione chiamava se stessa (sei lavori morti dopo 12 minuti)
4. salvavo solo dopo tre ore: una morte e spariva tutto
5. il segnalibro faceva ripartire le fette dalle **vecchie** posizioni, annullando due correzioni di fila
6. deduplicavo per transazione, ma una transazione può contenere **più scambi** (1.014 duplicati)
7. su Robinhood cercavo l'identità del pool nel posto sbagliato (pool dentro un unico contratto)

E cinque volte ho tratto conclusioni da **copie locali vecchie** invece che dai dati veri. La regola
era scritta. L'ho violata lo stesso, ogni volta con una buona ragione.

---

## 6. COSA SUCCEDE SE NON TOCCHI NIENTE

Le dodici fette continuano a scavare. La copertura sale da sola. Il guardiano controlla che quello
che entra serva a qualcosa, e la potatura tiene il repo sotto controllo.

**Non parte nessuna ricerca di strategie** finché non c'è l'ufficializzazione scritta, come hai
chiesto.

---

# AGGIORNAMENTO DELLE 6 — perché la copertura si è fermata al 14%

## Il quadro esatto

| | base | robinhood |
|---|---|---|
| pool con **contratto proprio** | **248/298 = 83%** | 157/331 = 47% |
| pool dentro un **contratto unico** | **0/1.413** | 0/347 |
| totale | 14,5% | 23,2% |

Il meccanismo funziona benissimo dove il pool ha un contratto suo. Sui pool che vivono dentro un
unico contratto — che su Base sono **l'83% di quelli che ci servono** — non ne abbiamo preso **uno**.

## Non è un difetto di codice: l'ho tracciato

Su 100 blocchi recenti di Base:

```
704 scambi di quel tipo
 → 52 sono su pool NOSTRI          ✅ il riconoscimento funziona
 → 52 si decodificano              ✅ la firma è giusta
 → 0 passano il filtro sulla nascita  ← qui
```

Li scartiamo perché sono **oltre le prime 6 ore di vita del pool**. E hanno ragione a essere
scartati: a noi servono i **primi** scambi, non quelli di oggi.

Il punto è che stiamo guardando i blocchi di adesso, mentre quei pool sono nati **23-25 giorni fa**.
Le fette che partono da 24 e 30 giorni indietro sono quelle giuste — e infatti una di loro aveva
raccolto **105.068 scambi** prima di morire.

## Perché moriva

Il contatore degli intoppi non si azzerava mai. In una corsa di tre ore i 25 tollerati si accumulano
per forza: quella fetta è stata uccisa dal ventiseiesimo, **sparso su 551 chiamate riuscite**.

> Un guasto va contato quando è **consecutivo**. Altrimenti non misura la salute: misura la durata —
> e più a lungo lavori, più è certo che ti ammazzi.

Riparato, insieme alla fascia di blocchi che si dimezzava a ogni intoppo e non tornava mai grande
(restava a 10 blocchi per sempre, scavando dieci volte più piano del possibile).

## Cosa aspettarsi

Con le fette che non muoiono più, quelle a 24 e 30 giorni arrivano sulle nascite dei pool dentro il
contratto unico. È lì che si sblocca l'83% mancante di Base.

**Non ho toccato altro.** Il resto della notte è stato il mio riavviare continuo — otto corse
annullate da me, tutte le migliorie giuste applicate una alla volta, e messe insieme hanno prodotto
meno di quanto avrebbe prodotto lasciarle lavorare.
