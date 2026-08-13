# 📊 REPORT FASE 2 — whale-radar (2026-08-13)

**Metodo:** double-double deep-search (AI scrive il prompt → AI interpreta i dati reali).
**Dataset:** 2.982 balene misurabili, 100 token, 1.239 wallet.
**Metrica:** equal-weight per token, survivorship-corretta, netta di slippage.

## VERDETTO: ❌ NESSUN EDGE (confidenza media)

Seguire le balene alla cieca (entra 1h dopo, tieni, esci) **distrugge capitale** a ogni orizzonte credibile.

| Orizzonte | Token | Media/token | Token positivi | Note |
|---|---|---|---|---|
| 24h | 92 | **−33,7%** | 8% | campione valido → no edge |
| 72h | 81 | **−25,3%** | 9% | campione valido → no edge |
| 168h | 22 | +32,7% | 40% | **artefatto** (22 token, senza top3 → +4,6%) |

## I 3 segnali interpretati
1. **Naive (segui la balena):** nessun edge. Negativo netto su campioni ampi e validi. Il +33% a 7 giorni è un miraggio da pochi token concentrati.
2. **Smart-money INVERTITO:** i wallet "bravi" nella 1ª metà → −1,1% dopo; gli "scarsi" → **+25,7%**. È **anti-persistenza**: il segnale "segui la balena" è così debole che il suo **opposto** funziona meglio out-of-sample → potrebbe essere un **FADE signal** (fare il contrario). Ma campione ancora piccolo (63 token).
3. **Dimensione $10-30k:** buy medi = **−1,1%** (quasi in pari) vs −25,3% dei piccoli. Anomalia interessante ma fragile (22 token, 7 positivi → potrebbe essere rumore).

## DECISIONE: 🔁 TORNARE IN FASE 1
Non c'è edge dal naive, ma ci sono **2 piste vere** (fade + size) troppo poco campionate per fidarsi. Servono più dati:
1. Espandere a **300-500 token** per potere statistico
2. Serie temporale wallet lunga per un **walk-forward rigoroso** dell'inversione smart-money (200+ token)
3. Validare la fascia **$10-30k** con 100-150 osservazioni per token

## PROSSIME 3 ANALISI (quando avremo i dati)
1. **Walk-forward out-of-sample dell'inversione smart-money** (300 token, 500+ wallet, finestre multiple)
2. **Backtest dedicato della fascia $10-30k** (>100 token) per confermare/respingere l'anomalia
3. **Decomposizione rendimento per ora/giorno** (>300 token) per escludere un timing sistematicamente sfavorevole

---
**In una riga:** il "segui la balena" è morto, MA abbiamo scoperto due indizi promettenti — *forse va fatto il CONTRARIO (fade)* e *la size $10-30k conta*. Servono più dati per dire se sono oro o rumore. → Fase 1, spingere fino a 300-500 token, poi ri-testare.

---
## ⚠️ REQUISITO FASE 2 (Nicolò, 13/08): incrociare il DATABASE FORENSE
Quando si torna in Fase 2, l'analisi NON deve guardare solo il rendimento delle balene, ma incrociare
`data/raw/forensics/` (funding-graph, EOA origine per wallet):
1. Raggruppare i wallet per ENTITÀ-origine (stessa fonte di capitale, oltre i contratti-bridge).
2. Testare la strategia "segui l'ENTITÀ" (tutte le sue sub-wallet) invece del singolo wallet.
3. Usare l'origine come FEATURE: i wallet finanziati da certe entità rendono di più? le sub-wallet della
   stessa entità comprano gli stessi token insieme (segnale anticipato)?
Il database forense e le metriche di rendimento vanno uniti nella stessa analisi.

---
## 🕵️ REQUISITO FASE 2 (Nicolò, 13/08): CACCIA AGLI INSIDER
I wallet piccoli vincenti potrebbero essere INSIDER (l'insider crypto non viene beccato; entra piccolo per non
farsi notare, da un wallet grosso, ed esce grosso — ripetuto). In Fase 2 costruire uno **SCORE INSIDER** per wallet:
1. Entry piccola ($2-10k) ma return outsized (5x-20x)
2. Entra PRIMA del pump/volume-spike (ha informazione) — ts buy vs partenza volume
3. RIPETUTO su piu' token diversi (non fortuna)
4. FINANZIATO da wallet/entita' piu' grande (dal database forense)
5. Early buyer / vicino al lancio del token
I wallet con score alto = candidati insider da SEGUIRE. Unire con il database forense.
