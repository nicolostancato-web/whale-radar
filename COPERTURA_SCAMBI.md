# 🔌 IL BUCO SOTTO LA CLASSE RICCA

*14/09/2026 · scoperto provando a testare le variabili su wallet e sequenze · €0*

La classe arricchita (identità dei wallet, sequenza, tempi) **non è stata bocciata: non è stata
testabile.** E il motivo è un guasto di raccordo fra archivi, non una proprietà del mercato.

## Quante righe hanno davvero gli scambi che servono

| chain | righe valutate | con scambi sufficienti | copertura |
|---|---|---|---|
| base | 1.200 | 117 | **10%** |
| solana | 751 | 87 | **12%** |
| robinhood | 651 | **0** | **0%** |

## Il caso Robinhood: 4.281 file di scambi che non servono a niente

| | |
|---|---|
| pool valutati (hanno candele ed esito) | 400 |
| file di scambi raccolti | **4.281** |
| **in comune** | **0** |

Zero. Nemmeno traducendo i pool nei rispettivi token con la mappa: **0 su 239**.

Le lunghezze degli indirizzi coincidono (42 e 66 caratteri), quindi non è un problema di formato: i
due archivi coprono **universi diversi**. Il collettore degli scambi e quello delle candele guardano
insiemi di pool che non si incrociano mai.

> Abbiamo raccolto **4.281 file di scambi su Robinhood che non possono essere uniti a nessun token
> valutato**. Non sono dati sbagliati: sono dati che non incontrano mai gli altri.

## Perché conta più di quanto sembri

L'audit di stanotte ha concluso che il segnale, se esiste, vive probabilmente nelle variabili che la
classe povera non rappresenta: **chi** compra, in **che ordine**, con **che tempi**. Tutte quelle
variabili si costruiscono **dagli scambi**.

Quindi: sulla chain dove il costo d'uscita è più basso (Robinhood, 0,10%) e dove entra il flusso di
partecipanti nuovi, **non possiamo nemmeno formulare la domanda**, perché i due archivi non si
parlano. E su Base e Solana possiamo formularla su **una riga su dieci**.

## Cosa NON dico

Non dico che la classe ricca sia migliore o peggiore. **Non è stata provata.** Dire «no» qui sarebbe
spacciare per risposta uno zero che viene dal non aver guardato — l'errore che questo progetto
insegue da giorni e che stanotte ho commesso io per primo: la prima esecuzione ha scritto «nemmeno
la classe ricca batte il caso» quando il test non era mai partito.

## Il prossimo lavoro, in ordine

1. **Capire perché i due archivi di Robinhood non si incrociano** — è un difetto di raccordo, e una
   volta riparato sblocca l'unica chain con costi bassi.
2. Poi, e solo poi, rifare la prova di permutazione sulla classe ricca.

Finché la copertura resta al 10%, qualunque verdetto su wallet e sequenze sarebbe un verdetto su un
decimo del mondo, presentato come se fosse sul mondo.

---

## CORREZIONE (stessa notte): non era un difetto di raccordo. È peggio.

Avevo scritto che i due collettori «camminavano sulla stessa lista da estremi diversi». Ho riparato
il collettore degli scambi perché desse **priorità ai pool già valutabili** — e dopo la riparazione
l'intersezione era **ancora zero**. Quindi la mia spiegazione era sbagliata.

Verificato:

| | |
|---|---|
| pool nel registro Robinhood | 20.180 |
| serie di prezzo (candele + battito) | 3.507 |
| **di queste, presenti nel registro** | **3.507 su 3.507** |

Gli indirizzi si parlano benissimo. Il problema è un altro, e si vede nel giro che ho appena
eseguito: **90 pool interrogati, 12 con scambi**. Gli altri 78 non hanno restituito niente.

### La causa vera: il tempo, non gli indirizzi

La fonte gratuita restituisce solo **gli ultimi ~300 scambi** di un pool. Per un token nato giorni
fa, **i primi acquisti non esistono più**: nessuno li conserva e non si possono recuperare.

Quindi gli scambi *prima dell'entrata* — quelli che servono per sapere **chi** compra, in che ordine,
con che tempi — si possono avere **solo per i token catturati da giovani**. Il nostro archivio di
candele contiene molti token vecchi: per quelli la domanda non è difficile, è **impossibile**.

### Cosa cambia

1. **La classe ricca non è testabile all'indietro.** Non per un bug: perché il dato non è mai
   esistito dalla nostra parte. Dichiarare un verdetto su wallet e sequenze usando il 10% dei token
   che per caso furono catturati giovani significherebbe giudicare un mondo diverso da quello che
   diciamo di giudicare.
2. **Si può costruire solo in avanti.** La riparazione che ho fatto (prima i pool già valutabili)
   non recupera il passato, ma da adesso ogni scambio scaricato diventa una riga interrogabile
   invece che peso morto.
3. **Il 3 ottobre arriva prima** di un archivio in avanti abbastanza profondo. Va detto adesso, non
   il 2 ottobre.

> **La lezione, ed è la più dura della notte**: abbiamo passato settimane a ottimizzare dentro una
> classe di ipotesi povera, mentre l'unico dato che avrebbe potuto arricchirla **stava evaporando
> ogni giorno**, e nessuno lo raccoglieva nel momento in cui era ancora raccoglibile.

---

## SECONDA CORREZIONE: il numero «0 in comune» era FALSO

L'avevo misurato su un clone locale vecchio di ore. Rifatto su dati freschi:

| chain | righe valutate | **hanno un file di scambi** | con scambi **prima dell'entrata** |
|---|---|---|---|
| base | 1.708 | **395** | 118 |
| solana | 754 | **510** | 87 |
| robinhood | 659 | **179** | **0** |

Quindi: su Robinhood i file di scambi **ci sono** per 179 token valutati — non zero, come avevo
scritto. Ma **nessuno di quei 179** contiene scambi avvenuti *prima* del momento in cui avremmo
potuto comprare.

### La conclusione non si indebolisce: si affila

Prima dicevo «gli archivi non si parlano». Era sbagliato. La verità è peggiore e più precisa:

> **Gli scambi li abbiamo. Arrivano semplicemente troppo tardi.**

Li scarichiamo quando il token è già maturo, e a quel punto la fonte gratuita ha già buttato via i
primi — quelli che dicono **chi** è entrato per primo, in che ordine, con che tempi. Restano gli
scambi di dopo, che per la nostra domanda non servono a niente: descrivono un mondo in cui il
movimento è già avvenuto.

È la stessa forma di errore che questo progetto continua a incontrare: **non un dato mancante, ma un
dato che arriva dopo il momento in cui avrebbe avuto valore.**

### La terza volta stanotte

Questa è la terza conclusione sbagliata che ho tratto in una notte leggendo una copia locale invece
dei dati veri — e la seconda che avevo già pubblicato. La regola era scritta, e l'ho violata lo
stesso tre volte:

> Lo stato si legge da GitHub. Una cartella scaricata ieri mostra numeri di ieri, e sembrano di oggi.

Non è disattenzione: è che ogni volta avevo *una ragione* per usare la copia locale — era più
veloce, era lì, il clone era «recente». La ragione era sempre buona e il risultato sempre sbagliato.
