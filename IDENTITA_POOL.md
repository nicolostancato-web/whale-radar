# 🔑 L'IDENTITÀ DI UN POOL — regola, e perché

*18 settembre 2026 · nato da un rilievo della revisione esterna su un errore non ancora commesso*

## Il rilievo

> «State per confondere o fondere identità di pool tra namespace diversi. Guardate ogni join,
> vincolo di unicità e deduplicazione che usa un `pool_id` senza chiave composta da
> `chain + versione + identificatore normalizzato`. Avete già trovato doppioni: il prossimo errore
> è chiamare "deduplica" una fusione di entità diverse.»

## Verificato: la collisione esiste

Su **58.165 identificativi** censiti fra le due chain, **uno compare su entrambe**:

```
0xc968d6917d0959792d45b8aebaa9…   (id Uniswap V4)
```

Non è una coincidenza rara e basta. Un id V4 è l'impronta della **configurazione** del pool — la
coppia di token, la commissione, gli hook. La stessa configurazione su due chain diverse produce
**lo stesso id**. Con l'aumentare del censimento le collisioni aumenteranno.

## La regola

**L'identità di un pool è la coppia `(chain, identificativo)`. Mai l'identificativo da solo.**

Vale per: chiavi di dizionario, nomi di file, join fra insiemi, deduplicazioni, conteggi di pool
distinti, e qualunque confronto fra chain.

E l'identificativo va sempre **normalizzato in minuscolo** prima di essere usato come chiave. Oggi
i nostri file sono puliti (zero nomi con maiuscole su 5.460 controllati), ma è una proprietà che si
rompe alla prima fonte nuova.

## Oggi siamo al sicuro, e solo per fortuna

I dati stanno in cartelle separate per chain (`data/multichain/base/...`,
`data/multichain/robinhood/...`), quindi la collisione non fonde niente: la cartella fa da
namespace. Anche `nascita_vera.json`, `coppie.json` e `censimento.jsonl.gz` sono per chain.

**Ma è una protezione accidentale, non una scelta.** Bastava un'analisi che caricasse i pool di
entrambe le chain in un dizionario solo per fondere due pool diversi in uno — e il risultato non
sarebbe sembrato sbagliato: sarebbe sembrato un pool con il doppio dell'attività.

## Perché questo documento esiste

Il rilievo riguarda un errore **che non abbiamo ancora fatto**. È la prima volta in tre giorni che
chiudiamo un difetto prima che si manifesti, invece di inseguirlo dopo il sintomo.

Vale la pena notare come è successo: non l'ho trovato io. L'ha previsto un revisore che non ha
accesso al codice, partendo dall'elenco dei difetti già fatti e chiedendosi *quale sia il prossimo
della stessa famiglia*. È esattamente il mestiere per cui esiste.

---

## Aggiornamento del 18/09: la regola non bastava

Avevo scritto che l'identita' e' `(chain, identificativo)`. La revisione esterna ha fatto notare
che per i pool V4 **non basta**:

> «Il pool id deriva dalla configurazione, non identifica necessariamente l'istanza di
> `PoolManager`. Due manager o fork sulla stessa chain possono produrre lo stesso id.»

**Verificato su base, e i due manager ci sono gia':**

```
0x498581ff718922c3f8e6a244956af099b2652b2b   10.679 swap V4
0x60b393a76cea4a3afff00e1fb08d0f63a8f4a314       10 swap V4
```

Una collisione oggi non l'abbiamo vista — ma **non potremmo vederla**, perche' salvavamo solo
`topics[1]` e buttavamo via chi aveva emesso il log. Un pool del secondo manager con lo stesso id
del primo sarebbe finito nello stesso file, e il risultato non sarebbe sembrato sbagliato: sarebbe
sembrato un pool con piu' attivita'.

### La regola corretta

**L'identita' di un pool e' la terna `(chain, contratto emittente, identificativo)`.**

Da oggi ogni record porta il campo `mgr` con l'indirizzo del contratto che ha emesso il log. I
record precedenti non ce l'hanno: per quelli il manager e' **ignoto**, e vanno trattati come tali —
non come «sicuramente il manager principale».

### Due volte lo stesso avvertimento

E' la seconda volta in un giorno che la revisione esterna indica un errore di identita' **prima che
si manifesti**, e la seconda volta che verificandolo si scopre che la condizione per commetterlo
esiste gia'. La prima era la collisione fra chain (un id su 58.165, trovato). Questa e' la
collisione dentro la stessa chain (due manager, trovati).

Il filo comune: **un identificativo derivato da una configurazione non e' una chiave primaria.**
Sembra unico perche' nei dati che abbiamo lo e' stato finora.
