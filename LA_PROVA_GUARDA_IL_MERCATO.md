# La prova in avanti guarda finalmente il mercato — 8 ottobre 2026, sera

Quattro difetti in fila, tutti nel mio codice, tutti trovati inseguendo un numero che non tornava.

| difetto | sintomo | perché succedeva |
|---|---|---|
| pool riconosciuti dal **registro** | vedeva monete lanciate **59-915 ore prima** e le chiamava nuove | il registro contiene solo pool già noti |
| valute lette dai **dati** invece che dai topics | «0 pool nuovi», **senza errori** | prendeva commissione (10000) e tick spacing (200) come indirizzi |
| **elenco dei lanci vecchio di 54 ore** | su 12 pool nuovi, 1 solo aveva un gettone noto | la fotografia su disco si ferma al blocco 81.567.695 |
| accettava **solo coppie in ETH nativo** | 1 pool riconosciuto su ~140 creati | i lanci usano **72** valute di quotazione diverse |

Dopo le correzioni: **3 pool nuovi riconosciuti in 831 blocchi**, contro 1 in 21.000 prima.

## Il filo conduttore della giornata

Ogni volta che ho dato per buono un **file** invece della chain, ho misurato una cosa diversa da
quella che credevo: il registro dei pool (ha falsificato il +18,9%, la sensibilità del segnale e il
+84%), l'elenco dei lanci, e due volte la costruzione del campione.

Adesso la prova non si appoggia a nessuna fotografia: creazione del pool dalla chain, lanci dalla
chain a ogni giro, decimali chiesti al contratto, prezzi dalla chain, e un'autoverifica che
ricalcola due entrate per giro e marca **sospetta** la posizione che non combacia.

## Come si entra, misurato

Domanda di Nicolò: *come facciamo a entrare appena viene promossa?*

| | |
|---|---|
| ritardo fra creazione del pool e primo scambio, mediana | **0 blocchi** (stesso istante) |
| entro 5 blocchi | 90% delle monete |
| scambi nel primo minuto, mediana | **382** |
| massimo osservato | 1.302 |

Nella metà dei casi il primo scambio è **nello stesso blocco** della creazione: «arrivare primi» è
una gara di infrastruttura, non di informazione. E non paga comunque, perché il pool apre al
prezzo di chiusura della curva (mediana 1,068x): **non c'è nessun salto da rubare**.

Per questo la regola entra alla **fine** del primo minuto. È una scelta dichiarata, non una
rinuncia.

## E la correzione sulla lettura della tabella

Nicolò ha letto come positivo che il 58% delle monete faccia almeno 1,5x. È comprensibile ed è
sbagliato: **uscire a 1,5x rende −8,8%**. Si vince 45 volte su 77 e si perde, perché le 32 che
perdono perdono il **95-99%**: quattro vittorie da +47% le cancella **una** perdita totale.

Un tasso di vittoria alto e un'aspettativa negativa convivono benissimo. È la trappola di chi
guarda «quante volte ho ragione» invece di «quanto perdo quando ho torto».
