# ⚖️ IL COSTO VERO — mettere d'accordo misura e modello
*2026-09-05 17:19 UTC · 1094 token misurati su Jupiter · €0*

> **Il problema**: diciamo di aver misurato il costo, e poi nei conti ne usiamo un altro,
> **33%**. Finché le due cose non si parlano, «tutte le chain sono negative»
> non è una scoperta: è un'assunzione travestita da risultato.

> **La correzione non è abbassare il 33% al 4%.** Sono due domande diverse, e mescolarle è
> l'errore: *si può uscire?* è una perdita totale, *quanto costa uscire?* è una percentuale.
> Un costo medio le fonde male — punisce ogni trade con un pezzo del disastro altrui, e
> insieme sottostima il disastro vero.

| se metti | **trappole** (non esci, o esci con nulla) | costo quando esci davvero | peggiori | pareggio |
|---|---|---|---|---|
| $25 | **24%** (267/1094) | **4.0%** | 5% | 1.04x |
| $100 | **26%** (285/1078) | **8.2%** | 10% | 1.09x |
| $500 | **31%** (326/1058) | **25.7%** | 30% | 1.35x |

| *quello che usiamo oggi nei conti* | *non modellato* | *33%* | — | *1.50x* |

## Cosa cambia davvero

A **$25**, quando si esce davvero, costa **4.0%** — molto meno del 33% che assumiamo.
Ma **24%** dei token è una **trappola**: o non c'è uscita, o l'uscita restituisce nulla.
Quella non è una percentuale di costo: è tutto il capitale.

Messe insieme: un trade che riesce deve fare almeno **1.38x** perché il gruppo
vada in pari. **Non 1.50x, e nemmeno 1.04x.**

> La taglia conta più di quanto pensassimo: passare da $25 a $100 raddoppia il costo di uscita.
> Se una strategia funziona, funziona **piccola**.

## Proposta aperta

> Sostituire nel backtest il costo unico con le due macchine separate: probabilità di non
> uscire (perdita totale) + costo misurato sui casi in cui si esce.
> **Non lo cambio da solo**: è il metro con cui giudichiamo ogni cosa, e cambiarlo di nascosto
> rifarebbe tutti i numeri senza che nessuno abbia deciso niente.

> Nota onesta: le quote sono indicative, prese su token vivi in un momento di calma. Non dicono
> quanto costerebbe uscire durante un crollo — che è esattamente quando si vuole uscire.