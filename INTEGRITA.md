# 🔍 INTEGRITÀ — quello che abbiamo corrisponde a quello che la catena dice?
*2026-09-19 15:26 UTC · seme 20260915 · condizione 5 · €0*

> Zero duplicati **non dimostra completezza**. Un file può essere perfettamente pulito e
> mancare metà degli scambi, e nessuno dei controlli che facciamo se ne accorgerebbe.

> Qui si sorteggiano fasce di blocchi già scavate, si richiedono alla catena **da capo**, e
> si confronta con quello che abbiamo in casa.

**Finestre verificate: 1225** · identiche: **834** · letture fallite (non contano): 630

| esito | finestre |
|---|---|
| ✅ identiche | 834 |
| 🔴 MANCANO DA NOI | 391 |

## Le discrepanze

- `base` blocchi 50838656-50838716: la catena dice **9**, noi abbiamo **10** (mancanti 6, in più 0)
- `base` blocchi 50814786-50814846: la catena dice **73**, noi abbiamo **33** (mancanti 40, in più 0)
- `base` blocchi 50670209-50670269: la catena dice **27**, noi abbiamo **16** (mancanti 11, in più 0)
- `base` blocchi 50838795-50838855: la catena dice **16**, noi abbiamo **4** (mancanti 16, in più 0)
- `robinhood` blocchi 51947220-51947420: la catena dice **4**, noi abbiamo **5** (mancanti 4, in più 0)
- `base` blocchi 50814703-50814763: la catena dice **98**, noi abbiamo **46** (mancanti 52, in più 0)

## Verdetto

> 🔴 **391 discrepanze su 1225**. Una sola basta a far fallire
> la condizione: non stiamo misurando quanto siamo bravi, stiamo cercando se esiste
> un modo silenzioso di perdere dati. Se esiste, va trovato prima di fidarsi.