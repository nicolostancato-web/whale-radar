#!/bin/bash
# RIAVVIARE UN PROCESSO CHE HA UNA GUARDIA: si lascia fare a LEI.
#
# Difetto trovato il 7/11 sera, e me lo sono fatto io cinque volte di
# seguito. Per attivare il codice nuovo uccidevo la sentinella e la
# riavviavo a mano. Ma la sentinella HA una guardia che fa esattamente
# questo, e nei secondi fra l'uccisione e il mio avvio partivano entrambi:
# risultato, la guardia scriveva «riavvio_non_riuscito», il C-check diceva
# «manca la guardia di sentinella» e il blocco 1 crollava dal 97% al 90%.
# Tutto falso, e il colpevole era la mia procedura.
#
# E il danno vero non e' il falso allarme: e' il rischio di DUE processi
# armati insieme sulle stesse porte, che e' il modo in cui il 5/11 ci siamo
# fatti strozzare dalle fonti.
#
# LA REGOLA: non si avvia niente a mano. Si uccide, e si ASPETTA che la
# guardia faccia il suo lavoro -- che e' anche il solo modo di verificare
# che la guardia funzioni davvero a ogni riavvio, invece di crederci.
#
#   uso:  ./agents/riavvia.sh sentinella [attesa_massima_secondi]
cd "$(dirname "$0")/.." || exit 1
CHI="${1:-sentinella}"
MAX="${2:-150}"
VITA="data/liquidazioni/${CHI}_viva.json"
[ -f "$VITA" ] || VITA="data/liquidazioni/${CHI}_vivo.json"
[ -f "$VITA" ] || { echo "non trovo il file di vita di $CHI"; exit 1; }
pid() { python3 -c "import json;print(json.load(open('$VITA')).get('pid',0))" 2>/dev/null || echo 0; }
PRIMA=$(pid)
# AVVIARE UNA GUARDIA DA QUI HA CREATO IL DANNO CHE DOVEVO EVITARE (7/11).
# Questo blocco avviava una guardia se non la trovava, il controllo mi e'
# sfuggito una volta, e si sono ritrovate DUE guardie per la sentinella --
# quindi DUE sentinelle armate con sette connessioni ciascuna sulle stesse
# porte. Lo strumento scritto per impedire la duplicazione l'ha causata.
# Ora la guardia ha un lucchetto atomico (vedi guardia.sh) e avviarne una
# in piu' e' innocuo, ma qui NON si avvia niente: se la guardia manca si
# dice e si esce, perche' questo strumento serve a riavviare un lavoratore,
# non a mettere su l'impalcatura.
if ! pgrep -f "guardia.sh $CHI" >/dev/null; then
  echo "FERMO: $CHI non ha una guardia viva. Avviala tu con:"
  echo "   nohup ./agents/guardia.sh $CHI 600 $VITA >/dev/null 2>&1 &"
  exit 1
fi
echo "uccido $CHI (pid $PRIMA) e lascio riavviare alla guardia"
[ "${PRIMA:-0}" != "0" ] && kill -9 "$PRIMA" 2>/dev/null
T=0
while [ "$T" -lt "$MAX" ]; do
  sleep 5; T=$((T+5))
  DOPO=$(pid)
  if [ "${DOPO:-0}" != "0" ] && [ "$DOPO" != "$PRIMA" ] && kill -0 "$DOPO" 2>/dev/null; then
    echo "RIAVVIATO DALLA GUARDIA in ${T}s: $PRIMA -> $DOPO"
    pgrep -f "${CHI}.py" | wc -l | xargs echo "processi ${CHI} vivi (deve essere 1):"
    exit 0
  fi
done
echo "FALLITO: la guardia non ha riavviato $CHI in ${MAX}s -- intervenire"
exit 1
