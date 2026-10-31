# Ritiro il +18,9%: era il campione — 8 ottobre 2026

## Il confronto, fatto sullo stesso codice e sulla stessa regola

Regola invariata: compro a fine primo minuto dopo il diploma, vendo al raddoppio, 1% + 1% di
costi e scivolamento misurato per 200 $.

| campione | monete comprabili | medio | mediano | in guadagno |
|---|---|---|---|---|
| estratto dal **nostro registro** | 334 | **+15,2%** | +89,5% | 196/334 (59%) |
| **casuale vero, dalla chain** | **77** | **−10,4%** | −57,9% | 32/77 (42%) |

E tutto il resto si rimpicciolisce insieme:

| | registro | casuale vero |
|---|---|---|
| massimo raggiunto, mediana | 2,43x | **1,66x** |
| 90° percentile | 10,61x | **6,08x** |
| migliore | 123,7x | 57,7x |

## Com'era costruito il campione sbagliato

`coppie.json` contiene i pool che i nostri raccoglitori hanno **visto scambiare**. Un pool che non
scambia non entra nel registro — e su un campione casuale vero i pool muti sono l'**82,1%** delle
diplomate. Quindi il registro non era un campione del mercato: era l'elenco dei vivi.

Misurare una strategia sull'elenco dei vivi è come misurare la mortalità intervistando i
sopravvissuti.

## Il verdetto

**La regola senza selezione perde: −10,4% per moneta.** Il +18,9% (e il +15,2% con lo
scivolamento) sono **ritirati**. Non valgono niente, e nessuna decisione va costruita su quei
numeri — il mio documento di stamattina `QUINTA_CONFERMATA.md` va letto con questa correzione
accanto.

Era una previsione **registrata prima** e passata su dati mai usati per scegliere: ha superato
quella prova e **non** ha superato questa. La lezione è che la pre-registrazione protegge dalla
scelta del risultato, **non** dalla costruzione storta del campione. Sono due difetti diversi e
servono due controlli diversi.

## Cosa resta in piedi

1. **Il premio esiste**: il 9,9% delle diplomate è comprabile, e fra quelle il 90° percentile fa
   **6x**, la migliore 57,7x. I soldi ci sono, sono solo molto più rari di quanto dicessi.
2. **La capienza c'è**: vendite singole verificate da 6.824 $ e 7.771 $, e lo scivolamento
   misurato è l'1,71% a 200 $.
3. **Il segnale sul diploma regge**: «curva a ≥3,8 ETH in 60 minuti» cattura il 91,8% dei diplomi
   con quasi zero falsi, e al diploma resta ancora +83,9% di salita.
4. **La prova in avanti è l'unico giudice non contaminato**: riconosce i pool in diretta dagli
   scambi del gestore, quindi vede anche i pool muti e non eredita questo difetto. Oggi ho trovato
   e corretto un suo errore (due pool mescolati nella stessa posizione) controllandola contro la
   chain.

## Cosa non faccio

Non cerco un'altra regola sui dati storici. Oggi ho ritirato due risultati miei in dodici ore, e
il motivo è lo stesso: lo storico che possediamo è un campione di noi stessi. **Il prossimo numero
che porto viene dalla prova in avanti**, dove il campione è il mondo e la regola è scritta prima.
