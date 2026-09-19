# 📐 CHE COSA STIAMO STUDIANDO — proposta di definizione congelata

*18 settembre 2026 · nata dalla domanda della revisione esterna, ancora DA APPROVARE*

## La domanda che l'ha resa necessaria

> «Qual è la definizione congelata, verificabile e applicata uniformemente di "memecoin" che rende
> quei 50.110 pool il denominatore giusto?»

Non ne avevamo una. Dicevamo «memecoin» e misuravamo «tutto ciò che ha emesso un log di swap» —
due cose diverse. Senza una definizione, né il 3,6% di copertura né il 95% richiesto dalla
condizione 1 significano qualcosa: non si sa di cosa siano la percentuale.

## Cosa contiene davvero il censimento di base (3 giorni, intervallo dichiarato)

| attività del pool | quanti | quota |
|---|---|---|
| esattamente 1 scambio | 22.665 | **45%** |
| fino a 5 scambi | 37.945 | 76% |
| fino a 20 scambi | 42.836 | **85%** |
| oltre 20 scambi | **7.458** | **15%** |
| mediana | **2 scambi** | |

**Quarantacinquemila pool su cinquantamila sono nati e hanno scambiato una volta o poche.**
Usarli come denominatore gonfia il problema: non stiamo «perdendo» quei pool, non esistono come
mercato.

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
   esistono come mercato da quelli nati e morti in un blocco. Con 20, base passa da 50.110 a 7.458.

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
