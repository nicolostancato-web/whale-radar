# 🔍 INTEGRITÀ — quello che abbiamo corrisponde a quello che la catena dice?
*2026-09-15 19:18 UTC · seme 20260915 · condizione 5 · €0*

> Zero duplicati **non dimostra completezza**. Un file può essere perfettamente pulito e
> mancare metà degli scambi, e nessuno dei controlli che facciamo se ne accorgerebbe.

> Qui si sorteggiano fasce di blocchi già scavate, si richiedono alla catena **da capo**, e
> si confronta con quello che abbiamo in casa.

**Finestre verificate: 19** · identiche: **15** · letture fallite (non contano): 1

| esito | finestre |
|---|---|
| ✅ identiche | 15 |
| 🔴 MANCANO DA NOI | 4 |

## Le discrepanze

- `base` blocchi 50193559-50193619: la catena dice **1**, noi abbiamo **0** (mancanti 1, in più 0)
- `robinhood` blocchi 43644463-43644663: la catena dice **3**, noi abbiamo **0** (mancanti 3, in più 0)
- `robinhood` blocchi 37302882-37303082: la catena dice **3**, noi abbiamo **1** (mancanti 2, in più 0)
- `robinhood` blocchi 42326348-42326548: la catena dice **1**, noi abbiamo **0** (mancanti 1, in più 0)

## Verdetto

> 🔴 **4 discrepanze su 19**. Una sola basta a far fallire
> la condizione: non stiamo misurando quanto siamo bravi, stiamo cercando se esiste
> un modo silenzioso di perdere dati. Se esiste, va trovato prima di fidarsi.