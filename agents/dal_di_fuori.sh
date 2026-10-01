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
CRITICHE="pubblicatore:60 sentinella:120 heartbeat:180 guardiani:240 hook:90 scoperta:90 censimento:90 insieme:240 soccorso:120 vivo:150 ciclo:360 deposito:180"
RILANCIATE=0
for VOCE in $CRITICHE; do
  W="${VOCE%%:*}"; LIM="${VOCE##*:}"
  ETA=$(curl -s -H "Authorization: token $TOK" \
    "https://api.github.com/repos/$REPO/actions/workflows/$W.yml/runs?per_page=10" \
    | python3 -c "
import sys,json,datetime as dt
d=json.load(sys.stdin).get('workflow_runs',[])
if not d: print(99999); raise SystemExit
# in coda O in corso, su QUALSIASI dei giri recenti, non solo il piu' nuovo: una corsia che
# aspetta un posto non va rilanciata, il rilancio la fa solo annullare (misurato 1/10 su hook)
if any(x['status']!='completed' for x in d): print(0); raise SystemExit
# L'ETA' SI CONTA DALL'ULTIMO SUCCESSO, NON DALL'ULTIMO LANCIO (1/10). Qui si prendeva d[0],
# cioe' il giro piu' recente QUALUNQUE fosse il suo esito. Tre giri annullati di fila alle
# 11:53/11:55/11:57 — che non hanno fatto nulla — rimettevano l'orologio a zero, e la guardia
# diceva «nei limiti» su una corsia morta dalle 06:00. Un lancio non e' un lavoro.
vivi=[x for x in d if x.get('conclusion')=='success']
if not vivi: print(99999); raise SystemExit
r=vivi[0]
n=dt.datetime.strptime(r['created_at'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
print(int((dt.datetime.now(dt.timezone.utc)-n).total_seconds()//60))" 2>/dev/null || echo 0)
  if [ "${ETA:-0}" -gt "$LIM" ]; then
    C=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Authorization: token $TOK" \
      -H "Accept: application/vnd.github+json" \
      "https://api.github.com/repos/$REPO/actions/workflows/$W.yml/dispatches" -d '{"ref":"main"}')
    echo "   DAL DI FUORI | $W ferma da ${ETA} min (limite $LIM) — rilanciata (HTTP $C)"
    RILANCIATE=$((RILANCIATE+1))
  fi
done
[ "$RILANCIATE" = "0" ] && echo "   DAL DI FUORI | tutte le corsie critiche sono nei limiti"
exit 0
