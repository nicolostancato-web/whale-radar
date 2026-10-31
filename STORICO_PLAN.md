# PIANO DI RACCOLTA STORICA AGGRESSIVA

## 1. **Strategia Storica Ottimale**
Blocco iniziale = primo evento `PoolCreated` della factory Uniswap V2 (blocco 0 se non trovato). Recupero TUTTI gli eventi di pool via `eth_getLogs` (2000 blocchi/chiamata). Filtro spam con: liquidità iniziale >0.5 ETH O almeno 3 swap nei primi 7 giorni. Candele: priorità a pool filtrati, GeckoTerminal (1000 candele max) + backfill RPC per OHLCV base se necessario. Ogni evento swap (qualsiasi size) viene estratto e allineato a candele orarie. Checkpoint per ogni lotto di 10k blocchi per timeout GitHub.

## 2. **Ordine di Raccolta Prioritizzato**
1. **Lista completa pool storici** - via `eth_getLogs` su evento `PoolCreated` dalla factory (indirizzo noto). Fondamentale per avere l'universo completo, incluso token morti.
2. **Metadati pool e filtraggio** - per ogni pool, recupero via RPC: liquidità iniziale (evento `Mint` al blocco creazione) e conteggio swap primi 7 giorni (eventi `Swap`). Filtro spam qui.
3. **Eventi swap storici completi** - per ogni pool filtrato, estrazione di TUTTI gli eventi `Swap` (nessun filtro su amount). Base per volume, pressione, distribuzione size.
4. **Candele storiche massime** - per ogni pool filtrato: candele orarie da GeckoTerminal (max 1000, ~41 giorni), poi daily da RPC (blocco a blocco) per coprire i ~100 giorni. Priorità a pool più vecchi.
5. **Dati balena (sottoinsieme)** - derivato dagli swap già raccolti, filtrando per value >= $3k (calcolato con prezzo storico).
6. **Dati aggiuntivi low-cost** - holder count storico (da eventi `Transfer` cumulativi), deployer/timestamp creazione token (evento `TokenCreated` se disponibile).

## 3. **Procedura per Recuperare Token Morti Gratis**
**Endpoint RPC**: `POST https://rpc.robinchain.org` (pubblico)  
**Evento**: `PoolCreated(address indexed token0, address indexed token1, address pool)` dalla factory Uniswap V2 (indirizzo: `0x...` da verificare su Blockscout).  
**Query esempio**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "eth_getLogs",
  "params": [{
    "fromBlock": "0x0",
    "toBlock": "0xLatest",
    "address": "0xFactoryAddress",
    "topics": ["0xPoolCreatedTopic"]
  }]
}
```
**Filtri anti-spam**:
1. **Liquidità iniziale**: dopo evento `PoolCreated`, cercare primo evento `Mint` nello stesso blocco. Se `amount0` o `amount1` in ETH < 0.5 (via prezzo storico), scarta.
2. **Swap reali**: contare eventi `Swap` nei primi 50400 blocchi (~7 giorni). Se <3, scarta.
**Costo stimato**: ~50 chiamate RPC (100k blocchi / 2000) per recupero pool, + ~2 chiamate per pool per filtraggio.

## 4. **Rischi e Mitigazioni**
| Rischio | Mitigazione |
|---------|-------------|
| **Rate-limit RPC/Blockscout** | Backoff esponenziale + coda prioritaria. Per Blockscout (10 req/min), parallelizza solo metadati non critici. |
| **Timeout GitHub Actions (max 6h)** | Partiziona in lotti di 100k blocchi (~1.5h/lotto). Checkpoint dopo ogni lotto in file `checkpoint.json`. |
| **Spazzatura sovraccarica dataset** | Filtro a due stadi: (1) liquidità iniziale >0.5 ETH O (2) >=3 swap primi 7 giorni. Riduce pool ~80% mantenendo morti validi. |

## 5. **Piano Dettagliato e Pseudo-codice**

**Passo 1 – Recupero universale pool (resumable)**
```python
# Config
START_BLOCK = 0  # o primo blocco factory se >0
END_BLOCK = latest
CHUNK = 2000
factory = "0x..."
topic = "0x..."

# Checkpoint
if exists("checkpoint_pools.json"):
    start = load("checkpoint_pools.json")["last_block"]
else:
    start = START_BLOCK

# Loop
for from_block in range(start, END_BLOCK, CHUNK):
    to_block = min(from_block + CHUNK - 1, END_BLOCK)
    logs = rpc_call("eth_getLogs", [{
        "fromBlock": hex(from_block),
        "toBlock": hex(to_block),
        "address": factory,
        "topics": [topic]
    }])
    save_logs(logs)  # formato jsonl.gz
    save_checkpoint({"last_block": to_block})
    if time_elapsed() > 5h: break  # per GitHub
```

**Passo 2 – Filtraggio pool (per token)**
```python
pools = load_all_pools()  # da passo 1
valid_pools = []
for pool in pools:
    # 1. Liquidità iniziale
    mint_events = get_logs(pool.block, pool.block, pool.address, "Mint")
    if mint_events:
        liq_eth = convert_to_eth(mint_events[0].amount0, mint_events[0].amount1)
        if liq_eth >= 0.5:
            valid_pools.append(pool)
            continue
    
    # 2. Almeno 3 swap nei primi 7 giorni
    swap_count = count_logs(pool.block, pool.block + 50400, pool.address, "Swap")
    if swap_count >= 3:
        valid_pools.append(pool)
```

**Passo 3 – Raccolta swap completi (per pool validi)**
```python
for pool in valid_pools:
    swaps = get_logs(pool.creation_block, END_BLOCK, pool.address, "Swap")
    for swap in swaps:
        # Calcola size USD usando prezzo storico da candele
        usd_value = calculate_usd_value(swap, get_historical_price(pool.token, swap.block))
        save_swap(swap, usd_value)  # include TUTTI gli swap
```

**Passo 4 – Candele forward per ogni evento**
```python
for swap in all_swaps:
    # Allinea blocco -> timestamp orario
    swap_time = block_to_timestamp(swap.block)
    candle_1h = get_candle(swap_time, "1h", pool.address)  # da GeckoTerminal o RPC
    # Candele forward: 72h e 168h
    if swap_time + 168h < now():
        fwd_72h = aggregate_candles(swap_time, swap_time + 72h, "1h")
        fwd_168h = aggregate_candles(swap_time, swap_time + 168h, "1h")
        save_forward_candles(swap.id, fwd_72h, fwd_168h)
    else:
        mark_as_incomplete(swap.id)  # escludi dall'analisi se finestra incompleta
```

**Passo 5 – Dati aggiuntivi low-cost**
- **Holder count**: conta `Transfer` cumulativi per token fino al blocco evento.
  ```python
  holders = set()
  for transfer in get_logs(token_creation_block, event_block, token_address, "Transfer"):
      holders.update([transfer.args.from, transfer.args.to])
  holder_count = len(holders)
  ```
- **Deployer**: primo `Transfer` da address zero (evento `Transfer` al blocco creazione token).

**Passo 6 – Checkpoint e ripartenza**
```python
# File checkpoint.json
{
  "pool_scan": {"last_block": 123456},
  "filtered_pools": ["0xabc...", "0xdef..."],
  "swaps_done": ["pool1", "pool2"],
  "candles_done": ["pool1", "pool2"]
}
# Dopo ogni passo aggiorno. Se job GitHub fallisce, riparte dall'ultimo checkpoint.
```

**Passo 7 – Esportazione dataset finali**
- `swaps_all.jsonl.gz`: tutti gli swap con USD value.
- `candles_1h.jsonl.gz`: candele orarie per pool validi.
- `forward_returns.jsonl.gz`: performance 72h/168h per ogni swap.
- `metadata_pools.jsonl.gz`: liquidità iniziale, deployer, holder count storico.