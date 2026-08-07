# 📖 DATA_DICTIONARY — struttura esatta di ogni file dati

## `data/state/paper_state.json` — stato paper trading live
```json
{"open":[{"pool":"0x..","name":"CASHCAT / WETH","entry_ts":1786.., "entry":0.11,"liq":220000,
  "max_px":0.12,"sold":0.25,"realized":0.30}], "closed":[...], "last_sig":{"0x..":ts}, "runs":5,
  "stats":{"n_closed":0,"mean_ret":0.0,"median_ret":0.0,"win_rate":0.0,"paper_pnl_usd":0.0}}
```

## `data/raw/snapshots/AAAA-MM/GG/HHMM.jsonl.gz` — foto oraria della chain (immutabile)
Una riga per pool:
```json
{"ts":1786..,"a":"0x<pool>","n":"NOME / WETH","p":0.0038,"liq":220000,"v1":448000,"v24":850000,"pc1":62.1}
```
Campi: `ts` epoch · `a` pool address · `n` nome · `p` prezzo USD · `liq` liquidità $ · `v1`/`v24` volume 1h/24h · `pc1` variazione % 1h.

## `data/processed/events.jsonl.gz` — eventi (grande acquisto) con grafico-prima + esito-dopo
```json
{"pool":"0x..","name":"..","ts":1786..,"entry":0.0038,"liq":220000,
 "flat_24h":0.15,"prior_ret_24h":0.30,"vol_ratio":8.0,"vol_usd":48000,
 "r6":0.05,"r24":-0.02,"r72":0.40,"peak72":0.90,"drawdown72":-0.30,"hours_to_peak":18}
```
`flat_24h`/`prior_ret_24h`/`vol_ratio` = setup PRIMA · `r6/r24/r72`/`peak72`/`drawdown72`/`hours_to_peak` = esito DOPO.
