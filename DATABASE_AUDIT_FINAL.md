# 🗄️ DATABASE_AUDIT_FINAL

*14/09/2026 · audit del database, non delle strategie · tutto misurato sul repo vero · €0*

## 1. Riassunto

> **Domanda:** se domani volessimo cercare un edge completamente nuovo, il database attuale ce lo
> permetterebbe in modo scientificamente valido?

> **Risposta: 🔴 NO.**

Non per mancanza di dati — ne abbiamo molti — ma per **quattro difetti misurati**, ognuno dei quali
basterebbe da solo a invalidare i risultati.

| # | difetto | gravità |
|---|---|---|
| 1 | l'embargo temporale azzera le feature sugli scambi nel 92% delle righe | **CRITICA** |
| 2 | l'unico 8% che le ha, ha la data di nascita sbagliata di ~3 settimane | **CRITICA** |
| 3 | analizziamo solo i token sopravvissuti: gli esclusi vivono 1 ora, gli ammessi 23 | **CRITICA** |
| 4 | non possiamo più sapere quando abbiamo saputo (storia git schiacciata) | **ALTA** |

---

## 2. Cosa abbiamo davvero

| chain | pool scoperti | con serie di prezzo | **righe analizzabili** |
|---|---|---|---|
| base | 15.178 | 4.577 (30%) | **1.710 (11,3%)** |
| solana | 15.225 | 1.847 (12%) | **759 (5,0%)** |
| robinhood | 20.839 | 4.162 (20%) | **670 (3,2%)** |

File di scambi: base 1.472, solana 3.983, robinhood 4.438.
Misure di costo: 815 su Solana (via Jupiter, per token), 255 Base + 121 Robinhood (on-chain, per pool).

**Analizziamo fra il 3% e l'11% di ciò che scopriamo.**

---

## 3. Difetto 1 — l'embargo che cancella metà del database

`ENTRY_H` = 3 ore. `RITARDO_OSS` = 35,4 ore (il **massimo** fra le chain, preso da **BSC, chain
abbandonata il 9 settembre**). Finestra utile per le feature sugli scambi: **−32,4 ore**.

Verificato riga per riga su Base: in ogni caso campionato **0 scambi passano il cutoff**, mentre
prima dell'entrata ce n'erano da 4 a 101. Unità coerenti (secondi), join funzionante.

**Risultato: 1.577 righe su 1.710 (92,2%) hanno le quattro feature sugli scambi bloccate sul valore
neutro.** Il modello che credevamo a dieci variabili ne ha avute sei di informative.

E anche senza BSC non si ripara: base e solana misurano 10,7h e 10,6h di ritardo, contro un'entrata
a 3h. Solo Robinhood (3,8h) ci si avvicina.

---

## 4. Difetto 2 — l'8% che sopravvive è contaminato

| | quando comincia la storia scambi, prima dell'entrata |
|---|---|
| righe con feature **neutre** (194) | mediana **2,8 ore** |
| righe **con feature attive** (133) | mediana **529 ore** (22 giorni) |

Passano l'embargo **solo i pool che non erano nuovi**: li avevamo già visti da settimane e la
"nascita" assegnata è sbagliata di tre settimane.

> L'unica esposizione del modello ai dati sugli scambi è venuta **dalle righe con la data di nascita
> rotta**. È peggio che non averne: è contaminazione sistematica.

---

## 5. Difetto 3 — sopravvivenza

Perché una serie di prezzo non diventa una riga analizzabile (Base):

| motivo | serie |
|---|---|
| meno di 5 candele | 860 |
| presa troppo tardi | 414 |
| morta prima di +3h | 7 |
| **ammesse** | **3.296** |

| | durata di vita osservata |
|---|---|
| serie **escluse** | mediana **1,0 ora** |
| serie **ammesse** | mediana **23,4 ore** |

**809 delle 1.281 escluse vivono meno di 3 ore.** L'esclusione non è casuale: è **esattamente per
sopravvivenza**. Ogni nostro rendimento è condizionato all'essere sopravvissuti ~23 ore.

In più `pulse.py` raccoglie solo pool sopra **$5.000 di liquidità**: i più sottili — dove il costo
esplode e i rug vivono — non entrano mai nel campione.

---

## 6. Difetto 4 — non sappiamo più quando abbiamo saputo

La domanda che decide la validità di ogni ricerca — *«questo dato ce l'avevamo, al momento in cui la
strategia avrebbe deciso?»* — richiede un timestamp di acquisizione immutabile.

Provato a ricostruirlo dalla storia git: **11 file su 12 hanno come commit più vecchio
`GC prune+squash 2026-09-11`**. Il nostro stesso GC ha schiacciato la storia.

> Per tutto ciò che è stato raccolto **prima dell'11 settembre, la verifica point-in-time è
> impossibile e resterà impossibile.**

**Riparato oggi**: ogni record di scambi, battito e candele porta adesso il campo `acq` — il momento
in cui il dato è entrato da noi — dentro il dato stesso, dove nessuna manutenzione può cancellarlo.

---

## 7. Audit delle join (tasso di riuscita reale)

| chain | serie→registro | serie→scambi | serie→mappa token | file scambi **orfani** |
|---|---|---|---|---|
| base | 67% | **18%** | 71% | 663 (45%) |
| solana | 97% | **51%** | 79% | 3.093 (78%) |
| robinhood | 100% | **9%** | 61% | 4.083 (**92%**) |

> Su Robinhood **il 92% dei file di scambi non si unisce a nessuna serie di prezzo**. Sono dati
> raccolti, conservati, e inutilizzabili per qualsiasi domanda che colleghi comportamento ed esito.

---

## 8. Copertura delle famiglie di strategie

| famiglia | stato | perché |
|---|---|---|
| prezzo / rendimento | 🟡 | testabile, ma solo sui sopravvissuti a 23h |
| volume | 🟡 | idem |
| liquidità | 🔴 | la liquidità **non è mai una feature**; e sotto $5k non la raccogliamo |
| wallet | 🔴 | azzerata dall'embargo; `wallet_scores.json` (9.743 wallet) non è letto da nessun modello |
| creator | 🔴 | provato e morto, e comunque senza point-in-time |
| sequenza degli scambi | 🔴 | azzerata dall'embargo |
| primi compratori | 🔴 | entrano solo come conteggio, e l'embargo li cancella |
| concentrazione | 🔴 | mai calcolata |
| tempo / orario | 🔴 | ora del giorno ed età al segnale non esistono come variabili |
| flusso | 🔴 | `sell_ratio` collassa ordine e tempi in un numero |
| esecuzione / liquidità condizionata | 🟡 | curva costo esiste su Solana, 255+121 misure on-chain EVM |
| rete fra wallet | 🔴 | dati presenti, mai trasformati in variabile |
| regime / anomalie | 🔴 | mai tentato |

**Nessuna famiglia è 🟢.**

---

## 9. Verdetto

> ## 🔴 ROSSO
>
> Fare ricerca di strategie adesso produrrebbe conclusioni false, e ne ha già prodotte: il test di
> permutazione di stanotte mostra che il nostro miglior risultato non batte il caso — su un dataset
> in cui il 92% delle righe aveva quattro feature costanti e le altre avevano la data sbagliata.

**Non è il momento di cercare un edge. È il momento di rendere il database capace di rispondere.**

---

## 10. Cosa NON è dimostrato

| affermazione | stato |
|---|---|
| esiste un edge nei dati | **NON GIUDICABILE** |
| riparando i quattro difetti comparirà un edge | **NON GIUDICABILE** |
| il ritardo di 10,7h su Base è un limite informativo vero | **NON GIUDICABILE** — serve la distribuzione per record di `acq − ts`, che sarà possibile solo sui dati nuovi |
| i token esclusi avrebbero rendimenti peggiori | **INFERITO** (vivono 1 ora) — misurabile solo raccogliendoli |

---

# 11. REVISIONE AVVERSARIALE — cosa mi ha tolto

Ho chiesto a un revisore esterno di distruggere questo audit. Ha trovato **due incoerenze mie** e ha
corretto il verdetto.

## 11.1 Correzioni accettate

**«0 scambi passano il cutoff» era il campione, non l'universo.** Valeva per gli 8 casi mostrati.
Nell'universo passano **133 righe su 1.710 (7,8%)** — che è esattamente il difetto 2. La frase come
l'avevo scritta era incompatibile con il resto del mio stesso audit.

**I due cohort non erano lo stesso.** Ho accostato «1.710 righe» e «3.296 ammesse» come se fossero
confrontabili: il primo è il numero di righe finali, il secondo il numero di serie che superano i
filtri prima degli altri scarti. Numeri veri, accostamento sbagliato.

**«La nascita è sbagliata di ~3 settimane» è INFERITO, non misurato.** Misurato è che la storia
scambi comincia 529 ore prima dell'entrata. Concludere che la nascita sia *errata* assume che
l'entrata debba coincidere con la nascita economica vera — assunzione che non ho dimostrato.
Può essere un ri-avvistamento, una migrazione, un cambio di pool.

**«Sopravvivenza» è il nome sbagliato.** Ho misurato la **durata osservata**, non la vita del token.
La differenza 1,0h contro 23,4h può venire da mortalità reale **oppure** da buchi di copertura,
limiti di frequenza, cambi di identificativo, o dalla soglia dei $5.000. Il nome corretto è
**selezione su vita osservata e disponibilità dei dati**. Distinguere le due richiede un test
prospettico che non abbiamo ancora fatto: a +3h chiedere a un canale indipendente se il pool è ancora
attivo, e confrontare con la presenza della candela da noi.

## 11.2 Il verdetto, corretto

Non «ogni analisi è invalida». La formulazione giusta è più stretta e più difendibile:

> 🔴 **ROSSO** per qualsiasi affermazione **generalizzabile ai token nuovi che scopriamo**.
> 🟡 **GIALLO** per analisi **esplicitamente condizionate** al cohort osservato — «pool che il
> sistema ha visto con almeno 5 candele, con questo protocollo» — e senza le feature sugli scambi.

## 11.3 Quali risultati storici sono nulli, e quali no

**Nulli** (o comunque non identificabili): qualunque affermazione sul potere predittivo delle quattro
feature-scambi, sulla loro importanza, sulle interazioni con le altre, e qualunque generalizzazione a
pool nuovi. Nel 92,2% del cohort quelle feature non variano: lì l'effetto non è stimabile. Nell'8%
restante la variazione viene da pool con storia radicalmente diversa, quindi è confusa con l'anzianità.

**Non automaticamente nulli**: i conteggi descrittivi datati correttamente, le analisi che non usano
le feature-scambi, e i risultati riprodotti escludendo le 133 righe attive — purché dichiarati validi
**solo** per il cohort osservato.

La verifica minima, da fare: rieseguire ogni risultato (a) senza feature-scambi, (b) sulle sole righe
neutre, (c) escludendo le attive. Se la conclusione cambia, il risultato storico non è difendibile.

## 11.4 Un difetto che non avevo cercato — e che PASSA

Il revisore ha chiesto: la stessa entità compare in più righe, finendo sia in addestramento che in
prova? Controllo deterministico:

| chain | righe | pool distinti | duplicati |
|---|---|---|---|
| base | 1.710 | 1.710 | **0** |
| solana | 759 | 759 | **0** |
| robinhood | 670 | 670 | **0** |

**Nessuna duplicazione. ✅ PASS** — verificato, non assunto.

## 11.5 Disaccordi che restano

Nessuno sostanziale sui fatti. Restano **tre cose non giudicabili** finché non arrivano dati nuovi:
il ritardo reale per chain, la mortalità contro la copertura, e se l'embargo corretto cambierebbe
qualche conclusione.

---

# 12. L'ORDINE DELLE RIPARAZIONI

Il revisore è stato netto su cosa viene prima, e ho seguito il suo ordine invece del mio:

> *«Correggere l'embargo senza poter provare quando il dato è arrivato produce semplicemente un
> embargo più elegante ma non verificabile.»*

| # | riparazione | stato |
|---|---|---|
| 1 | libro mastro point-in-time, in sola aggiunta | 🟢 **fatto oggi** — `agents/registro_pit.py`, prima annotazione vera registrata |
| 2 | misurare i ritardi veri per chain / fonte / periodo | ⏳ possibile solo sui dati nuovi |
| 3 | risolvere l'identità e la semantica di «nascita» | 🔴 da fare |
| 4 | separare copertura da mortalità col cohort prospettico | 🔴 da fare |
| 5 | rieseguire tutti i confronti storici sui dataset ricostruiti | 🔴 dopo i precedenti |

**L'embargo NON è stato toccato.** Cambiarlo adesso modificherebbe retroattivamente ogni confronto
storico senza poter dimostrare che la nuova versione è più vera della vecchia.
