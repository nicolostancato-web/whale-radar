# La prova in avanti misurava tutt'altro: azzerata e rifatta — 8 ottobre 2026

## Cosa non andava

La prova riconosceva i pool da `coppie.json`, il nostro registro — che contiene i pool **già
noti**, cioè vecchi. Quindi non vedeva le monete appena diplomate: vedeva **pool vecchi che
scambiavano adesso**, e chiamava «primo scambio del pool» il primo che capitava di leggere in quel
giro.

Controllate otto posizioni aperte, confrontando il blocco di lancio della moneta col blocco del
presunto primo scambio:

| moneta | ore fra il lancio e il «primo scambio» |
|---|---|
| `0xe9e5cfdc…` | **724** |
| `0x3786728a…` | **915** |
| `0x4f9be3c0…` | 755 |
| `0xa36fbbe3…` | 59 |

Otto su otto erano vecchie. **Tutto quello che la prova aveva accumulato in otto ore era senza
valore**: 985 posizioni, buttate. Nessuna era chiusa, quindi non ho buttato risultati — ma se
avessi aspettato il verdetto avrei portato a Nicolò un numero su una cosa che non esiste.

## Come l'ho scoperto, ed è il punto

Non guardando i conti della prova: quelli sembravano sani (nuove posizioni, finestre, scarti).
L'ho visto **confrontando due numeri che non avevo mai confrontato** — il blocco di lancio della
moneta e il blocco del suo presunto primo scambio.

Era partito tutto da un'anomalia: la prova scartava il **99,4%** delle monete, contro il **9,9%**
che il campione storico dice comprabili. Un numero che non torna va inseguito, non spiegato.

## Com'è adesso

Un pool è nuovo quando **la chain dice che è stato creato**: evento `Initialize` emesso dal gestore
Uniswap v4, che porta l'id del pool e le due valute. Niente registro, niente deduzioni.

La prova riparte dal blocco **83.484.901**, con le stesse regole di prima — entrata 600 blocchi
dopo la creazione, uscita al raddoppio, orizzonte 16,7 ore (corretto il 9/10: 600.000 blocchi NON sono 7 giorni), costi e scivolamento misurati.

## Cosa resta vero di oggi

Che è il terzo difetto della stessa famiglia trovato in dodici ore: il registro che fa da campione.
Ha falsificato il +18,9%, la sensibilità del segnale sul diploma (91,8% invece di 63%), il +83,9%
che era +48%, e ora la prova in avanti.

**Il registro non è una fonte: è un appunto.** Ogni misura che lo usa come campione è sospetta
finché non viene rifatta dalla chain.
