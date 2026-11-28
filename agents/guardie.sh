#!/bin/bash
# LE TRE GUARDIE CRITICHE, IN UN LOOP PROPRIO (5/11).
#
# PERCHE' ESISTE. Prima stavano dentro il giro del laghetto, programmate
# "ogni N passate". Le ho legate all'orologio e NON E' BASTATO: un cancello
# a tempo impedisce di girare troppo spesso, ma non puo' far girare qualcosa
# se il ciclo arriva a quel punto una volta all'ora. Il termine dominante era
# la DURATA DEL CICLO (passata da 7 minuti a oltre un'ora), e il tabellone
# risultava vecchio di 3,8 ore pur avendo un cancello da 30 minuti.
#
# LA REGOLA: una cadenza garantita non puo' dipendere dal tempo di
# qualcos'altro. Chi deve girare ogni 15 minuti gira in un ciclo suo, corto,
# che non fa nient'altro.
cd "$(dirname "$0")/.." || exit 1

# UN SOLO CICLO ALLA VOLTA. Il 5/11 mi sono ritrovato QUATTRO cicli di
# guardie in esecuzione perche' li riavviavo senza fermare i precedenti:
# si pestavano sui file di stato e martellavano il nodo per niente.
# Un ciclo senza lucchetto si moltiplica a ogni riavvio.
LUCCHETTO=data/liquidazioni/.guardie.pid
if [ -f "$LUCCHETTO" ] && kill -0 "$(cat "$LUCCHETTO" 2>/dev/null)" 2>/dev/null; then
  echo "un altro ciclo di guardie e' vivo (pid $(cat "$LUCCHETTO")): non parto"
  exit 0
fi
echo $$ > "$LUCCHETTO"
trap 'rm -f "$LUCCHETTO"' EXIT
PY=.venv_bot2/bin/python

# L'OROLOGIO CONDIVISO col giro del laghetto: lo stesso timbro, cosi' chi
# arriva primo rinfresca e l'altro salta. Serve perche' la lista corta e' il
# pezzo che NON puo' invecchiare, e stava in un ciclo che dura un'ora.
scaduto() {   # scaduto <nome> <minuti>
  local f="data/liquidazioni/.ultimo_$1" ora q
  [ -f "$f" ] || return 0
  ora=$(date +%s); q=$(cat "$f" 2>/dev/null || echo 0)
  [ $((ora - q)) -ge $(( $2 * 60 )) ]
}
segna() { date +%s > "data/liquidazioni/.ultimo_$1" 2>/dev/null || true; }

while true; do
  echo "== guardie $(date '+%Y-%m-%d %H:%M:%S')"
  $PY agents/tabellone.py 2>&1 | tail -2
  # il percorso v4 ogni 8 giri di guardia (~2 ore): costa qualche decina di
  # secondi perche' prova piu' candidate su una copia della catena
  G4=$(( ${G4:-0} + 1 ))
  if [ $((G4 % 8)) -eq 1 ]; then $PY agents/da_capo_a_fondo.py v4 2>&1 | tail -1; fi
  # la catena a TRE passaggi (due piazze), sfasata rispetto a quella a due
  if [ $((G4 % 8)) -eq 5 ]; then $PY agents/da_capo_a_fondo.py tre 2>&1 | tail -1; fi
  $PY agents/check_finale.py 2>&1 | tail -3
  $PY agents/blocchi.py 2>&1 | tail -4
  # IL PUNTEGGIO che conta solo dalla riparazione del contratto, e poi la
  # SORVEGLIANZA (tre domande e un permesso), che legge gli esiti dei passi
  # sopra invece di rifarli. Vanno in quest'ordine: la sorveglianza dipende
  # dal tabellone, dal punteggio e dai blocchi.
  # DOVE ERAVAMO: la fotografia della nostra posizione, legata al blocco.
  # Va PRIMA del punteggio: e' la prova che l'autopsia usera' se nel
  # frattempo si chiude una liquidazione.
  $PY agents/dove_eravamo.py 2>&1 | tail -1
  # IL CONTATORE CHE NON PUO' SBAGLIARE: due metodi indipendenti, e se non
  # concordano dice "non lo so" invece di dare un numero. Va PRIMA del
  # punteggio, perche' e' la cosa che non deve sfuggire: l'ottava
  # liquidazione la dobbiamo VEDERE.
  $PY agents/conta_sicuro.py 2>&1 | tail -2
  $PY agents/da_quando_siamo_veri.py 2>&1 | tail -2
  $PY agents/perche_lui_e_non_io.py 2>&1 | tail -8
  # LA DISTANZA SOTTILE: non "abbiamo perso" ma "di quanto". E' il goal dei
  # giri, deciso con Nicolo' il 5/11 sera: assottigliare la vicinanza.
  $PY agents/di_quanto_abbiamo_perso.py 2>&1 | tail -7
  $PY agents/sorveglianza.py 2>&1 | tail -7
  # IMPARARE DAI GIORNI SCORSI, a pezzi, nei giri in cui il live e' vuoto.
  # Va per ULTIMO: il live ha la precedenza, e lo studio si sospende da se'
  # se c'e' un caso live da spiegare.
  $PY agents/impara_dai_giorni_scorsi.py 2>&1 | tail -3
  date +%s > data/liquidazioni/.ultimo_tabellone
  date +%s > data/liquidazioni/.ultimo_ccheck
  date +%s > data/liquidazioni/.ultimo_blocchi
  # LA POPOLAZIONE, QUI E NON SOLO NEL LAGHETTO (6/11).
  #
  # La lezione in cima a questo file -- «una cadenza garantita non puo'
  # dipendere dal tempo di qualcos'altro» -- era scritta e NON applicata al
  # pezzo che conta di piu'. Il rinfresco della lista corta e' rimasto nella
  # passata del laghetto, che dura un'ora: col cancello da 20 minuti girava
  # ogni 31+, perche' il cancello non puo' far girare niente se il ciclo
  # arriva a quel punto una volta all'ora.
  # COSTO MISURATO DI QUEL RITARDO: la nona e la decima liquidazione hanno
  # colpito posizioni che non erano nel libro (salute 1,0047 e 1,0068, in
  # piena fascia) perche' la lista era ferma da 15 ore.
  # Il timbro e' lo stesso del laghetto: chi arriva primo rinfresca.
  if scaduto listaCorta 20; then
    echo "-- rifaccio la lista corta (giro veloce)"
    $PY agents/lista_corta.py 2>&1 | tail -2
    segna listaCorta
  fi
  sleep 900
done
