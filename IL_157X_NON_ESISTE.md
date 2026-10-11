# Il 157x non esiste — 6 ottobre 2026, sera

## Cosa avevo annunciato un'ora fa

Che `0x77c0dfa98f7832…` aveva fatto **157 volte il capitale** su 19 operazioni, entrando non per
primo ma al 37° posto, 43 secondi dopo la nascita. E che sei portafogli simili condividevano una
firma d'ingresso riconoscibile.

## Cosa l'ha smontato

Nicolò ha chiesto: *«ma è ufficiale che hanno fatto sti soldi? Hai visto il wallet, hai visto che
in quel giorno la ricchezza è aumentata?»*

Non l'avevo visto. Avevo verificato gli **eventi** di acquisto e vendita, non il **movimento di
ricchezza**. Sono andato a guardarlo, e il primo caso non tornava:

| | |
|---|---|
| gettoni comprati | **27.798** |
| gettoni venduti | **2.792.958** |

Ha venduto **cento volte** i gettoni che aveva comprato. Quei gettoni non li aveva presi lì.
Quindi l'«82x» era il rapporto fra due cifre di denaro **che non si riferiscono alla stessa
merce**: non è un guadagno, è un'entrata e un'uscita scollegate.

## Quanto era diffuso

| | gettoni bilanciati |
|---|---|
| tutte le posizioni chiuse sulla curva | **90,4%** |
| `0x77c0dfa9…` (il «157x») | **0 su 20** |
| `0xb2586df5…` | 3 su 38 |
| `0x7f898c8a…` | **0 su 36** |

**La classifica per eccesso aveva selezionato esattamente gli artefatti.** Non è un caso: sono
proprio le posizioni squilibrate a produrre rapporti enormi, quindi un ordinamento per multiplo
le mette in cima per costruzione.

## Il difetto, nominato con precisione

Il controllo «i gettoni venduti devono essere quelli comprati» **l'avevo costruito io stamattina**
— per il lato pool. Non l'ho portato sul lato curva. Una lezione applicata a un posto solo vale
una volta: è la terza volta oggi che pago questa.

## Il quadro vero, col filtro applicato

Solo posizioni dove i gettoni tornano (90-110%), lanciatori esclusi:

| portafogli con… | ritorno mediano | il migliore | sopra 1x |
|---|---|---|---|
| ≥20 operazioni pulite | 1,008x | **1,744x** | 34 su 61 |
| ≥100 operazioni pulite | 0,987x | 1,348x | 8 su 18 |
| ≥500 operazioni pulite | 1,011x | **1,053x** | 3 su 5 |

**Nessun portafoglio, nemmeno uno, raggiunge 10x su un giro pulito.** Il miglior giocatore
ripetuto fa **+5,3% su 5.266 operazioni**.

Non è «tante X». È un margine sottile, che potrebbe essere vero o potrebbe essere rumore — e che
il gas e lo slittamento possono mangiarsi interamente.

## Cosa resta in piedi dell'analisi di un'ora fa

**Niente della parte spettacolare.** Il wallet da 157x non è bravo. La firma d'ingresso era
misurata su sette portafogli che ora sappiamo essere artefatti.

Resta la **struttura del ragionamento**, che era giusta e che i revisori avevano corretto bene:
contare l'eccesso rispetto a chi ha fatto lo stesso numero di tentativi, non il conteggio nudo.
Applicata ai dati puliti, quella struttura dà una risposta negativa invece che entusiasmante — ed
è esattamente a questo che serve.

## La lezione

Avevo tre verifiche in fila e le ho fatte tutte: eccesso sui tentativi, esclusione dei lanciatori,
firma su più portafogli. **Mi mancava la quarta, ed era quella che contava: i gettoni tornano?**

Ho pubblicato prima di farla. La domanda di Nicolò — *«è ufficiale?»* — ha fatto il lavoro che
avrei dovuto fare io.

**Regola, scritta dove serve:** nessun multiplo entra in una classifica se i gettoni venduti non
sono quelli comprati. Il controllo ora è dentro `agents/storie_complete.py`, non nella mia testa.
