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
CRITICHE="accumulator:360 astra:4320 censimento:90 ciclo:360 collector:360 deposito:180 finanziatori:60 guardiani:240 heartbeat:180 hook:90 iniziatori:180 insider:180 insieme:240 ispezione:180 paper_bot:360 piu_intelligente:4320 popolazione:180 previsioni:180 prova_avanti:4320 pubblicatore:60 riparazione:180 riserve:180 scoperta:90 sentinella:120 soccorso:120 solana_helius:90 storico:180 vivo:150"
RILANCIATE=0
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
    echo "   DAL DI FUORI | $W ferma da ${ETA} min (limite $LIM) — rilanciata (HTTP $C)"
    RILANCIATE=$((RILANCIATE+1))
  fi
done
[ "$RILANCIATE" = "0" ] && echo "   DAL DI FUORI | tutte le corsie critiche sono nei limiti"
exit 0

# CORSIE CHE GITHUB NON SA LEGGERE (2/10). Due volte in un giorno un file di corsia illeggibile
# ha mandato email a raffica — `riserve` e `guardia` — e in entrambi i casi il sintomo stava
# nei dati di GitHub: come nome della corsia riportava il percorso del file. Questo controllo
# non si puo' fare prima di pubblicare, perche' serve il file sul ramo: si fa subito DOPO.
GH_TOKEN="$TOK" python3 -B "$(dirname "$0")/corsia_illeggibile.py" || true
