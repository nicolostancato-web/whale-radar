# 📥 ACCUMULATION ROADMAP (Fase 1) — dai deep-search #9 + #10

> Fase 1 = SOLO accumulo, al millimetro. L'analisi (Fase 2) solo quando l'archivio è ricco.
> Verità: i memecoin Robinhood sono GIOVANI → storia corta per natura → catturarli alla NASCITA è la chiave.

## ✅ FATTO
- Candele OHLCV (daily 1000gg + orarie) — `data/raw/candles/`
- Whale-buy >= $10k (wallet+$+time) + pressione buy/sell — `data/raw/whales/`
- Storage immutabile compresso (no corruzione) + dedup + resumable
- **Registro pool che CRESCE** = top-volume + **NUOVI NATI** (`/new_pools`, catturati alla nascita)

## 🔜 PROSSIMI (in ordine di valore, tutti GRATIS)
1. **DexScreener come 2ª fonte trade** (real-time, no buffer 2h) → non perdere whale.
2. **Abbassare soglia**: accumulare TUTTI i trade (non solo $10k) con wallet+amount → analisi ricca. (scartare < $100 = rumore)
3. **Pool metadata**: deployer, creation_ts, decimals, symbol (GeckoTerminal/DexScreener) — già in parte nel registro.
4. **Feature pre-calcolate per candela**: whale_count, net_flow, pressure_ratio (durante l'accumulo).
5. **Blockscout — storico completo trade** (oltre i 300 del buffer): `/api?module=logs&action=getLogs&address={pool}` → early whale accumulation.
6. **Holder snapshots giornalieri** (top 1000): Blockscout `tokenbalance` → concentrazione.
7. **Contract events** (Transfer/Mint/Burn/Ownership) + **LP changes** (chi aggiunge/toglie liquidità).
8. **Wallet first/last seen** + (poi) reputazione/cluster.

## 🗓️ Schedule stratificato (deep-search #9)
- ogni ~5-15 min: nuovi pool + trade dei top → non perdere whale
- ogni 4-6h: refresh registro pool (top + nati) + candele
- giornaliero: holder snapshot
- rate-limit: ~30 req/min (IP GitHub condiviso). Backfill grossi dal PC su richiesta.

## 🗑️ NON accumulare (spreco)
trade < $100 · candele < 1h (5m/15m) · social real-time (API troppo limitata) · wallet non-EOA (per ora) · storia pre-listing (impossibile gratis).

## 🔑 Chiavi di join (per l'analisi futura)
`pool` (address) · `ts` (allinea le serie) · `wallet` · `tx` (trade univoco). Feature: età token, whale/candela, net-flow.
