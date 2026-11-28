# V2/V3 e' letto bene. L'invertita e' la V4 — il 56-82% delle pool.

*5 ottobre 2026 · verifica sulla chain, senza interpretazione*

## Il metodo, e perche' non lascia spazio a opinioni

Per una pool V2/V3 — che **e' un contratto** — si prende uno scambio **emesso da quella pool**
e si guarda **quale gettone le e' arrivato davvero**, confrontandolo con quello che l'evento
dichiara. Nessuna plausibilita', nessuna correlazione: cio' che l'evento dice contro cio' che i
gettoni hanno fatto.

## Il risultato

| | casi | coerenti | incoerenti |
|---|---|---|---|
| V2/V3, robinhood | **6** | **6** | **0** |

Esempi: `amount0` negativo → l'evento dice «entra token1» → e nella pool entra il memecoin
(STOCKIMPALER, KEKODYSSEUS, LEMON). Una **vendita**, letta correttamente.

**V2/V3 e' decodificato bene. Quindi, per differenza, l'invertita e' la V4** — che e' il
**56,1% delle pool su base e l'81,6% su robinhood**.

Questo conferma l'indizio del codice (nel V4 gli importi sono dalla prospettiva di chi scambia,
non della pool, e il nostro decodificatore li legge come quelli V3) e **smentisce** il test di
correlazione, che dava la direzione opposta — e che avevo gia' dichiarato debole (correlazioni
di −0,07 e +0,01).

## L'errore di metodo, che e' la parte utile di questo documento

La prima versione della corsia chiedeva `/addresses/{pool}/transactions`. Per una pool V2/V3
quell'elenco e' **vuoto per costruzione**: gli scambi non sono transazioni *verso* la pool, sono
transazioni verso il **router**, che poi la chiama. La pool non e' ne' mittente ne' destinatario.

E il punto non e' l'endpoint sbagliato — succede. Il punto e' che **ho messo in corsia un filtro
che non avevo mai visto riuscire nemmeno una volta.** I due tentativi a mano avevano gia'
restituito zero casi, e invece di chiedermi perche' ho scalato il fallimento a **1.600
transazioni e 2.400 strozzature**, su otto macchine.

> **Prima si fa funzionare una volta, poi si scala.** Uno zero ripetuto non e' un dato: e' un
> difetto che si sta moltiplicando.

L'endpoint giusto e' `/logs`: gli scambi sono **eventi emessi** dalla pool, e ogni evento porta
la sua transazione. Verificato su tre casi **prima** di riscrivere la corsia, e su sei dopo —
zero strozzature.

## Cosa comporta il verdetto

Tutto cio' che deriva da compra/vende e' **invertito** sulle pool V4:
`quota_acquisti`, `pressione_numero`, `pressione_delta`, `quota_solo_compra`, e la contabilita'
per portafoglio (`speso`, `incassato`, i quattro stati di posizione).

Quindi: il «gettoni usciti maggiori di quelli entrati» che ho inseguito per tutto il pomeriggio
**e' spiegato** — su quattro pool su cinque di robinhood, acquisti e vendite erano scambiati.

## Cosa manca prima di correggere

I sei casi sono **tutti nella stessa direzione** (`amount0` negativo). Serve confermare anche
il verso opposto — `amount0` positivo, cioe' un acquisto — prima di invertire qualcosa: una
convenzione si verifica in **entrambe** le direzioni, altrimenti si sta misurando un caso
particolare.

La corsia gira e archivia i casi uno per uno. Appena ci sono abbastanza esempi nei due versi,
la correzione diventa una decisione separata e documentata — non un aggiustamento.
