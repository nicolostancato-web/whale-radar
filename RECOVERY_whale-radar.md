# RECOVERY — whale-radar

*aggiornato 10 ottobre 2026, pomeriggio*

## Cosa stiamo facendo (una frase)

Una prova in avanti con soldi finti su robinhood: compriamo ogni moneta appena **diplomata**
(cioè appena il pool apre), vendiamo al **raddoppio**, e se entro **16,7 ore** non raddoppia
usciamo comunque. Regola **congelata**: non si tocca finché non ci sono 50 chiusure.

## Dove siamo, in numeri

**25 chiusure su 50** (circa metà vinte, metà perse), 2 aperte, ~345 pool archiviati.
Media a 21 chiusure: **+6,5% ± 34 punti** — l'intervallo contiene lo zero, quindi *non sappiamo
ancora* se guadagna. Accumulo: **16,7 posizioni al giorno** → le 50 arrivano il **11 ottobre**.

**La coda è grassa:** su 21 chiuse, il 62% ha toccato 1,5x, il 43% 2x, il 29% 3x, il 14% 5x,
il 5% 10x. La probabilità di continuare moltiplicata per il passo oscilla intorno a 1: **dove si
incassa è quasi indifferente**.

**Due cose solide:** (1) il cordino che segue il massimo **peggiora** tutto, ed è monotono su tre
larghezze (+3,8% a −30%, −4,4% a −50%, −14,6% a −60%): queste monete non scendono, crollano.
(2) uno stop a 0,30 non uccide nessuna vincente (la discesa peggiore prima del raddoppio ha
minimo 0,165x) e ferma 6 perdenti.

**Il vincolo che conta:** dispersione **80 punti per posizione**. Per distinguere due regole di
10 punti servono ~486 posizioni per braccio (27 giorni), di 20 punti ~122 (6 giorni). **Limare i
parametri è inutile**: si possono scoprire solo effetti da 50 punti in su.

## Ultimi 5 passi fatti (10 ottobre)

1. **Recuperate 30 consulenze di Astra** (3-10 ottobre) che la corsia produceva e **non
   pubblicava**: il codice cercava una cartella del Mac, sul runner non esiste, e il file moriva
   col runner. Riscritta la pubblicazione con l'API dei contenuti.
2. **Creato il custode della memoria** (`agents/custode_memoria.py`), cancello davanti a ogni
   pubblicazione: conosce i due depositi (GitHub 10 GB, R2 100 GB), giudica per **costo**
   (peso × riscritture) e indica cosa riscrivere a righe.
3. **Emergenza quota risolta:** il repo era a 9,85/10 con crescita 2,5 GB/giorno. Spente 8 corsie
   delle fasi chiuse; il pubblicatore salta le loro consegne arretrate leggendo
   `data/corsie_spente.json`; **qualunque file oltre 2 MB in `multichain/base` o `loop1` resta
   fuori dal ramo** (verificato su corsa vera: 9 file, 38 MB). Dopo la pulizia: **7,68 GB,
   margine 2,32**, crescita **0,07 GB/giorno**.
4. **Database del cammino alla versione 2:** ogni punto porta `[blocchi, mediana, minimo, massimo]`
   dell'intervallo. Serviva: la mediana nascondeva un tocco breve del raddoppio e la simulazione
   sbagliava di 76 punti su un caso.
5. **Previsione registrata** in `PREVISIONE_STOP_E_USCITA_10OTT.md`, prima di misurare: lo stop
   non batterà il 2x secco di più di 10 punti; il cordino resterà peggiore; a 50 chiusure la
   media resterà indistinguibile da zero.

## Prossimo passo

A **50 chiusure** (attese l'11 ottobre): eseguire le domande del
`PIANO_ANALISI_FRA_CINQUE_GIORNI.md`, **domanda 8 inclusa** (l'orizzonte di 16,7 ore ci taglia i
colpi grossi? tre monete hanno fatto il massimo dopo la nostra uscita, due dopo aver già incassato
il raddoppio, arrivando a 8,70x e 6,04x) — ma la 8 si risponde solo su posizioni che hanno
compiuto 7 giorni.

## File e comandi

- recap: `python3 agents/recap_promozione.py` (comando di Nicolò: «recap promozione»)
- maglia di controlli, da questo Mac: `bash agents/dal_di_fuori.sh`
- stop e uscita: `agents/dove_mettere_lo_stop.py`, `agents/dove_uscire.py`
- memoria e quota: `agents/custode_memoria.py`, `agents/quanto_pesa.py`, `agents/quanto_cresce.py`
- pubblicare: `python3 agents/pubblica_file.py <file>`
- deposito R2: `python3 agents/deposito.py` (elenco), `prova_ripristino.py` (ripristino vero)

## Risorse esterne

- repo: `nicolostancato-web/whale-radar` (pubblico)
- deposito R2: bucket `whale-radar`, 6,31 GB su 100 — contiene `demo_robinhood.tar.gz` (il
  database della prova), `multichain-base/robinhood.tar.gz`, `loop1.tar.gz`, `memoria.tar.gz`
- credenziali: `~/Documents/b2b-finder-credentials.txt` (sezione `CLOUDFLARE R2`, GitHub, OpenAI)
- corsie spente con motivo: `data/corsie_spente.json`; attese: `data/inventario_atteso.json`

## Come riprendere

Apri una chat nuova, leggi questo file, poi `bash agents/dal_di_fuori.sh` e
`python3 agents/recap_promozione.py`. Se il recap dice 50 o più chiusure, parte l'analisi.
