# Il secondo occhio sulla gara — verificato il 7/11/2026

## Il problema, misurato

Censimento di **30 indirizzi websocket gratuiti** col criterio giusto
(`agents/censimento_porte.py`): consegna transazioni intere leggibili
**UNO SOLO**, publicnode.

- **drpc**: accetta la richiesta di transazioni intere, **non da' errore**, e
  manda solo gli hash. 25.333 messaggi in 34 minuti, **zero utili**. Su 177
  campanelle publicnode e' stata prima 177 volte, drpc zero.
- **tenderly**: muta (zero messaggi in 35 secondi), cadeva 40 volte l'ora.
- **le altre 27**: rifiutano il saluto, chiedono una chiave, o sono morte.
- **`ethereum.publicnode.com`** funziona ma risolve agli **stessi due
  indirizzi IP** di `ethereum-rpc.publicnode.com`: non e' un secondo
  fornitore, protegge solo dall'essere strozzati su un nome.

**Quindi: un solo fornitore ci serve il mempool, ed e' caduto 2 volte in 5
ore.** Se cade, siamo ciechi sull'unica cosa che decide se vinciamo.

Un flusso di soli hash **non si recupera** come ripiego: per sapere se un
hash e' un aggiornamento d'oracolo bisogna risolverlo con una richiesta di
rete, e ne arrivano 12 al secondo — ci farebbero bandire in un minuto.

## La soluzione, ed e' GRATIS

Alchemy ha `alchemy_pendingTransactions`, che fa due cose che nessuna porta
gratuita fa:

1. **restituisce la transazione intera** col campo `input` (quindi il
   selettore si legge senza una seconda richiesta);
2. **filtra lato server per `toAddress`** — possiamo chiedere SOLO le
   transazioni dirette ai forwarder Chainlink.

Il filtro cambia tutto, in tre modi: ci rende indipendenti da publicnode,
riduce il nostro carico da ~43.000 messaggi l'ora a ~35, e togliendo quel
lavoro dal processo libera il filo caldo (e' la stessa causa che faceva
costare 84-304 ms la composizione di un pacchetto).

## I conti, verificati oggi sul sito ufficiale

- piano gratuito: **30 milioni di CU al mese**, permanente (non una prova);
- le sottoscrizioni si pagano **a banda: 0,04 CU per byte**, cioe' ~40-80 CU
  per transazione intera;
- **con il filtro** `toAddress`: ~35 campanelle/ora = ~25.200 al mese
  x 80 CU = **~2 milioni di CU/mese = il 7% del gratuito**. Costo **0 euro**.

## ⚠️ LA TRAPPOLA, e va detta prima

**Senza** il filtro `toAddress` sarebbero 12 messaggi/secondo = ~31 milioni
di messaggi al mese x 40 CU = **1,24 MILIARDI di CU**. Oltre il gratuito si
paga **$0,52 per milione**, quindi circa **$640 al mese** (~€780 con IVA).

E' esattamente lo schema dei €77,51 di Google Places: un piano "gratis fino
a tanto" dove un parametro dimenticato moltiplica il consumo per seicento.

**Regole non negoziabili se si fa:**
1. il filtro `toAddress` e' **obbligatorio**, scritto nel codice e verificato
   dal C-check a ogni giro;
2. **nessun metodo di pagamento** sull'account Alchemy, cosi' il tetto e'
   fisico: finito il gratuito si ferma, non addebita;
3. un contatore del consumo nel C-check, con allarme al 50% del gratuito.

## Cosa serve da Nicolo'

Un account Alchemy gratuito (email + password, nessuna carta) e la chiave API
nel file delle credenziali, sezione `=== ALCHEMY ===`. Io non posso creare
account. Il resto lo scrivo io.

**Senza carta registrata non c'e' rischio di addebito**, e questo e' il punto
che rende la cosa diversa dal caso Google.
