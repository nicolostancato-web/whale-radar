# 🔁 LOOPS — i meeting del sistema
*2026-09-05 02:18 UTC · un meeting per goal, a ogni ciclo (~30 min)*

## Architetto: 🟢 tutti i loop si stanno riunendo

| loop | la domanda | dove siamo | ago | cosa si fa |
|---|---|---|---|---|
| `accumulo-base` | Stiamo raccogliendo token Base nuovi? | 4297 token con dati (2138 osservati dal vivo, 2159 con storico) su 15557 pool noti | ⏸ fermo dall'ultimo meeting | ✋ mano alzata: rilanciato **pulse.py** (fermo da 1 meeting) |
| `accumulo-solana` | Stiamo raccogliendo token Solana nuovi? | 1129 token con dati (129 osservati dal vivo, 1000 con storico) su 14655 pool noti | ⏸ fermo dall'ultimo meeting | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (solana_helius.py, multichain_collector.py) → non li ripet |
| `percentuale-robinhood` | Come alziamo la percentuale su Robinhood? | robusta -17% (media +22%) su 71 token | ⏸ fermo da 2h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer.py, learner.py) → non li ripetiamo, se |
| `percentuale-base` | Come alziamo la percentuale su Base? | robusta +0% (media +3%) su 1079 token | ⏸ fermo da 3h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_base.py, learner.py) → non li ripetiam |
| `percentuale-solana` | Come alziamo la percentuale su Solana? | robusta -13% (media -9%) su 698 token | ⏸ fermo da 6h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_solana.py, wallet_insider.py) → non li |
| `demo-robinhood` | Come arriviamo a 3.000 euro su Robinhood? | 🔴 SOSPESO dal cancello — campione troppo piccolo: 71 token (ne servono 150) | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `demo-base` | Come arriviamo a 3.000 euro su Base? | 🔴 SOSPESO dal cancello — il LOOP 1 e' a **+0%** robusta, sotto la soglia di **+40%**: andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `accumulo-robinhood` | Stiamo raccogliendo token Robinhood nuovi? | 725 token con dati (0 osservati dal vivo, 725 con storico) su 17282 pool noti | ⏸ fermo dall'ultimo meeting | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (whale_candles.py, whale_backfill.py, multichain_collector |
| `accumulo-bsc` | Stiamo raccogliendo token BSC nuovi? | 1062 token con dati (146 osservati dal vivo, 916 con storico) su 17485 pool noti | ⏸ fermo dall'ultimo meeting | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (pulse.py, multichain_collector.py, multichain_rpc.py) → n |
| `percentuale-bsc` | Come alziamo la percentuale su BSC? | robusta -24% (media -21%) su 577 token | ⏸ fermo da 18h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (explorer.py, learner.py) → non li ripetiamo, serve cambia |

## 🎯 Le 3 cose che contano adesso

1. **percentuale-bsc** — fermo da 18h. robusta -24% (media -21%) su 577 token
2. **percentuale-solana** — fermo da 6h. robusta -13% (media -9%) su 698 token
3. **percentuale-base** — fermo da 3h. robusta +0% (media +3%) su 1079 token

> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.
> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).
> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md.