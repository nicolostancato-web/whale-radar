# Il repository è pieno al 90%, e una delle tre strade è una tua decisione

**10 ottobre, misurato — non stimato.**

## I numeri

| cosa | quanto |
|---|---|
| peso totale | **9,00 GB** su un limite di 10 |
| margine | **1,00 GB** |
| contenuto attuale su `main` | 3,66 GB (48.501 file) |
| **storia** (versioni vecchie degli stessi file) | **~5,3 GB** |
| di cui `data/multichain` | 3,08 GB |
| di cui `data/loop1` | 0,56 GB |

**Al limite GitHub blocca le scritture.** Non «rallenta»: blocca. E con esse si ferma la
pubblicazione del database della prova in avanti, cioè il lavoro che stiamo accumulando.

## Perché la storia pesa più del contenuto

I file grossi non vengono aggiunti: vengono **riscritti interi** a ogni giro. `coppie.json`
(9 MB) è stato riscritto 49 volte in 24 ore, `iniziatori.json.gz` (32 MB) 17 volte. Ogni
versione resta nella storia per sempre. `repo_gc` gira e riesce — tre volte ieri e oggi, tutte
con successo — ma non può liberare ciò che un commit ancora referenzia.

## Cosa ho già fatto (reversibile, nessun dato perso)

Spente cinque corsie che ripubblicavano i file grossi, tutte della fase **base/multichain**, che
è parcheggiata: `insieme` (~252 MB ogni due ore), `coppie`, `censimento`, `iniziatori`, `hook`.
Verificato prima di spegnerle: `prova_in_avanti`, `cammino_posizioni` e `integrita_database`
**non leggono** nessuno di quei file. Motivo e comando per riaccenderle in `data/corsie_spente.json`.

Questo **ferma la crescita**. Non libera il margine.

## Le tre strade per liberare il margine

| strada | recupera | rischio | chi decide |
|---|---|---|---|
| **A — riscrivere la storia** togliendo le versioni vecchie dei file grossi | ~5 GB | **irreversibile**; servono force-push e una pulizia dal lato GitHub; i dati vecchi di `multichain`/`loop1` spariscono per sempre | **tu** |
| **B — togliere i file grossi da `main`** (restano nella storia) | 0 GB subito | nessuno, ma non risolve | io |
| **C — spostare gli archivi fuori dal repository** (release assets: non contano nel limite) | ~3 GB di contenuto attuale | basso, i dati restano scaricabili | io, se dici sì |

La **A** non la faccio da solo: cancella mesi di raccolta, ed è irreversibile.

## Cosa consiglio

**C, poi A solo se serve.** La C recupera i 3 GB di contenuto attuale senza cancellare nulla —
gli archivi di `multichain` e `loop1` restano scaricabili come allegati di una release, fuori dal
conteggio del limite. Con la crescita già fermata e 1 GB di margine, questo basta per settimane:
il database della demo pesa pochi megabyte.

La A resta la sola che libera i 5,3 GB di storia, ma è anche la sola che distrugge qualcosa.
Prima di proporla voglio vedere se la C è sufficiente.
