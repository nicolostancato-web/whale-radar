# RECOVERY — whale-radar

*aggiornato 3 ottobre 2026, notte*

## Cosa stiamo facendo (una frase)

Cerchiamo un vantaggio incassabile sulle memecoin appena nate di due chain (base, robinhood)
rischiando ZERO euro, e la pista viva è **l'insider**: mani ricche che finanziano flotte di
portafogli nuovi che comprano per primi.

## Dove siamo, in numeri

**Quello che regge:** il passato chiuso di chi compra predice la moneta successiva per
**+19 punti su robinhood e +18 su base** (prima +16 e +20: con più dati le due chain
convergono, che è il comportamento di un effetto vero). Resta un **filtro**, non un motore: il
quinto migliore è ancora negativo (−0,3% e −4,4%).

**La scoperta strutturale:** flotte di portafogli nuovi finanziate dalla stessa mano. I tre
finanziatori più grandi tengono **$5,6M**, **$62,9M**, **$23,6M** con **65**, **371**, **172**
transazioni in tutta la vita — non sono exchange, sono persone. Il 41% dei portafogli nuovi
risolti appartiene a una flotta.

**Quello che manca:** dimostrare che seguirle faccia guadagnare. Il legame coi risultati è
appeso a **sei** pool, perché abbiamo risolto **83 finanziatori su 11.000**. Servono ~1.000.

**Due ipotesi cadute:** le squadre visibili (vanno *peggio*, −19,8%) e i portafogli appena
creati (il nonce non predice). Entrambe cercavano l'ombra del fenomeno.

## Ultimi cinque passi fatti

1. Trovato che **robinhood HA un esploratore** (`robinhoodchain.blockscout.com`): rifiutava le
   richieste per le intestazioni sbagliate, e per un giorno ho scritto il contrario. **Con due
   chain la regola di ripetizione diventa soddisfacibile**: è la differenza fra indizio e
   strategia.
2. Trovato che metà dei finanziamenti su robinhood sono **transazioni interne**, invisibili
   all'elenco standard — e una flotta era nascosta esattamente lì.
3. Scritta la **definizione di insider PRIMA dei numeri** (`CHE_COSA_E_UN_INSIDER.md`): poche
   monete (3-20) e almeno il 60% di successo = insider; molte (100+) e metà = fabbrica.
4. Lanciata la misura **quanto guadagna ognuno** (`agents/profitto_persone.py`), che tiene
   separato il **chiuso** dall'**aperto** — un portafoglio ancora in posizione ha un conto
   negativo che non è una perdita.
5. Riparata la perdita di dati nella **riunione**: il pubblicatore fondeva sulla propria copia
   vecchia e `git pull -X ours` la teneva, sovrascrivendo il ramo più nuovo.

## Prossimo passo

Leggere i profitti persona per persona e **classificare le flotte col criterio già scritto**.
Poi, se qualcosa passa, verificare la ripetizione su entrambe le chain.

## File da leggere per ricostruire il contesto

- `INSIDER_ESISTONO.md` — i +19/+18 punti e i due attacchi che hanno sopravvissuto
- `FLOTTE_CHI_PAGA.md` — i milioni dietro le flotte, e la mia spiegazione confutata
- `CHE_COSA_E_UN_INSIDER.md` — la definizione con le soglie
- `SQUADRE_E_FINANZIATORI.md` — perché le squadre visibili non sono il fenomeno
- `CORREZIONE_LATENZA.md` — il falso titolo del 30/09 e come è nato
- `RIARMI_CHE_DORMONO.md` — il 52% di capacità sprecata e perché

## Macchina

Email di guasto da **tredici l'ora a zero**. 28 corsie su 28 sorvegliate. La guardia gira
**dentro GitHub** innescata dal completamento del pubblicatore (gli orologi GitHub li salta a
qualunque frequenza, misurato). Nessuna corsia si riarma più da sola.

## Costi

**Zero euro.** Endpoint RPC pubblici, esploratori pubblici, macchine gratis su repository
pubblico. L'unica cosa che accorcerebbe i tempi è una **chiave gratuita Etherscan** (senza
carta, 100.000 chiamate al giorno): la corsia la usa da sola se la trova in `ETHERSCAN_KEY`.

## Come riprendere

Apri una chat nuova, leggi questo file e i sei documenti elencati, poi riparti dal prossimo
passo. Il loop autonomo si riarma con `/loop`.
