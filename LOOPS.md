# 🔁 LOOPS — i meeting del sistema
*2026-09-15 22:34 UTC · un meeting per goal, a ogni ciclo (~30 min)*

## Architetto: 🟢 tutti i loop si stanno riunendo

| loop | la domanda | dove siamo | ago | cosa si fa |
|---|---|---|---|---|
| `accumulo-base` | Stiamo raccogliendo token Base nuovi? | 4839 token con dati (3309 osservati dal vivo, 1530 con storico) su 14818 pool noti | ⏸ fermo dall'ultimo meeting | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (pulse.py, multichain_collector.py) → non li ripetiamo, se |
| `accumulo-solana` | Stiamo raccogliendo token Solana nuovi? | 1467 token con dati (201 osservati dal vivo, 1266 con storico) su 14813 pool noti | ⏸ fermo dall'ultimo meeting | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (solana_helius.py, multichain_collector.py) → non li ripet |
| `percentuale-robinhood` | Come alziamo la percentuale su Robinhood? | robusta -26% (media -17%) su 45 token | ⏸ fermo da 10h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer.py, learner.py) → non li ripetiamo, se |
| `percentuale-base` | Come alziamo la percentuale su Base? | robusta -8% (media -3%) su 1909 token | ⏸ fermo da 11h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_base.py, learner.py) → non li ripetiam |
| `percentuale-solana` | Come alziamo la percentuale su Solana? | robusta -26% (media -24%) su 769 token | 📈 si muove | avanti cosi' |
| `demo-robinhood` | Come arriviamo a 3.000 euro su Robinhood? | 🔴 SOSPESO dal cancello — campione troppo piccolo: 45 token (ne servono 150) | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `demo-base` | Come arriviamo a 3.000 euro su Base? | 🔴 SOSPESO dal cancello — il LOOP 1 e' a **-8%** robusta, sotto la soglia di **+40%**: andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `accumulo-robinhood` | Stiamo raccogliendo token Robinhood nuovi? | 2537 token con dati (233 osservati dal vivo, 2304 con storico) su 19020 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-bsc` | Stiamo raccogliendo token BSC nuovi? | 1065 token con dati (291 osservati dal vivo, 774 con storico) su 17481 pool noti | 📈 si muove | avanti cosi' |
| `percentuale-bsc` | Come alziamo la percentuale su BSC? | robusta -24% (media -21%) su 604 token | ⏸ fermo da 8h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (explorer.py, learner.py) → non li ripetiamo, serve cambia |

## 🎯 Le 3 cose che contano adesso

1. **percentuale-base** — fermo da 11h. robusta -8% (media -3%) su 1909 token
2. **percentuale-robinhood** — fermo da 10h. robusta -26% (media -17%) su 45 token
3. **percentuale-bsc** — fermo da 8h. robusta -24% (media -21%) su 604 token

> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.
> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).
> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md.