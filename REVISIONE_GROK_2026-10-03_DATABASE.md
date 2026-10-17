# Revisione di Grok sul database degli attori — 3 ottobre 2026

Domanda posta mentre fermavamo la ricerca tecnica per costruire il database: come riconoscere
un'ENTITA' senza il finanziatore, e come progettare lo SCHEMA perche' la sopravvivenza non
possa entrarci. Revisore ostile, costo zero (abbonamento).

## Cosa ho verificato subito, e l'esito

**Il colpo centrale: l'effetto disposizione.** «Chi vende i vincenti e tiene i perdenti ha un
tasso alto sul passato chiuso E sul futuro chiuso, perche' il futuro entra nel campione solo
quando viene venduto. Le quattro flotte su cinque che non hanno mai venduto sono la massa che
questo filtro cancella. Il taglio delle sei ore non lo tocca.»

**Verificato nel codice: NON colpisce i +19/+18.** In `agents/combinazioni.py` riga 202 il
passato di un portafoglio registra `x["_bersaglio"]`, cioe' **l'esito del POOL** — quello che
avrebbe fatto un compratore qualunque — non se quel portafoglio ha venduto in guadagno. Il
campione non e' condizionato dalla politica di uscita.

**Ma colpisce in pieno il registro dei vincenti** che stiamo per costruire, perche' quello si
basa sul conto in dollari REALIZZATO, cioe' solo su chi ha venduto. L'avvertimento arriva nel
momento esatto in cui serviva.

## Le due obiezioni che PRENDONO i +19/+18, e che non avevo considerato

**1. Sopravvivenza del capitale.** Vediamo la moneta successiva di un portafoglio solo se
continua a comprare, e per comprare servono soldi: «ha vinto prima» e' in parte un proxy di
«esiste ancora». Serve il saldo immediatamente prima della decisione successiva. **Non testato.**

**2. Il controllo e' diluito.** I compratori di un'altra moneta della stessa ora si SOVRAPPONGONO
a quelli della moneta trattata. Piu' si sovrappongono, piu' il controllo e' una copia annacquata
dello stesso effetto, e +6 contro +41 diventa rumore di composizione invece di un nullo.
**Non misurato: va calcolata la sovrapposizione fra le due coorti.**

**3. Il 55,9% non e' abilita'**, e va misurato anche pesato sui dollari: con code da memecoin
mediana e media raccontano due storie, e stiamo per costruire sulla metrica ordinabile.

**4. I 62,9 milioni sono una valutazione, non denaro.** «Un artefatto finche' non mostri quanti
dollari escono davvero dalla pool con un impatto del 2%.» Finche' non lo mostro, quel nodo non
entra nel grafo come padre di nessuno: e' «un hub finto che ti terra' occupato».

## Il resto della revisione, integrale

Il controllo sulla seconda chain vale +41 e l'effetto +18. Se quei quattro numeri sono lordi, una delle due chain non ha replicato: ha vinto il nulla. Il quinto migliore è sotto zero su entrambe. Un database di attori non trasforma questa cosa in un'aspettativa positiva. La congela.

La lettura che segue tratta +19 e +18 come effetto e +6 e +41 come controllo. Se invece +19/+18 sono già il residuo dopo sottrazione, i numeri non sono auditabili: un residuo di +18 accanto a un nullo di +41 non si può ricostruire. In quel caso il primo lavoro è pubblicare i quattro lordi, non progettare tabelle.

## Cosa è già rotto, prima dello schema

L'effetto è identificato solo dalle persone con almeno due posizioni chiuse. Le 11.638 con "almeno una chiusura" includono chi ha una sola chiusura: quelle fissano il 55,9% e non identificano nessuna transizione. Non hai detto quante hanno N≥2. Se sono poche, +19 punti è un N piccolo con errore standard calcolato come se 11.638 scommesse fossero indipendenti. Le flotte dimostrano che non lo sono.

Il 55,9% non è abilità. È la frazione di chi ha chiuso ed è in guadagno. Mediana dei guadagni +27$, mediana delle perdite −18$, niente media, niente media pesata sui dollari. Con code da memecoin la mediana e la media raccontano due storie diverse, e tu stai per costruire il database su quella che si può ordinare.

C'è un meccanismo che produce autocorrelazione sulle chiuse senza alcuna abilità, e il taglio delle 6 ore non lo tocca. Chi vende i vincenti e tiene i perdenti (effetto disposizione) ha un tasso alto sul passato chiuso e un tasso alto sul futuro chiuso, perché il futuro entra nel campione solo quando viene venduto. Le 4 flotte su 5 che non hanno mai venduto sono esattamente la massa che questo filtro cancella. Il controllo "compratori di un'altra moneta della stessa ora" non rompe il meccanismo: misura un'altra coorte, non la politica di chiusura dello stesso indirizzo. Il +41 è compatibile con coorte e sopravvivenza del capitale, non con un residuo di abilità.

Sopravvivenza del capitale: osservi la moneta successiva solo se il portafoglio ha ancora soldi per comprarla. "Ha vinto prima" è un proxy di "esiste ancora". Senza il saldo immediatamente prima della decisione successiva, il passato predice il futuro per questo motivo.

Il controllo è pulito solo se i compratori della moneta di controllo sono quasi disgiunti dai compratori della moneta trattata. Sulla stessa ora, sulla stessa chain, le persone si sovrappongono. Più si sovrappongono, più il controllo è una copia diluita dello stesso effetto, e +6 contro +41 diventa rumore di composizione, non un nullo.

## 1. Riconoscere l'entità senza il finanziatore

Oggi il buco non è "manca un'euristica sofisticata". È che il grafo del valore è incompleto. 83 finanziatori su 11.275 significa che stai guardando quasi solo il nativo. Chi si finanzia in stablecoin, chi riceve il gas da una chiamata interna, chi passa da un paymaster, nel tuo grafo non ha padre. Sono sovrarappresentati proprio tra chi ha un motivo per non sembrare un EOA fresco finanziato da un amico.

Ordine di affidabilità. Per ognuno: cosa aggrega davvero, e l'unico falso che lo uccide.

### A. Misure di flusso, non somiglianze. Precisione alta, copertura ancora bassa

**1. Stessa chiave ECDSA.** Stesso indirizzo EOA su Base e sull'altra chain è la stessa chiave. Su uno smart account, il proprietario recuperato dalla firma dello UserOperation è la stessa mano su più account. È il legame migliore che i dati pubblici ti danno, perché non inferisce: verifica una firma.

Falsificazione: il firmatario che recuperi è il bundler, il paymaster o una session key, non il proprietario. Se due utenti dello stesso bundler finiscono nello stesso cluster, l'euristica è morta. Test a costo zero: prendi i bundler e i paymaster che compaiono in migliaia di UserOp e verifica che la tua regola non aggreghi i loro `sender`. Dopo EIP-7702 il test "ha bytecode quindi è un contratto" è falso: un EOA delegato ha codice e resta la stessa chiave. Il test giusto è recuperare la chiave, non classificare il codice.

**2. Catena di valore con conservazione.** A invia nativo o stable a B, B a C, in pochi minuti, importo che torna a meno del gas, senza interazione con terzi in mezzo. Vale anche per uno stable (USDC e simili) e per WETH, non solo per il gas. Vale per il trasferimento interno nella stessa transazione, se Blockscout te lo mostra: il padre è il chiamante del contratto, non il contratto.

Falsificazione: il mittente è infrastruttura che non hai ancora etichettato. Su una chain giovane la lista dei ponti, faucet, dispenser, relayer è vuota, quindi la regola fallisce aperta e fonde estranei. Uccisione concreta: due indirizzi finanziati dallo stesso hot wallet di un exchange, o dallo stesso contratto di bridge, non devono mai fondersi. Se si fondono, butti la regola, non "la tieni per i casi ovvi". I casi ovvi sono il modo in cui la selezione entra nel grafo.

Secondo uccisione: l'importo non si conserva. Un passaggio da un router o un rimborso parziale non è una pelatura.

**3. Finanziamento in batch in una sola transazione**, da un mittente che non è infrastruttura: una disperse che manda importi simili a N indirizzi nuovi.

Falsificazione: il mittente ha migliaia di destinatari, oppure è un faucet, un claim, un airdrop di piattaforma. Soglia scritta prima: destinatari massimi e età del mittente. Un contratto giovane con 8 destinatari è una flotta. Un contratto con 4.000 destinatari è un prodotto. Se abbassi la soglia finché non riacciuffi la flotta da 263$, la soglia è scelta sull'esito.

**4. Spender o operator oscuro in comune.** Molti EOA che danno approval allo stesso contratto, e quel contratto non è un router pubblico (Universal Router, Aerodrome, un bot noto con migliaia di utenti). Un operator privato con pochi utenti, finanziato dalla stessa catena di valore, è una mano.

Falsificazione: togli i router e i bot pubblici e il cluster si scioglie. Allora avevi aggregato i clienti di un prodotto. Il test si fa sulla popolarità dello spender misurata su tutti gli indirizzi, non sui vincenti.

**5. Deployer diretto, non factory.** Lo stesso EOA che dispiega più token, oppure che finanzia i compratori, lega i lanciatori. È un'entità utile e non è l'entità dei compratori. Tenerle nella stessa tabella `actors` è il modo in cui un lanciatore seriale diventa "smart money".

Falsificazione: il bytecode è quello di una factory di lanci (sulla Base di oggi: i template condivisi). Stesso bytecode di factory significa stessa piattaforma. Clusterizzare dopo aver strippato gli argomenti immutabili del template; se il cluster resta grande quanto la piattaforma, è la piattaforma.

### B. Utilizzabili solo come eccesso rispetto a un nullo, mai come regola di merge

**6. Stesso indirizzo cross-chain solo dopo aver verificato che sia un EOA (o la stessa chiave), non un contratto dispiegato in CREATE2 da una factory canonica.** Due Safe o due smart wallet con lo stesso indirizzo su due chain possono essere la factory, non la persona.

Falsificazione: ricalcoli l'indirizzo atteso dalla factory a partire da un owner noto. Se collassa, l'uguaglianza di indirizzo era il counterfactual della factory.

**7. Co-acquisto in eccesso, non co-acquisto.** Comprire la stessa moneta nuova non lega nessuno: è la moneta. Su una L2 il sequencer mette nello stesso blocco gente che non si è mai vista, e il mempool pubblico non è quello di Ethereum. "Stesso blocco" è un nullo.

Falsificazione: il tasso di co-presenza tra portafogli nuovi sul lancio più comprato dell'ora. Un legame conta solo se l'eccesso sopravvive a quel tasso e a una permutazione che conserva quante monete compra ogni indirizzo e quanti compratori ha ogni moneta. Se l'eccesso muore sotto quel nullo, era la popolarità della moneta. Jaccard sui token senza questo nullo è una tautologia, e se lo usi sia per fondere le entità sia per misurare l'abilità la misura è circolare.

### C. Sembrano solidi. Non lo sono

**8. Finanziatore comune se il finanziatore è un exchange, un bridge, un paymaster, un bundler, un relayer.** È il falso merge classico. I tuoi tre grandi (5,6M$, 62,9M$, 23,6M$ con 65, 371, 172 transazioni in tutta la vita) non sono "non-exchange" solo perché hanno poche transazioni. Quel profilo è anche un tesoro, un bridge, un market maker, o un saldo prezzato a uno spot che non può essere venduto. 62,9M$ con 371 transazioni è un artefatto di valutazione finché non mostri quanti dollari escono davvero dalla pool con un impatto del 2%. Finché non lo mostri, quel nodo non entra nel grafo come padre di nessuno: è un hub finto che ti terrà occupato.

Falsificazione del saldo: vendi virtualmente contro le riserve del blocco, non contro l'ultimo prezzo. Se l'eseguibile è centinaia di dollari, il "finanziatore da 62,9M$" è una riga di contabilità.

**9. Priority fee, gas price, method id, router, nonce al primo acquisto.** Sulla Base post-1559 la priority fee è il default del wallet. Rabby, MetaMask e Coinbase Wallet producono la stessa impronta su persone diverse. Il nonce basso è la coorte intera delle memecoin, non una mano: aggregare su nonce=0 fonde tutti i portafogli nuovi. Il nonce è una proprietà dell'indirizzo, da tenere come covariata, mai come chiave di cluster.

Falsificazione: la similarità dentro i tuoi cluster deve battere la similarità tra utenti distinti dello stesso software, nello stesso ora. Se non la batte, stai clusterizzando il wallet software.

**10. Orario di attività e intervallo tra transazioni.** L'attività è guidata dal lancio. L'ora è della moneta, non della persona.

Falsificazione: permuti gli indirizzi dentro lo stesso insieme di monete. Se la similarità circadiana resta, era il calendario delle monete.

**11. "Non ha mai venduto" come tratto dell'entità.** È un esito censurato. Le 4 flotte su 5 sono il pattern atteso di un bundle di lancio che non ha ancora scaricato, o di borse morte. Non è un'identità e non è convinzione.

**12. Qualsiasi regola comportamentale aggiustata a mano** dopo aver visto che la flotta da 263$ faceva 3 su 3. N=5 flotte, una sola con vendite, 263$. Non è un campione. È un aneddoto che sta per diventare una soglia.

Regola di lavoro, dato il vincolo RPC pubblico e Blockscout: prima chiudi il grafo del valore (nativo, stable, interni Blockscout, owner delle UserOp), con una coda FIFO su tutti gli 11.275 e non sui vincenti. Poi le regole A, scritte con soglie fissate prima di guardare il PnL. Le regole B solo come feature in eccesso al nullo. Le regole C non si implementano. `debug_trace` sui RPC pubblici spesso non c'è: se non c'è, non lo sostituisci con una somiglianza. Segni il padre come mancante.

La copertura resterà bassa. Va bene. Alzare la copertura abbassando la precisione, e giudicare il risultato dal fatto che "ora le flotte tornano", è il modo in cui gli estranei entrano nel tasso di vincita di qualcuno.

## 2. Lo schema, perché la sopravvivenza non possa entrarci

Il principio: il database registra esposizioni e fatti con il blocco in cui sono diventati pubblici. L'esito si calcola al momento della query, con un tempo di decisione passato come parametro. Non esiste una colonna `winner`, `smart_money`, `win_rate` o `entity_id` aggiornata sul posto. Se quelle colonne esistono, ogni analisi successiva è una lettura della selezione, e nessuna correzione a valle la toglie.

Unità che entrano da sole, nel momento in cui appaiono, prima di qualsiasi chiusura:

- ogni firmatario, ogni destinatario di valore, ogni mittente di valore;
- ogni moneta nel momento in cui ha una pool, non nel momento in cui qualcuno del tuo campione la vende;
- ogni tentativo di acquisto revertito (Blockscout li mostra). Un revert è una decisione. Tenerlo fuori arricchisce il campione di chi è stato riempito.

Cose che oggi, da come descrivi il sistema, non stai registrando e che decidono se il +19 è disposizione, capitale, o altro.

**Saldo immediatamente prima di ogni decisione**, in nativo e negli stable maggiori, più il massimo eseguibile contro la pool in quel blocco. Senza questo, "ha vinto prima" non è separabile da "ha ancora i soldi".

**Chiusura e orizzonte fisso come due fatti diversi.** Per ogni acquisto: ogni uscita parziale (lotto, non booleano "chiuso"), e il mark-to-market a 1h, 6h, 24h, 48h che la posizione sia aperta o no. Prezzo, riserve, liquidità eseguibile, blocco del prezzo, fonte. Lo storico del prezzo non si aggiorna. "Ancora aperto" senza mark è un buco, e il buco è correlato con l'esito: è lì che siedono le 4 flotte.

**Il campione della moneta successiva si definisce all'acquisto, non alla vendita.** Se la riga nasce quando la posizione si chiude, hai già messo la disposizione dentro la chiave primaria.

**Insieme a rischio.** Per ogni indirizzo e ogni ora in cui era attivo e aveva saldo eseguibile sopra una soglia fissata prima: le monete nate in quell'ora che non ha comprato. Senza i non-acquisti hai il rendimento condizionato all'aver tradato, che è ciò che hai già misurato, non l'abilità di scelta. Se non sai definire l'esposizione, registri esplicitamente che l'esposizione è ignota, e non calcoli un tasso di selezione.

**Assenze da non confondere con zeri.** Non indicizzato fino al blocco X. Prezzo mancante (diverso da prezzo zero: un rug senza print non è uno zero pulito). Nessuna vendita entro l'orizzonte. Nessun padre nel grafo di finanziamento. Transazione revertita. Trasferimento ricevuto che non è un acquisto. Ognuna di queste è uno stato, non una riga che non scrivi.

**`known_at` su ogni fatto.** La vista che produce le feature prende `decision_time` e può usare una chiusura solo se `exit_time <= decision_time - 6h`. La regola delle 6 ore vive nella vista, non in un notebook. Un tasso ricalcolato con lag zero deve essere impossibile da quella vista, non "sconsigliato". Le posizioni ancora aperte a `decision_time` contribuiscono uno stato censurato, non un tasso parziale e non un'esclusione.

**Il controllo assegnato prima.** Per ogni decisione, la moneta di controllo della stessa ora è scelta e salvata in quel momento, insieme alla sovrapposizione tra i due insiemi di compratori. Rifare il controllo dopo aver visto +41 è un secondo sguardo. La vista di valutazione non restituisce un PnL di persona se non affianca il basale della coorte.

**I legami sono asserzioni, non identità.** Tabella `link(addr_a, addr_b, heuristic_id, evidence_tx, created_at, retracted_at)`. L'entità è una vista sulle asserzioni non ritirate. Quando un test del punto 1 uccide un'euristica, ritiri le righe. Non riscrivi la storia. Un `entity_id` sulla persona è permanente: i merge falsi restano nel tasso, e tu scioglierai i cluster che hanno perso e terrai quelli che hanno vinto. Quella pulizia manuale è la selezione dentro la struttura.

**Lo split è temporale e scritto prima.** Blocchi di scoperta e blocchi di conferma, assegnati dalla data, non dall'esito. Le soglie (N minimo di chiusure, dollari minimi, dimensione flotta, nonce) stanno in una tabella `hypothesis` con il momento in cui sono state fissate. Una soglia nata guardando la flotta da 263$ è scoperta, anche se la chiami definizione.

**PnL di indirizzo e PnL di entità sono due estimand diversi e non si validano a vicenda.** Prima il PnL di indirizzo, con i trasferimenti interni alla flotta che non contano come vendite solo sotto un'euristica già congelata. Se aspetti le entità perfette per calcolare i rendimenti, non avrai mai un numero non selezionato. Se calcoli i rendimenti e poi fondi usando i rendimenti, il merge è scelto sull'esito.

**Niente tasso grezzo ordinabile.** Con N=1 il tasso è l'esito stesso. Una colonna `win_rate` verrà ordinata, e in cima ci saranno i 100% a una sola operazione. Se proprio materializzi un punteggio, è uno shrinkage verso il tasso base, con il denominatore salvato accanto, ricalcolabile as-of, e la vista non permette `ORDER BY` su un tasso con N sotto la soglia pre-registrata. Meglio non materializzarlo.

**Coda di indicizzazione FIFO**, con `indexed_through_block` per indirizzo. Blockscout e i RPC pubblici hanno un limite di frequenza. Se tracci per primi i PnL alti, la mancanza del padre diventa correlata con l'esito. A quel punto "83 finanziatori" non è un fatto sul mondo: è l'ordine in cui hai guardato.

Definizione di popolazione da congelare adesso, in una riga, usando solo informazione nota al primo blocco visto: tutti i firmatari e tutti i destinatari di valore sulle monete nate dopo il blocco B, su entrambe le chain, separatamente. Non "chi ha almeno una posizione chiusa". Quella definizione è già il filtro che ha prodotto il 55,9%.

## 3. L'errore dei prossimi tre giorni

Stai per scrivere `win_rate` e `entity_id` come colonne aggiornate sul posto, sullo stesso intervallo che ha prodotto +19 e +18, e stai per scegliere le regole di fusione guardando la flotta 3 su 3 da 263$ e i tre saldi da milioni. Tra tre giorni ogni query farà gruppo per entità e filtro sul tasso, e il database risponderà con la selezione che ci hai messo dentro. Nessuna analisi successiva lo vede, perché la popolazione a una sola chiusura e le posizioni mai vendute non saranno neanche righe.

È questo, e non "manca un'euristica di clustering", il passo che rende il bias irreversibile. Il clustering è il lavoro che sembra progresso perché gli aneddoti sono nitidi. L'oggetto che potrebbe ancora uccidere il risultato — o lasciarlo in piedi — è un altro, e va eseguito prima di qualsiasi tabella di attori:

prendi la moneta successiva, la valuti a un orizzonte fisso anche se non è stata venduta, controlli il saldo precedente e il basale della stessa ora, tieni le chain separate, e guardi se il +19 resta. Se crolla, era la politica di chiusura e la sopravvivenza del capitale. Se resta, resta comunque un rendimento assoluto negativo in coda, misurato su dati che hai già guardato: la conferma è solo un periodo successivo che non hai ancora ispezionato, non una leaderboard riletta meglio.

Il secondo errore, connesso, è trattare le due chain come un solo schema con un solo punteggio. Sulla chain dove il controllo vale +41, un punteggio condiviso importa il nullo dentro la chain dove forse c'era qualcosa. La tentazione opposta, scartare in silenzio la chain scomoda perché le flotte dell'altra sono più belle, è lo stesso errore.

Il terzo, quello che il database non può riparare perché non è un problema di schema: anche un punteggio ex-ante perfetto ti dice chi comprerà, non che tu possa comprare dopo di loro a un prezzo ancora utile. Il tuo dato arriva da RPC pubblici ed esploratori, quindi dopo che la transazione è nel blocco. La coda che hai misurato è già sotto zero prima di fee, impatto e fill mancati. I prossimi tre giorni di risoluzione delle entità migliorano la biografia di chi ha già comprato. Non creano un fill. La domanda da scrivere sopra la prima migrazione, e da non lasciare implicita, è se il vantaggio sta nel passato noto sei ore prima — l'unica cosa che puoi usare prima del lancio — o nella loro presenza nella moneta, che conosci solo quando loro sono già dentro e tu sei l'uscita.
