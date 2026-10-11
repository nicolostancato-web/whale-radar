# Non lo 0,77%: si diploma l'8% — e il nostro registro vedeva un pool su dodici

8 ottobre 2026. Correzione di un numero che ho ripetuto per giorni.

## Come l'ho scoperto

Misurando le **false sveglie** del segnale «la curva ha incassato 3,8 ETH in 60 minuti». Nel
campione risultavano 8 monete che avevano incassato **5-11 ETH** senza diplomarsi — impossibile,
perché la soglia è 4,2.

Controllate sulla chain, una per una: **tutte e otto avevano un pool**. Erano diplomate, e il
nostro registro non lo sapeva.

## Il tasso vero

Su 150 lanci presi a caso, verificando sulla chain l'esistenza del pool (trasferimenti del gettone
verso il gestore dei pool di Uniswap v4):

| | |
|---|---|
| hanno un pool, cioè si sono **diplomate** | **12 su 150 = 8,00%** |
| presenti nel **nostro** registro | 1 su 150 = 0,67% |
| **copertura del nostro registro** | **8% delle diplomate** |

**Si diploma l'8%, non lo 0,77%: una su dodici, non una su centotrenta.** Il «0,77%» era la quota
di monete di cui *noi* avevamo il pool, non la quota che gradua — e per giorni l'ho ripetuta come
se fosse un fatto del mondo.

## Le tre conseguenze, in ordine di peso

**1. Il segnale a 3,8 ETH è quasi deterministico.** Delle 8 presunte false sveglie, zero erano
false. Non sorprende: incassare 4,2 ETH **è** il diploma, e fermarsi a 3,8 è raro. Il valore del
segnale non è indovinare, è **sapere quando guardare** — e quello funziona.

**2. L'occasione è dieci volte più grande di quanto dicevo.** Una moneta su dodici arriva al
mercato vero, non una su centotrenta. Questo cambia la scala del lavoro, non la direzione.

**3. E qui la parte scomoda: tutte le misure sul mercato dopo il diploma vengono da un campione
preso dal registro**, che copre un pool su dodici. Se il registro contiene i pool che i nostri
raccoglitori hanno *visto scambiare*, allora contiene i più **attivi** — e il +18,9% della regola
senza selezione potrebbe essere misurato su una fetta fortunata del mondo.

## Perché la prova in avanti era già la cura

La prova aperta stamattina **non usa il registro**: riconosce i pool nuovi dagli scambi del gestore
di Uniswap v4, in diretta. Quindi vede tutte le diplomate, non una su dodici — ed è l'unico
giudice che non eredita questo difetto.

Il che vuol dire: il +18,9% resta **sospetto di selezione** finché la prova in avanti non lo
conferma su monete viste in diretta. Lo scrivo adesso, non quando i numeri mi smentiranno.

## Cosa faccio

1. Rifaccio il registro delle diplomate dalla chain, non dai pool che abbiamo visto per caso: la
   verifica costa **una chiamata per moneta** e la copertura passa dall'8% al 100%.
2. Rimisuro il mercato dopo il diploma su un campione **casuale di diplomate vere**.
3. La prova in avanti continua: è l'unica cosa che oggi non ha questo difetto.
