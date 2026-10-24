# 🔁 LOOPS — i meeting del sistema
*2026-09-17 18:25 UTC · un meeting per goal, a ogni ciclo (~30 min)*

## Architetto: 🟢 tutti i loop si stanno riunendo

| loop | la domanda | dove siamo | ago | cosa si fa |
|---|---|---|---|---|
| `accumulo-base` | Stiamo raccogliendo token Base nuovi? | 5398 token con dati (3484 osservati dal vivo, 1914 con storico) su 15202 pool noti | ⏸ fermo dall'ultimo meeting | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (pulse.py, multichain_collector.py) → non li ripetiamo, se |
| `accumulo-solana` | Stiamo raccogliendo token Solana nuovi? | 1922 token con dati (220 osservati dal vivo, 1702 con storico) su 15249 pool noti | ⏸ fermo dall'ultimo meeting | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (solana_helius.py, multichain_collector.py) → non li ripet |
| `percentuale-robinhood` | Come alziamo la percentuale su Robinhood? | robusta -22% (media -10%) su 49 token | ⏸ fermo da 6h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer.py, learner.py) → non li ripetiamo, se |
| `percentuale-base` | Come alziamo la percentuale su Base? | robusta -8% (media -4%) su 1920 token | ⏸ fermo da 37h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_base.py, learner.py) → non li ripetiam |
| `percentuale-solana` | Come alziamo la percentuale su Solana? | robusta -26% (media -24%) su 786 token | ⏸ fermo da 6h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_solana.py, wallet_insider.py) → non li |
| `demo-robinhood` | Come arriviamo a 3.000 euro su Robinhood? | 🔴 SOSPESO dal cancello — campione troppo piccolo: 49 token (ne servono 150) | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `demo-base` | Come arriviamo a 3.000 euro su Base? | 🔴 SOSPESO dal cancello — il LOOP 1 e' a **-8%** robusta, sotto la soglia di **+40%**: andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `accumulo-robinhood` | Stiamo raccogliendo token Robinhood nuovi? | 3914 token con dati (340 osservati dal vivo, 3574 con storico) su 20339 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-bsc` | Stiamo raccogliendo token BSC nuovi? | 1135 token con dati (323 osservati dal vivo, 812 con storico) su 17541 pool noti | ⏸ fermo da 6h | 🚨 fermo da 6h e la scala e' finita: serve una decisione umana |
| `percentuale-bsc` | Come alziamo la percentuale su BSC? | robusta -24% (media -21%) su 605 token | ⏸ fermo da 34h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (explorer.py, learner.py) → non li ripetiamo, serve cambia |

## 🎯 Le 3 cose che contano adesso

1. **percentuale-base** — fermo da 37h. robusta -8% (media -4%) su 1920 token
2. **percentuale-bsc** — fermo da 34h. robusta -24% (media -21%) su 605 token
3. **percentuale-robinhood** — fermo da 6h. robusta -22% (media -10%) su 49 token

> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.
> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).
> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md.