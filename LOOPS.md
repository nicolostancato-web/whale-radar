# 🔁 LOOPS — i meeting del sistema
*2026-09-05 16:28 UTC · un meeting per goal, a ogni ciclo (~30 min)*

## Architetto: 🟢 tutti i loop si stanno riunendo

| loop | la domanda | dove siamo | ago | cosa si fa |
|---|---|---|---|---|
| `accumulo-base` | Stiamo raccogliendo token Base nuovi? | 4868 token con dati (2316 osservati dal vivo, 2552 con storico) su 15939 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-solana` | Stiamo raccogliendo token Solana nuovi? | 1275 token con dati (132 osservati dal vivo, 1143 con storico) su 14754 pool noti | 📈 si muove | avanti cosi' |
| `percentuale-robinhood` | Come alziamo la percentuale su Robinhood? | robusta -19% (media +24%) su 60 token | ⏸ fermo da 2h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer.py, learner.py) → non li ripetiamo, se |
| `percentuale-base` | Come alziamo la percentuale su Base? | robusta +1% (media +4%) su 1142 token | ⏸ fermo da 2h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_base.py, learner.py) → non li ripetiam |
| `percentuale-solana` | Come alziamo la percentuale su Solana? | robusta -13% (media -9%) su 707 token | ⏸ fermo da 2h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_solana.py, wallet_insider.py) → non li |
| `demo-robinhood` | Come arriviamo a 3.000 euro su Robinhood? | 🔴 SOSPESO dal cancello — campione troppo piccolo: 60 token (ne servono 150) | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `demo-base` | Come arriviamo a 3.000 euro su Base? | 🔴 SOSPESO dal cancello — il LOOP 1 e' a **+1%** robusta, sotto la soglia di **+40%**: andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `accumulo-robinhood` | Stiamo raccogliendo token Robinhood nuovi? | 873 token con dati (0 osservati dal vivo, 873 con storico) su 17382 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-bsc` | Stiamo raccogliendo token BSC nuovi? | 1181 token con dati (147 osservati dal vivo, 1034 con storico) su 17545 pool noti | 📈 si muove | avanti cosi' |
| `percentuale-bsc` | Come alziamo la percentuale su BSC? | robusta -24% (media -21%) su 582 token | ⏸ fermo da 27h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (explorer.py, learner.py) → non li ripetiamo, serve cambia |

## 🎯 Le 3 cose che contano adesso

1. **percentuale-bsc** — fermo da 27h. robusta -24% (media -21%) su 582 token
2. **percentuale-robinhood** — fermo da 2h. robusta -19% (media +24%) su 60 token
3. **percentuale-solana** — fermo da 2h. robusta -13% (media -9%) su 707 token

> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.
> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).
> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md.