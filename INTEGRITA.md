# 🔍 INTEGRITÀ — quello che abbiamo corrisponde a quello che la catena dice?
*2026-09-16 00:16 UTC · seme 20260915 · condizione 5 · €0*

> Zero duplicati **non dimostra completezza**. Un file può essere perfettamente pulito e
> mancare metà degli scambi, e nessuno dei controlli che facciamo se ne accorgerebbe.

> Qui si sorteggiano fasce di blocchi già scavate, si richiedono alla catena **da capo**, e
> si confronta con quello che abbiamo in casa.

**Finestre verificate: 34** · identiche: **7** · letture fallite (non contano): 36

| esito | finestre |
|---|---|
| ✅ identiche | 7 |
| 🔴 MANCANO DA NOI | 27 |

## Le discrepanze

- `base` blocchi 50861800-50861860: la catena dice **135**, noi abbiamo **60** (mancanti 78, in più 0)
- `base` blocchi 50897737-50897797: la catena dice **52**, noi abbiamo **32** (mancanti 20, in più 0)
- `base` blocchi 50819264-50819324: la catena dice **72**, noi abbiamo **28** (mancanti 44, in più 0)
- `base` blocchi 50875911-50875971: la catena dice **70**, noi abbiamo **63** (mancanti 7, in più 0)
- `base` blocchi 51075122-51075182: la catena dice **196**, noi abbiamo **75** (mancanti 126, in più 0)
- `base` blocchi 50668346-50668406: la catena dice **19**, noi abbiamo **1** (mancanti 18, in più 0)

## Verdetto

> 🔴 **27 discrepanze su 34**. Una sola basta a far fallire
> la condizione: non stiamo misurando quanto siamo bravi, stiamo cercando se esiste
> un modo silenzioso di perdere dati. Se esiste, va trovato prima di fidarsi.