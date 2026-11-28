#!/bin/bash
# LA GUARDIA, terza versione. Le due precedenti hanno sbagliato ENTRAMBE allo
# stesso modo: cercavano una STRINGA nella lista dei processi.
#
#  v1 (tieni_vivo_pescatore.sh): `pgrep -f in_acqua.py` trovava lo ZOMBIE del
#     figlio morto. Il sistema armato e' stato giu' mezz'ora sembrando sano.
#  v2 (questa, prima stesura): scartava gli zombie ma il filtro
#     `*python*in_acqua.py*` agganciava QUALUNQUE processo python con quel
#     nome fra gli argomenti -- compreso il mio comando di pubblicazione
#     `python agents/pubblica_file.py ... agents/in_acqua.py`. Il battito
#     annunciava pid che non erano il pescatore.
#
# LA LEZIONE: non si identifica un lavoratore indovinandolo da fuori. Il
# lavoratore DICHIARA il proprio pid nel suo file di vita, e la guardia
# controlla due cose:
#   1. quel pid e' vivo (kill -0)
#   2. il file di vita e' FRESCO
# Il secondo controllo e' quello che le versioni precedenti non avevano, ed
# e' il piu' importante: prende anche il processo vivo ma BLOCCATO, che un
# controllo sui processi dichiara sano per sempre.
cd "$(dirname "$0")/.." || exit 1
CHI="$1"; MINUTI="${2:-600}"; VITA="$3"
[ -z "$VITA" ] && VITA="data/liquidazioni/${CHI}_vivo.json"
BATTITO="data/liquidazioni/guardia_${CHI}.json"
# UNA GUARDIA SOLA PER LAVORATORE, GARANTITO DA UN LUCCHETTO (7/11).
# Difetto che mi sono fatto io, e la cosa peggiore e' che l'ha creato lo
# strumento scritto per evitarlo: riavvia.sh avvia una guardia se non la
# trova, il controllo mi e' sfuggito una volta, e si sono ritrovate DUE
# guardie per la sentinella -- quindi DUE sentinelle armate, ognuna con
# sette connessioni aperte sulle stesse porte. E' il modo esatto in cui il
# 5/11 ci siamo fatti strozzare dalle fonti.
# «Non avviarne due» non e' una regola che si puo' ricordare: e' un
# invariante, e un invariante si mette nel codice che lo puo' violare.
# Il lucchetto e' una cartella, perche' mkdir e' atomico su qualunque
# filesystem: se esiste gia', un'altra guardia sta lavorando e questa esce.
LUCCHETTO="data/liquidazioni/.guardia_${CHI}.lock"
if ! mkdir "$LUCCHETTO" 2>/dev/null; then
  # il lucchetto puo' essere rimasto da una guardia morta male: si guarda
  # se il pid dentro e' ancora vivo prima di arrendersi.
  VECCHIO=$(cat "$LUCCHETTO/pid" 2>/dev/null || echo 0)
  if [ "${VECCHIO:-0}" != "0" ] && kill -0 "$VECCHIO" 2>/dev/null; then
    echo "$(date -u '+%F %T') c'e' gia' una guardia di $CHI (pid $VECCHIO): esco" >> "/tmp/guardia_${CHI}.log"
    exit 0
  fi
  echo "$(date -u '+%F %T') lucchetto orfano di $CHI (pid $VECCHIO morto): lo prendo" >> "/tmp/guardia_${CHI}.log"
  echo $$ > "$LUCCHETTO/pid"
else
  echo $$ > "$LUCCHETTO/pid"
fi
trap 'rm -rf "$LUCCHETTO"' EXIT INT TERM
LOG="/tmp/guardia_${CHI}.log"
MAX_FERMO=240          # secondi: oltre questo il file di vita e' stantio
GIRO=0
while true; do
  GIRO=$((GIRO+1)); STATO="ok"; PID=0
  PID=$(python3 -c "import json;print(json.load(open('$VITA')).get('pid',0))" 2>/dev/null || echo 0)
  if [ "${PID:-0}" = "0" ]; then
    STATO="senza_pid"
  elif ! kill -0 "$PID" 2>/dev/null; then
    STATO="morto"
  else
    ETA=$(python3 -c "import os,time;print(int(time.time()-os.path.getmtime('$VITA')))" 2>/dev/null || echo 9999)
    [ "$ETA" -gt "$MAX_FERMO" ] && STATO="bloccato_da_${ETA}s"
  fi
  if [ "$STATO" != "ok" ]; then
    if [ -f data/liquidazioni/preso.flag ]; then
      echo "$(date -u '+%F %T') presa avvenuta, non riavvio ($STATO)" >> "$LOG"
    else
      echo "$(date -u '+%F %T') $CHI e' $STATO -> RIAVVIO" >> "$LOG"
      [ "${PID:-0}" != "0" ] && kill -9 "$PID" 2>/dev/null   # se bloccato, si chiude
      nohup .venv_bot2/bin/python -u "agents/${CHI}".py "$MINUTI" \
        >> "/tmp/${CHI}.log" 2>&1 &
      sleep 25   # il primo giro del pescatore legge TUTTE le posizioni
                 # (18 secondi su 846): cercare il pid dopo 6 lo dichiarava
                 # morto e innescava un ciclo di riavvii
      PID=$(python3 -c "import json;print(json.load(open('$VITA')).get('pid',0))" 2>/dev/null || echo 0)
      echo "$(date -u '+%F %T') dopo il riavvio: pid ${PID}" >> "$LOG"
      # lo STATO va ricalcolato: mostrare «senza_pid» subito dopo un riavvio
      # riuscito e' un falso allarme, e un allarme che grida a vuoto si
      # impara a ignorare. Era lo stesso difetto della versione precedente:
      # l'ho reintrodotto riscrivendo, quindi ora e' scritto qui.
      if [ "${PID:-0}" != "0" ] && kill -0 "$PID" 2>/dev/null; then
        STATO="ok_dopo_riavvio"
      else
        STATO="riavvio_non_riuscito"
      fi
    fi
  fi
  printf '{"quando":"%s","chi":"%s","giro":%d,"pid":%s,"stato":"%s"}\n' \
    "$(date -u '+%F %T')" "$CHI" "$GIRO" "${PID:-0}" "$STATO" > "$BATTITO.tmp" \
    && mv -f "$BATTITO.tmp" "$BATTITO"
  # SI SCRIVE SU UN TEMPORANEO E SI SPOSTA (7/11 sera). Scrivere diretto sul
  # file lascia una finestra in cui chi legge trova un file VUOTO: il C-check
  # e' andato rosso con «Expecting value: line 1 column 1», che sembra un
  # guasto della guardia e invece e' una lettura strappata. Lo spostamento e'
  # atomico, quindi chi legge vede il vecchio contenuto o il nuovo, mai
  # niente. Stessa lezione dell'archivio a prova di interruzione.
  sleep 45
done
