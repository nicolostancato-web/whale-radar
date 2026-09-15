# 🧫 COORTE — è morto, o non l'abbiamo guardato?
*2026-09-15 16:57 UTC · test prospettico · €0*

> L'audit aveva misurato che le serie escluse vivono 1 ora e le ammesse 23, e l'avevo
> chiamato survivorship bias. La revisione ha corretto: è una **durata osservata**, non la
> vita del token. La stessa differenza può venire da mortalità vera **oppure da buchi
> nostri**. Sono cose opposte: una è il mondo, l'altra siamo noi.

> Qui si chiede a un canale **indipendente** — la catena, non la stessa fonte delle candele —
> se il pool era vivo a +3h, e si confronta con quello che abbiamo noi.

**Osservazioni accumulate: 5453** (+50 in questo giro)

| la catena dice | noi abbiamo la candela | quanti | lettura |
|---|---|---|---|
| True | False | 3929 | 🔴 **buco nostro** |
| True | True | 591 | 🟢 copertura funzionante |
| None | True | 574 | ❓ non so |
| None | False | 276 | ❓ non so (contratto muto) |
| False | False | 69 | ⚫ mortalità vera |
| False | True | 14 | ⚠️ incoerente |

> Fra i casi in cui **non abbiamo la candela** e la catena ha risposto: **3929 su 3998** erano ancora vivi — cioè **buchi nostri**, non morti.

> ⚠️ **Cosa vuol dire «vivo» qui, per non farsi illusioni.** Vivo = il contratto risponde
> con riserve non nulle. Non vuol dire che qualcuno lo stia scambiando, né che sia
> vendibile: un pool può avere riserve e nessuno scambio. Quindi un «buco nostro» dice che
> **il pool esisteva ancora**, non che valesse la pena guardarlo. È comunque la distinzione
> che serviva: dice che non l'abbiamo guardato, non che era morto.

> **Limite dichiarato**: su Solana non abbiamo un RPC pubblico, quindi il confronto userebbe
> la stessa fonte delle candele. Non lo facciamo: un test che si conferma da solo non è un
> test. Solana resta non giudicabile su questa domanda.

> **Questo test non si può fare all'indietro**: chiede com'era il mondo a +3h da un pool
> scoperto poche ore fa. Comincia oggi e si accumula.