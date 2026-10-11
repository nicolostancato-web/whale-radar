# Dopo il diploma: la prima occhiata, e perché non è ancora un risultato

7 ottobre, notte. La curva è chiusa come strada (vedi `TRADARE_DENTRO_LA_SCATOLA_NON_PAGA.md`).
Resta il mercato **dopo** il diploma. Prima occhiata, con due difetti miei trovati lungo la strada.

## I due difetti, perché contano più del numero

**Primo: unire due pool.** La stessa moneta ha un pool in nativo e uno in un altro asset. Unendo
le due serie, il «prezzo» saltava fra due scale e dava una salita monotona su **tutte** le monete,
mediana 17x. Un risultato troppo uniforme è un difetto, non una scoperta.

**Secondo: i lati invertiti.** Se il gettone sta sul lato `t1`, il suo importo è `a1`. Io prendevo
`a0`: calcolavo il rapporto fra due merci diverse, che deriva piano e **somiglia** a un prezzo che
sale. Con i lati corretti il quadro si capovolge.

## Il quadro vero, su 20 monete diplomate (un solo pool, in nativo)

| | |
|---|---|
| massimo/inizio, mediana | **1,80x** |
| prezzo **finale**/iniziale, mediana | **0,054x** — meno 95% |
| quante finiscono sotto il prezzo di partenza | **19 su 20** |
| quante superano 10x | **2 su 20** (23x e 27x) |

È il pattern classico: quasi tutte muoiono, pochissime fanno molte volte. **Le X stanno qui**, non
sulla curva.

## Le regole provate, su 30 monete

Prezzo = mediana di 10 scambi (un singolo scambio non è un prezzo), 1% in entrata e 1% in uscita.

| regola | medio per moneta | mediana | vinte |
|---|---|---|---|
| compro al diploma, vendo a 2x | +14,7% | **+96,1%** | 17/30 |
| vendo a 3x | +51,0% | +57,9% | 15/30 |
| vendo a 10x, taglio a 0,5x | **+104,2%** | −51,0% | 5/30 |
| tengo fino alla fine | **−82,0%** | −93,6% | 1/30 |

## Perché NON lo chiamo un edge

1. **30 monete.** La media di +104% poggia su **5 vincenti**: togline due e diventa negativa.
2. **Sette regole provate sugli stessi dati.** Cercando fra molte configurazioni si trova sempre
   qualcosa: senza una parte dei dati mai vista, non si distingue il segnale dal rumore.
3. **Il prezzo non è eseguibile.** La mediana di 10 scambi non è un prezzo a cui si compra:
   manca lo scivolamento, e su queste dimensioni è la voce che decide.
4. **Nessun campione di controllo.** Non ho ancora un confronto che dica quanto renderebbe
   comprare *a caso* con la stessa regola.

## Il prossimo passo, già definito

Leggere **300 monete** diplomate, dividerle in due metà **per data**: scegliere la regola sulla
prima metà, provarla sulla seconda **senza più toccarla**. Se regge, aggiungere lo scivolamento
misurato e il confronto col caso. Solo allora è un numero da portare a Nicolò.

La differenza con tre giorni fa è che questo lo sto scrivendo **prima** di dirgli che funziona.
