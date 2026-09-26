#!/bin/bash
# PUBBLICA SOLO CIO' CHE COMPILA (25/09).
#
# Il controllo di sintassi lo facevo gia'. Il 25/09 ho pubblicato lo stesso un file rotto — un
# commento infilato dentro un'espressione — perche' avevo legato il controllo alla pubblicazione
# con `;` invece che con `&&`: il controllo falliva, e il push partiva un comando dopo.
#
# La lezione NON e' «stare piu' attento a quale segno uso»: e' che un controllo la cui bocciatura
# non ferma niente non e' un controllo, e' un commento.
# IN POSITIVO: **si pubblica da qui, e da qui la pubblicazione non parte se qualcosa non compila.**
#
# uso:  ./pubblica.sh "messaggio del commit"
set -e

[ -n "$1" ] || { echo "manca il messaggio del commit"; exit 1; }

echo "— controllo che tutto compili"
python3 - <<'PY'
import ast, pathlib, sys
rotti = []
for f in sorted(pathlib.Path("agents").glob("*.py")):
    try:
        ast.parse(f.read_text())
    except SyntaxError as e:
        rotti.append(f"{f}:{e.lineno} {e.msg}")
if rotti:
    print("NON PUBBLICO, questi file sono rotti:")
    for r in rotti:
        print("   ", r)
    sys.exit(1)
print("   tutti i file di agents/ compilano")
PY

echo "— controllo che i file di lavoro non restino solo qui"
git add -A
git -c user.name="whale-radar-bot" -c user.email="bot@users.noreply.github.com" \
    commit -q -m "$1" || { echo "niente da salvare"; exit 0; }

# LA CRONOLOGIA A MONTE VIENE RISCRITTA (26/09). Una corsia di manutenzione compatta il
# repository ogni tanto («GC squash»), e dopo quel momento una copia superficiale ha una storia che
# non si collega piu' a quella del server: `git pull` risponde «refusing to merge unrelated
# histories» e si ferma. Oggi mi ha dato numeri vecchi per mezz'ora senza dirmi niente; se capitasse
# durante una pubblicazione, il lavoro resterebbe su questa macchina — che e' il modo in cui ho
# perso tre file questa settimana.
# `--allow-unrelated-histories` fa la cosa giusta: le due storie si uniscono, e `-X ours` tiene le
# mie modifiche in caso di conflitto.
for i in $(seq 1 10); do
  git pull --no-rebase --no-edit --allow-unrelated-histories -X ours origin main >/dev/null 2>&1 || true
  if git push origin main >/dev/null 2>&1; then echo "— spinto al tentativo $i"; exit 0; fi
  sleep 6
done
echo "NON SONO RIUSCITO A SPINGERE: il lavoro resta solo su questa macchina."
exit 1
