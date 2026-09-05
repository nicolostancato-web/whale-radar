# 🧱 SCALETTA — cosa costruiamo, in che ordine

## Il goal, nella catena esatta

```
LOOP CLOUD (Claude, ogni ora, in continuazione)
      │
      └─> costruisce IL CASTELLO = LOOP 0 + LOOP 1 su GitHub
              │
              ├─> perché LOOP 0 faccia il suo lavoro: ispezionare, non fermarsi mai
              │
              └─> perché LOOP 1 faccia il suo lavoro:
                          ⬛ AUMENTARE QUELLA PERCENTUALE ⬛
```

**Il goal finale è uno solo, ed è l'ultimo anello. Tutto il resto è impalcatura.**

Il materiale da costruzione arriva dai feedback esterni (consulenze, esperti): sono **metodi**,
e vanno trasformati in codice che gira.

---

> **Il loop di Claude non cerca la percentuale: costruisce la macchina che la cerca.**
> Ogni giro fa due cose, in quest'ordine:
> 1. verifica che **LOOP 0** (ispezione) e **LOOP 1** (percentuale) su GitHub stiano girando
> 2. porta avanti **un item** di questa scaletta
>
> Un item alla volta, fino in fondo. Aprire tre cantieri e non chiuderne nessuno è il modo
> più elegante di non finire niente.
>
> Goal unico e immutabile: **aumentare la percentuale**. Ogni item deve poter rispondere
> alla domanda *"come ci avvicina a quel goal?"*. Se non ci riesce, non entra qui.

---

## ✅ APPENA FATTO — le cicatrici

**Ogni errore che ci frega una volta diventa un controllo che gira per sempre.**

Nato da un'obiezione di Nicolò: *"non ci illudiamo, tanto hai un agente che sa se ci stiamo illudendo"*.
Mezza verità, e la metà che manca conta: quel revisore l'ho scritto io, quindi controlla i modi di
illudersi che **avevo pensato**. La prova è che in tre giorni sono usciti quattro errori gravi e
**tutti e quattro gli sono passati sotto il naso** mentre scriveva "nessun salto sospetto".

Non diventa onnisciente scrivendone uno più grosso — lo scriverei sempre io. Ma le illusioni già
incontrate possono smettere di funzionare:

| l'errore che ci ha fregato | il controllo che ora gira per sempre |
|---|---|
| **un archivio è tornato indietro** (800 → 609 misure, nessuno aveva cancellato) | nessun archivio che accumula può arretrare |
| costi assunti al posto di quelli misurati | nessun agente può riscriversi i costi a mano scavalcando il metro |
| bias dei sopravvissuti | i disastri contati devono essere coerenti con la mortalità misurata |
| momentum travestito da segnale | chi dichiara un segnale deve mostrare il placebo all'indietro |
| trappole contate come stop a −40% | l'elenco delle trappole non può svuotarsi o invecchiare |

Tutti e quattro **provati simulando il guasto**: un controllo che non scatta mai è inutile.
Quando ne troveremo un quinto, si aggiunge lì.

> Resta il limite vero: contro l'errore che non abbiamo ancora fatto, l'unica difesa è **qualcuno
> fuori dal sistema** — la revisione esterna e i criteri scritti prima. Quelli non sono sostituibili
> da un agente scritto da noi.

---

## 🔴 IN CORSO

### 1. ~~Curva costo-liquidità~~ ✅ FATTA (3/9)
Il costo di uscita ora dipende dalla liquidità del momento, misurato su **796 osservazioni**:

| la posizione è, del volume orario | costo andata+ritorno |
|---|---|
| sotto lo 0,4% | 2,5% |
| 1,5% – 4,4% | 2,9% |
| 4,4% – 16% | 4,2% |
| oltre il 135% | **10,4%** |

**Il costo si moltiplica per 4,1** dai token liquidi a quelli sottili. Non è più un'assunzione.
Il punto pratico: **lo stop scatta quando il volume è crollato**, cioè nella fascia più cara — un
backtest col costo medio dichiara un prezzo che non avresti pagato.

### ~~1bis~~ Curva costo-liquidità (dettaglio storico)
**Cosa:** il costo di uscita deve dipendere dalla liquidità **nel momento in cui esci**, non essere
un moltiplicatore fisso ×3.
**Perché:** oggi il ×3 è un'assunzione dichiarata. È l'ultima cosa che separa il metro da qualcosa
di cui fidarsi. Da chi ci ha fatto l'audit: *«non voglio né il vecchio 33% fisso, né un nuovo 4%
fisso, né un ×3 arbitrario permanente»*.
**Serve:** token con **sia** candele **sia** misura Jupiter. Erano 0, ora sono 560 (sbloccato il 3/9).
**Fatto quando:** `metro.py` calcola l'uscita da una curva calibrata, non da una costante.

---

## 🟡 PROSSIMI (in ordine)

### 2. Il secondo stadio — cosa COMPRARE  🔴 **APERTO 4/9, in attesa di dati**
Costruito `secondo_stadio.py`: quattro candidati con una ragione economica, non pescati a caso —
**accelerazione** del volume, **ampiezza** (quante mani diverse), **squilibrio** compra/vendi sulla
liquidità, **facce nuove** (compratori mai visti su quel token).

Un candidato passa solo con **tre condizioni insieme**: positivo su ≥2 orizzonti, in fascia di
validazione, e placebo all'indietro pulito. Con 4 segnali × 5 orizzonti = 20 prove, qualcosa sembra
buono per forza: le tre condizioni servono a quello.

**Primo risultato (fascia di ricerca, non fa fede):** tre candidati su quattro mostrano media
**+70%** e mediana **+0,0%** → sono lotterie, non segnali. Pochi token estremi tirano su la media
mentre il caso tipico non guadagna niente.

**Stato:** nessun candidato passa. Il criterio di morte NON scatta finché la validazione non ha
abbastanza casi — bocciare per mancanza di dati sarebbe l'errore opposto, non l'onestà.

### 2bis. (storico)
**Cosa:** un segnale indipendente che scelga fra i token che superano il cancello dei creator.
**Perché:** è il buco più grande del progetto. Il cancello dice cosa **non** toccare; non fa
guadagnare. *«Non dimostra che quelli che superano il filtro facciano guadagnare.»*
**Serve:** cancello confermato su holdout (item 3).

### 3. ~~Cancello creator sull'holdout~~ ❌ **CHIUSO 4/9 — non serve nemmeno l'holdout**
Il 3/9 su Base sembrava forte: 91% di disastri fra i creator marchiati contro 57% fra i puliti.
Con i dati cresciuti — **840 puliti contro 73 marchiati** — la differenza e' **8 punti** (65% vs 73%).
Il criterio di morte, scritto il 3/9 prima di vedere questi numeri, dice di chiudere. Chiuso.

**Non era una pista sbagliata: era un campione piccolo.** Ed e' la seconda volta in tre giorni che un
numero forte si scioglie appena i dati crescono (l'altra: il flusso dei cluster, che era momentum).

### 3bis. (storico)
**Cosa:** far giudicare il 91%-contro-57% di Base sulla fascia mai vista.
**Perché:** funziona su Base e non su BSC. Un filtro che vale su una chain sola è un segnale o è
rumore? Lo decide l'holdout, non noi.
**Serve:** fascia di validazione più matura (nata il 31/08).

### 4. Sopravvivenza + evento di domanda
**Cosa:** la terza pista mai provata: non comprare a "30 minuti di età", ma **aspettare un evento**
su un token che ha passato sicurezza, è vendibile, costo d'uscita sotto soglia, liquidità non in calo.
**Perché:** è l'ultima idea della prima consulenza rimasta intatta. Due stadi: prima togli la
probabilità di morte, poi cerchi la domanda che fa muovere il prezzo.
**Criterio di morte (scritto prima):** se il cancello migliora solo la perdita media ma il segnale
di domanda non produce extra-rendimento contro i controlli, non c'è strategia direzionale.

### 5. Creator su Solana
**Cosa:** oggi la copertura è **0%**. Solana è la chain più grossa per numero di token.
**Perché:** senza il creator, la pista viva non si può nemmeno testare lì.
**Ostacolo noto:** l'autorità del mint è revocata, l'API pubblica di pump.fun risponde 530.
Via possibile: Helius DAS `getAsset` (chiave già nei secret, gratis) — non testabile in locale.

### 6. Honeypot su Base
**Cosa:** copertura al **16%** (41 token su 258). Su BSC è al 66%.
**Perché:** senza il flag honeypot, le trappole su Base non si vedono e il backtest le conta come
uscite normali — l'errore che abbiamo appena corretto altrove.

---

## 🟢 PRONTI MA NON ORA (aspettano LOOP 2)

### 7. Framework di rischio all'ingresso
Invalidazione decisa **prima** di entrare; dimensionare dal ribasso e non dal rialzo; accettare
mentalmente la perdita massima come già avvenuta. *(dal video di Miles Deutscher, §9.9 di LEARNINGS.md)*

### 8. Brief mattutino del rischio
Un agente che ogni mattina dice quanto rischio stiamo portando e quanto siamo lontani
dall'invalidazione. È il nostro watchdog, applicato alle posizioni. *(§9.6)*

---

## 🧪 IPOTESI PROVATE E SCARTATE (per non riprovarle a vuoto)

Due scorciatoie che sembravano ragionevoli, entrambe **validate dove la verità la conosciamo** e
bocciate in pochi minuti. È il modo più economico di non perdere una settimana.

| l'ipotesi | come l'abbiamo provata | esito |
|---|---|---|
| «su Solana il creator è il primo che compra il proprio token» | su BSC e Base, dove il creator vero ce l'ha GoPlus | coincide nel **2-3%** dei casi ❌ |
| «un token dove nessuno vende è un honeypot» | sulle trappole dichiarate da GoPlus | ne becca **0**, e il campione (3 su BSC, 16 su Base) è troppo piccolo persino per bocciarla ⏸️ |

> Il principio: **una scorciatoia si valida dove la verità è nota, poi si applica dove non lo è.**
> Se non si può validare, non si usa — per quanto ragionevole suoni.

---

## ⛔ NON SI FA (e perché)

| cosa | perché no |
|---|---|
| **CT Signal Scout** (momentum su X) | È l'idea migliore vista di recente, ma serve X Premium o un VPS. **Nessun euro finché LOOP 1 non è positivo.** |
| **Aprire piste nuove** | Vietato dai criteri: una pista alla volta, e non se ne apre una mentre un'altra aspetta il verdetto. |
| **Riottimizzare Robinhood** | Congelata il 3/9. L'holdout si legge una volta sola. |
| **Andare live (LOOP 2)** | Il cancello evita disastri ma non genera rendimento. Manca il secondo stadio. |

---

## ✅ FATTI (per non rifarli)

- **Metro dei costi misurato** invece che assunto — un solo posto, `metro.py`
- **Gambe separate** entrata/uscita + **uscita in fuga** (stop ≠ take profit)
- **Trappole a −100%** senza doppio conteggio
- **Criteri di STOP** scritti *prima* dei risultati — `data/criteri.json`
- **Congelamento** configurazioni + divieto di riottimizzare
- **Controlli appaiati**, orizzonti fissati prima, **placebo all'indietro** — `controlli.py`
- **LOOP 0 controlla la lista dei convocati**, non solo chi risponde
- **Rubrica** pool↔token su tutto l'archivio + censimento allineato ai token studiabili
- **Lapidi** sui dati potati (morte vera ≠ potatura nostra)
- Piste chiuse: **copy-trading**, **flusso di cluster** (era momentum)
