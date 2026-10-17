# 🔬 AUDIT DELLO SPAZIO DI RICERCA

*13/09/2026 · commissionato da Nicolò · nessuna difesa del codice esistente*

> **La domanda:** stiamo davvero cercando l'edge, o stiamo ottimizzando le idee che abbiamo già
> dato al sistema?

> **La risposta, in una riga: è la seconda, e i numeri non lasciano margine.**

---

## 1. LA PROVA, PRIMA DI TUTTO

LOOP 1 (`agents/explorer.py`) esplora uno spazio **fisso** di nove parametri scritti a mano:

| parametro | valori possibili |
|---|---|
| ora d'ingresso | 1, 2, 3, 6, 12 |
| volume minimo | 0, 500, 3.000, 10.000, 30.000 |
| ore minime di storia | 0, 2, 4 |
| rapporto vendite/acquisti minimo | 0, 0.10, 0.15, 0.30 |
| primo take profit | 2×, 3×, 4×, 5× |
| secondo take profit | 6×, 8×, 12×, 15×, 25× |
| trailing | 0.3, 0.4, 0.5, 0.6 |
| stop duro | 0.5, 0.6, 0.7, 0.8 |
| soglia del modello | 0.2, 0.3, 0.4, 0.5 |

**Combinazioni totali possibili: 384.000.**

Tentativi già effettuati, letti dai suoi stessi file di stato:

| chain | tentativi | giri |
|---|---|---|
| base | **1.958.455** | 846 |
| solana | 951.143 | 835 |
| bsc | 262.113 | 433 |
| robinhood | 94.562 | 163 |

**Base ha provato lo spazio intero più di cinque volte.** Non è una ricerca che non ha ancora
finito: è una ricerca che ha finito da settimane e continua a girare sugli stessi punti.

> **Conseguenza statistica, non opinione.** Con ~2 milioni di tentativi su dati rumorosi, la
> configurazione "migliore" trovata è quasi certamente **rumore selezionato**. Con 2 milioni di
> estrazioni si trova sempre qualcosa che sembra funzionare. Il nostro stesso `MIGLIORAMENTO_MINIMO
> = 8 punti` riconosce il problema ma non lo risolve: alza l'asticella di un singolo confronto, non
> corregge per i due milioni di confronti fatti.

---

## 2. VERDETTO: A o B?

**B. LOOP 1 è un ottimizzatore, non un motore di scoperta.**

Non può, per costruzione:

- inventare una feature che non gli abbiamo dato;
- scoprire una relazione fra variabili che non abbiamo modellato;
- cambiare la *forma* della strategia (entra a ora fissa, esce a take profit / trailing / stop);
- proporre un fenomeno diverso da «compra presto, tieni, esci a multipli».

Quello che chiamiamo "apprendimento" (`learner.py`, `multichain_brain.walkforward`) è una
**regressione logistica su 10 feature scritte a mano**:

- da candele (6): caduta dal massimo, log-volume, quota di volume verde, volatilità, accelerazione
  del volume, frazione di candele verdi
- da scambi (4): rapporto vendite/acquisti, log del comprato, log dei compratori distinti,
  accelerazione degli acquisti

Il modello può **pesare** queste dieci. Non può accorgersi dell'undicesima.

---

## 3. MAPPA DELLO SPAZIO DI RICERCA: cosa guardiamo e cosa no

| categoria | lo misuriamo? | diventa feature? | cosa NON estraiamo |
|---|---|---|---|
| prezzo | sì (OHLC orario) | solo caduta e volatilità | forma della candela, gap, sequenza dei movimenti, ora del giorno |
| volume | sì | log totale + accelerazione | distribuzione, burst, volume per scambio |
| liquidità | sì (battito) | **no, mai** | crescita/ritiro della riserva, rapporto volume/liquidità |
| wallet | sì (ogni scambio ha il wallet) | solo **quanti** sono | chi sono, se tornano, se si muovono insieme, la loro storia |
| creator | parzialmente | no (cancello provato e morto) | storia dei lanci precedenti, tempo fra lanci |
| transazioni | sì (13.000 file) | 4 aggregati | sequenza, tempi fra un'operazione e l'altra, taglie, concentrazione |
| flussi | sì | rapporto vendite/acquisti | flusso per fascia di taglia, chi compra da chi vende |
| tempo | sì | **no** | ora del giorno, giorno della settimana, età al momento del segnale |
| microstruttura | no | no | tutto |
| sicurezza | sì (GoPlus) | no, solo filtro | tasse, proprietà, capacità di vendere come variabile continua |
| distribuzione holder | **no** | no | concentrazione, numero di detentori |
| wallet ricorrenti | **raccolti ma inutilizzati** | no | chi torna su più token |
| relazioni fra wallet | parzialmente (`cluster` in controlli.py) | **no** | grafo di finanziamento, entità dietro più wallet |
| cross-chain | sì | no (provato e morto) | — |
| momentum | sì | caduta dal massimo | momentum a più scale, cambio di regime |
| segnali sociali | **no** | no | tutto (e costerebbe: fuori dal budget) |

### I dati che abbiamo costruito e non usiamo mai

Questa è la scoperta più concreta dell'audit:

- **`data/wallet_scores.json` — 3,2 MB, 9.743 wallet con punteggio.** Letto **solo** dall'agente che
  lo scrive. Nessun modello lo consuma.
- **`data/insider_scores.json`** — letto solo dal suo scrittore e dall'auditor.
- **`data/first_buyers`** — 211 file raccolti; entrano nel modello solo come *conteggio*.
- **La rete dei wallet ricorrenti**: 2.153 wallet su Base e 4.970 su Robinhood compaiono su 3+ token
  nostri. Mai usata come variabile.

> Abbiamo costruito magazzini e non abbiamo aperto le porte.

---

## 4. DOMANDE CHE NON ABBIAMO MAI FATTO AI DATI

Non sono idee da implementare: sono domande che i nostri dati **possono** già rispondere.

1. Conta il **livello** o il **cambiamento**? Tutte le nostre feature sono livelli o rapporti; quasi
   nessuna è una derivata seconda (accelerazione dell'accelerazione, cambio di regime).
2. Conta la **sequenza**? Oggi ogni feature è un aggregato: `sell_ratio` è identico se le vendite
   arrivano prima o dopo gli acquisti. L'ordine degli eventi è buttato via interamente.
3. Contano i **tempi fra un'operazione e l'altra**? Un token con 50 scambi in 5 minuti e uno con 50
   scambi in 5 ore hanno oggi le stesse feature.
4. Conta **chi** compra, non quanti? Wallet ricorrenti, wallet che comprano e non vendono mai,
   wallet che appaiono solo sui token che poi esplodono.
5. Esistono **interazioni**? Una regressione logistica è additiva: non può rappresentare
   «volume alto **solo se** la liquidità cresce». Tutte le interazioni ci sono precluse per forma
   del modello, non per mancanza di dati.
6. Esistono **condizioni di validità**? Un segnale che funziona solo di notte, o solo sotto una certa
   liquidità, oggi appare come segnale debole ovunque invece che forte da qualche parte.
7. Esistono segnali che **precedono** invece di accompagnare? Le nostre feature sono quasi tutte
   contemporanee al movimento.

---

## 5. COSA CI STA FACENDO PERDERE SENZA CHE CE NE ACCORGIAMO

| rischio | stato | prova |
|---|---|---|
| **multiple testing** | 🔴 **grave e attivo** | 2 milioni di tentativi su 384.000 combinazioni |
| sguardo nel futuro | 🟢 presidiato | `xt < ent` nel walk-forward, ritardo osservativo applicato |
| campioni non indipendenti | 🟢 presidiato | `indipendenza.py`, t sui gruppi giorno/creator |
| token morti esclusi | 🟡 parziale | la potatura tiene le lapidi, ma il conteggio le ignora |
| costi sottostimati | 🟡 **al contrario**: erano **sovrastimati** | pedaggio vero 0,1-0,9% contro 6% assunto |
| costi su chain sbagliata | 🔴 aperto | 0 misure EVM su 815 (copertura Base 0,6%, Robinhood 1%) |
| costi durante la fuga | 🔴 aperto | richiesto il 04/09, mai eseguito |
| sopravvivenza del campione | 🟡 da verificare | i token senza candele non entrano mai nel dataset |
| esecuzione irrealistica | 🟢 presidiato | curva costo-liquidità, trappole a -100% |

> Il rischio numero uno **non è** che la strategia sia sbagliata. È che, con 2 milioni di tentativi,
> non abbiamo modo di distinguere una strategia buona dal miglior rumore trovato.

---

## 6. COSA FUNZIONA DAVVERO

Va detto, perché è quasi tutto ciò che abbiamo costruito in bene:

- **l'apparato di misura**: `controlli.py` ha controlli appaiati, markout, placebo all'indietro,
  clustering, unità indipendenti. È infrastruttura scientifica seria.
- **la cassaforte temporale**: la divisione è per TEMPO, non per hash. È la divisione giusta.
- **i criteri scritti prima**: 10 idee provate, 8 morte, nessuna soglia spostata dopo il risultato.
- **le quattro corsie**: girano da sole, si riaccendono da sole, a costo zero.
- **il consulente esterno**: ha trovato due errori veri che il revisore interno non poteva vedere.

**Il laboratorio è buono. È lo spazio di ricerca a essere piccolo.**

---

## 7. L'ARCHITETTURA CHE MANCA

Oggi:

```
DATI → 10 feature scritte a mano → regressione → griglia di 384.000 parametri → migliore
```

Il pezzo mancante non è in fondo: è **all'inizio**. Manca la generazione delle domande.

Proposta:

```
DATI GREZZI
   ↓
COSTRUZIONE AUTOMATICA DI FEATURE      ← non esiste oggi
   (trasformazioni: livello, variazione, accelerazione, sequenza,
    concentrazione, tempi, identità dei wallet, interazioni a coppie)
   ↓
SCOPERTA DI RELAZIONI sulla metà VECCHIA   ← esiste da oggi (esploratore.py), ma minuscolo
   ↓
REGISTRAZIONE DELL'IPOTESI (criterio di morte scritto prima)
   ↓
PROVA sulla metà RECENTE, mai vista
   ↓
CONTROLLI AVVERSARIALI (placebo, controlli appaiati, permutazione)
   ↓
CASSAFORTE (una lettura sola)
   ↓
GIUDICE
```

La differenza non è tecnologica: è che **le domande devono nascere dai dati**, e il numero di
domande fatte va contato e pagato statisticamente.

---

## 8. IL PROSSIMO ESPERIMENTO PIÙ INFORMATIVO

Non è una strategia. È una **prova sul sistema stesso**:

> **Dare in pasto al sistema una relazione che sappiamo essere vera e che NON gli abbiamo
> suggerito, e vedere se la trova.**

Concretamente: si costruisce una feature nascosta e artificiale (per esempio: nei dati storici,
marchiare i token in cui i primi tre acquisti vengono dallo stesso wallet) che ha per costruzione
un legame con l'esito, e si verifica se la pipeline la scopre partendo dai dati grezzi.

- **Se la trova** → è un motore di scoperta, e possiamo fidarci di quello che dice.
- **Se non la trova** → è dimostrato che non può scoprire nulla che non gli abbiamo messo dentro,
  e ogni ora spesa a ottimizzare i suoi parametri è un'ora persa.

Costo: nessuno. Dati: quelli che abbiamo. È il test che separa A da B **con un fatto** invece che
con un ragionamento sul codice.

---

## 9. STATO DELLE AFFERMAZIONI

| affermazione | tipo |
|---|---|
| lo spazio strategie è 384.000 e Base ha fatto 1.958.455 tentativi | **MISURATO** |
| le feature sono 10, scritte a mano | **MISURATO** |
| wallet_scores non è letto da nessun modello | **MISURATO** |
| la copertura costi EVM è sotto l'1% | **MISURATO** |
| il "migliore" trovato è in gran parte rumore selezionato | **INFERITO** (dalla scala del multiple testing) |
| feature di sequenza/identità avrebbero potere predittivo | **IPOTIZZATO** — non ancora giudicabile |
| esiste un edge nei dati disponibili | **NON ANCORA GIUDICABILE** |
