# 🔁 LOOPS — i meeting del sistema
*2026-09-12 05:23 UTC · un meeting per goal, a ogni ciclo (~30 min)*

## Architetto: 🟢 tutti i loop si stanno riunendo

| loop | la domanda | dove siamo | ago | cosa si fa |
|---|---|---|---|---|
| `accumulo-base` | Stiamo raccogliendo token Base nuovi? | 4242 token con dati (2903 osservati dal vivo, 1339 con storico) su 14629 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-solana` | Stiamo raccogliendo token Solana nuovi? | 1239 token con dati (176 osservati dal vivo, 1063 con storico) su 14630 pool noti | ⏸ fermo da 4h | 🚨 fermo da 4h e la scala e' finita: serve una decisione umana |
| `percentuale-robinhood` | Come alziamo la percentuale su Robinhood? | robusta -25% (media -16%) su 44 token | ⏸ fermo da 7h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer.py, learner.py) → non li ripetiamo, se |
| `percentuale-base` | Come alziamo la percentuale su Base? | robusta -3% (media +2%) su 1688 token | ⏸ fermo da 7h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_base.py, learner.py) → non li ripetiam |
| `percentuale-solana` | Come alziamo la percentuale su Solana? | robusta -21% (media -18%) su 752 token | ⏸ fermo da 3h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (strategy_optimizer_solana.py, wallet_insider.py) → non li |
| `demo-robinhood` | Come arriviamo a 3.000 euro su Robinhood? | 🔴 SOSPESO dal cancello — campione troppo piccolo: 44 token (ne servono 150) | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `demo-base` | Come arriviamo a 3.000 euro su Base? | 🔴 SOSPESO dal cancello — il LOOP 1 e' a **-3%** robusta, sotto la soglia di **+40%**: andare live vorrebbe dire attuare una strategia che sappiamo gia' non pagare | 📈 si muove | ⏸ il cancello è chiuso: prima il LOOP 1 deve alzare la percentuale |
| `accumulo-robinhood` | Stiamo raccogliendo token Robinhood nuovi? | 2377 token con dati (115 osservati dal vivo, 2262 con storico) su 18941 pool noti | 📈 si muove | avanti cosi' |
| `accumulo-bsc` | Stiamo raccogliendo token BSC nuovi? | 1027 token con dati (246 osservati dal vivo, 781 con storico) su 17417 pool noti | ⏸ fermo da 5h | 🚨 fermo da 5h e la scala e' finita: serve una decisione umana |
| `percentuale-bsc` | Come alziamo la percentuale su BSC? | robusta -24% (media -21%) su 600 token | ⏸ fermo da 18h | ✋ mano alzata: tutti i rimedi noti hanno gia' fallito 3 volte (explorer.py, learner.py) → non li ripetiamo, serve cambia |

## 🎯 Le 3 cose che contano adesso

1. **percentuale-bsc** — fermo da 18h. robusta -24% (media -21%) su 600 token
2. **percentuale-robinhood** — fermo da 7h. robusta -25% (media -16%) su 44 token
3. **percentuale-base** — fermo da 7h. robusta -3% (media +2%) su 1688 token

> Come si legge: ogni riga e' una riunione. Se l'ago non si muove qualcuno alza la mano e si ripara.
> Se resta fermo troppo a lungo non si insiste: si cambia approccio (la scala e' scritta in data/loops.json).
> Le RIPARAZIONI sono automatiche. Le DECISIONI (soglie, strategia) restano umane: passano da DECISIONS.md.