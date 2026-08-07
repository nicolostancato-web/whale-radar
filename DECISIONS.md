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
