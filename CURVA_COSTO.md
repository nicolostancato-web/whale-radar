# 📈 QUANTO COSTA USCIRE, SECONDO QUANTO E' LIQUIDO IL TOKEN
*2026-09-05 03:11 UTC · 1135 osservazioni (token con **sia** una misura vera su Jupiter **sia** le nostre candele) · €0*

> Un costo costante è comodo e sbagliato. Su un pool che gira 50.000 dollari l'ora, uscire
> con 25 dollari non si sente. Sullo stesso token quando il volume è crollato a 200, quei
> 25 dollari sono metà del mercato — **e lo stop scatta proprio lì, mai nel primo caso.**

| la posizione è, del volume orario | costo andata+ritorno | nei casi peggiori | osservazioni |
|---|---|---|---|
| 0.00% – 0.35% | **2.7%** | 3.5% | 189 |
| 0.36% – 1.37% | **2.7%** | 3.9% | 189 |
| 1.37% – 4.46% | **3.2%** | 5.5% | 189 |
| 4.47% – 18.04% | **4.2%** | 8.5% | 189 |
| 18.41% – 273.57% | **6.2%** | 10.3% | 189 |
| 279.61% – 20861908.60% | **10.1%** | 25.8% | 189 |

## Cosa dicono i dati

> ✅ **La relazione c'è.** Passando dai token più liquidi ai più sottili il costo di uscita
> si moltiplica per **3.8**. Non è più un'assunzione: è misurato, e il backtest può
> usare la curva invece di una costante.

> Il punto pratico: **lo stop scatta quando il volume è crollato**, cioè nella fascia più
> cara. Un backtest che applica il costo medio a quell'uscita sta dichiarando un prezzo
> che non avresti pagato.

> Nota: le trappole (costo ≥ 50%) sono escluse. Non sono un costo alto: sono una perdita
> totale, e vanno contate a parte — mescolarle qui rifarebbe l'errore del costo medio.