# 📐 CHE COSA STIAMO STUDIANDO — proposta di definizione congelata

*18 settembre 2026 · nata dalla domanda della revisione esterna, ancora DA APPROVARE*

## La domanda che l'ha resa necessaria

> «Qual è la definizione congelata, verificabile e applicata uniformemente di "memecoin" che rende
> quei 50.110 pool il denominatore giusto?»

Non ne avevamo una. Dicevamo «memecoin» e misuravamo «tutto ciò che ha emesso un log di swap» —
due cose diverse. Senza una definizione, né il 3,6% di copertura né il 95% richiesto dalla
condizione 1 significano qualcosa: non si sa di cosa siano la percentuale.

## Cosa contiene davvero il censimento

*Rigenerata il 21/09/2026 da UNA SOLA estrazione per chain, dopo che la revisione esterna ha
trovato che la tabella precedente non quadrava.*

**Cosa non andava nella tabella di prima.** Diceva 50.110 pool in un punto, ma le sue classi
sommavano 50.294: centottantaquattro di scarto. Non era un arrotondamento — erano DUE estrazioni
di momenti diversi presentate come una popolazione sola. Ed era anche costruita sulla classe
«oltre 20», mentre la regola qui sotto dice «almeno 20»: due insiemi diversi.

Classi disgiunte, somma che quadra, ognuna da un'unica lettura del censimento:

| scambi nell'intervallo | base | robinhood |
|---|---|---|
| esattamente 1 | 29.728 | 215.104 |
| da 2 a 5 | 19.672 | 26.450 |
| da 6 a 19 | 6.738 | 15.430 |
| **esattamente 20** | **200** | **328** |
| oltre 20 | 13.095 | 26.248 |
| **totale censito** | **69.433** | **283.560** |
| **almeno 20 (la regola)** | **13.295** | **26.576** |

I duecento e i trecentoventotto della riga «esattamente 20» sono quelli che la tabella vecchia
buttava via pur essendo dentro la regola. Sul totale pesano poco; contano perche' sono il genere
di scarto che poi fa non tornare i conti senza che si capisca da dove viene.

**La maggioranza schiacciante dei pool nasce e scambia una volta sola** — il 43% su base, il 76%
su robinhood. Usarli come denominatore gonfia il problema: non stiamo «perdendo» quei pool, non
esistono come mercato.

**Il censimento cresce.** Questi numeri valgono per l'estrazione del 21/09; base era a 50.110 il
18/09. Ogni percentuale calcolata su di essi deve dichiarare la data dell'estrazione, altrimenti
si confrontano fotografie diverse credendo di confrontare la stessa cosa.

## La definizione proposta

Un pool entra nella popolazione studiata se soddisfa **tutte e tre**:

**1. Ha una valuta di base da un lato.**
   Lista congelata per chain, scritta qui e non modificabile senza registrarlo in `DECISIONS.md`:

   base:       nativo (0x0), WETH `0x4200000000000000000000000000000000000006`,
               USDC `0x833589fcd6edb6e08f4c7c32d4f71b54bda02913`
   robinhood:  nativo (0x0), più le valute di base che il censimento mostrerà come ricorrenti
               (da fissare quando il censimento di robinhood chiude)

**2. L'altro lato NON è una valuta di base.**
   Esclude così le coppie fra valute (WETH/USDC e simili), che sono infrastruttura, non memecoin.

**3. Ha almeno 20 scambi nell'intervallo dichiarato.**
   La soglia è arbitraria ma **dichiarata prima di misurare**. Serve a separare i pool che
   esistono come mercato da quelli nati e morti in un blocco. Con «almeno 20», base passa da
   69.433 a **13.295** e robinhood da 283.560 a **26.576** (estrazione del 21/09).
   «Almeno» vuol dire che i pool con esattamente 20 scambi sono DENTRO: contarli fuori era
   l'errore della versione precedente.

## Cosa cambia se la si adotta

- il denominatore della copertura diventa **quello e solo quello**, non «tutto ciò che scambia»
- la condizione 1 (≥95%) si misura su una popolazione definita, e diventa un obiettivo sensato
  invece di un numero impossibile
- ogni esclusione ha una **causa nominabile**: non è una valuta di base, è una coppia fra valute,
  è sotto soglia

## Cosa NON risolve, e va detto

**Non sappiamo ancora la coppia di token per la maggior parte dei pool censiti**: la conosciamo per
333 dei 7.458 attivi (4%), perché `coppie.json` copre solo il nostro registro. Finché non la
risolviamo per tutti, la definizione **non è applicabile** — si può scrivere ma non usare.

Risolverla è fattibile: per i pool V4 dall'evento `Initialize` (che porta currency0 e currency1),
per quelli con indirizzo con due chiamate al contratto. È il prossimo lavoro.

**E resta una scelta arbitraria**: la soglia dei 20 scambi. Un pool con 19 scambi non è
qualitativamente diverso da uno con 21. La difesa non è che sia la soglia giusta — è che è
**dichiarata prima**, uguale per tutti, e che spostandola si vede subito quanto cambia il risultato.

## Stato: PROPOSTA, non ancora adottata

Serve l'approvazione del fondatore prima di usarla come denominatore ufficiale. Fino ad allora le
percentuali di copertura restano quelle grezze, con tutti i loro difetti dichiarati.


---

## AGGIORNAMENTO 19 SETTEMBRE — la definizione è diventata applicabile, e ha rivelato una crepa

### Adesso si può usare

Questo documento diceva di sé: «non sappiamo la coppia di token per la maggior parte dei pool
censiti — la conosciamo per 333 dei 7.458 attivi (4%) — quindi la definizione **non è
applicabile**: si può scrivere ma non usare».

Da oggi le coppie sono risolte al **98% su base e al 100% su robinhood** (corsia parallela su
quattro IP: il nodo limita per indirizzo, non per connessione, quindi la velocità si compra fra
lavori). La definizione si applica.

Popolazione che ne esce:

| | pool che soddisfano la definizione |
|---|---:|
| base | 7690 |
| robinhood | 16955 |

### La crepa: «≥20 scambi nell'intervallo» non vuol dire «20 scambi ravvicinati»

L'intervallo dichiarato dura settimane. Un pool con 23 scambi sparsi su 1,4 milioni di blocchi
soddisfa la soglia ed è un pool **dormiente**, non un evento. Misurato su sei pool a caso: quelli
con arco stretto rendono 201 e 239 righe nelle loro prime ore, quelli con arco largo **una**.

La popolazione si divide quasi a metà:

| | pool | di cui con attività **concentrata entro 8 ore** |
|---|---:|---:|
| base | 7690 | 3613 |
| robinhood | 16955 | 8596 |

### Perché conta per il goal, e non è una comodità

Il picco breve **è** come si presenta una memecoin che pompa. E la scoperta scomoda è che il nostro
archivio conteneva soprattutto l'altra metà: al momento della misura avevamo il 14,2% dei diluiti
e solo il **4,0%** dei concentrati.

La causa è precisa: la raccolta storica veniva da un filtro che pretendeva almeno 5 candele e un
minimo di volume — cioè **essere sopravvissuti**. Quel filtro esclude il 52% dei pool per motivi
che dipendono dall'esito, e l'esito è l'unica cosa che al momento di decidere non si può sapere.
Un archivio selezionato così gonfia qualunque percentuale il loop 1 andrà a misurare.

### Cosa ho cambiato e cosa NO

**Non ho cambiato la definizione.** Resta «≥20 scambi nell'intervallo dichiarato, una valuta di
base da un lato, l'altro lato no». Spostarla dentro un agente per far salire un numero sarebbe
esattamente il difetto che questo documento esiste per impedire.

**Ho cambiato l'ordine di raccolta**: prima i pool concentrati, poi quelli di cui non vediamo
l'inizio (36% su base, 8% su robinhood hanno l'àncora sul bordo dell'intervallo, quindi quel blocco
non è la loro nascita). È una scelta operativa, reversibile, che non tocca chi appartiene alla
popolazione.

Effetto misurato sulla resa: da **1 riga per pool a 94**.

### Stato della copertura sui concentrati

| | concentrati | usabili (≥20 righe) |
|---|---:|---:|
| base | 3613 | 3442 = 95.3% |
| robinhood | 8596 | 3552 = 41.3% |

### La domanda che resta aperta per il fondatore

Se la popolazione da studiare dovesse essere **solo** quella concentrata, la definizione va
modificata qui dentro e registrata in `DECISIONS.md`. Io non la sposto: la misuro in entrambi i
modi e li riporto entrambi.
