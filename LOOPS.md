# 🔁 LOOPS — i meeting del sistema
*2026-09-05 20:19 UTC · un meeting per goal, a ogni ciclo (~30 min)*

## Architetto: 🟢 tutti i loop si stanno riunendo

| loop | la domanda | dove siamo | ago | cosa si fa |
|---|---|---|---|---|
| `accumulo-base` | Stiamo raccogliendo token Base nuovi? | 5003 token con dati (2349 osservati dal vivo, 2654 con storico) su 16039 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-solana` | Stiamo raccogliendo token Solana nuovi? | 1329 token con dati (134 osservati dal vivo, 1195 con storico) su 14773 pool noti | 📈 si muove | avanti cosi' |
| `percentuale-robinhood` | Come alziamo la percentuale su Robinhood? | robusta -20% (media +23%) su 59 token | ⏸ fermo da 4h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer.py, learner.py) → non li ripetiamo, se |
| `percentuale-base` | Come alziamo la percentuale su Base? | robusta +1% (media +4%) su 1139 token | ⏸ fermo da 4h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_base.py, learner.py) → non li ripetiam |
| `percentuale-solana` | Come alziamo la percentuale su Solana? | robusta -13% (media -9%) su 708 token | ⏸ fermo da 4h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_solana.py, wallet_insider.py) → non li |
| `demo-robinhood` | Come arriviamo a 3.000 euro su Robinhood? | 🔴 SOSPESO dal cancello — campione troppo piccolo: 59 token (ne servono 150) | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `demo-base` | Come arriviamo a 3.000 euro su Base? | 🔴 SOSPESO dal cancello — il LOOP 1 e' a **+1%** robusta, sotto la soglia di **+40%**: andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `accumulo-robinhood` | Stiamo raccogliendo token Robinhood nuovi? | 925 token con dati (0 osservati dal vivo, 925 con storico) su 17402 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-bsc` | Stiamo raccogliendo token BSC nuovi? | 1231 token con dati (149 osservati dal vivo, 1082 con storico) su 17565 pool noti | 📈 si muove | avanti cosi' |
| `percentuale-bsc` | Come alziamo la percentuale su BSC? | robusta -24% (media -21%) su 583 token | ⏸ fermo da 30h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (explorer.py, learner.py) → non li ripetiamo, serve cambia |

## 🎯 Le 3 cose che contano adesso

1. **percentuale-bsc** — fermo da 30h. robusta -24% (media -21%) su 583 token
2. **percentuale-robinhood** — fermo da 4h. robusta -20% (media +23%) su 59 token
3. **percentuale-solana** — fermo da 4h. robusta -13% (media -9%) su 708 token

> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.
> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).
> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md.