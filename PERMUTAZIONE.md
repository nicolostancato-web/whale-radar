# 🎲 PERMUTAZIONE A BLOCCHI — il nostro numero migliore significa qualcosa?
*2026-09-13 20:37 UTC · audit · forma corretta dopo la revisione avversariale · €0*

> Il nostro «migliore» è il massimo di tantissimi tentativi. Un massimo va confrontato con
> **altri massimi**, non con una media: anche in dati senza alcun legame, chi cerca abbastanza
> trova sempre qualcosa che sembra funzionare.

> **La forma del test** (corretta dopo che la mia prima versione è stata demolita): l'ordine
> temporale resta intatto, gli esiti si scambiano **solo fra token nati lo stesso giorno** —
> perché chi nasce insieme si muove insieme — e si riesegue **tutta** la selezione, non solo
> la configurazione finale.

6 configurazioni per mondo, 8 mondi permutati, max 700 righe per chain.

| chain | righe | **vero** | finti: mediana | finti: **massimo** | il vero batte il caso? |
|---|---|---|---|---|---|
| **base** | 700 | **-23.9%** | -24.3% | **-23.4%** | ⚠️ solo la mediana |
| **solana** | 700 | **-29.7%** | -30.3% | **-28.4%** | ⚠️ solo la mediana |
| **robinhood** | 651 | **-13.5%** | -12.6% | **-11.7%** | ❌ **no** |

## Come si legge

> **Se il vero non batte il massimo dei mondi permutati**, il nostro numero non è un
> vantaggio: è il premio di aver guardato tante volte. Nessuna quantità di ottimizzazione lo
> renderà vero, e continuare a ottimizzare è tempo speso a lucidare il rumore.

> **Se lo batte nettamente**, la differenza fra i due è l'unica parte che vale la pena
> guardare: tutto il resto è il prezzo della ricerca.

> ⚠️ **Limite dichiarato**: qui si provano poche decine di configurazioni per mondo, non due
> milioni. Va nella direzione **prudente** — il placebo vero, con due milioni di tentativi,
> troverebbe **di più**. Il confronto reale è quindi ancora più severo di questo.

> ⚠️ **Cosa questo test NON dice**: non dice se esiste un vantaggio nei dati. Dice soltanto
> se *il numero che stiamo guardando* si distingue da quello che produrrebbe la sola ricerca.
---

## ESITO SU TRE CHAIN (700 righe, 6 configurazioni, 8 mondi permutati)

| chain | vero | finti: mediana | finti: **massimo** | batte il caso? |
|---|---|---|---|---|
| base | −23,9% | −24,3% | **−23,4%** | ❌ no |
| solana | −29,7% | −30,3% | **−28,4%** | ❌ no |
| robinhood | −13,5% | −12,6% | **−11,7%** | ❌ no |

> **Su nessuna delle tre chain il numero vero batte il massimo dei mondi permutati.**
> Su Base e Solana supera la *mediana* dei finti — ma è irrilevante: il nostro numero è un
> **massimo**, e va confrontato con dei massimi. Confrontarlo con la mediana sarebbe scegliere
> l'avversario più debole dopo aver visto il risultato.

### Cosa è dimostrato

Con **questa classe di ipotesi** (dieci feature scritte a mano, nessuna identità di wallet, nessuna
sequenza di scambi, nessuna interazione) e **questa procedura di ricerca**, il vantaggio che
misuriamo **non si distingue da quello che la sola ricerca produce su dati privi di legame**.

La tesi «il migliore è rumore selezionato» era stata dichiarata *non dimostrata* dal revisore
avversariale. **Adesso è dimostrata**, con il test nella forma che lui stesso ha indicato.

### Cosa NON è dimostrato

Che nei dati non ci sia un vantaggio. Il test non giudica i dati: giudica **la coppia
classe-di-ipotesi + procedura**. Un segnale che vivesse nell'identità dei wallet, nella sequenza
degli eventi o in un'interazione non lineare **non potrebbe comparire qui**, perché queste variabili
non entrano nel test — non perché non esistano nei dati.

Il risultato punta forte verso **«stiamo cercando nel posto sbagliato»**, non verso «non c'è niente».
