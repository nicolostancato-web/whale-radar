#!/bin/bash
# ASTRA_REVIEW - la revisione esterna quotidiana, senza Nicolo in mezzo.
#
# Perche esiste: le due consulenze esterne che ci hanno dato piu valore (il metro dei costi e i
# cinque punti del 04/09) hanno trovato errori che il nostro revisore interno non poteva vedere,
# perche l ho scritto io e controlla i modi di illudersi che avevo gia immaginato.
# Contro l errore che non abbiamo ancora fatto serve qualcuno FUORI dal sistema.
#
# UNA VOLTA AL GIORNO, non a ogni ciclo. Un critico che parla ogni ora produce suggerimenti ogni
# ora, e ogni suggerimento e una spinta a toccare qualcosa. Da qui al 3 ottobre la cosa giusta e
# NON toccare: il ritmo lento e una scelta, non un limite tecnico.
#
# SOLA LETTURA: nessun accesso al test sigillato, nessuna modifica alla strategia.
# Usa l abbonamento ChatGPT gia attivo (login con account, nessuna API key, nessun addebito extra).
set -u
# IL BINARIO SI CERCA, NON SI INCHIODA (09/09). Era fissato a una versione precisa
# dell estensione: basta un aggiornamento di VS Code e la consulenza sparisce in silenzio.
# Qui si prende sempre la piu recente presente.
CX=$(ls -d "$HOME"/.vscode/extensions/openai.chatgpt-*/bin/macos-aarch64/codex 2>/dev/null | sort -V | tail -1)
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-ASTRA_REVIEW.md}"
STATO="${2:-DOSSIER_ASTRA.md}"   # il fascicolo completo, non il solo riassunto
if [ ! -x "$CX" ]; then echo "ASTRA | binario non trovato"; exit 1; fi
if [ ! -f "$STATO" ]; then
  # il fascicolo si costruisce da solo: contiene cosa ha detto l ultima volta, cosa abbiamo fatto
  # dopo, i numeri di adesso, il cimitero delle idee morte e un angolo diverso ogni volta.
  python3 "$DIR/agents/dossier_astra.py" >/dev/null 2>&1 || true
fi
if [ ! -f "$STATO" ]; then echo "ASTRA | manca $STATO"; exit 1; fi

PROMPT=$(cat "$(dirname "$0")/prompt_astra.txt")

RISP=$("$CX" exec --skip-git-repo-check -c model_reasoning_effort="high" "$PROMPT

--- FASCICOLO ---
$(cat "$STATO")" 2>&1 | sed -n "/^codex$/,\$p" | sed "1d;/^tokens used/,\$d")

# UNA CONSULENZA FALSA E PEGGIO DI NESSUNA CONSULENZA (10/09). Se la chiamata fallisce — piano
# scaduto, modello non disponibile, 401 — l errore finiva dentro RISP e veniva scritto nel file come
# se fosse il parere del consulente: intestazione giusta, data di oggi, dentro un messaggio di
# errore. Il guardiano avrebbe visto "Astra ha parlato 0 ore fa" ed era verde su una cosa morta.
# Adesso, se la risposta non e una consulenza, il file vecchio NON si tocca e il fallimento si vede.
if [ ${#RISP} -lt 400 ] || printf '%s' "$RISP" | grep -qE 'invalid_request_error|^ERROR:|401 Unauthorized|not supported when using'; then
  echo "ASTRA | LA CONSULENZA NON E ARRIVATA. Non sovrascrivo $OUT. Motivo:"
  printf '%s\n' "$RISP" | tail -3
  exit 2
fi
DATA=$(date -u "+%Y-%m-%d %H:%M UTC")
{
  echo "# 🔭 REVISIONE ESTERNA (Astra)"
  echo "*$DATA · una volta al giorno · sola lettura · nessun accesso al sigillo*"
  echo
  echo "> Serve contro l errore che non abbiamo ancora fatto: il revisore interno l ho scritto io,"
  echo "> quindi controlla i modi di illudersi che avevo gia immaginato. Questo no."
  echo
  echo "$RISP"
} > "$OUT"
N=$(wc -l < "$OUT")
echo "ASTRA | scritto $OUT, $N righe"
