# 📈 QUANTO COSTA USCIRE, SECONDO QUANTO E' LIQUIDO IL TOKEN
*2026-09-12 07:48 UTC · 95 osservazioni (misure con il volume dell'ORA in cui sono state prese, non la mediana storica) · €0*

> Un costo costante è comodo e sbagliato. Su un pool che gira 50.000 dollari l'ora, uscire
> con 25 dollari non si sente. Sullo stesso token quando il volume è crollato a 200, quei
> 25 dollari sono metà del mercato — **e lo stop scatta proprio lì, mai nel primo caso.**

| la posizione è, del volume orario | costo andata+ritorno | nei casi peggiori | osservazioni |
|---|---|---|---|
| 0.02% – 0.27% | **2.6%** | 3.0% | 15 |
| 0.31% – 2.28% | **4.2%** | 5.9% | 15 |
| 3.37% – 22.81% | **4.2%** | 8.6% | 15 |
| 33.26% – 166.30% | **5.7%** | 10.5% | 15 |
| 192.23% – 4978.89% | **5.5%** | 16.8% | 15 |
| 5735.83% – 81196.73% | **9.3%** | 16.0% | 15 |

## Cosa dicono i dati

> ✅ **La relazione c'è.** Passando dai token più liquidi ai più sottili il costo di uscita
> si moltiplica per **3.6**. Non è più un'assunzione: è misurato, e il backtest può
> usare la curva invece di una costante.

> Il punto pratico: **lo stop scatta quando il volume è crollato**, cioè nella fascia più
> cara. Un backtest che applica il costo medio a quell'uscita sta dichiarando un prezzo
> che non avresti pagato.

## ⚠️ Cosa questa curva NON misura (dichiarato, non nascosto)

Tre limiti, e il terzo non è correggibile con i dati che abbiamo:

1. **È calibrata in condizioni di mercato calme**, su token vivi. Le quote sono state prese
   in momenti qualunque, non durante una fuga.
2. **Il volume scambiato è un surrogato della profondità**, non la profondità. Sono due cose
   diverse.
3. **Durante un crollo il volume ESPLODE mentre la profondità evapora.** Quindi proprio nel
   momento peggiore la formula assegna la fascia più *economica*: il surrogato ha il segno
   rovesciato dove conta di più. Il caso peggiore usato in fuga è un cerotto, non una cura.

> **I costi di fuga vanno letti come limite inferiore ottimistico, non come stima.**
> Lo stato di panico non è mai stato campionato, quindi questa curva non può contenerlo.
> Per misurarlo davvero servono quote prese DURANTE un crollo — ed è esattamente quello che
> fa `costo_fuga.py` quando un paper trade tocca lo stop. Quei dati, quando ci saranno,
> sostituiranno questa estrapolazione.

> Nota sul campione: si usano solo le misure per cui esiste una candela nell'ora in cui sono
> state prese. Sono meno (95 contro le oltre mille grezze), ma sono le uniche in cui
> calibrazione e applicazione guardano la stessa grandezza. **Meno punti giusti battono più
> punti sbagliati.**

> Nota: le trappole (costo ≥ 50%) sono escluse. Non sono un costo alto: sono una perdita
> totale, e vanno contate a parte — mescolarle qui rifarebbe l'errore del costo medio.