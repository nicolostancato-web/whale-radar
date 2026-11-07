# La notte dell'1 ottobre — cosa ho rotto io, e cosa ho imparato

**Nicolò mi ha detto che il sistema regredisce e si scorda le cose. Aveva ragione, e la notte
ha mostrato una cosa che non mi aspettavo: buona parte dei guasti li ho creati io, nelle ore
in cui stavo riparando.**

## La catena, in ordine

| ora | cosa ho fatto | cosa ha prodotto |
|---|---|---|
| 20:00 | rete di guardiani che si rilanciano a vicenda | **tempesta di rilanci**: tre raccoglitori annullati a raffica |
| 08:00 | risvegliato un guardiano morto dal 27/08 | **38 giri uccisi** a metà lavoro |
| 02:00 | detto «sì, la memoria è salva» | era **falsa**: codice scritto, fatto non verificato |
| 22:00 | il pubblicatore raccoglie i pacchi | **un pacco rotto** ha fermato lo scrittore unico |

Nessuno di questi guasti l'ho trovato guardando. Li hanno trovati: l'inventario (nato mezz'ora
prima da un consiglio di Grok), la prova di ripristino (che non avevo mai fatto), e Nicolò.

## I nomi, che sono il regalo vero della notte

Grok, cercando su GitHub e nei paper, ha portato i **nomi consolidati** dei nostri guasti. Non
li stavamo inventando: li subivamo senza saperli cercare.

| nome | il nostro caso |
|---|---|
| `silent failure` / `dead man's switch` | 33 corsie ferme un mese: chi non parte non fallisce |
| `common-mode failure` | tre guardiani morti insieme: erano un guardiano solo |
| `specification drift` | «migliaia di combinazioni» diventate una manopola in sette giorni |
| `policy erosion` | `compliance_check.py` sparito, e nessuno se n'è accorto |
| `retry storm` | la mia rete che annullava i raccoglitori |
| `head-of-line blocking` | un pacco rotto che ferma lo scrittore unico |
| `write amplification` | 6,2 GB/giorno per una riga che riordinava |
| `fail-plausible` | tre ore di ritentativi su un rifiuto definitivo |
| `adaptive overfitting` | il motore che trova sempre qualcosa se cerchi abbastanza |
| `context rot` | 3.031 messaggi non sono un requisito attivo |

**Avere i nomi ha cambiato il modo di cercare.** Prima riparavo sintomi uno per uno; nelle
ultime due ore riconoscevo famiglie.

## Il dato che spiega tutto

Dal lavoro di Wu che Grok ha citato, misurato su un sistema della nostra forma:

> **Il 70% dei fallimenti silenziosi l'ha visto un umano guardando l'output. Test, health check
> e audit di governance sono rimasti verdi.**

E: lo strato di governance dichiarativa ha **0% di prevenzione ex ante** e **87% di blocco delle
regressioni**. L'audit codifica il passato; l'80% dei buchi era una categoria mai concepita.

È esattamente successo stanotte: tutti i miei controlli erano verdi mentre tre raccoglitori
giravano a vuoto. Li ha visti Nicolò, guardando che Astra era muto.

## La lezione su di me

Ogni correzione di stanotte era **giusta guardando il difetto che aveva davanti**, e **sbagliata
guardando il sistema intero**. La rete di guardiani è una buona idea che ha prodotto una
tempesta. Risvegliare un guardiano morto è prudente in generale e distruttivo in questo caso.

> **Ogni miglioramento ha una dose, e la dose non si legge nel difetto: si misura dopo averlo
> applicato.** E va misurata su chi non hai toccato.

## Cosa resta nelle mani di Nicolò

1. **healthchecks.io**, piano gratuito, nessuna carta: un osservatore in un dominio di guasto
   diverso. Finché i miei guardiani girano tutti su GitHub Actions, sono un guardiano solo.
2. **Una regola sul repository** che richieda la sua revisione per `.github/workflows/`: finché
   il mio token può modificare il guardiano, tre guardiani sono un file.
3. **La chiave OpenAI fra i segreti**, perché Astra giri da solo tre volte al giorno.
