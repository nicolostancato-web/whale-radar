# Il 12x esiste, è scritto nelle regole, ed è recintato — 7 ottobre, notte

## Il numero

La documentazione di Pons (`docs.ponsfamily.com/v2`) dice che una moneta **gradua** quando la
curva ha incassato **4,2 ETH reali**, e che in quel momento il prezzo è **12,25×** quello di
apertura.

Non l'ho creduto: l'ho misurato sui nostri dati, su 39 monete graduate, confrontando il prezzo del
**primo** acquisto sulla curva con quello dell'**ultimo**.

| | |
|---|---|
| mediana del rapporto ultimo/primo | **11,79x** |
| massimo osservato | **12,21x** |
| quante stanno fra 11x e 13,5x | **26 su 39** |

**Nessuna supera 12,25.** È il comportamento di un tetto, non di un caso: il numero della
documentazione è confermato da una misura indipendente.

## Perché questo cambia la lettura di tutto

Fin qui misuravamo mediane intorno a **0,8-1,0x** e concludevamo «non c'è edge». Era vero di
*chi compra a metà curva*. Ma la curva, dal primo all'ultimo acquisto, **vale 12 volte, per
costruzione**. Non è un'opinione di mercato: è una formula.

E allora la domanda cambia: non «esiste un 12x?» — esiste, è scritto — ma **«perché nessuno lo
prende?»**

## La risposta, nei due pezzi trovati oggi

**Primo pezzo: il recinto.** Nei primi cinque secondi c'è una tassa anti-sniper del **99%**,
confermata sulla chain (10 acquisti su 441 l'hanno pagata, tutti nei primissimi blocchi). Chi
arriva primo senza autorizzazione consegna 99 centesimi su ogni euro. Questo spiega una cosa che
avevamo misurato senza capirla: entrare primi *peggiorava* il risultato — 0,66x che scendeva a
0,24x su 580.000 operazioni.

**Secondo pezzo: chi ha la chiave non la usa per questo.** Gli indirizzi esentati esistono, sono
pochi e ricorrenti (uno esente su 22 lanci su 30). Ma misurati: mediana **0,987x**, massimo 1,10x,
migliaia di unità di capitale. È il profilo di chi fa il mercato, non di chi prende un 12x.

## Il pezzo che manca, e che è la prossima domanda

Se il 12x è nelle regole e la tassa si evita essendo autorizzati, **perché gli autorizzati chiudono
in pari?** Due spiegazioni possibili, e vanno distinte con una misura, non scelte per gusto:

1. **il 12x non è incassabile**: è l'intervallo di prezzo fra primo e ultimo acquisto, ma vendere
   ripercorre la curva al contrario, e 5/7 della fornitura viene distribuita lungo la salita —
   quindi l'ingresso medio è molto più alto del primo prezzo;
2. **gli autorizzati non sono lì per guadagnare**: sono i bot della piattaforma, e il loro
   compito è un altro.

La prima è verificabile: si prende chi ha comprato nei primissimi acquisti **senza** pagare il 99%
e si guarda quanto ha incassato vendendo. Se nemmeno loro fanno il 12x, il 12x non è incassabile e
la curva è chiusa come strada. Se qualcuno lo fa, abbiamo trovato chi cerchiamo.

## Nota di metodo: perché Grok ha funzionato solo stasera

Due giri su due la domanda lunga tornava **troncata** — solo il preambolo, 300-440 caratteri.
Diagnosticato per esclusione invece che per intuizione: una domanda **corta** che richiede ricerca
sul web funziona perfettamente (ha dato il gas token di Robinhood Chain col link, risposta piena);
la stessa domanda lunga si ferma, a sforzo alto e a sforzo medio. È un tetto sull'uscita.

Ora ogni tema è una **lista di domande corte** e il fascicolo lo assemblo io: la prima prova ha
reso 3.980 caratteri con la fonte ufficiale, dove prima rendeva 440 di preambolo.
