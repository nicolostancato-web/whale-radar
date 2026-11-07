#!/bin/bash
# LE COPIE SUL REPO SONO ALLINEATE A QUELLE LOCALI?
#
# Perche' esiste (3/11). La cartella temporanea cancella i file, e
# ripristina.sh li riscarica dal repository. Ma se la copia sul repo fosse
# VECCHIA, il ripristino reintrodurrebbe un difetto gia' corretto -- e
# sarebbe invisibile: il file c'e', il sistema parte, e gira con un bug che
# credevo chiuso. Stamattina ho trovato nel log 7 NameError di un difetto
# corretto il 1/11, ed e' stato quel sospetto a far nascere questo controllo.
# I file erano identici, ma «verificato una volta» non e' una garanzia.
cd "$(dirname "$0")/.." || exit 1
REPO="https://raw.githubusercontent.com/nicolostancato-web/whale-radar/main"
LOG=/tmp/copie.log
diversi=0; mancanti=0
# AGGIUNTI il 5/11 i tre pezzi dell'occhio largo. Senza di loro nella lista,
# un ripristino non li recupererebbe e la sentinella tornerebbe a sentire
# l'8% degli aggiornamenti -- cioe' il guasto che ci e' costato 8
# liquidazioni su 8, rimesso dentro da chi doveva ripararne un altro.
for f in keccak.py pescatore.py in_acqua.py sentinella.py invia_pacchetto.py \
         prepara_vendite.py conferma_e_avvisa.py avvisa.py prezzi_dall_oracolo.py \
         occhio_ws.py grezzo_in_casa.py prezzo_nuovo.py misura_occhio.py \
         indirizzi.py check_finale.py; do
# indirizzi.py E check_finale.py AGGIUNTI il 5/11 sera, e la mancanza era
# grave: indirizzi.py e' la SORGENTE UNICA dell'indirizzo del contratto --
# quello che ha chiuso lo zero di sei settimane -- e non era fra i file che
# il ripristino confronta. Un ripristino avrebbe potuto riportare la firma
# di un contratto che non e' in catena, cioe' esattamente il guasto che
# quel file esiste per rendere impossibile.
  [ -f "agents/$f" ] || continue
  if curl -sfL -o "/tmp/.cmp_$f" "$REPO/agents/$f" 2>/dev/null; then
    if ! diff -q "agents/$f" "/tmp/.cmp_$f" >/dev/null 2>&1; then
      echo "$(date -u '+%F %T') DIVERSO agents/$f: la copia sul repo non e' quella locale" >> "$LOG"
      diversi=$((diversi+1))
    fi
    rm -f "/tmp/.cmp_$f"
  else
    echo "$(date -u '+%F %T') MANCA sul repo: agents/$f" >> "$LOG"
    mancanti=$((mancanti+1))
  fi
done
printf '{"quando":"%s","diversi":%d,"mancanti_sul_repo":%d}\n' \
  "$(date -u '+%F %T')" "$diversi" "$mancanti" > data/liquidazioni/copie.json
[ "$diversi" -gt 0 ] && echo "   ATTENZIONE: $diversi file hanno la copia sul repo DIVERSA da quella locale"
[ "$mancanti" -gt 0 ] && echo "   ATTENZIONE: $mancanti file non sono sul repo: un ripristino non potrebbe recuperarli"
exit 0
