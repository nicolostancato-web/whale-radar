# Dieci su dieci: le transazioni esistono e sono loro. Ma gli IMPORTI non sono ancora provati.

*6 ottobre 2026 · prima volta che il cancello passa, e cosa resta aperto*

## Il risultato

Campione a caso (seme 20261006) di posizioni oltre 2X, ognuna con l'hash della sua
transazione d'acquisto allegato:

| | esito |
|---|---|
| transazioni che **esistono** sulla chain | **10 su 10** |
| firmate dal portafoglio che **noi** attribuiamo | **10 su 10** |
| falsi | **0** |

Esempi: `0xaf2bfb6b69…` a 15,1X, `0xdd509c9f91…` a 15,9X, `0x1886538cf5…` a 16,5X — tutte
verificate, su entrambe le chain.

## Quindi il «10 su 10 falsi» di due ore fa era il mio cancello, non i dati

Il cancello precedente cercava i **trasferimenti del gettone nel portafoglio**. Ma in un
mercato automatico il gettone in uscita va al **destinatario dello scambio** — un router o un
contratto del bot, verificato `is_contract=True` — e **mai al firmatario**. Bocciava anche i
dati giusti.

Vale annotare la sequenza, perche' e' istruttiva: il controllo a campione di Nicolo' ha
smentito un nostro numero (giustamente), io ho costruito un cancello che ha bocciato tutto, e
il cancello era rotto. **Due errori diversi, e il secondo mi ha quasi fatto buttare dati
buoni.** Un controllo troppo severo non e' prudente: e' sbagliato in modo opposto, e costa
quanto l'altro.

## Cosa e' provato, e cosa NON lo e'

**Provato:** la transazione esiste, l'ha firmata il portafoglio che diciamo, nella pool che
diciamo. L'**esistenza** e l'**attribuzione** dello scambio.

**NON provato: gli IMPORTI.** Il multiplo nasce da `incassato / speso`, e quei due numeri
dipendono da quale lato e' la valuta, dai decimali e dal prezzo. Tutte cose che oggi hanno
sbagliato almeno una volta ciascuna.

Ed e' esattamente cio' che Nicolo' chiede di poter verificare: «deve vedere che questo wallet
ha comprato a 10 e ha venduto a 50». Noi oggi possiamo provare che **ha comprato**, non ancora
**a quanto**.

## Il prossimo passo, dichiarato

Per ogni transazione della prova, leggere gli **importi dell'evento di scambio** dalla chain e
confrontarli con quelli che abbiamo registrato. Se coincidono, il multiplo e' difendibile e i
dati si possono dichiarare veritieri. Se no, il difetto e' negli importi — ed e' l'ultimo
posto dove puo' nascondersi.

Finche' non e' fatto, la risposta a Nicolo' resta **«sto ancora lavorando»**. Ma per la prima
volta so **quale** pezzo manca, invece di sospettare tutto.
