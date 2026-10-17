# L'assenza di record veri, spiegata

Per tre consulenze di fila la revisione esterna ha messo al primo posto la stessa cosa:

> «State perdendo tempo a celebrare zero record inventati: l'errore dominante dichiarato e'
> l'assenza di record veri. Con eventi mancanti non avete una misura di copertura ne' candele
> verificabili; avete contatori su un archivio potenzialmente troncato.»

Aveva ragione a metterla prima. Ma «manca il 66%» non era una cosa sola, ed e' per questo che tre
ipotesi di seguito sono cadute: le stavo sparando contro un bersaglio che era cinque bersagli.

## Il metodo

Una finestra che fallisce (base, blocchi 50819802-50819862): la catena dichiara **2.083 eventi**,
noi ne avevamo 88. Per OGNI evento ho chiesto, in ordine: il pool e' nel nostro registro? quella
finestra cade dentro la sua vita utile? il pool e' al tetto? e se e' passato da tutti i filtri,
**ce l'abbiamo davvero, quell'evento, con la sua transazione e il suo indice di log?**

Non un campione. Tutti e 2.083.

## Il risultato

| causa | eventi | quota | che cos'e' |
|---|---:|---:|---|
| il pool non e' nel nostro registro | 975 | 47% | **scelta**, non difetto |
| la finestra e' prima della nascita che gli abbiamo dato | 617 | 30% | **nascita sbagliata** |
| il pool e' al tetto di 300 righe | 149 | 7% | **scelta** dichiarata |
| la finestra e' oltre le prime 6 ore | 126 | 6% | **scelta** dichiarata |
| ce l'abbiamo | 88 | 4% | — |
| **manca davvero** | **128** | **6%** | **difetto** |

## Le due cose che contano

**1. Nessun buco dentro cio' che raccogliamo.** Dei 128 eventi che mancano davvero, **zero**
cadono in un tratto di blocchi che stavamo gia' leggendo. Tutti e 128 appartengono a due soli
pool che sono nel registro e per i quali **non abbiamo UNA SOLA RIGA**: il file non esiste.
Il difetto non e' «leggiamo male»: e' «di alcuni pool non abbiamo mai cominciato a leggere».

Questo ribalta la preoccupazione del consulente nel punto preciso in cui contava: l'archivio
**non e' troncato in mezzo**. Quello che entra, entra intero. Mancano interi pool, non frammenti
di pool — ed e' un guasto molto piu' facile da chiudere, perche' e' numerabile.

Quanti sono, su tutto il registro:

| chain | registro | con righe | **zero righe** |
|---|---:|---:|---:|
| base | 1.923 | 1.777 | **146 (8%)** |
| robinhood | 797 | 593 | **204 (26%)** |

350 pool registrati e mai letti. Su robinhood e' un quarto del registro.

**2. Le nascite di ripiego sono il secondo errore, e sono tutte della stessa specie.** Dei 617
eventi «prima della nascita», **306 su 306 verificabili vengono da una nascita di ripiego** presa
dalla prima candela — e **nessuno** da una nascita risolta sulla catena. Zero. La prima candela
non e' la nascita: e' il momento in cui ABBIAMO COMINCIATO A GUARDARE. Quando la usiamo come
nascita, gli eventi veri precedenti finiscono classificati come «fuori vita» e spariscono dal
conto senza lasciare traccia.

Oggi la nascita e' risolta sulla catena per l'84% di base ma solo il **62%** di robinhood. Quel
38% residuo e' esattamente la popolazione che genera questa classe di sparizioni.

## Cosa cambia

La frase «manca il 66%» andava letta cosi': **l'86% di quel 66% sono scelte nostre o nascite
sbagliate, il 6% e' un difetto vero, e lo 0% e' corruzione dell'archivio.**

Il che vuol dire che il gate non si chiude accumulando di piu'. Si chiude con due lavori precisi:
leggere i 350 pool mai letti, e portare la nascita da catena vicino al 100% su robinhood.

Entrambi sono finiti e contabili. Nessuno dei due e' «raccogliere ancora un po'».
