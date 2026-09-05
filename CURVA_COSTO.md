# 📈 QUANTO COSTA USCIRE, SECONDO QUANTO E' LIQUIDO IL TOKEN
*2026-09-05 00:01 UTC · 1150 osservazioni (token con **sia** una misura vera su Jupiter **sia** le nostre candele) · €0*

> Un costo costante è comodo e sbagliato. Su un pool che gira 50.000 dollari l'ora, uscire
> con 25 dollari non si sente. Sullo stesso token quando il volume è crollato a 200, quei
> 25 dollari sono metà del mercato — **e lo stop scatta proprio lì, mai nel primo caso.**

| la posizione è, del volume orario | costo andata+ritorno | nei casi peggiori | osservazioni |
|---|---|---|---|
| 0.00% – 0.34% | **2.7%** | 3.5% | 191 |
| 0.34% – 1.35% | **2.8%** | 4.0% | 191 |
| 1.36% – 4.46% | **3.2%** | 5.5% | 191 |
| 4.47% – 18.44% | **4.2%** | 8.6% | 191 |
| 18.82% – 288.81% | **6.2%** | 10.7% | 191 |
| 288.93% – 4172381.72% | **9.9%** | 25.8% | 191 |

## Cosa dicono i dati

> ✅ **La relazione c'è.** Passando dai token più liquidi ai più sottili il costo di uscita
> si moltiplica per **3.7**. Non è più un'assunzione: è misurato, e il backtest può
> usare la curva invece di una costante.

> Il punto pratico: **lo stop scatta quando il volume è crollato**, cioè nella fascia più
> cara. Un backtest che applica il costo medio a quell'uscita sta dichiarando un prezzo
> che non avresti pagato.

> Nota: le trappole (costo ≥ 50%) sono escluse. Non sono un costo alto: sono una perdita
> totale, e vanno contate a parte — mescolarle qui rifarebbe l'errore del costo medio.