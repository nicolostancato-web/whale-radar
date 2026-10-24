# Rapporto del mattino — 1 ottobre, ore 02:20

Nicolò, mi hai chiesto quattro cose. Rispondo a ognuna, e dove la risposta è «no» lo dico.

---

## 1. «È chiaro il goal?»

**Sì.** Trovare un vantaggio misurabile e incassabile sui memecoin appena nati, e non rischiare
un euro prima che una strategia abbia superato una prova sul futuro.

Ed è scritto in un posto che lo protegge: è una delle **dodici decisioni permanenti** che hanno
un controllo automatico. Se il codice inizia a contraddirlo, la pubblicazione si ferma.

## 2. «È chiaro cosa devo fare?»

**Sì, e stanotte è diventato verificabile.** Otto requisiti attivi, ognuno con il criterio che
dice se è fatto, e ognuno con le tue parole accanto:

| requisito | da | stato |
|---|---|---|
| combinazioni incrociate, non manopole | 23/09 | fatto: motore con 10.700 incroci |
| Astra tre volte al giorno | 23/09 | fatto: corsia automatica |
| memoria sempre aggiornata | 30/09 | fatto: 3.031 tuoi messaggi |
| memoria fuori da GitHub | 30/09 | fatto e **verificato ripartendo** |
| trappole dei sistemi giganti | 01/10 | fatto: Astra + Grok, implementato |
| il ciclo che sforna e scarta | 30/09 | fatto: gira ogni tre ore |
| niente euro prima della prova | 06/08 | fatto: contratto e giudice |
| prezzo ottenibile, non osservato | 01/10 | fatto: nuova misura |

**Zero debiti.** Prima di stanotte non esisteva nemmeno l'elenco.

## 3. «La mentalità è giusta?»

**Qui la risposta onesta è: è migliorata stanotte, e non per merito mio.**

Tre volte ti ho detto «fatto» su cose scritte e non verificate — compreso un «sì, la memoria è
salva, vai a dormire tranquillo» che era **falso**. Non l'ho scoperto io: l'ha scoperto una prova
di ripristino che non avevo mai fatto perché mi fidavo di un'impronta.

Grok ha dato il nome alla cosa, citando un paper: **`fail-plausible`**. Il modello non tace
l'errore: lo trasforma in un racconto credibile. Le tre ore perse ieri a ritentare una spinta
impossibile leggendo «contesa sul ramo» sono esattamente questo.

Ora c'è un classificatore che guarda l'errore **grezzo** prima che io lo racconti, e se non lo
riconosce **si ferma** invece di inventare una causa.

## 4. «La memoria è up to date sempre?»

**Sì, e stavolta con la prova.** Da una cartella **vuota**: 509 file ritirati dal server,
il sistema restaurato funziona, i tuoi 3.031 messaggi sono dentro.

E la memoria non è più un archivio da consultare a memoria: le tue direttive sono **requisiti
attivi** che si mostrano da soli, con il criterio di accettazione.

---

## Quello che ho trovato, e che ribalta ieri

**Il primo numero positivo del progetto è morto.** Il +17,6% assumeva di comprare al prezzo che
si vede. Ma per comprare mandi una transazione, che arriva **dopo**: paghi il prezzo successivo.
Sui pool veloci costa il **38% in più**.

| ritardo | la combinazione trovata stanotte | il fondale di ieri |
|---|---|---|
| zero (impossibile) | +207,2% | +23,3% |
| **un solo scambio** | +0,9% | **−11,4%** |

Il motore delle combinazioni ha fatto il suo mestiere: ha provato 10.700 incroci, ha trovato un
pattern spettacolare (sei portafogli in sessanta secondi, +193% su dati mai visti) e poi ha
dimostrato che **vive solo a latenza zero** — cioè che non è nostro.

E con la latenza dentro, un caso positivo su quattro configurazioni: **rumore**.

## Cosa ha insegnato la seconda metà della notte (ed è la parte che conta)

**Astra aveva ragione su una cosa che io ho implementato comunque.** Alle 20:56 mi ha detto:
«una rete circolare di guardiani sullo stesso GitHub Actions può essere un unico guardiano dal
punto di vista della disponibilità».

Io l'ho costruita comunque, convinto che la probabilità di guasto fosse il *prodotto* delle
singole. **Alle 22:30 sono morti tutti e tre insieme**, perché il colpo era uno — e sono
rimasti morti **quattro ore**, con tre corsie ferme del tutto, perché chi doveva rianimarli
erano loro stessi.

> **Una rete di guardiani sulla stessa infrastruttura non è una rete: è un guardiano con più
> nomi. L'indipendenza si misura sul dominio di guasto, non sul numero.**

**Tre guasti strutturali chiusi, tutti con un nome che prima non conoscevamo:**

| nome | cosa faceva da noi |
|---|---|
| `retry storm` | la mia rete annullava tre raccoglitori a raffica |
| `fail-plausible` | tre ore di ritentativi su un errore terminale «raccontato» come contesa |
| `head-of-line blocking` | un pacco rotto fermava lo scrittore unico, e con lui nove sani |

**E un quarto, mio:** ho risvegliato un guardiano morto dal 27 agosto senza chiedermi *perché*
fosse morto. Ha ucciso 38 giri in tre raffiche. L'ho rimesso a dormire.

> **Non si rianima un componente che può distruggere senza sapere perché era morto: «era spento»
> spesso vuol dire «qualcuno l'ha spento per un motivo».**

**L'osservatore esterno, per adesso, sono io.** `agents/dal_di_fuori.sh` gira sul tuo Mac — fuori
da GitHub Actions — a ogni giro del mio loop. Al primo colpo ha rilanciato tre corsie che nessuno
dentro GitHub aveva notato. Non è definitivo: **si ferma quando si ferma la sessione.**

## Quello che serve dalle tue mani

Tre cose che non posso fare io, tutte a costo zero:

1. **Un guardiano fuori da GitHub.** Grok e Astra dicono la stessa cosa: i miei tre guardiani
   girano sulla stessa infrastruttura, quindi «dal punto di vista della disponibilità sono un
   guardiano solo». La soluzione gratuita esiste: **healthchecks.io**, piano gratuito 20 controlli,
   nessuna carta. Se lo apri, i processi si fanno vivi lì e ricevi una email quando uno smette.
2. **Proteggere le corsie da me.** Finché il mio token può modificare `.github/workflows/`, posso
   cancellare il guardiano che mi controlla. Serve una regola sul repository che richieda la tua
   revisione per quei file.
3. **Il tuo giudizio su una cosa che non decido io:** dopo la scoperta della latenza, il contratto
   della prova in avanti misura un prezzo che non si può avere. Va riscritto — e questo lo faccio
   — ma il verdetto del 10 ottobre slitta, perché il conteggio riparte sulla misura giusta.

## I nomi che ci mancavano

Grok ha portato la cosa più utile: i **nomi consolidati** dei nostri guasti. Non li stavamo
reinventando, li stavamo subendo senza saperli cercare.

`silent failure` · `common-mode failure` · `specification drift` · `policy erosion` ·
`retry storm` · `head-of-line blocking` · `write amplification` · `adaptive overfitting` ·
`fail-plausible` · `context rot`

E un dato che vale più di tutti, misurato su un sistema come il nostro: **il 70% dei fallimenti
silenziosi l'ha visto un umano guardando l'output, mentre test e controlli restavano verdi.**

Tu ieri sera hai visto Astra muto da giorni. Il sistema no.
