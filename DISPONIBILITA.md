# ⏱️ IL SEGNALE ERA UTILIZZABILE IN QUEL MOMENTO?
*2026-09-05 03:11 UTC · €0*

> Un risultato può essere falso in due modi che nessun raggruppamento salva: se una feature
> guarda il futuro, o se il dato ci arriva **dopo** il momento in cui avremmo dovuto agire.
> Sono due difetti diversi e servono due prove diverse.

## Prova 1 — il futuro cambia il passato?

*Le feature si calcolano due volte allo stesso istante: una con tutti i dati di oggi, una
con i soli dati fino a quell'istante. Devono venire identiche. Leggere il codice non basta:
si legge quello che si crede di aver scritto.*

> ✅ **Nessuna differenza su 47 token.** Le feature usano solo il passato:
> non è una dichiarazione del codice, è una verifica sui numeri.

## Prova 2 — quanto tardi arriva il dato a noi

*Un bot vero non può agire su una candela che non ha ancora scaricato. Questo ritardo va
aggiunto all'entrata: senza, stiamo comprando col senno di poi.*

*Nota di metodo: si legge sulla coda bassa della distribuzione. La mediana direbbe 58 ore,
ma quelle sono i token MORTI — la loro ultima candela è vecchia perché hanno smesso di essere
scambiati, non perché siamo lenti noi. Misurando così, la morte del token diventerebbe un
nostro difetto.*

| chain | ritardo tipico | quando andiamo lenti | misure |
|---|---|---|---|
| base | **204 min** | 224 min | 400 |
| bsc | **306 min** | 1689 min | 398 |
| solana | **261 min** | 1606 min | 400 |
| robinhood | **247 min** | 1520 min | 400 |

> Il ritardo tipico peggiore è di **306 minuti**. Su un memecoin che si
> muove del 5% al minuto, entrare mezz'ora dopo non è la stessa strategia: è un'altra.

> ⚠️ **Questo ritardo NON è ancora applicato nei backtest**, e la conseguenza è più grave
> di quanto sembri.

> Le nostre strategie entrano 3 o 6 ore dopo il listing. Se i dati ci arrivano con 3-7 ore
> di ritardo, un bot vero a quell'ora avrebbe in mano **quasi solo i dati del momento del
> listing**: entrerebbe alla stessa ora, ma decidendo su informazioni molto più povere.
> Non è la stessa strategia con un handicap — è una strategia diversa.

> Finché non lo applichiamo, ogni risultato va letto sapendo che stiamo decidendo con
> informazioni che al momento dell'ingresso non avremmo avuto.
