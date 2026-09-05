# 📈 QUANTO COSTA USCIRE, SECONDO QUANTO E' LIQUIDO IL TOKEN
*2026-09-05 10:53 UTC · 1158 osservazioni (token con **sia** una misura vera su Jupiter **sia** le nostre candele) · €0*

> Un costo costante è comodo e sbagliato. Su un pool che gira 50.000 dollari l'ora, uscire
> con 25 dollari non si sente. Sullo stesso token quando il volume è crollato a 200, quei
> 25 dollari sono metà del mercato — **e lo stop scatta proprio lì, mai nel primo caso.**

| la posizione è, del volume orario | costo andata+ritorno | nei casi peggiori | osservazioni |
|---|---|---|---|
| 0.00% – 0.37% | **2.7%** | 3.5% | 193 |
| 0.38% – 1.42% | **2.8%** | 4.0% | 193 |
| 1.43% – 4.77% | **2.7%** | 5.1% | 193 |
| 4.81% – 21.57% | **4.2%** | 8.7% | 193 |
| 21.60% – 305.24% | **6.8%** | 11.4% | 193 |
| 312.21% – 43611241.41% | **10.1%** | 25.9% | 193 |

## Cosa dicono i dati

> ✅ **La relazione c'è.** Passando dai token più liquidi ai più sottili il costo di uscita
> si moltiplica per **3.7**. Non è più un'assunzione: è misurato, e il backtest può
> usare la curva invece di una costante.

> Il punto pratico: **lo stop scatta quando il volume è crollato**, cioè nella fascia più
> cara. Un backtest che applica il costo medio a quell'uscita sta dichiarando un prezzo
> che non avresti pagato.

> Nota: le trappole (costo ≥ 50%) sono escluse. Non sono un costo alto: sono una perdita
> totale, e vanno contate a parte — mescolarle qui rifarebbe l'errore del costo medio.