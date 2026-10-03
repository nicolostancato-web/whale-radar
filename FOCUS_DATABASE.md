# 🏗️ FOCUS DATABASE — il terreno prima del castello

*14/09/2026 · direttiva di Nicolò · si costruisce SOLO database finché non c'è l'ufficialità*

## La direttiva, e perché ha ragione

> «Due mesi fa ti avevo detto: il database deve essere perfetto. Tu hai detto va bene va bene.
> Oggi, dopo un mese di calcoli, mi dici che la scatola non è piena.»

È esatto. Ho costruito castelli — quattro corsie, esperimenti, test di permutazione, audit — su un
terreno che non avevo verificato. E il test più elegante della notte scorsa ha misurato una cosa
sola: che il terreno non regge.

**Da adesso e per 2-3 giorni: solo database.** LOOP 0 e LOOP 1 continuano a girare (accumulano), ma
niente strategie nuove, niente esperimenti nuovi, niente ottimizzazione.

**Si riparte solo quando** io e il consulente esterno mettiamo per iscritto, su documento, che il
database contiene tutto ciò che serve.

---

## 1. LA SCOPERTA DI OGGI: stiamo usando il 27% di UN indirizzo

Il primo numero che avrei dovuto calcolare due mesi fa.

| | |
|---|---|
| interrogazioni che facciamo oggi | **~11.700 al giorno** |
| tetto della fonte gratuita, **per indirizzo IP** | **43.200 al giorno** (30/minuto) |
| **quanto ne usiamo** | **27%** |

E c'è il moltiplicatore vero:

| | |
|---|---|
| lavori in parallelo che GitHub concede (repo pubblico) | **fino a 20** |
| oggi ne usiamo | **4** |
| ogni lavoro gira su una macchina diversa, con IP diverso | → **limite separato** |

**Tetto teorico: 20 × 43.200 = 864.000 interrogazioni al giorno.** Con 6 corsie dedicate alla
raccolta, prudenti a 25 chiamate/minuto: **~216.000 al giorno, 18 volte quello che facciamo adesso**.

> **Quello che pensavo richiedesse un mese può richiedere due giorni.** Non serve pagare niente: i
> minuti di GitHub Actions sui repository **pubblici** sono gratuiti e illimitati.

**Costo: €0.** Nessuna API a pagamento, nessun VPS, nessun account nuovo.

---

## 2. Perché non l'avevo calcolato

Perché ho sempre trattato la raccolta come un vincolo del mondo — «la fonte è lenta», «il free tier
è saturo» — invece di misurarlo. È la stessa malattia degli ultimi giorni: **uno zero che viene dal
non aver guardato, travestito da limite**.

Il vincolo non era la fonte. Era **la nostra architettura di raccolta**: un motore solo, sequenziale,
che fa tutto a turno.

---

## 3. Cosa succede adesso, in ordine

| # | passo | stato |
|---|---|---|
| 1 | misurare il tetto reale delle fonti | 🟢 **fatto** (sopra) |
| 2 | scrivere la **specifica completa** del database: cosa deve contenere, per sempre | ⏳ **in corso** |
| 3 | farla a pezzi dal consulente esterno, e riscriverla | ⏳ |
| 4 | costruire le corsie di raccolta in parallelo | ⏳ |
| 5 | riempire, misurando ogni giorno quanto manca | ⏳ |
| 6 | **ufficializzare** per iscritto che il database è completo | ⏳ |

**Solo dopo il punto 6 si torna a cercare l'edge.**

---

## 4. La regola per questi giorni

Ogni volta che mi viene un'idea di strategia, la scrivo in coda e **non la eseguo**. Il tempo di
calcolo va tutto alla raccolta.

E una regola contro l'errore opposto, che è reale: **il database non si perfeziona all'infinito.**
La specifica del punto 2 deve dire *quando basta*, con numeri, prima di cominciare a riempire —
altrimenti «perfetto» diventa una scusa per non decidere mai.
