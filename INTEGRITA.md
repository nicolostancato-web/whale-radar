# 🔍 INTEGRITÀ — quello che abbiamo corrisponde a quello che la catena dice?
*2026-09-15 22:47 UTC · seme 20260915 · condizione 5 · €0*

> Zero duplicati **non dimostra completezza**. Un file può essere perfettamente pulito e
> mancare metà degli scambi, e nessuno dei controlli che facciamo se ne accorgerebbe.

> Qui si sorteggiano fasce di blocchi già scavate, si richiedono alla catena **da capo**, e
> si confronta con quello che abbiamo in casa.

**Finestre verificate: 113** · identiche: **86** · letture fallite (non contano): 7

| esito | finestre |
|---|---|
| ✅ identiche | 86 |
| 🔴 MANCANO DA NOI | 25 |
| 🔴 ABBIAMO DI PIU' | 2 |

## Le discrepanze

- `base` blocchi 50825940-50826000: la catena dice **41**, noi abbiamo **42** (mancanti 0, in più 1)
- `base` blocchi 49807068-49807128: la catena dice **1**, noi abbiamo **0** (mancanti 1, in più 0)
- `robinhood` blocchi 40245779-40245979: la catena dice **1**, noi abbiamo **0** (mancanti 1, in più 0)
- `robinhood` blocchi 42468957-42469157: la catena dice **2**, noi abbiamo **1** (mancanti 1, in più 0)
- `base` blocchi 50392091-50392151: la catena dice **2**, noi abbiamo **1** (mancanti 1, in più 0)
- `base` blocchi 50308968-50309028: la catena dice **14**, noi abbiamo **11** (mancanti 3, in più 0)

## Verdetto

> 🔴 **27 discrepanze su 113**. Una sola basta a far fallire
> la condizione: non stiamo misurando quanto siamo bravi, stiamo cercando se esiste
> un modo silenzioso di perdere dati. Se esiste, va trovato prima di fidarsi.