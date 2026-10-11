#!/bin/bash
# L'OSSERVATORE IN UN DOMINIO DI GUASTO DIVERSO (1/10).
#
# Astra: «una rete circolare di guardiani sullo stesso GitHub Actions puo' essere un unico
# guardiano dal punto di vista della disponibilita'. Serve almeno un osservatore in un dominio
# di guasto distinto, che possa avvisare anche quando GitHub, il pubblicatore o l'agente sono
# fermi.»
#
# Aveva ragione, e la prova e' arrivata in quattro ore: l'1/10 alle 22:30 un guardiano
# distruttivo ha ucciso 38 giri, compresi tutti e tre i guardiani — che non sono mai ripartiti,
# perche' chi doveva rianimarli erano loro stessi.
#
# Questo script gira sul MAC, cioe' fuori da GitHub Actions. Non e' la soluzione definitiva
# (si ferma quando si ferma la sessione), ma e' un dominio diverso, ed e' quello che si puo'
# avere a costo zero finche' Nicolo' non apre un conto su healthchecks.io.
set -u
TOK=$(grep -o 'gh[ps]_[A-Za-z0-9]*' ~/Documents/b2b-finder-credentials.txt | head -1)
REPO=nicolostancato-web/whale-radar
# corsia:minuti_massimi_di_silenzio
# finanziatori e insider aggiunte il 2/10: nate oggi, con l'orologio, e NON sorvegliate —
# GitHub ha saltato i loro cron e sono rimaste ferme due ore. Da quando nessuna corsia si
# riarma piu' da sola, questa lista e' il motore di riserva.
# IL DENOMINATORE, TERZA VOLTA (4/10). Ieri ho scritto «28 corsie su 28 sorvegliate» ed era
# vero e inutile: erano 28 su 28 DELLA MIA LISTA, mentre le corsie con un orologio erano 39.
# Dieci avevano un orologio e nessuna guardia — fra cui `database`, `ricerca` e `loop0`, cioe'
# il cuore. E' la stessa famiglia del 3/10 («le flotte comprano in scia»: 5 pool su 6 perche'
# il denominatore era 73 su 11.275): un rapporto non dice niente se non si guarda su cosa sta.
# IN POSITIVO: `agents/corsia_non_vista.py` ricava l'elenco dai file delle corsie invece che
# dalla mia memoria, e grida se una corsia con l'orologio non e' qui dentro. La lista non puo'
# piu' restare indietro da sola.
CRITICHE="accumulator:360 arbitraggi:540 curva:240 curva_lanci:480 astra:4320 campione:360 candidati:540 censimento:180 ciclo:360 collector:360 completezza:360 coppie:180 database:900 deposito:1080 engine:1080 finanziatori:60 guardia:180 guardiani:540 heartbeat:360 hook:180 iniziatori:180 insider:360 insieme:240 ispezione:180 lanciatori:180 loop0:150 nascite:180 paper_bot:360 piu_intelligente:4320 popolazione:180 previsioni:180 profitto:360 prova_avanti:4320 pubblicatore:60 repo_gc:4320 ricerca:1080 riparazione:180 riserve:180 scoperta:180 segni:360 sentinella:1080 soccorso:120 solana_helius:90 sperimenti:900 storico:180 vivo:150"
RILANCIATE=0
FALLITI=0
SALTATE=0
for VOCE in $CRITICHE; do
  W="${VOCE%%:*}"; LIM="${VOCE##*:}"
  ETA=$(curl -s -H "Authorization: token $TOK" \
    "https://api.github.com/repos/$REPO/actions/workflows/$W.yml/runs?per_page=10" \
    | TOK="$TOK" python3 -c "
import sys,json,os,datetime as dt
TOK=os.environ['TOK']
d=json.load(sys.stdin).get('workflow_runs',[])
if not d: print(99999); raise SystemExit
# in coda O in corso, su QUALSIASI dei giri recenti, non solo il piu' nuovo: una corsia che
# aspetta un posto non va rilanciata, il rilancio la fa solo annullare (misurato 1/10 su hook)
if any(x['status']!='completed' for x in d): print(0); raise SystemExit
# L'ETA' SI CONTA DALL'ULTIMO SUCCESSO, NON DALL'ULTIMO LANCIO (1/10). Qui si prendeva d[0],
# cioe' il giro piu' recente QUALUNQUE fosse il suo esito. Tre giri annullati di fila alle
# 11:53/11:55/11:57 — che non hanno fatto nulla — rimettevano l'orologio a zero, e la guardia
# diceva «nei limiti» su una corsia morta dalle 06:00. Un lancio non e' un lavoro.
# IL LAVORO, NON IL VERDETTO DEL GIRO (1/10). Un giro risulta «annullato» anche quando le sue
# raccolte sono riuscite e si e' fermato solo il passo di RIARMO, che aspetta dieci minuti e
# viene superato dal giro dopo. Misurato: hook e censimento avevano ZERO giri «riusciti» e
# QUATTRO giri in cui il lavoro era riuscito. Li dichiaravo morti e li rilanciavo: stavano bene.
import urllib.request as u
def ha_lavorato(g):
    if g.get('conclusion')=='success': return True
    if g.get('conclusion') is None: return False
    try:
        j=json.load(u.urlopen(u.Request(g['jobs_url'],headers={'Authorization':'token '+TOK}),timeout=30))['jobs']
    except Exception:
        return False
    veri=[x for x in j if 'riarmo' not in x['name'].lower()]
    return bool(veri) and all(x.get('conclusion')=='success' for x in veri)
vivi=[x for x in d if ha_lavorato(x)]
if not vivi: print(99999); raise SystemExit
r=vivi[0]
n=dt.datetime.strptime(r['created_at'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
print(int((dt.datetime.now(dt.timezone.utc)-n).total_seconds()//60))" 2>/dev/null || echo 0)
  if [ "${ETA:-0}" -gt "$LIM" ]; then
    # TETTO AI RILANCI PER GIRO (8/10). Tre corsie hanno fallito il proprio riarmo con HTTP
    # **403** mentre Actions era operativa: non e' un guasto loro, e' un limite secondario di
    # GitHub sui rilanci — e il sospetto cade su di me, perche' questa maglia ne spara decine
    # ogni venticinque minuti, in aggiunta ai riarmi delle corsie. Saturando il limite rompo
    # proprio le corsie che volevo tenere in vita.
    # Quindi: massimo RILANCI_MAX per giro, le piu' ferme prima, e cio' che salto lo DICO —
    # un tetto silenzioso si legge come «ho coperto tutto».
    if [ "${RILANCIATE:-0}" -ge "${RILANCI_MAX:-8}" ]; then
      echo "   DAL DI FUORI | $W ferma da ${ETA} min: NON la rilancio, tetto di ${RILANCI_MAX:-8} rilanci per giro raggiunto (il limite di GitHub rompe i riarmi delle corsie)"
      SALTATE=$((SALTATE+1))
      continue
    fi
    C=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: token $TOK" \
      -H "Accept: application/vnd.github+json" \
      "https://api.github.com/repos/$REPO/actions/workflows/$W.yml/dispatches" -d '{"ref":"main"}')
    # SPENTA A MANO NON E' FERMA (2/10). `solana_helius` e' un relitto messo a riposo l'anno
    # scorso: l'orologio c'e' ma la corsia e' disabilitata, e GitHub risponde 422 a chi prova a
    # lanciarla. Chiamarla «ferma» e rilanciarla a ogni giro vuol dire sporcare l'allarme con
    # una cosa che e' una DECISIONE, non un guasto — e un allarme sporco si smette di leggere.
    if [ "$C" = "422" ]; then
      echo "   DAL DI FUORI | $W e' spenta a mano (HTTP 422): e' una decisione, non un guasto"
      continue
    fi
    # UN RILANCIO CHE FALLISCE NON E' UN RILANCIO (7/10). Fino a oggi stampavo «rilanciata
    # (HTTP 500)»: la parola diceva che era partita, il numero diceva il contrario, e io leggevo
    # la parola. E' la famiglia di errore che mi perseguita — un fallimento riportato come
    # successo. Solo il 204 e' un rilancio.
    if [ "$C" = "204" ]; then
      echo "   DAL DI FUORI | $W ferma da ${ETA} min (limite $LIM) — rilanciata"
    else
      echo "   DAL DI FUORI | $W ferma da ${ETA} min (limite $LIM) — RILANCIO FALLITO (HTTP $C): NON e' partita"
      FALLITI=$((FALLITI+1))
    fi
    RILANCIATE=$((RILANCIATE+1))
  fi
done
[ "$RILANCIATE" = "0" ] && echo "   DAL DI FUORI | tutte le corsie critiche sono nei limiti"
# QUI C'ERA UN `exit 0` (rimosso il 7/10). Tutto cio' che segue — due guardie piu' vecchie
# (corsia_illeggibile, corsia_non_vista) e il rapporto sui guasti — era scritto, cablato e MAI
# ESEGUITO: la riga di uscita stava prima. Un controllo che non gira e' peggio di un controllo
# che manca, perche' nel frattempo credi di essere coperto.
# Lo ho scoperto perche' il rapporto sui guasti, cablato un'ora prima, non stampava niente: il
# silenzio di una guardia va trattato come un sintomo, non come «tutto bene».

# CORSIE CHE GITHUB NON SA LEGGERE (2/10). Due volte in un giorno un file di corsia illeggibile
# ha mandato email a raffica — `riserve` e `guardia` — e in entrambi i casi il sintomo stava
# nei dati di GitHub: come nome della corsia riportava il percorso del file. Questo controllo
# non si puo' fare prima di pubblicare, perche' serve il file sul ramo: si fa subito DOPO.
GH_TOKEN="$TOK" python3 -B "$(dirname "$0")/corsia_illeggibile.py" || true
# UNA CORSIA CON L'OROLOGIO E SENZA GUARDIA NON SI VEDE MAI (4/10): vedi corsia_non_vista.py
python3 -B "$(dirname "$0")/corsia_non_vista.py" || true

if [ "${SALTATE:-0}" -gt 0 ]; then
  echo "DAL DI FUORI | $SALTATE corsie ferme NON rilanciate per non saturare il limite di GitHub: le prende il giro prossimo."
fi
if [ "${FALLITI:-0}" -gt 0 ]; then
  echo "DAL DI FUORI | $FALLITI rilanci NON sono partiti: quelle corsie restano ferme."
fi

# I GUASTI DELLE CORSIE LI DEVO SAPERE IO (7/10). Le email di GitHub arrivavano a Nicolo', che
# non puo' farci niente: l'iscrizione ai repo e' spenta (verificata via API) e il carico passa
# qui, a ogni giro del loop. Spegnere un avviso senza prendersi il carico sarebbe peggio.
python3 "$(dirname "$0")/guasti_da_sapere.py" || echo "   DAL DI FUORI | il rapporto sui guasti non e' girato"

# LA RICERCA DI GROK DENTRO IL LOOP (7/10). Era ferma da un giorno a 3 domande su 10 per un
# motivo banale: gira solo da questo Mac (l'abbonamento e' autenticato qui; da GitHub userebbe
# la chiave a consumo) e dipendeva dal fatto che mi ricordassi di lanciarla. Una cosa che
# dipende dalla mia memoria si ferma: qui si lancia da se', e il suo stesso freno (una domanda
# ogni 3 ore) la fa uscire subito quando non e' il momento. Costo: ZERO.
python3 -B "$(dirname "$0")/ricerca_visibile.py" || echo "   DAL DI FUORI | ricerca sul nostro 50% non girata"
python3 -B "$(dirname "$0")/ricerca_base.py" || echo "   DAL DI FUORI | ricerca su Base non girata"
python3 -B "$(dirname "$0")/ricerca_prelancio.py" || echo "   DAL DI FUORI | ricerca sull'altro 50% non girata"

# LA PROVA IN AVANTI (8/10). La regola regge sulla storia (+15,2% per moneta a 200$ con lo
# scivolamento misurato dentro), ma la storia e' un posto dove si sbaglia in modo elegante: il
# solo giudice vero e' cio' che succede DOPO aver scritto la regola. Qui si apre e si aggiorna
# da se', a ogni giro, con soldi finti. Le regole stanno nel registro e non si toccano.
# SE LA PROVA NON GIRA, E' UN ALLARME, NON UNA RIGA DI LOG (11/10, pagata con 4,6 ore di
# accumulo perso). Mancava `agents/firma_evento.py` in questa copia — c'era su GitHub, qui no — e
# `curva_pons` non si importava piu'. La maglia scriveva «prova in avanti non girata» e andava
# avanti: l'ho visto solo perche' sono andato a guardare, quattro ore e mezza dopo.
# La demo e' la cosa che stiamo accumulando: se non gira, deve finire fra gli allarmi che si
# leggono a ogni giro, con il motivo dentro.
if ! python3 -B "$(dirname "$0")/prova_in_avanti.py" 2> /tmp/avanti_err.txt; then
  echo "   DAL DI FUORI | LA PROVA IN AVANTI NON E' GIRATA — l'accumulo e' FERMO"
  tail -3 /tmp/avanti_err.txt | sed 's/^/      /'
  python3 - <<'FINE_PY'
import json, time
try:
    with open("data/allarmi_da_leggere.jsonl", "a", buffering=1) as f:
        f.write(json.dumps({"quando": int(time.time()), "da": "maglia",
                            "testo": "LA PROVA IN AVANTI NON GIRA: l'accumulo e' fermo. "
                                     + open("/tmp/avanti_err.txt").read()[-400:]}) + "\n")
    print("      allarme scritto in data/allarmi_da_leggere.jsonl")
except Exception as e:
    print(f"      non riesco nemmeno a scrivere l'allarme: {e}")
FINE_PY
fi
# IL DATABASE DEL CAMMINO (9/10, chiesto da Nicolo'): registra minimi, massimi, orizzonti fissi e
# la discesa peggiore prima del raddoppio. Serve per decidere lo stop loss COI DATI fra cinque
# giorni, invece di inventarlo adesso su tre risultati.
python3 -B "$(dirname "$0")/cammino_posizioni.py"
# IL CONTROLLO DI INTEGRITA' (9/10): sei verifiche sul database, a ogni giro. Un buco nei dati si
# scopre quando li si analizza, e allora i cinque giorni sono passati e non si rifanno.
# UN `|| echo` DI TROPPO (11/10). Questa riga portava in coda anche «prova in avanti non
# girata», rimasto attaccato quando ho spostato quel messaggio dentro il blocco con l'allarme:
# se l'integrita' fosse fallita, avrebbe stampato un motivo FALSO. Nessun danno finora perche'
# non e' mai fallita — ed e' il tipo di bugia che si scopre solo nel giorno brutto.
python3 -B "$(dirname "$0")/integrita_database.py" || echo "   DAL DI FUORI | controllo integrita non girato"
# il peso del repository si MISURA a ogni giro (vedi quanto_pesa.py): al limite si ferma tutto
python3 agents/quanto_pesa.py || echo "   PESO | metro non disponibile"

# IL CUSTODE DELLA MEMORIA a ogni giro: la memoria cresce bene o cresce male, e si vede solo misurando
python3 agents/custode_memoria.py | head -6 || echo "   CUSTODE | non disponibile"

# gli allarmi scritti dalle corsie: il canale di riserva da quando le email sono chiuse
python3 agents/allarmi.py || echo "   ALLARMI | non leggibili"

# quanti byte grossi entrano nella storia, finestra UTC esplicita (vedi quanto_cresce.py)
python3 agents/quanto_cresce.py 30 || echo "   CRESCITA | non misurabile"

# chi vende quando la moneta crolla (idea di Nicolo, 10/10): accumula per due giorni
python3 agents/chi_vende_nel_dump.py || echo "   DUMP | non misurabile"

# le tre strade per cui la memoria si perde (vedi dove_si_perde.py)
python3 agents/dove_si_perde.py || echo "   PERDITE | non misurabili"

# I PROCESSI LANCIATI A MANO SU QUESTO MAC (11/10): sono il punto cieco delle guardie, che
# guardano solo le corsie di GitHub. Un `while true` del 9 ottobre e' girato 44 ore rubando
# il nodo RPC alla prova in avanti senza che nessuno lo vedesse.
python3 agents/processi_a_mano.py || echo "   PROCESSI | non elencabili"

