# 🐦 ESPERIMENTO SOCIAL — l'attenzione su X anticipa il prezzo, o lo segue?

*avviato il 16 settembre 2026 · separato dal LOOP 1 · nessun trading, nessun capitale*

## La domanda

Quando l'attenzione su X accelera su una memecoin, quell'accelerazione contiene informazione sul
comportamento **successivo** del token — oppure arriva **dopo** che prezzo e volume si sono già
mossi, e stiamo solo leggendo il commento di un fatto già avvenuto?

Tre esiti possibili, tutti e tre utili:

| esito | significato |
|---|---|
| **SOCIAL LEADS** | l'attenzione accelera PRIMA del movimento |
| **SOCIAL FOLLOWS** | il movimento c'è già, X lo commenta |
| **RUMORE** | nessuna relazione stabile |

Questa distinzione conta più del rendimento medio: **un segnale che segue non è un segnale.**

## Cosa NON è

Non compra niente. Non tocca il LOOP 1, non ne legge le configurazioni e non ne cambia le
conclusioni. Non chiede a Grok «quale coin salirà»: chiede **evidenza osservabile** — menzioni,
account distinti, quando l'accelerazione sembra iniziata, se c'è odore di spam — e la registra
così com'è, `null` compreso.

## Le tre regole che rendono valido l'esperimento

**1. Gli snapshot sono immutabili.** Ogni rilevazione è un file nuovo che nessuno riscrive mai, con
dentro la risposta grezza, la versione del prompt e l'identificativo del giro. La tentazione di
«sistemare» uno snapshot dopo aver visto com'è andata non è un rischio teorico: è il modo normale
in cui un risultato falso viene costruito da persone oneste.

**2. Nessuno sguardo al futuro.** I token sono scelti solo con ciò che si sapeva al momento della
chiamata. Gli esiti li misura un agente diverso, che scrive in un file diverso e **non ha il
permesso** di toccare uno snapshot.

**3. C'è un gruppo di controllo.** Token comparabili dello stesso periodo che Grok non ha segnalato,
scelti in modo deterministico dall'identificativo del giro — riproducibile da chiunque — e misurati
con **lo stesso strumento, le stesse finestre, la stessa fonte prezzi**. Senza controllo, un +30%
medio non direbbe niente: non sapremmo cosa avrebbe fatto un memecoin qualunque nelle stesse ore.

## Come funziona

```
Grok/X  ->  snapshot immutabile  ->  prezzi point-in-time  ->  esiti futuri  ->  analisi
```

Finestre misurate dall'istante dello snapshot: **T+5m, T+30m, T+1h, T+6h, T+24h**.
Una finestra misurata troppo tardi non viene aggiustata: viene marcata **PERSA**. Una finestra
mancante taciuta diventa, mesi dopo, una media calcolata solo sui sopravvissuti.

## Costo — verificato e poi misurato

| | |
|---|---|
| stima dalle fonti ufficiali xAI (16/09) | ~$0,07 a rilevazione |
| **misurato sulla prima chiamata vera** | **$0,0606**, cinque chiamate X |
| tre rilevazioni al giorno | ~$0,18/giorno ≈ **€6,70/mese** con IVA |

> ⚠️ **Dal 21 settembre, 12:00 PT**, X Search passa da **$5 per 1.000 chiamate** a **$5 per 1.000
> post recuperati** (+ $10 per 1.000 profili). Con la stessa cadenza il costo passerebbe a
> **~€107/mese**. Questo pilota esiste per arrivare a quella data con i numeri veri in mano invece
> che con una stima.

## Registro delle decisioni

| data | cosa è cambiato | perché | impatto sul test |
|---|---|---|---|
| 16/09/2026 | esperimento avviato, prompt `v1-2026-09-16`, 3 rilevazioni/giorno | sfruttare la finestra di prezzo prima del 21/09 | nessuno: è l'inizio |
| 16/09/2026 | cadenza autoregolata sull'orologio dei fatti invece che su tre cron | GitHub salta i cron quando il repo è occupato; oggi è già costato 5 ore su un'altra corsia | un giro saltato **sposta** la rilevazione, non la salta |
| 16/09/2026 | gruppo di controllo da `new_pools` Solana, deterministico dal run_id | senza controllo un rendimento non è una risposta | rende confrontabile il risultato |
| 16/09/2026 | risoluzione simbolo→contratto con regola dichiarata prima (simbolo esatto, pool con più liquidità allo snapshot) + marchio «scelta fragile» | Grok dà il simbolo e quasi mai il contratto; un simbolo non identifica un token (TRAINCAT: 20 pool, GIGADOG: 15) | senza, **nessun esito era misurabile**; la fragilità dichiarata permette di scartare i casi ambigui |
| 16/09/2026 | ritmo tenuto dall'interno del giro invece che da cron ogni 10 min | in 33 minuti il cron non è scattato **nemmeno una volta** | senza, la finestra T+5m sarebbe stata marcata PERSA sempre: l'esperimento si sarebbe svuotato senza mai fallire |
| 16/09/2026 | **scartata la rilevazione `f00d26bc25cb`** e ripetuta subito, fuori cadenza | i suoi 3 token non avevano contratto (difetto corretto dopo), quindi nessuna sua finestra era misurabile: 3 PERSE e 3 NON MISURABILI | costo €0,05. Non è un aumento di frequenza: è la sostituzione di un'osservazione difettosa, dichiarata qui invece che nascosta |

*Ogni modifica metodologica va scritta qui prima di essere applicata.*

## Stato

Prima rilevazione: **16/09/2026 17:30 UTC** — 2 token, entrambi classe A (attenzione che sta
iniziando). Uno dei due, `$GIGADOG`, marcato da Grok come **non organico** con indizi di shilling:
i dati di mercato lo confermano con **$6 di liquidità e $34 di volume in 24 ore**. Il classificatore
dello spam funziona, ed è la prima conferma incrociata fra le due fonti.

*Nessuna conclusione sarà tratta prima di avere un campione sufficiente. Pochi casi non fanno un
edge — e su questo progetto lo abbiamo già imparato a nostre spese.*
