**1. LISTA COMPLETA DELLE FEATURE (Prioritarizzata)**

| Nome Feature | Priorità | Definizione/Formula Esatta | Fonte Dati Primaria | Perché Individua l'Insider |
| :--- | :--- | :--- | :--- | :--- |
| `eta_token_ore` | ESSENZIALE | `(timestamp_blocco_acquisto - timestamp_primo_swap_token) / 3600`. Se nessuno swap, usa `timestamp_blocco_acquisto - timestamp_creazione_pool`. | RPC/Eventi (`Sync` di un pool DEX, o evento `PoolCreated`). | Un insider agisce nella finestra di opportunità iniziale, prima che il token diventi noto. Un trader normale raramente trova e valuta token con meno di 24h di vita. |
| `posizione_in_sequenza_acquisti` | ESSENZIALE | `indice_acquisto_wallet / numero_totale_acquisti_token`. `indice_acquisto_wallet` = conteggio sequenziale (1,2,3...) degli acquisti di quel token da parte di wallet unici, ordinati per `timestamp_blocco`. Primo acquirente = 1. | Flusso Swap (eventi `Swap` filtrati per token in uscita). | Gli insider sono tra i primi a muoversi. Essere tra i primi 10-20 acquirenti è statisticamente anormale per un wallet casuale. |
| `delta_prezzo_acquisto_min_24h` | ESSENZIALE | `(prezzo_acquisto_usd - prezzo_minimo_24h_usd) / prezzo_minimo_24h_usd`. `prezzo_minimo_24h_usd` = minimo di `prezzo_usd` di tutti gli swap del token nelle 24h PRECEDENTI il `timestamp_blocco_acquisto`. | Candele OHLCV (1h o 5m) derivate da flusso swap. | Comprare vicino al minimo delle ultime 24h indica timing perfetto o conoscenza di un pavimento di prezzo, non comune per un retail. |
| `percentile_prezzo_acquisto_storico` | ESSENZIALE | `(conteggio_swap_con_prezzo_inferiore + 1) / (conteggio_totale_swap_token + 1)`. Conta tutti gli swap del token dalla creazione fino al blocco dell'acquisto. Prezzo di riferimento = `amountOut / amountIn` normalizzato in USD. | Flusso Swap (tutti gli eventi storici del token). | Un insider compra "basso" nella storia del token. Un acquirente normale ha una distribuzione uniforme; un percentile <20% è sospetto. |
| `wallet_funding_size_usd` | ESSENZIALE | Somma del valore USD di *tutti* i trasferimenti in entrata (ETH, USDC, etc.) sul wallet acquirente nei 30 giorni prima dell'acquisto. Il valore USD è calcolato al prezzo al momento di ogni trasferimento in entrata. | Forensica (tracciamento flussi da CEX, wallet noti, altri contatti). | Un insider operativo è spesso finanziato da un'entità grande. Un wallet con funding >$100k che compra un token da $5k è un pattern da "soldato". |
| `pattern_consistenza_cross_token` | UTILE | `conteggio_token_giovani_acquisiti / conteggio_totale_acquisti`. `token_giovane_acquisito` = token con `eta_token_ore` < 168 al momento del relativo acquisto. Conteggi fatti sulla cronologia del wallet fino al blocco corrente. | Flusso Swap + RPC/Eventi (cronologia wallet). | Un insider ripete il pattern. Un wallet che ha >30% dei suoi acquisti su token <7gg è anomalo. |
| `dimensione_acquisto_percentuale_liquidity` | UTILE | `(valore_usd_acquisto) / (liquidity_pool_usd)`. `liquidity_pool_usd` = riserva del token in USD nel pool DEX più liquido al blocco PRECEDENTE l'acquisto. | RPC (`getReserves` chiamata al pool) + Candele per prezzo. | Un insider evita di muovere troppo il mercato. Un acquisto >2-5% della liquidità è rumoroso e rischioso; un insider tiene basso il profilo. |
| `intervallo_da_ultimo_acquisto_token` | UTILE | Se il wallet ha già acquistato lo stesso token in precedenza: `timestamp_blocco_acquisto - timestamp_ultimo_acquisto_wallet_su_token`. Altrimenti: `null`. | Flusso Swap (cronologia wallet per quel token). | Un insider può fare "scaling in" prima di un evento. Un secondo acquisto a distanza ravvicinata (es. <6h) suggerisce convinzione, non FOMO. |
| `clustering_temporale_acquisti` | OPPZIONALE | Deviazione standard (in ore) dei `timestamp_blocco` degli ultimi N acquisti (es. N=5) del wallet, considerando solo acquisti su token con `eta_token_ore` < 168. Calcolata al momento dell'acquisto. | Flusso Swap (cronologia wallet). | Gli insider operano in "sessioni". Una deviazione standard bassa (<24h) su acquisti cross-token indica attività concentrata, non comportamenti sparsi nel tempo. |
| `vicinanza_acquisto_lancio` | OPPZIONALE | `timestamp_blocco_acquisto - timestamp_primo_swap_token`. In secondi. | RPC/Eventi (`Sync`). | Complementare a `eta_token_ore`. Essere tra i primi swap in assoluto (es. <10 minuti) è estremamente raro e richiede automazione o conoscenza diretta. |

**2. DEFINIZIONI OPERATIVE RIGOROSE**

*   **"Entrato PRIMA del pump":** L'acquisto deve avvenire PRIMA che il prezzo del token aumenti del **+50% in un intervallo di 24 ore consecutivo**. Il "pump" è definito come: Esiste una candela OHLCV (oraria) dove `(close - open) / open >= 0.5`. L'acquisto è "prima" se il suo `timestamp_blocco` è **minore** del `timestamp_inizio` della prima candela di pump che soddisfa il criterio. Il controllo usa solo dati storici: si cerca indietro dal momento dell'acquisto per pump precedenti (irrilevante) e in avanti per un massimo di 24h dopo l'acquisto (definizione operativa). *Questa logica deve essere eseguita in Fase 2, ma il dato grezzo per calcolarla (`prezzo_post_acquisto_24h`) deve essere salvato ORA.*
*   **"Token giovane":** Token la cui durata di vita, al momento dell'acquisto, è **<= 168 ore (7 giorni)**. La durata è calcolata come: `timestamp_blocco_acquisto - timestamp_primo_evento_swap_token`. Se non esistono swap, non è un token commerciabile e viene scartato.
*   **"Comprato basso":** L'acquisto avviene ad un prezzo che si trova nel **20° percentile inferiore** della distribuzione storica dei prezzi di tutti gli swap del token fino a quel momento. Metriche: `percentile_prezzo_acquisto_storico <= 0.2`.
*   **"Ripetuto/Consistente":** Pattern identificato a livello di **wallet sorgente dei fondi**. Si traccia il grafo di funding (input) dell'wallet acquirente. Se un wallet sorgente (o un cluster di wallet collegati) ha finanziato **>=3 wallet distinti** che hanno effettuato acquisti classificabili come "prima del pump" su token "giovani" in un arco di 30 giorni, allora il pattern è considerato "ripetuto". La consistenza è un'analisi cross-wallet, non solo sul singolo wallet acquirente.
*   **"Finanziato da entità grossa":** Il wallet acquirente ha ricevuto, nel suo ultimo ciclo di funding (30 giorni), **>=40%** del suo inflow totale da un singolo wallet sorgente che, a sua volta, ha un **volume USD lifetime (somma di tutti i valori di swap in uscita) >= $1,000,000**. Il volume lifetime del sorgente è calcolabile al momento dell'acquisto.
*   **"Early buyer / Vicino al lancio":** L'acquirente è tra i **primi 20 wallet unici** ad aver effettuato un acquisto (swap in entrata) di quel token. Metriche: `posizione_in_sequenza_acquisti <= 20`. "Vicino al lancio" è anche definito come `vicinanza_acquisto_lancio < 3600` secondi (1 ora).

**3. TRAPPOLE DA IDENTIFICARE ED EVITARE**

1.  **Lookahead Bias (Il più letale):**
    *   **Problema:** Usare informazioni future (es. prezzo massimo del mese successivo) per definire un segnale al momento dell'acquisto. Invalida completamente l'analisi rendendola non replicabile in tempo reale.
    *   **Come si evita:** Ogni formula in **Punto 1** usa esclusivamente dati con `timestamp <= timestamp_blocco_acquisto`. Esempio: `prezzo_minimo_24h_usd` guarda solo le 24h PRIMA. Per definire "PRIMA del pump", il record salva il prezzo a 24h di distanza, ma la classificazione avviene in Fase 2.

2.  **Survivorship Bias:**
    *   **Problema:** Analizzare solo token che sono "sopravvissuti" ed hanno un prezzo/listato su CEX, ignorando i token falliti/rubati. Porta a sovrastimare l'abilità degli insider.
    *   **Come si evita:** Il sistema accumula dati per **OGNI** acquisto >$1k su **OGNI** token che soddisfa i criteri di età, indipendentemente dal suo futuro destino. Il dataset grezzo include quindi molti "failures".

3.  **Definizioni Circolari:**
    *   **Problema:** Definire un "insider" come "chi compra prima di un pump" e poi usare "acquisti prima di un pump" come feature per trovare insider. È una tautologia.
    *   **Come si evita:** Le feature in **Punto 1** sono **proxies indipendenti** del comportamento sospetto (tempistica, prezzo, pattern di wallet). La classificazione finale ("score insider") in Fase 2 combinerà queste proxy, ma la loro definizione non dipende dalla classificazione stessa.

4.  **Errate Assunzioni di Normalità:**
    *   **Problema:** Assumere che metriche come `percentile_prezzo_acquisto_storico` siano uniformemente distribuite per trader normali. In mercati illiquid e pump&dump, la distribuzione potrebbe essere skewata.
    *   **Come si evita:** Non si assume normalità. In Fase 2, le soglie (es. percentile <20%) saranno calibrate empiricamente sulla distribuzione osservata nella popolazione di *tutti* gli acquisti, non su assunzioni teoriche.

5.  **Bias di Aggregazione Temporale (Time-Aggregation Bias):**
    *   **Problema:** Calcolare feature su finestre temporali fisse (es. "24h") senza considerare l'età del token. Per un token di 2 ore, il "minimo delle ultime 24h" è un dato fuorviante.
    *   **Come si evita:** Per token con `eta_token_ore < 24`, la feature `delta_prezzo_acquisto_min_24h` viene sostituita con `delta_prezzo_acquisto_min_vita`: `(prezzo_acquisto - prezzo_minimo_dalla_creazione) / prezzo_minimo_dalla_creazione`. La logica di fallback è parte della definizione atomica.

**4. FORMATO DEL RECORD DA SALVARE**

```json
{
  "schema_version": "1.0",
  "record_type": "balena_acquisto",
  "data": {
    "campi_identificativi": {
      "wallet": "string",
      "token": "string",
      "timestamp_blocco": "integer",
      "hash_tx": "string",
      "block_number": "integer"
    },
    "metriche_contesto": {
      "eta_token_ore": "float",
      "timestamp_primo_swap_token": "integer",
      "liquidity_pool_usd_at_acquisto": "float",
      "prezzo_acquisto_usd": "float",
      "valore_usd_acquisto": "float",
      // Dati per calcolare "PRIMA del pump" in Fase 2
      "prezzo_token_24h_post_acquisto_usd": "float"
    },
    "feature_calcolate": {
      "posizione_in_sequenza_acquisti": "integer",
      "delta_prezzo_acquisto_min_24h": "float",
      "percentile_prezzo_acquisto_storico": "float",
      "wallet_funding_size_usd_30gg": "float",
      "pattern_consistenza_cross_token": "float",
      "dimensione_acquisto_percentuale_liquidity": "float",
      "intervallo_da_ultimo_acquisto_token_ore": "float|null",
      "clustering_temporale_acquisti_ore_std": "float|null",
      "vicinanza_acquisto_lancio_secondi": "integer"
    },
    "metadata_calcolo": {
      "finestra_calcolo_prezzo_min_ore": "float",
      "soglia_token_giovane_ore": "integer",
      "timestamp_elaborazione": "integer"
    }
  }
}
```
**Naming Convention:** Tutto in `snake_case`. Tipi: `string`, `integer`, `float`. I valori `null` sono ammessi per feature non applicabili. `timestamp` è sempre in secondi Unix.