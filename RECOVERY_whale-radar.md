# RECOVERY — whale-radar (snapshot 2026-08-21)

## Cosa stiamo facendo (1 frase)
Sistema auto-apprendente che trova quali memecoin nuove pumperanno, per guadagnarci, senza rischiare soldi
finche' l'edge non e' provato. GOAL: walk-forward onesto chiaramente positivo e ROBUSTO su abbastanza token.

## SVOLTA DI OGGI: ESPANSIONE MULTI-CHAIN
Robinhood chain e' TROPPO SOTTILE (~3 tradeabili/giorno, e in raffreddamento -72% dal picco luglio → ricerca web).
Robinhood resta la PALESTRA (dove abbiamo forgiato il metodo giusto), le CHAIN GROSSE sono la fabbrica.
- Ricerca chain (agosto 2026): Solana domina ($3B DEX vol, pump.fun 30-80k lanci/gg), poi ETH/Base/BSC (~$1.2B),
  Hyperliquid $609M. Solana non-EVM (rebuild), BSC/Base EVM (porting facile).
- **MULTICHAIN_COLLECTOR live e POTENZIATO**: 4 chain in PARALLELO (matrix, IP diversi=4x), via GeckoTerminal
  (1 API per tutte le chain), 120 candele/run ogni 20min. Accumula candele+pool per Solana/BSC/Base/Robinhood
  in data/multichain/<chain>/. Ieri sera: gia' 1076 pool in 1 giorno (vs 866 Robinhood in 52gg).

## STATO: accumulo multi-chain LIVE, cervello ANCORA solo Robinhood
- Il learner/edge_eval/paper_bot leggono ANCORA solo Robinhood (data/raw/*).
- I dati multi-chain (data/multichain/*) si accumulano ma NON sono ancora dati al modello.

## PROSSIMO STEP (DOMANI, deciso con Nicolo)
Costruire il CERVELLO + LOOP che impara su TUTTE le chain: adattare learner/edge_eval/data_analyst a leggere
data/multichain/* (candele+volume, chain-agnostico) → walk-forward per-chain e combinato → capire QUALE chain rende
di piu'. Poi portare le feature profonde (flow/first-buyers) per chain (EVM facile, Solana via endpoint trades GT).
NB: solo candele oggi nel multichain (no flow/first-buyers) → partire con feature candle+volume.

## Metodo/loop (invariato, ci fidiamo)
paper_bot (uscita scale-out 3x/6x, costi 100% reali) + learner (AUC out-of-sample, si attiva >=0.60) +
edge_eval (walk-forward onesto -> EDGE.md) + data_analyst (candidati -> ANALYSIS.md). No-lookahead sempre.
Ultimo edge Robinhood: base +15%, selezione +23% (ma concentrato su ~3 mostri = fragile, servono piu' dati).

## Come riprendere
Nuova chat: leggi questo + TRADER.md (il cervello: come imparo/analizzo/miglioro). A "news?" leggo EDGE.md/PAPER.md/
LEARNING.md + i contatori data/multichain/<chain>/pools.json. MINDSET: mai proporre di mollare (decide Nicolo),
push in LOOP come bestie fino al goal, onesto sui numeri.
