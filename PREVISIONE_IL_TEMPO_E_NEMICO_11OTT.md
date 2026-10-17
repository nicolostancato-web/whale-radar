# Previsione registrata: il tempo è nemico

**Scritta l'11 ottobre con 31 chiusure, PRIMA di misurare sulle prossime.**

## Il pattern trovato nei dati live

Provando le uscite **a tempo** — la famiglia di regole più onesta su pochi casi, perché non
sceglie nulla e si applica a tutte le monete allo stesso modo:

| regola | media | intervallo | mediana | vinte |
|---|---|---|---|---|
| 2x secco (la regola viva, orizzonte 16,7 h) | +4,3% | ±27,5 | −15,4% | 14/31 |
| esci dopo 5 min, qualunque sia | +5,5% | ±17,1 | −4,0% | 14/31 |
| esci dopo 15 min | +17,0% | ±25,8 | −2,5% | 15/31 |
| esci dopo 60 min | +21,5% | ±36,5 | −13,8% | 14/31 |
| esci dopo 240 min | +25,2% | ±55,4 | −25,3% | 12/31 |
| esci dopo 720 min | +0,6% | ±37,4 | −38,2% | 10/31 |
| **2x, ma al massimo 15 min** | **+11,0%** | **±17,9** | **+3,1%** | **16/31** |
| 2x, ma al massimo 60 min | +12,7% | ±23,7 | −4,3% | 15/31 |

**Tutti gli intervalli contengono lo zero: nessuna riga dimostra niente.** Quello che si vede è
una **forma**, e la forma è monotona su quattro valori: la mediana peggiora man mano che si resta
dentro — −2,5% a 15 minuti, −13,8% a un'ora, −25,3% a quattro ore, −38,2% a dodici. Una monotonia
su quattro punti è difficile da ottenere per caso.

E una riga sola ha la **mediana positiva** e l'**intervallo più stretto**: 2x con un tetto di 15
minuti (+3,1% di mediana, ±17,9). L'intervallo stretto conta più della media alta, perché è la
dispersione che uccide il capitale composto.

## Le previsioni, perché siano falsificabili

Sulle **prossime 30 chiusure**:

1. **La mediana continuerà a peggiorare con l'orizzonte**, nello stesso ordine: 15 min meglio di
   60, 60 meglio di 240, 240 meglio di 720. Se l'ordine si rompe in più di un punto, il pattern
   era rumore e lo scriverò.
2. **«2x al massimo 15 min» resterà fra le due righe con l'intervallo più stretto.**
3. **La mediana di «2x secco» resterà negativa.** Se diventa positiva, la regola viva è migliore
   di quanto dicono questi 31 casi.

## Cosa NON cambio, e perché

La regola viva resta **2x secco con orizzonte 16,7 ore**, congelata. Cambiarla adesso su un
pattern con tutti gli intervalli che contengono lo zero vorrebbe dire rendere le posizioni nuove
non confrontabili con le vecchie, cioè bruciare il solo campione pulito che abbiamo — per
inseguire una differenza che potrebbe non esistere.

**Ma se la previsione 1 regge sulle prossime 30, l'orizzonte va accorciato**, e c'è un secondo
vantaggio che vale quanto il primo: con un tetto di 15-60 minuti le posizioni si chiudono in
minuti invece che in ore, quindi il campione cresce **dieci volte più in fretta** — e il vincolo
vero di questo progetto non è l'idea, è la velocità con cui si può falsificarla (servono ~120
posizioni per braccio per distinguere 20 punti).

## La nota di cautela, risolta il giorno stesso

La prima versione di questo documento diceva che la simulazione ricostruiva la regola viva con
uno scarto massimo di **12,7 punti**, e che andava capito prima di fidarsi. L'ho capito:

Il cammino campiona un prezzo ogni cinque scambi, e **nell'istante dell'uscita all'orizzonte**
l'ultimo campione non è l'ultimo prezzo. Su due monete in caduta rapida la simulazione dava
−63% dove la realtà era −75%.

**La direzione dell'errore è quella che conta:** la simulazione era OTTIMISTA sulle uscite a
orizzonte lungo, quindi rendeva le righe lunghe migliori di quanto sono. Il pattern «il tempo è
nemico» era dunque **sottostimato**, non gonfiato — la correzione lo rafforza.

Corretto usando il prezzo vero dell'uscita, che la prova registra. Lo scarto massimo è ora
**0,5 punti su 31 posizioni**, e la riga della regola viva è passata da +5,3% a **+4,3%** di
media e da −14,7% a **−15,4%** di mediana. Le altre righe non cambiano: non erano affette.
