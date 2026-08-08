# 🧭 DECISIONS — registro decisioni (append-only, mai cancellare)
> Formato: Data · Problema · Decisione · Alternativa scartata · Esito.

## 2026-08-07 · Chain target: Robinhood (non Solana)
- **Problema:** su Solana seguivamo "whale" che erano bot-wash da $6. Nessun edge (provato: causal replay + forward study su 39k eventi).
- **Decisione:** spostarsi su **chain Robinhood** (EVM), dove le whale sono VERE (wallet $360k, token $53M, holder $300k-1M — verificato on-chain).
- **Alternativa scartata:** insistere su Solana / forex-BTC (mercati efficienti, retail perde).
- **Esito:** backtest Robinhood mostra aspettativa positiva (vedi EXPERIMENTS).

## 2026-08-07 · Storage: file compressi committati (no database ora)
- **Problema:** dove accumulare i dati gratis, poco spazio, per sempre?
- **Decisione:** file **.jsonl.gz compressi immutabili**, committati nel repo. Query con DuckDB. NO database.
- **Perché committati (non gitignore):** gli agenti girano su GitHub Actions **stateless** → i dati devono persistere fuori dalla run; e i dati dei **token morti non si riscaricano** (aggiusta survivorship). File piccoli+immutabili = git non si gonfia.
- **Alternativa scartata:** Supabase (satura 500MB), artifacts (scadono 7gg → perderemmo l'accumulo).

## 2026-08-07 · Strategia: scale-out su grandi acquisti (momentum)
- **Problema:** quale strategia testare?
- **Decisione:** entri dopo un grande acquisto, tieni, **prendi profitto a scaglioni** (25% a +30/+80/+180%).
- **Nota onesta:** il filtro "whale vera" (volume assoluto) NON migliora il segnale → è **momentum**, non smart-money. Funziona lo stesso.

## 2026-08-07 · Zero soldi reali finché il paper live non conferma
- **Decisione:** solo-analisi + paper test. Soldi veri SOLO se il forward test (out-of-sample) conferma l'edge.
- **Perché:** su Solana avremmo bruciato €1-2k. Qui €0 finché non è provato.

## 2026-08-07 · Organizzazione via deep-search (API cinese economica)
- **Decisione:** ogni decisione di struttura/organizzazione parte da un deep-search (CometAPI, ~1-2 cent). Budget €1/giorno.

## 2026-08-08 · Whale storiche via RPC pubblico (non Blockscout) + wallet = tx.from
- **Problema:** solo ~9 whale catturate (GeckoTerminal /trades dà solo ultimi ~300, buffer ~2h → le whale scorrono via).
- **Decisione:** nuovo reparto `whale_backfill.py`: eventi Swap storici on-chain via **RPC pubblico** `rpc.mainnet.chain.robinhood.com` (`eth_getLogs`), decode V2/V3, USD dal lato quote (WETH/stable) col prezzo GeckoTerminal.
- **Perché RPC e non Blockscout:** Blockscout gratis = 10 richieste/finestra (429 subito). Il RPC tollera ~2-3 req/s. Finestra blocchi **adattiva** (si dimezza sugli errori "troppi log"). Budget chiamate/run → ogni run GHA ~3-5 min, resumable per-pool.
- **Wallet = `tx.from` (EOA vero), NON il recipient del log:** verificato on-chain che il recipient è spesso il **router** (stesso indirizzo in tutti i leg di un multi-hop). Salvare il router = ripetere l'errore Solana (wallet sbagliati → analisi inutile). 1 chiamata `eth_getTransactionByHash` per whale (rare → costo trascurabile).
- **Timestamp:** modello lineare blocco→tempo (2 blocchi campione, ~0.10 s/blocco) — il RPC non mette il ts nei log.
