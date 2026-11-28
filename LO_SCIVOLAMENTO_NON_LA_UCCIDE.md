# Lo scivolamento misurato: non uccide la regola — 8 ottobre 2026

Era la voce che ha ucciso il progetto precedente su Solana, e l'unica non misurata della regola che
regge. Adesso è misurata.

## Quanto costa muovere i soldi, misurato su 412.000 scambi in 60 pool

Metodo: per ogni scambio eseguito, il suo prezzo contro la mediana dei 5 scambi precedenti. Non è
una formula: è quanto ha pagato chi ha scambiato davvero quella cifra in quel pool.

| dimensione dello scambio | impatto mediano | 75° | 90° |
|---|---|---|---|
| 0-25 $ | **0,69%** | 2,04% | 4,56% |
| 25-75 $ | **1,04%** | 2,55% | 5,23% |
| 75-300 $ | **1,71%** | 3,65% | 6,88% |
| 300-1.200 $ | **2,94%** | 5,50% | 9,60% |
| 1.200-5.000 $ | 5,61% | 8,83% | 13,95% |
| oltre 5.000 $ | **13,00%** | 21,02% | 33,69% |

## La regola, con lo scivolamento dentro

«Compro a fine primo minuto dopo il diploma, vendo al raddoppio» — 330 monete, costi 1% + 1% e
scivolamento in entrata **e** in uscita:

| se metto | medio per moneta | mediano | vinte |
|---|---|---|---|
| **50 $** | **+16,7%** | +92,1% | 194/330 |
| **200 $** | **+15,2%** | +89,5% | 194/330 |
| 1.000 $ | +12,4% | +85,0% | 194/330 |
| 5.000 $ | +6,8% | +75,8% | 194/330 |

E nel **caso brutto** (impatto al 90° percentile invece del mediano):

| se metto | medio |
|---|---|
| 50 $ | **+7,6%** |
| 200 $ | **+4,3%** |
| 1.000 $ | **−0,8%** |
| 5.000 $ | **−8,3%** |

## Cosa significa, detto senza entusiasmo

**Alla scala di 50-200 € per moneta la regola sopravvive anche nel caso brutto.** A 1.000 € nel
caso brutto va a zero, a 5.000 € muore. Quindi non è una strategia che scala: è una strategia da
scommesse piccole e numerose, ed è esattamente la scala di Nicolò.

**La differenza col progetto precedente è questa.** Su Solana lo scivolamento mangiava tutto il
margine e il progetto è morto lì. Qui l'ho misurato e il margine resta — *misurato*, non sperato.

## Cosa manca ancora, e non è poco

1. **Lo scivolamento misurato è quello che hanno pagato gli altri**, non il nostro: noi entriamo in
   un momento preciso (fine del primo minuto) che potrebbe essere peggiore della media.
2. **Le transazioni che non passano**: gas, blocco perso, vendita respinta. A zero nei conti, non a
   zero nella realtà.
3. **La prova in avanti.** Tutto questo è storia. La regola va provata su monete che si diplomano
   **da adesso**, con soldi finti, e il risultato va confrontato con questi numeri.

Il punto 3 è il prossimo lavoro, e fino a quel momento **zero euro impegnati**.
