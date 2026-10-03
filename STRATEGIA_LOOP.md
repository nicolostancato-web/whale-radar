# 🎯 STRATEGIA — i DUE LOOP (documento di riferimento, direttiva Nicolò 31/08/2026)

> Questo file viene PRIMA di ogni altra cosa. Se un agente, un report o una decisione contraddicono
> quanto scritto qui, sbagliano loro. Ogni modifica va discussa e registrata in `DECISIONS.md`.

## I TRE LOOP — nomenclatura ufficiale (direttiva Nicolò, 31/08)

| | nome | cosa fa | dove vive |
|---|---|---|---|
| **LOOP 0** | **ISPEZIONE** | che ogni componente del team faccia il suo lavoro | **UNO**, con verdetto per chain |
| **LOOP 1** | **PERCENTUALE** | alzare la percentuale | uno **per chain** (logiche diverse) |
| **LOOP 2** | **DEMO LIVE** | il conto verso €3.000 | uno **per chain** (oggi tutti fermi) |

**Il LOOP 0 non si spegne mai.** Nemmeno quando tutto va bene: se domani entra un agente nuovo nel team,
dev'esserci ancora qualcuno che controlla anche lui. Oggi gira ogni ora (fase aggressiva); in futuro si
potrà rallentare, mai fermare. Tre presidi indipendenti lo tengono vivo: il suo workflow orario, il loop di
ricerca ogni 4 giri, e il motore se il referto invecchia oltre 75 minuti.

**Perché il LOOP 0 conta più della lavagna:** dieci dipendenti dove uno fuma, uno va al bar e uno inventa i
numeri possono mostrare percentuali alte oggi — fra sei mesi non avranno niente. Un team dove ognuno ha un
compito preciso può partire da zero e superarli, perché la soluzione salta fuori dal **numero di test fatti
bene**. Non sappiamo ancora se la strategia giusta sia aspettare un picco di volume, un calo, sei ore o
venti, 2x o 5x. Lo sapremo se siamo organizzati. **L'organizzazione viene prima del risultato: il risultato
è una conseguenza.**

Quando si chiede "come va il LOOP 0?" si parla dell'ispezione. "LOOP 1 di Solana" è la percentuale di Solana.

---

## Il principio in una riga
**Il LOOP 1 cerca la percentuale. Il LOOP 2 la trasforma in soldi. Il LOOP 2 non si accende finché il
LOOP 1 non è robustamente positivo.**

---

## 🔁 LOOP 1 — LA PERCENTUALE (sempre acceso, per ogni chain)

**La domanda, ripetuta all'infinito:** *come faccio ad avere una percentuale positiva e più alta?*

**Come lavora:**
1. **Accumula dati**: storico + tutto ciò che arriva dal vivo. Il database cresce sempre, non si ferma mai.
   Se si accorge che mancano dati importanti, **se li scarica da solo**: deve essere autonomo.
2. **Prova strategie una per una**, e le scrive: *"entro a +6h, stop loss 80%, take profit 2x / 3x / 4x / 5x"*
   → misura sullo storico → esce un numero → *"questa non va, avanti"* → ne prova un'altra.
3. **Ogni volta che il numero sale, tiene la strategia nuova.** Poi riparte a cercarne una migliore.
4. **Il goal non finisce mai.** Anche a +108% la domanda resta la stessa: come lo alzo ancora.
5. **Lungo la strada scopre CONCETTI**, non solo parametri. È così che è nato l'insider: guardando i dati si
   è visto che certi wallet comprano prima del pump. Un concetto nuovo può valere più di mille parametri —
   può arrivare il giorno in cui si scopre che i grafici non servono, basta l'insider, e si fa 500% con un
   trade ogni tre giorni. Quel giorno arriva **cercando**, non aspettando.

**Regola di misura:** conta la percentuale **ROBUSTA** (tolti i 3 risultati migliori), non la media. La media
è gonfiata dai mostri: se il numero regge solo grazie a un 300x, non è una strategia, è una lotteria.

---

## 💰 LOOP 2 — IL LIVE (acceso SOLO col permesso del LOOP 1)

**Il cancello (GATE):** il live di una chain si accende **solo se** il LOOP 1 di quella chain ha una
percentuale robusta ≥ **+40%** su almeno **150 token**. Sotto quella soglia il conto resta **SOSPESO**.

> *Perché:* andare live con il loop 1 a -3% (Base) o -21% (Solana) significa attuare una strategia che sappiamo
> già essere perdente, e poi stupirsi che perda. È l'errore del 30-31/08: acceso il live su chain negative.

**Cosa fa il LOOP 2 quando è acceso:**
1. **Attua la strategia del LOOP 1**, senza reinventarla: entrata e uscita le decide il loop 1.
2. **Aggiunge ciò che nello storico non c'è**: gas, swap, slippage, latenza, e soprattutto **quanto capitale**
   per posizione e **quante posizioni insieme**.
3. **Calibra sapendo COM'È FATTA la percentuale.** Se il +50% arriva da 2 vincenti su 10, non basta "entrare":
   bisogna entrare **in quelli giusti** ed essere pronti a molte perdite piccole. Il loop 2 deve conoscere la
   forma della distribuzione, non solo la media.
4. **Impara e ricalibra in piccolo**, restando allineato al loop 1.
5. **Reset** se il conto scende sotto soglia: anche il reset è apprendimento, non un fallimento.

---

## ⏳ LA PAZIENZA (regola che vale sopra tutte le altre)

- **Due trade negativi NON sono un segnale.** Un giorno negativo non è un segnale. Non si cambia strategia,
  non si "alza la mano", non si tocca nulla.
- Prima di giudicare un live servono **almeno 20 trade chiusi**. Sotto quel numero il verdetto è
  *"in raccolta, troppo presto"*.
- Se il LOOP 1 dice +50% e il live perde nei primi trade, la reazione giusta non è cambiare strategia:
  è **capire come è fatto quel +50%** (quanti vincenti su quanti) e calibrare l'esecuzione.
- La fretta è il modo più veloce per buttare una strategia buona dopo tre lanci di moneta sfortunati.

---

## 🚦 STATO DEI CANCELLI (aggiornato dal sistema)

| chain | percentuale robusta (LOOP 1) | cancello LOOP 2 |
|---|---|---|
| robinhood | +34% su 230 token | 🔴 CHIUSO (sotto +40%) |
| base | -3% su 586 token | 🔴 CHIUSO |
| solana | -21% su 600 token | 🔴 CHIUSO |
| bsc | -31% | 🔴 CHIUSO |

**Oggi nessuna chain ha il permesso di andare live.** Tutto il lavoro è sul LOOP 1: alzare la percentuale.
Quando una chain supera il cancello, se ne parla e si accende il live — con pazienza.
