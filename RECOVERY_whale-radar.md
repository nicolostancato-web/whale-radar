# RECOVERY — whale-radar (snapshot 2026-08-17 )

## Cosa stiamo facendo (1 frase)
Loop auto-apprendente su chain Robinhood: il paper bot testa la strategia coda-grassa forward (€0, cloud),
il learner impara dai trade a distinguere vincenti da morti. Goal misurabile: **AUC >= 0.60 -> selezione ON -> portafoglio verde**.

## Stato oggi
- Paper bot v2 LIVE forward: filtro tradeabilita + uscita a scaglioni (ultimo 1/3 cavalca i mostri, hard-stop -70% pre-lock).
- AUTO-LEARNER live: 7 feature (ore_flow, volume, sell_ratio, buy_accel, dump_depth, smart_money_frac, n_firstbuyers).
  AUC robusta multi-split. Si attiva SOLO a >=60 trade E AUC>=0.60.
- Progresso: 38 trade chiusi (servono 60 per accendere il learner). Su STORICO l'AUC e' 0.68 base -> 0.715 coi first-buyers (SOPRA il goal). Forward = giudice vero.
- Accumulo Fase 1 attivo (collector/accumulator/director + whale/candele/first-buyers/flow). 14 workflow, tutti verdi.

## Ultimi 5 step
1. Analisi manuale "vincenti" su DexScreener -> scoperto honeypot (LWOOD), miraggi liquidita' (HOOPLA $12), dati close-only.
2. Bot v2: filtro anti-scam + uscita a scaglioni. Verita' cruda backtest: -36% realistico (2,6 morti per vincente).
3. Costruito AUTO-LEARNER (impara dai propri esiti, onesto: non si attiva su illusioni).
4. Loop iterazione feature: +first-buyers -> AUC 0.68->0.715. AUC resa robusta (media 8 split).
5. Snapshot di fine giornata.

## Prossimo step
Aspettare che i trade forward arrivino a 60 -> il learner si accende da solo se AUC>=0.60 -> selezione attiva.
Poi: (a) confermare AUC forward, (b) se serve alzarla, aggiungere feature liquidita' on-chain.

## Come riprendere
Nuova chat: leggi questo file + TRADER.md (il cervello: come imparo/analizzo/miglioro) + PAPER.md + LEARNING.md.
Comando rapido stato: l'utente scrive "news?" -> leggo PAPER.md/LEARNING.md dal repo.
