# 🔁 LOOPS — i meeting del sistema
*2026-09-15 10:26 UTC · un meeting per goal, a ogni ciclo (~30 min)*

## Architetto: 🟢 tutti i loop si stanno riunendo

| loop | la domanda | dove siamo | ago | cosa si fa |
|---|---|---|---|---|
| `accumulo-base` | Stiamo raccogliendo token Base nuovi? | 5275 token con dati (3270 osservati dal vivo, 2005 con storico) su 15293 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-solana` | Stiamo raccogliendo token Solana nuovi? | 1970 token con dati (196 osservati dal vivo, 1774 con storico) su 15325 pool noti | ⏸ fermo da 1h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (solana_helius.py, multichain_collector.py) → non li ripet |
| `percentuale-robinhood` | Come alziamo la percentuale su Robinhood? | robusta -26% (media -17%) su 45 token | ⏸ fermo da 2h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer.py, learner.py) → non li ripetiamo, se |
| `percentuale-base` | Come alziamo la percentuale su Base? | robusta -8% (media -3%) su 1711 token | ⏸ fermo da 4h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_base.py, learner.py) → non li ripetiam |
| `percentuale-solana` | Come alziamo la percentuale su Solana? | robusta -26% (media -24%) su 761 token | ⏸ fermo da 44h | 🚨 fermo da 44h e la scala e' finita: serve una decisione umana |
| `demo-robinhood` | Come arriviamo a 3.000 euro su Robinhood? | 🔴 SOSPESO dal cancello — campione troppo piccolo: 45 token (ne servono 150) | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `demo-base` | Come arriviamo a 3.000 euro su Base? | 🔴 SOSPESO dal cancello — il LOOP 1 e' a **-8%** robusta, sotto la soglia di **+40%**: andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `accumulo-robinhood` | Stiamo raccogliendo token Robinhood nuovi? | 4821 token con dati (208 osservati dal vivo, 4613 con storico) su 21319 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-bsc` | Stiamo raccogliendo token BSC nuovi? | 1149 token con dati (291 osservati dal vivo, 858 con storico) su 17555 pool noti | ⏸ fermo da 2h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (pulse.py, multichain_collector.py, multichain_rpc.py) → n |
| `percentuale-bsc` | Come alziamo la percentuale su BSC? | robusta -24% (media -21%) su 604 token | ⏸ fermo da 1h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (explorer.py, learner.py) → non li ripetiamo, serve cambia |

## 🎯 Le 3 cose che contano adesso

1. **percentuale-solana** — fermo da 44h. robusta -26% (media -24%) su 761 token
2. **percentuale-base** — fermo da 4h. robusta -8% (media -3%) su 1711 token
3. **percentuale-robinhood** — fermo da 2h. robusta -26% (media -17%) su 45 token

> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.
> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).
> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md.