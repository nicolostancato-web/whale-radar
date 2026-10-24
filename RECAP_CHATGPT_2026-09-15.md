# 📋 RECAP PER CHATGPT — 15 settembre 2026

*Scritto perché Nicolò possa parlarne a voce. Si legge da solo: non serve aprire altri file.*

---

## 1. Cosa vogliamo fare

Comprare e vendere token (memecoin) e guadagnarci. Serve trovare una **regola** che funzioni:
*«quando succede X, compra»*.

Obiettivo dichiarato: **+8% netto per operazione**. Il cancello formale è più severo: +10% netto,
t≥2 sui gruppi indipendenti, 25 prove indipendenti, 250 righe, configurazione congelata prima,
holdout letto una volta sola. **Scadenza pre-registrata: 3 ottobre 2026** — se nessuna configurazione
passa, si chiude questo mercato e si cambia.

Tutto gira gratis su GitHub Actions. Nessun soldo reale è mai stato in gioco.

---

## 2. Come si cerca una regola, e cosa serve

Si prova sul passato: prendi i token di un mese fa, applichi la regola, guardi se avresti guadagnato.

Per ogni token servono **due cose**:

1. **il prezzo** → per sapere com'è andata
2. **chi comprava** → per avere qualcosa su cui basare la regola

---

## 3. Il problema: avevamo solo metà

Avevamo il prezzo. **Non avevamo chi comprava.**

> È come voler capire perché un ristorante si riempie avendo solo l'incasso della sera: sai com'è
> andata, non sai chi è entrato, a che ora, in che ordine.

**Perché**: i siti che danno questi dati gratis mostrano solo **le ultime ~300 operazioni**. Per un
token di tre settimane, le prime — quelle che servono — sono sparite. Su questo eravamo bloccati da
mesi.

---

## 4. Le due scoperte che hanno cambiato tutto

### A) Il sistema non cercava: ottimizzava (13-14 settembre)

Il nostro motore di ricerca provava una griglia **fissa** di 9 parametri = 384.000 combinazioni. Su
Base ne aveva già provate **1.958.455**: aveva percorso lo spazio intero **cinque volte**.

**Il test decisivo** (permutazione a blocchi): abbiamo distrutto a mano il legame causa-effetto nei
dati — mescolando gli esiti fra token nati lo stesso giorno — e rifatto girare tutta la ricerca. In
quei dati, per costruzione, non c'è niente da trovare.

| chain | nostro risultato | il caso, al suo massimo | batte il caso? |
|---|---|---|---|
| base | −23,9% | −23,4% | ❌ |
| solana | −29,7% | −28,4% | ❌ |
| robinhood | −13,5% | −11,7% | ❌ |

**Su nessuna chain.** Quello che il sistema trovava era indistinguibile dal rumore.

**Ma attenzione a cosa NON dimostra**: il test giudica la coppia *classe-di-ipotesi + procedura*, non
i dati. Un segnale che vivesse in variabili che non rappresentiamo — chi compra, in che ordine, con
che tempi — **non poteva comparire**, perché quelle variabili non entravano nemmeno nel test.

### B) Il limite delle 300 operazioni era della fonte, non della blockchain (14-15 settembre)

Sulla blockchain c'è tutto, per sempre, ed è pubblica. Sbagliavamo il modo di chiedere: domandavamo
**un token alla volta** e il server ci mandava via. Chiedendo **«dammi tutto quello che è successo in
questi cinque minuti»**, risponde subito.

Prima prova: **108.000 operazioni in 50 secondi**. Tutto l'archivio precedente ne conteneva 30.000,
raccolte in settimane. **Costo: €0.**

---

## 5. Dove siamo adesso (15 settembre, mattina)

| | |
|---|---|
| copertura Base | ~15% |
| copertura Robinhood | ~24% |
| **dove il dato è arrivato, è utilizzabile** | **94%** |
| qualità del dato nuovo | wallet 100%, istanti 100%, duplicati 0 |
| costo | **€0** |

Le sei variabili nuove — ordine fra vendite e acquisti, tempi fra le operazioni, raffiche,
concentrazione del compratore più grosso, chi ricompra, wallet già visti — **esistono e sono sane**.
È la prima volta che questo progetto ha un dato reale su *chi compra*.

**Manca**: tempo di scavo. Serve arrivare al 70-80%.

---

## 6. Le API a pagamento: NON servono

| chain | come prendiamo i dati | costo |
|---|---|---|
| Base | leggiamo la blockchain noi, nodo pubblico | **€0** |
| Robinhood | idem | **€0** |
| Solana | Helius, piano gratuito (2 chiavi già nostre) | **€0** — ci serve lo **0,9%** del tetto |

Stavo per proporre **€57/mese** (Helius Developer). Ho fatto il conto prima di chiedere: 736 pool ×
25 chiamate = 18.400, contro 2.000.000 disponibili gratis. **Proposta chiusa.**

Tornerei a parlarne solo se il tetto gratuito si saturasse, o se i nodi pubblici cominciassero a
rifiutarci sistematicamente. Oggi non succede.

*(Prezzi verificati il 15/09 su helius.dev/pricing e bitquery.io/pricing. Bitquery costa di più e
l'archivio storico lo fa pagare a parte: $70-150/mese in aggiunta.)*

---

## 7. LA DECISIONE CHE ASPETTA NICOLÒ: l'embargo

### Cos'è, con un esempio

Immagina di testare un metodo per scommettere sulle partite dell'anno scorso. **Regola d'oro**: per
decidere la scommessa delle 15:00 puoi usare solo quello che sapevi **alle 15:00**. Se usi la
formazione uscita alle 15:30, il metodo sembrerà geniale e dal vivo perderà.

L'embargo è la regola che impedisce di ingannarsi da soli.

### Il nostro embargo è 35 ore, e nasce da una misura vera

Abbiamo misurato quanto tardi i fornitori ci consegnano i dati:

| chain | ritardo misurato |
|---|---|
| robinhood | 3,8 h |
| solana | 10,6 h |
| base | 10,7 h |
| **bsc** (chain abbandonata il 9/9) | **35,4 h** |

Il codice prende il **massimo** — che viene da BSC, una chain che non usiamo più — e lo applica a
tutti.

### Perché è un problema grave

Compriamo **3 ore** dopo la nascita del token. Con un embargo di 35 ore il sistema cerca dati di
**32 ore prima che il token esistesse**. Non ne esistono.

**Misurato: il 92% delle operazioni non ha nessun dato su chi comprava.** Il modello che credevamo
guardasse dieci variabili, ne guardava sei.

### E adesso la domanda

Quelle 35 ore descrivono **quanto ci mette il postino**. Ma i dati che raccogliamo adesso non
arrivano dal postino: **andiamo a prenderli noi** dalla blockchain. Un blocco è nostro nel momento in
cui esiste.

| opzione | conseguenza |
|---|---|
| **A) stesso embargo per tutti** | prudente e coerente col passato — **ma butta via tutto il valore della nuova raccolta** |
| **B) embargo per fonte**: postino 10 ore, blockchain ~zero | **sblocca le variabili nuove** — ma cambia il metro rispetto a ogni confronto storico |

**Claude propende per B**: fingere di ricevere in ritardo un dato che si ha in mano è una prudenza
che costa e non protegge da niente.

**Ma non la applica senza l'OK di Nicolò**, perché riscrive il significato di ogni numero passato.

> **Domanda per ChatGPT: B è difendibile? Quali bias introduce? C'è una terza via?**

---

## 8. Le idee già provate e morte (10, di cui 8 morte)

Ognuna con il criterio di morte scritto **prima** di guardare i numeri:

1. copy-trading dei wallet vincenti — morto
2. flusso dei cluster — morto
3. cancello sui creator — morto
4. quattro segnali di domanda — morti (media +70%, mediana 0%: una lotteria)
5. il gemello sull'altra chain — morto (−15%)
6. comprare prima di chi è *costretto* a comprare (voti DAO) — morto (−2,8%, 29 eventi)
7. quotazione su Robinhood di token già esistenti altrove — morto
8. comprare l'esaurimento del venditore — morto (−5,4% contro −1,3% dei controlli)
9. scegliere per costo d'uscita — premessa caduta (il pedaggio vero è sotto l'1%, non il 26%)
10. taglia fissa contro reinvestimento — morto (+0,00% contro il bersaglio +8%)

**Una scoperta trasversale**: su Robinhood a 72h, **il 99% della media di un gruppo veniva da UN SOLO
token**. Il trade mediano perde ~20%; la media è positiva solo per pochi colpi enormi.

> Cercare un «+8% medio» su una distribuzione così potrebbe essere **la domanda sbagliata**: o si
> prende il biglietto vincente, o non si prende niente.

---

## 9. L'audit del database: verdetto ROSSO

Quattro difetti misurati, tutti documentati:

1. **l'embargo** azzera le variabili sugli scambi nel 92% delle righe
2. l'8% che sopravvive è **contaminato**: sono pool vecchi con la data di nascita sbagliata di ~3 settimane
3. **selezione su vita osservata**: le serie escluse vivono 1 ora in mediana, le ammesse 23
4. **non possiamo più sapere quando abbiamo saputo**: il nostro GC ha schiacciato la storia git l'11/09

Il punto 4 è riparato (ogni record porta ora il timbro di quando è entrato). Il punto 3 è in verifica
con un test prospettico. I punti 1 e 2 dipendono dalla decisione sull'embargo.

**Nessuna ricerca di strategie è ripartita**, come richiesto da Nicolò: prima il database.

---

## 10. Onestà sul metodo

Nelle ultime 48 ore Claude ha commesso errori che vale la pena conoscere, perché riguardano il metodo:

- **cinque volte** ha tratto conclusioni da copie locali vecchie invece che dai dati veri
- **due verdetti falsi** prodotti dai suoi stessi strumenti, che dichiaravano un fallimento ogni volta
  che non riuscivano a distinguere
- un indicatore che ha mentito prima con uno **0%** (import mancante) e poi con un **99%** dove la
  verità era **18%** (criterio comodo invece di quello giusto)
- **nove riavvii** delle scavatrici in una notte, ognuno con una buona ragione, che messi insieme
  hanno prodotto meno che lasciarle lavorare

Tutti della stessa famiglia: **numeri nati dal non aver guardato, travestiti da risposte.** Il più
pericoloso è stato il 99%, perché era quello che faceva piacere leggere.

Ogni correzione è documentata, e i test di audit ora verificano di **avere potere** prima di emettere
un verdetto.

---

## 11. Le domande aperte per la conversazione

1. **L'embargo**: opzione B è difendibile? Che bias introduce? Esiste una terza via?
2. Il verdetto ROSSO sul database è giusto, o stiamo usando l'audit come scusa per non fare ricerca?
3. Con 18 giorni alla scadenza e il database in ricostruzione: riparare, spostare la scadenza, o
   chiudere?
4. La distribuzione a coda grassa (mediana −20%, media positiva per pochi colpi) **cambia la domanda
   da porre**? Una strategia che vive di code si giudica con strumenti diversi.
5. Se il segnale vive nelle variabili che stiamo solo ora raccogliendo, o se non c'è affatto:
   **non è ancora giudicabile**, e lo sarà solo quando la copertura sarà completa.

---

## 12. File di riferimento sul repo

`nicolostancato-web/whale-radar` (pubblico)

| file | contenuto |
|---|---|
| `MATTINA_15_09.md` | il lavoro della notte, con i numeri |
| `DATABASE_AUDIT_FINAL.md` | l'audit del database e la revisione avversariale |
| `PERMUTAZIONE.md` | il test che ha dimostrato che non battiamo il caso |
| `AUDIT_RICERCA.md` | l'audit dello spazio di ricerca |
| `QUALITA_DB.md` | lo stato di salute del database, aggiornato da solo |
| `STAFFETTA.md` | lo stato attuale del sistema |
| `DIARIO.md` | cosa cambia, giro per giro |
