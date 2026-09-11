#!/bin/bash
# ASTRA_GIORNALIERO - fa girare la consulenza esterna DUE VOLTE AL GIORNO (deciso il 06/09).
#
# Non serve un cron: cavalca il loop orario di Claude. A ogni giro guarda quanto e vecchia l ultima
# revisione; se ha meno di 20 ore non fa niente e lo dice in una riga.
#
# Perche due volte e non a ogni giro: un critico che parla ogni ora produce dieci
# suggerimenti al giorno e nessuno viene mai finito. Il ritmo lento e una scelta, non un limite.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$DIR/ASTRA_REVIEW.md"
ORE_MIN=${ORE_MIN:-11}   # due volte al giorno (11h, non 12: cosi' non slitta)
# L ETA SI LEGGE DENTRO IL FILE, NON DAL FILESYSTEM (09/09). Si usava la data di modifica: un
# semplice clone della cartella la azzera, e Astra si e messa a dormire 11 ore convinta di aver
# appena parlato. La data vera e scritta nell intestazione della consulenza, ed e l unica che un
# copia-incolla non puo falsificare.
if [ -f "$OUT" ]; then
  QUANDO=$(sed -n '2s/.*\*\([0-9-]* [0-9:]*\) UTC.*/\1/p' "$OUT")
  if [ -n "$QUANDO" ]; then
    SEC=$(date -u -j -f "%Y-%m-%d %H:%M" "$QUANDO" "+%s" 2>/dev/null || echo 0)
  else
    SEC=0
  fi
  [ "$SEC" = "0" ] && SEC=$(stat -f %m "$OUT")
  ETA=$(( ($(date +%s) - SEC) / 3600 ))
  if [ "$ETA" -lt "$ORE_MIN" ]; then
    echo "ASTRA | ultima consulenza $ETA ore fa, ne servono $ORE_MIN: salto"
    exit 0
  fi
fi
# PRIMA DI TUTTO, AGGIORNARSI (09/09). Astra girava in una cartella scaricata giorni prima:
# leggeva numeri vecchi e agenti che non esistevano piu. Un consulente a cui dai il mondo di
# ieri ti risponde su ieri, e la risposta sembra comunque sensata — e il modo piu silenzioso
# di sprecare una consulenza.
# LA CARTELLA E UNO SPECCHIO, NON UN BANCO DA LAVORO (11/09). Con "pull" bastava un rapporto
# generato qui a bloccare tutto: "Please move or remove them before you merge. Aborting" — e la
# consulenza girava lo stesso, sul mondo di ieri, senza dirlo. Qui si allinea e basta: quello che
# vale sta nel repo, ed e la sola cosa che il consulente deve leggere.
git -C "$DIR" fetch -q origin main 2>/dev/null && git -C "$DIR" reset --hard -q origin/main 2>/dev/null \
  && git -C "$DIR" clean -fdq -e "*.log" 2>/dev/null \
  || echo "ASTRA | ATTENZIONE: non sono riuscito ad allineare la cartella, i numeri potrebbero essere vecchi"
echo "ASTRA | avvio la consulenza giornaliera"
# IL FASCICOLO, NON UN FILE CHE NON ESISTE (09/09). Qui si passava STATO.md: non esiste, e il
# revisore sa costruire da solo solo il DOSSIER. Risultato: ogni giro moriva su "manca STATO.md"
# e Astra e stata muta tre giorni senza che nessuno se ne accorgesse. Un pezzo di impianto che
# fallisce sempre allo stesso modo non e un errore raro: e un pezzo che non ha mai funzionato.
"$DIR/astra_review.sh" "$OUT" "$DIR/DOSSIER_ASTRA.md"
