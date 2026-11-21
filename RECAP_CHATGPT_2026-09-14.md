# 📋 RECAP PER CHATGPT — 14 settembre 2026

*Documento scritto perché Nicolò possa parlarne a voce con un'altra AI. Contiene tutto il necessario:
non serve leggere altri file, ma se vuoi approfondire i riferimenti sono indicati.*

---

## 0. Come leggere questo documento

Ogni affermazione è marcata:

- **[MISURATO]** = viene da un conteggio o da un test eseguito, con il numero riportato
- **[INFERITO]** = deduzione da cose misurate, ma non verificata direttamente
- **[NON GIUDICABILE]** = non lo sappiamo, e serve un dato che non abbiamo

Se qualcosa non è marcato, è descrizione di contesto.

---

## 1. Che cos'è il progetto

**whale-radar** cerca un vantaggio statistico sistematico sui memecoin di tre chain — **Base, Solana,
Robinhood** — a costo **zero** (tutto gira su GitHub Actions gratuite, API gratuite, nessun servizio
a pagamento).

**Obiettivo dichiarato**: +8% netto per operazione. Il cancello pre-registrato per dichiarare
successo è più severo: ≥10% netto, t≥2 calcolato sui gruppi indipendenti, ≥25 prove indipendenti,
≥250 righe, configurazione congelata prima, holdout letto una volta sola.

**Scadenza pre-registrata: 3 ottobre 2026.** Se nessuna configurazione passa, si chiude questo
mercato e si cambia. Non è una resa: è un risultato che dice dove non cercare.

**Capitale previsto**: €100 iniziali. Non c'è mai stato denaro reale in gioco: tutto è simulazione su
dati storici.

### L'architettura

Quattro processi indipendenti girano 24 ore su 24 su GitHub Actions, si riavviano da soli:

| corsia | compito |
|---|---|
| motore | raccoglie i dati |
| ricerca (LOOP 1) | cerca la percentuale, chain per chain |
| loop 0 | ispeziona gli altri |
| sperimenti | brucia le idee, una per volta |

Più un **guardiano** che li sorveglia e li riaccende, una **staffetta** (foglio di stato che si
aggiorna da solo), un **diario** che registra cosa cambia, e un **consulente esterno** (un'altra AI)
che due volte al giorno cerca gli errori che il revisore interno non può vedere.

---

## 2. Il risultato più importante: il sistema non scopre, ottimizza

**[MISURATO]** LOOP 1 esplora una griglia **fissa** di 9 parametri scritti a mano (ora d'ingresso,
volume minimo, ore minime, rapporto vendite/acquisti, due take profit, trailing, stop, soglia del
modello) = **384.000 combinazioni**. Ha già fatto **1.958.455 tentativi** su Base: ha percorso lo
spazio intero cinque volte.

**[MISURATO]** Il "modello" è una regressione logistica su **10 feature scritte a mano**: 6 dalle
candele orarie, 4 dagli scambi.

### Il test decisivo: permutazione a blocchi

Abbiamo distrutto a mano il legame causa-effetto (esiti scambiati **solo fra token nati lo stesso
giorno**, struttura temporale intatta), rieseguito **tutta** la selezione, e confrontato il nostro
miglior risultato con il **massimo** dei mondi permutati — perché il nostro numero è un massimo e va
confrontato con dei massimi.

| chain | nostro risultato | il caso, al suo massimo | batte il caso? |
|---|---|---|---|
| base | −23,9% | −23,4% | ❌ |
| solana | −29,7% | −28,4% | ❌ |
| robinhood | −13,5% | −11,7% | ❌ |

**[MISURATO]** Su nessuna chain. E un controllo di potere conferma che il test poteva dire "sì" (a
soglie diverse selezionava 197/188/181 righe su Base).

**[MISURATO]** Il nostro placebo prova poche decine di configurazioni; LOOP 1 ne ha provate due
milioni. Il premio della ricerca vero è quindi **più grande** di quello misurato: il confronto reale
è ancora più severo.

**[INFERITO]** Quello che il sistema ha trovato finora è rumore selezionato.

**[NON GIUDICABILE]** Se esista un edge nei dati. Il test giudica **la coppia classe-di-ipotesi +
procedura**, non i dati.

---

## 3. L'audit del database: quattro difetti misurati

Dopo il test di permutazione abbiamo fatto l'audit del **database**, non delle strategie. Domanda:
*se domani volessimo cercare un edge completamente nuovo, i dati ce lo permetterebbero?*

### D1 — L'embargo cancella metà del database **[MISURATO]**

Il momento d'entrata è **+3 ore** dalla nascita del token. Il "ritardo osservativo" imposto è
**35,4 ore**. Finestra utile per le feature sugli scambi: **−32,4 ore**. Negativa.

Risultato: **1.577 righe su 1.710 (92,2%)** hanno le quattro feature sugli scambi bloccate sul valore
neutro di ripiego. Il modello che credevamo a dieci variabili **ne ha avute sei informative**.

Le 35,4 ore vengono dal **massimo fra le chain**, e il massimo è **BSC — una chain abbandonata il 9
settembre**. Ma togliendo BSC non si ripara: base 10,7h, solana 10,6h, robinhood 3,8h, sempre contro
un'entrata a 3h.

**Asimmetria [MISURATO]**: le feature dalle **candele** non sottraggono alcun ritardo. Stessa
decisione, stesso istante, trattamenti opposti.

### D2 — L'8% che sopravvive è contaminato **[MISURATO]**

| | quando comincia la storia scambi, prima dell'entrata |
|---|---|
| righe con feature **neutre** (194) | mediana **2,8 ore** |
| righe **con feature attive** (133) | mediana **529 ore** (22 giorni) |

Passano l'embargo solo pool che **non erano nuovi**. **[INFERITO — non misurato]**: che la "nascita"
assegnata sia sbagliata. Potrebbe anche essere un ri-avvistamento o una migrazione di pool.

### D3 — Selezione su vita osservata **[MISURATO, ma il nome era sbagliato]**

Perché una serie non diventa una riga analizzabile (Base): 860 per meno di 5 candele, 414 "presa
troppo tardi", 7 morte prima di +3h, 3.296 ammesse.

| | durata di vita **osservata** |
|---|---|
| serie escluse | mediana **1,0 ora** |
| serie ammesse | mediana **23,4 ore** |

L'avevo chiamato *survivorship bias*. **La revisione avversariale ha corretto**: è una **durata
osservata**, non la vita vera del token. Può venire da mortalità reale **oppure da buchi nostri**.

**Test prospettico costruito ieri** — a +3h si chiede **alla catena** (fonte indipendente dalle
candele) se il pool è ancora vivo:

| la catena dice | noi abbiamo la candela | quanti |
|---|---|---|
| vivo | **no** | **17 su 17** |

**[MISURATO, campione piccolo]** Tutti e 17 erano ancora vivi: **buchi nostri, non mortalità**.
**Limite dichiarato**: "vivo" = il contratto ha riserve non nulle; non vuol dire che fosse scambiato
o vendibile.

### D4 — Non sappiamo più quando abbiamo saputo **[MISURATO]**

Per verificare *"avevamo il dato quando la strategia avrebbe deciso?"* serve un timestamp di
acquisizione. Ricostruirlo da git non funziona: **11 file su 12** hanno come commit più vecchio
`GC prune+squash 2026-09-11`. Il nostro stesso GC ha schiacciato la storia.

**Per tutto ciò che precede l'11 settembre, la verifica point-in-time è impossibile per sempre.**

---

## 4. Altri numeri dell'audit **[MISURATO]**

| chain | pool scoperti | con serie di prezzo | righe analizzabili |
|---|---|---|---|
| base | 15.178 | 4.577 (30%) | **1.710 (11,3%)** |
| solana | 15.225 | 1.847 (12%) | **759 (5,0%)** |
| robinhood | 20.839 | 4.162 (20%) | **670 (3,2%)** |

**Analizziamo fra il 3% e l'11% di ciò che scopriamo.**

Join serie→scambi: base 18%, solana 51%, robinhood **9%**.
File di scambi **orfani** (senza serie di prezzo): base 45%, solana 78%, robinhood **92%**.

**Costi d'uscita misurati**: sui pool che scambiano davvero il pedaggio mediano è **0,1–0,9%**, non
il 26% che assumevamo. A $25 su Base è **0,10%**. Ma cresce in fretta con la taglia: **3,95% a $25,
8,14% a $100, 25,44% a $500** (misure su 666 token Solana).

**Controllo passato ✅**: nessuna entità duplicata fra addestramento e prova (1.710 righe = 1.710 pool
distinti su Base; idem sulle altre).

---

## 5. Il verdetto sul database

> 🔴 **ROSSO** per qualsiasi affermazione **generalizzabile ai token nuovi che scopriamo**.
> 🟡 **GIALLO** per analisi **esplicitamente condizionate** al cohort osservato e senza le feature
> sugli scambi.

**Non è il momento di cercare un edge. È il momento di rendere il database capace di rispondere.**

### Quali risultati storici sono nulli

**Nulli**: tutto ciò che riguarda il potere predittivo delle feature sugli scambi, la loro importanza,
le interazioni, e ogni generalizzazione a pool nuovi.

**Non automaticamente nulli**: conteggi descrittivi datati bene, analisi che non usano quelle
feature, risultati riprodotti escludendo le 133 righe attive — validi **solo** per il cohort
osservato.

---

## 6. Cosa abbiamo riparato in queste 48 ore

| riparazione | stato |
|---|---|
| libro mastro point-in-time in sola aggiunta (`registro_pit.jsonl`) | 🟢 fatto, scrive dai collettori veri |
| timbro `acq` dentro ogni record di scambi, battito e candele | 🟢 fatto |
| test prospettico coorte (mortalità vs copertura) | 🟢 fatto, accumula |
| collettore scambi: priorità ai pool già valutabili | 🟢 fatto |
| Robinhood ha finalmente un "battito" (liquidità, compratori/venditori) | 🟢 fatto |
| costi misurati **on-chain** su Base e Robinhood, non presi da Solana | 🟢 fatto, copertura 8% e 3% e in crescita |
| i due test di audit ora verificano di **avere potere** prima di dare un verdetto | 🟢 fatto |
| **l'embargo** | 🔴 **NON toccato, deliberatamente** |

Perché l'embargo non è stato toccato — è la frase del revisore esterno:

> *«Correggere l'embargo senza poter provare quando il dato è arrivato produce semplicemente un
> embargo più elegante ma non verificabile.»*

Cambiarlo adesso modificherebbe **retroattivamente** ogni confronto storico senza poter dimostrare
che la versione nuova è più vera della vecchia.

---

## 7. Le idee già provate e morte **[MISURATO]**

Dieci idee, otto morte, ognuna con il criterio di morte scritto **prima** di guardare i numeri:

1. copy-trading dei wallet vincenti — morto
2. flusso dei cluster — morto
3. cancello sui creator — morto
4. quattro segnali di domanda — morti (media +70%, mediana 0%: una lotteria)
5. il gemello sull'altra chain — morto (−15%)
6. comprare prima di chi è **costretto** a comprare (voti DAO) — morto (−2,8% contro i giorni normali, 29 eventi)
7. chi vuole comprare e **non può** comprarlo altrove (quotazioni su Robinhood di token già esistenti) — morto
8. comprare **l'esaurimento del venditore** — morto (−5,4% contro −1,3% dei controlli, limite inferiore al 95% = −8,2%)
9. scegliere per **costo d'uscita** — premessa caduta (la soglia non tagliava niente: il pedaggio vero è sotto l'1%)
10. taglia fissa contro reinvestimento — morto (+0,00% contro il bersaglio +8%)

**Vivo**: "i soldi che entrano nel pool contro il prezzo che sale" — in attesa dei giorni indipendenti.

### Una scoperta trasversale **[MISURATO]**

Su Robinhood a 72h, **il 99% della media di un gruppo veniva da UN SOLO token**. Il trade mediano
**perde ~20%**, la media è positiva solo per pochi colpi enormi. **[INFERITO]**: cercare un
"+8% medio" su una distribuzione così potrebbe essere la domanda sbagliata — o si prende il biglietto
vincente, o non si prende niente.

---

## 8. Cosa vorrei discutere con te (le domande aperte)

1. **Il verdetto ROSSO è giusto, o stiamo usando l'audit come scusa per non fare ricerca?** C'è un
   rischio opposto reale: perfezionare il database all'infinito.

2. **Con 19 giorni alla scadenza e un database rosso, qual è la mossa?** Riparare e accettare che il
   3 ottobre si chiuda senza verdetto? Spostare la scadenza? Chiudere adesso?

3. **La distribuzione a coda grassa** (mediana −20%, media positiva per pochi colpi): cambia la
   domanda da porre? Una strategia che vive di code si giudica con strumenti diversi.

4. **L'embargo**: qual è la riparazione corretta? Ritardo per chain? Per record? Spostare l'entrata a
   +11h (ma introduce nuovi bias: entrano solo i token ancora vivi a 11h)?

5. **[NON GIUDICABILE]** Se il segnale vive nelle variabili che non rappresentiamo — identità dei
   wallet, sequenza degli scambi, tempi — o se non c'è affatto. Non lo sapremo finché il database non
   permette la domanda.

---

## 9. File di riferimento sul repo

`nicolostancato-web/whale-radar` (pubblico)

| file | contenuto |
|---|---|
| `DATABASE_AUDIT_FINAL.md` | l'audit completo del database, con la revisione avversariale |
| `NOTTE.md` | il consuntivo della notte del 13-14 |
| `PERMUTAZIONE.md` | il test che ha dimostrato che non battiamo il caso |
| `AUDIT_RICERCA.md` | l'audit dello spazio di ricerca |
| `CONFRONTO_AUDIT.md` | il confronto avversariale, con le tesi demolite |
| `REPERTO_RITARDO.md` | il reperto dell'embargo |
| `PIANO_ACCUMULO.md` | cosa raccogliere e in che ordine |
| `COORTE.md` | mortalità contro copertura |
| `STAFFETTA.md` | lo stato attuale, aggiornato da solo |
| `DIARIO.md` | cosa è cambiato, giro per giro |

---

## 10. Nota sul metodo, per onestà

In 48 ore ho commesso **sei errori** di cui vale la pena sapere, perché riguardano il metodo e non i
numeri:

- tre conclusioni tratte da **copie locali vecchie** invece che dai dati veri (due già pubblicate)
- due **verdetti falsi** prodotti dai miei stessi strumenti, che dichiaravano un fallimento ogni volta
  che non riuscivano a distinguere
- un indicatore che ha mentito prima con uno **0%** (import mancante) e poi con un **99%** dove la
  verità era **18%** (criterio comodo invece di quello giusto)

Tutti della stessa famiglia: **numeri nati dal non aver guardato, travestiti da risposte.** Il più
pericoloso è stato il 99%, perché era quello che faceva piacere leggere.

Ogni correzione è scritta nei documenti, e i due test di audit ora verificano di avere potere prima
di emettere un verdetto.
