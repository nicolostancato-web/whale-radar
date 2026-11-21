# La tassa del 99% e chi non la paga — 7 ottobre, sera

## Da dove è uscita

Grok, girato sul **nostro** 50% invece che sull'altro, ha scritto una riga prima di essere
troncato: *«la documentazione dice 99% in 5 secondi»*. Non l'ho creduta: l'ho verificata sulla
chain, dove il nostro lettore estrae già la commissione di ogni acquisto.

## Confermata, e con una sorpresa dentro

Su 441 acquisti letti su 8 monete:

| quando compra | commissione mediana |
|---|---|
| nei primi 50 blocchi (~5 secondi) | **4,09%** |
| dopo | **1,00%** |

La mediana nascondeva la cosa vera. Guardando i singoli: **10 acquisti su 441 hanno pagato il
99%**, tutti nei primissimi blocchi. La tassa anti-sniper esiste ed è brutale.

**Ma nello stesso blocco altri pagano l'1%.** Quelli sono **esentati**. Non sono bravi: sono
autorizzati.

## Gli esenti sono pochi e sempre gli stessi

Su 30 lanci letti: 36 indirizzi esenti distinti, **14 presenti su più di un lancio**.

| indirizzo | esente su | capitale messo | mediana | migliore | mai uscito |
|---|---|---|---|---|---|
| `0x65050a9b7e50…` | **22 lanci su 30** | 9.250 | **0,987x** | 1,10x | 0 su 15 |
| `0xa22a5cf8b666…` | 7 | 76,7 | 0,000x | 1,94x | 6 su 7 |
| `0xb8ca7242d1d2…` | 7 | 76,7 | 0,000x | 1,80x | 6 su 7 |
| `0xb72b5d767fd0…` | 7 | 76,7 | 0,000x | 1,92x | 6 su 7 |

Chi paga il 99%: 11 indirizzi distinti, quasi mai ripetuti. Sono sniper che si bruciano una volta.

## La risposta, che è un «no» pulito

**Il privilegio esiste, è identificabile, e non è dove stanno i soldi.** Il grande esente mette
migliaia di unità e chiude a 0,987x con un massimo di 1,10x: è il profilo di chi fa il mercato,
non di chi fa X. Gli altri tre, identici fra loro fino al terzo decimale (76,67 di capitale
ciascuno, 6 posizioni su 7 mai chiuse), sono con ogni evidenza i portafogli di un solo operatore,
e perdono.

Non è una delusione: spiega una cosa che avevamo **misurato senza capirla** — entrare primi
peggiorava il risultato (0,66x che scendeva a 0,24x su 580.000 operazioni). Ora si sa perché:
nei primi cinque secondi, o sei autorizzato, o paghi il 99%.

E chiude una porta che stava aperta nelle nostre classifiche: il buco dichiarato in
`storie_complete.py` sugli indirizzi esentati non è più un buco — sono questi, si leggono dalla
commissione, e non vanno cercati fra i bravi.

## Sull'altro 50%, per chiudere

I tre fascicoli di Grok dicono tutti la stessa cosa: **nessun programma scritto**. Base è in
«esplorazione» senza criteri dal settembre 2025; Ink, Arc e Soneium non pubblicano soglie; l'unico
ponte con regole scritte, deBridge, ha **entrambe le stagioni chiuse** e nessuna terza annunciata.
Non ci sono «robe incredibili» da prendere: c'è un mondo che non ha ancora pubblicato le sue
regole. Grok continua ad accumulare, ma oggi di là non c'è niente da fare.
