# 🧫 SOPRAVVIVENZA — è morto, o non l'abbiamo guardato?

*15/09/2026 · 3.791 casi utilizzabili · la condizione 7 dei criteri*

## La domanda

L'audit aveva misurato che le serie **escluse** dall'analisi vivono **1,0 ora** in mediana, mentre
quelle **ammesse** ne vivono **23,4**. L'avevo chiamato *survivorship bias* — cioè: il mercato uccide
i token e noi vediamo solo i sopravvissuti.

La revisione ha corretto il nome: quella è una **durata osservata**, non la vita del token. La stessa
differenza può venire da mortalità vera **oppure da buchi nostri**. Sono cose opposte: una è il
mondo, l'altra siamo noi — e si riparano in modi diversi.

## Il test

Per ogni pool, a +3h si chiede **alla catena** — fonte diversa da quella delle candele — se esiste
ancora, e si confronta con quello che abbiamo noi.

| la catena dice | noi abbiamo la candela | casi | lettura |
|---|---|---|---|
| vivo | **no** | **3.730** | 🔴 **buco nostro** |
| vivo | sì | 561 | 🟢 copertura funzionante |
| non risponde | — | 715 | ❓ non si conclude niente |
| **morto** | no | **61** | ⚫ **mortalità vera** |
| morto | sì | 14 | ⚠️ incoerente |

## Il risultato

Sui **3.791 casi in cui la catena ha risposto e noi non avevamo la candela**:

| | |
|---|---|
| buchi nostri | **3.730 = 98,4%** |
| mortalità vera | 61 = 1,6% |
| **limite inferiore al 95%** | **98,1%** |

**La soglia richiesta era «limite inferiore sopra il 95%». È soddisfatta.**

> Quando avevo 17 casi su 17 e ho scritto «sono tutti buchi nostri», il limite inferiore era
> **83,8%**: compatibile con oltre il 16% di mortalità vera. Non era una prova, era un indizio.
> Adesso i casi sono 3.791 e il numero regge.

## Cosa questo significa

**Il problema non è che il mercato uccide i token prima che li vediamo. Il problema è che non li
guardiamo.** È una diagnosi migliore, perché un buco di copertura si ripara — e lo stiamo riparando:
la copertura è passata dal 15% al 98% su Base in una giornata.

## Le due debolezze, dichiarate

**1. «Vivo» è definito debolmente.** Significa che il contratto risponde con riserve non nulle. Non
significa che qualcuno lo stesse scambiando. Un pool può avere riserve e zero scambi — e in quel
caso «buco nostro» dice che *il pool esisteva*, non che valesse la pena guardarlo.
La definizione forte richiederebbe di verificare uno **scambio** entro +3h, non solo l'esistenza.

**2. Il campione non è casuale.** I casi vengono dai pool più recenti fra quelli in età 3-8h, non da
un sorteggio. Quindi il risultato vale con certezza per quella fascia; estenderlo a tutto l'universo
è un'inferenza, non una misura.

**Nessuna delle due invalida il risultato. Entrambe lo restringono**, ed è giusto che chi legge lo
sappia senza doverlo dedurre.

## E i 14 casi incoerenti

Quattordici pool che la catena dà per morti ma di cui **abbiamo la candela**. Sono pochi (0,3%), ma
non sono spiegati: o la nostra candela è di un momento precedente alla morte, oppure la lettura
della catena ha sbagliato. Vanno guardati, non archiviati.

---

# CORREZIONE (stesso giorno): i numeri erano gonfiati

Ho pubblicato **3.791 casi**. Sono **626**.

Il test ricontrolla lo stesso pool a ogni giro, e io contavo ogni controllo come un caso nuovo.
4.844 osservazioni erano in realtà **670 pool distinti**, ciascuno guardato in media sette volte.

Me ne sono accorto guardando i «14 casi incoerenti»: erano **lo stesso pool, contato quattordici
volte**. Se non fossi andato a vederli uno per uno, il numero sbagliato sarebbe rimasto.

> Un pool controllato sette volte non sono sette prove. È una prova, guardata sette volte — e
> contarla sette volte fa sembrare il campione sette volte più solido di quanto sia.

## I numeri onesti, un caso per pool

| esito | pool distinti |
|---|---|
| 🔴 buco nostro | **616** |
| 🟢 copertura funzionante | 28 |
| ⚫ mortalità vera | **10** |
| ❓ lettura fallita | 15 |
| ⚠️ incoerente | **1** |

| | |
|---|---|
| casi utilizzabili distinti | **626** |
| quota di buchi nostri | **98,4%** |
| **limite inferiore al 95%** | **97,6%** |
| soglia richiesta | 95% → ✅ **superata** |
| casi richiesti | 59 → ✅ ne abbiamo 626 |

## La conclusione regge

Con i numeri gonfiati il limite era 98,1%; con quelli veri è **97,6%**. **Sopra la soglia in
entrambi i casi** — ma il primo numero non avevo il diritto di scriverlo.

E i «14 incoerenti» diventano **uno solo**: un singolo pool che la catena dà per morto mentre noi
abbiamo una candela di poco precedente. Una candela vecchia di dodici minuti rispetto al controllo:
il pool è morto **fra** la nostra ultima lettura e la verifica. Non è un'incoerenza, è una corsa.
