# 🔁 LOOPS — i meeting del sistema
*2026-09-05 22:56 UTC · un meeting per goal, a ogni ciclo (~30 min)*

## Architetto: 🟢 tutti i loop si stanno riunendo

| loop | la domanda | dove siamo | ago | cosa si fa |
|---|---|---|---|---|
| `accumulo-base` | Stiamo raccogliendo token Base nuovi? | 5086 token con dati (2368 osservati dal vivo, 2718 con storico) su 16102 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-solana` | Stiamo raccogliendo token Solana nuovi? | 1362 token con dati (137 osservati dal vivo, 1225 con storico) su 14813 pool noti | 📈 si muove | avanti cosi' |
| `percentuale-robinhood` | Come alziamo la percentuale su Robinhood? | robusta -20% (media +17%) su 77 token | ⏸ fermo da 1h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer.py, learner.py) → non li ripetiamo, se |
| `percentuale-base` | Come alziamo la percentuale su Base? | robusta +0% (media +3%) su 1146 token | ⏸ fermo da 6h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_base.py, learner.py) → non li ripetiam |
| `percentuale-solana` | Come alziamo la percentuale su Solana? | robusta -13% (media -9%) su 712 token | ⏸ fermo da 1h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_solana.py, wallet_insider.py) → non li |
| `demo-robinhood` | Come arriviamo a 3.000 euro su Robinhood? | 🔴 SOSPESO dal cancello — campione troppo piccolo: 77 token (ne servono 150) | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `demo-base` | Come arriviamo a 3.000 euro su Base? | 🔴 SOSPESO dal cancello — il LOOP 1 e' a **+0%** robusta, sotto la soglia di **+40%**: andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `accumulo-robinhood` | Stiamo raccogliendo token Robinhood nuovi? | 957 token con dati (0 osservati dal vivo, 957 con storico) su 17422 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-bsc` | Stiamo raccogliendo token BSC nuovi? | 1246 token con dati (150 osservati dal vivo, 1096 con storico) su 17605 pool noti | 📈 si muove | avanti cosi' |
| `percentuale-bsc` | Come alziamo la percentuale su BSC? | robusta -24% (media -21%) su 583 token | ⏸ fermo da 31h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (explorer.py, learner.py) → non li ripetiamo, serve cambia |

## 🎯 Le 3 cose che contano adesso

1. **percentuale-bsc** — fermo da 31h. robusta -24% (media -21%) su 583 token
2. **percentuale-base** — fermo da 6h. robusta +0% (media +3%) su 1146 token
3. **percentuale-robinhood** — fermo da 1h. robusta -20% (media +17%) su 77 token

> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.
> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).
> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md.