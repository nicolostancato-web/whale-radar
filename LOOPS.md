# 🔁 LOOPS — i meeting del sistema
*2026-09-12 13:50 UTC · un meeting per goal, a ogni ciclo (~30 min)*

## Architetto: 🟢 tutti i loop si stanno riunendo

| loop | la domanda | dove siamo | ago | cosa si fa |
|---|---|---|---|---|
| `accumulo-base` | Stiamo raccogliendo token Base nuovi? | 4280 token con dati (2919 osservati dal vivo, 1361 con storico) su 14669 pool noti | ⏸ fermo da 2h | 🚨 fermo da 2h e la scala e' finita: serve una decisione umana |
| `accumulo-solana` | Stiamo raccogliendo token Solana nuovi? | 1283 token con dati (180 osservati dal vivo, 1103 con storico) su 14670 pool noti | ⏸ fermo dall'ultimo meeting | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (solana_helius.py, multichain_collector.py) → non li ripet |
| `percentuale-robinhood` | Come alziamo la percentuale su Robinhood? | robusta -26% (media -16%) su 44 token | ⏸ fermo da 1h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer.py, learner.py) → non li ripetiamo, se |
| `percentuale-base` | Come alziamo la percentuale su Base? | robusta -4% (media -0%) su 1689 token | ⏸ fermo da 13h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_base.py, learner.py) → non li ripetiam |
| `percentuale-solana` | Come alziamo la percentuale su Solana? | robusta -21% (media -18%) su 743 token | ⏸ fermo da 2h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_solana.py, wallet_insider.py) → non li |
| `demo-robinhood` | Come arriviamo a 3.000 euro su Robinhood? | 🔴 SOSPESO dal cancello — campione troppo piccolo: 44 token (ne servono 150) | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `demo-base` | Come arriviamo a 3.000 euro su Base? | 🔴 SOSPESO dal cancello — il LOOP 1 e' a **-4%** robusta, sotto la soglia di **+40%**: andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `accumulo-robinhood` | Stiamo raccogliendo token Robinhood nuovi? | 2651 token con dati (118 osservati dal vivo, 2533 con storico) su 19240 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-bsc` | Stiamo raccogliendo token BSC nuovi? | 1065 token con dati (262 osservati dal vivo, 803 con storico) su 17457 pool noti | 📈 si muove | avanti cosi' |
| `percentuale-bsc` | Come alziamo la percentuale su BSC? | robusta -24% (media -21%) su 600 token | ⏸ fermo da 24h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (explorer.py, learner.py) → non li ripetiamo, serve cambia |

## 🎯 Le 3 cose che contano adesso

1. **percentuale-bsc** — fermo da 24h. robusta -24% (media -21%) su 600 token
2. **percentuale-base** — fermo da 13h. robusta -4% (media -0%) su 1689 token
3. **percentuale-solana** — fermo da 2h. robusta -21% (media -18%) su 743 token

> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.
> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).
> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md.