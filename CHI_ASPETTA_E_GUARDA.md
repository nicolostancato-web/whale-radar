# Chi aspetta e guarda — 6 ottobre 2026, sera

## La correzione che ha cambiato tutto

Entrambi i revisori hanno detto la stessa cosa per strade diverse:

> Astra: *«Un portafoglio può aver comprato dieci vincitori perché ha comprato diecimila monete.»*
> Grok: *«Il conteggio dei successi senza il numero di tentativi è la classifica dei bot.»*

Così ho smesso di contare le X e ho misurato **l'eccesso rispetto a chi ha fatto lo stesso numero
di tentativi**, togliendo i lanciatori. Il risultato è brutale:

| classifica per **conteggio** | tentativi | successi ≥10x | ritorno sul capitale |
|---|---|---|---|
| `0x65050a9b…` | **55.691** | 2.188 | **0,947x** (perde) |
| `0x6aa80dbb…` | 12.132 | 248 | **0,570x** (perde il 43%) |
| `0x8f10b468…` | 6.269 | 180 | 0,671x |

| classifica per **eccesso** | tentativi | successi ≥10x | ritorno sul capitale |
|---|---|---|---|
| `0x77c0dfa9…` | **19** | 19 | **157,8x** |
| `0xb2586df5…` | 28 | 25 | **77,1x** |
| `0xfe82b354…` | 3 | 3 | 60,0x |

**Chi fa più X sta perdendo soldi. Chi moltiplica il capitale fa pochissimi tentativi.** La
classifica che avrei fatto ieri metteva in cima esattamente i perdenti.

## E il migliore di tutti NON entra per primo

`0x77c0dfa98f7832…` è **un programma**, non una persona. Venti monete, **venti creatori diversi**
(quindi non è complicità con un lanciatore). Multipli ammassati intorno a 95x con punte a 490x.
Puntate minuscole e ripetute, tranne una da 0,27 tornata **22,4**.

Entra in posizione **4, 25, 29, 30, 36, 38, 40, 42, 49, 50** — mediana il **37°** — circa **43
secondi dopo il lancio**.

**Aspetta, guarda, e poi compra.** È l'esatto contrario della tesi da cui eravamo partiti.

E combacia con il «residuo che si rovescia» misurato poche ore prima: dal decimo posto in poi chi
entra tardi paga i gettoni fino a 2,4 volte più cari e ne recupera oltre la metà. **L'informazione
vale più dei gettoni.**

## La firma d'ingresso, su 93 casi

Allargando ai 7 portafogli con lo stesso profilo (≤200 tentativi, ritorno ≥3x, almeno 5 posizioni
chiuse), 93 ingressi osservati:

| cosa vedono al momento di comprare | **loro** | curva tipica, stessa posizione |
|---|---|---|
| compratori distinti già entrati | **27** | 19 |
| secondi dal lancio | **34** | 114 |
| capitale già raccolto | 0,56 | 0,97 |
| **capitale al secondo** | **0,0163** | **0,0082** |

Posizione mediana **32**. Entrano per primi nell'**1,1%** dei casi.

**Non cercano chi ha raccolto tanto: cercano tanta gente diversa arrivata in fretta.** Più
compratori distinti, in un terzo del tempo, con *meno* capitale raccolto. La **velocità di
partecipazione**, non la taglia.

Ha senso meccanico: molti indirizzi diversi che arrivano subito sono interesse reale; un solo
portafoglio che butta dentro capitale non lo è.

## Il limite, dichiarato prima che qualcuno me lo chieda

**Questi 7 portafogli li ho scelti perché hanno vinto.** La firma d'ingresso potrebbe essere
senno di poi: ogni vincitore ha una firma, il punto è se quella firma *prediceva*.

Serve il test che entrambi i revisori hanno chiesto, in quest'ordine:

1. **congelare** la regola (≥25 compratori distinti entro 40 secondi, o simile) usando solo ciò
   che si sapeva a una data T;
2. nel periodo **dopo** T comprare **tutte** le monete che la regola segnala — comprese quelle che
   non andranno da nessuna parte;
3. contare il patrimonio finale netto, con cassa finita, gas, e l'inventario valutato a quello che
   si incassa vendendolo davvero.

Se i 7 continuano a fare X ma il copiatore perde, la tesi è morta comunque.

## Cosa manca ancora

- **Gli indirizzi esentati dalla tassa** (fino a 32 per lancio, scritti nella transazione di
  creazione) non sono ancora esclusi. Sono privilegio, non abilità: vanno tolti prima di
  qualunque classifica.
- Sette portafogli sono pochi. La lista va allargata appena la copertura cresce.
- I 93 ingressi vengono da una finestra parziale della storia.
