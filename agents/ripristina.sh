#!/bin/bash
# RIPRISTINA i file essenziali che la cartella temporanea cancella.
#
# COSA E' SUCCESSO il 2/11, e perche' questo file esiste.
# `prezzi_oracolo.json` e' sparito. Lo legge QUASI TUTTO il sistema, e
# pescatore.py lo legge ALL'IMPORT -- quindi anche in_acqua e sentinella, che
# lo importano. Il pescatore e la sentinella erano vivi solo perche' non si
# erano riavviati: giravano sulla copia in memoria. Al PRIMO RIAVVIO sarebbero
# morti entrambi, e la guardia li avrebbe rialzati in ciclo senza riuscirci,
# scrivendo «riavvio» all'infinito. Il sistema armato era a un riavvio dalla
# morte totale e tutti i battiti dicevano OK.
# Aveva gia' fatto fallire 15 esecuzioni nei log prima che me ne accorgessi.
#
# TRE DIFESE, perche' una sola non basta:
#  1. si RIGENERA quello che si puo' rigenerare (i prezzi dall'oracolo);
#  2. si SCARICA dal repo quello che non si puo' rigenerare;
#  3. si fa all'inizio di ogni giro, non una volta sola.
cd "$(dirname "$0")/.." || exit 1
REPO="https://raw.githubusercontent.com/nicolostancato-web/whale-radar/main"
LOG=/tmp/ripristina.log
ripristinati=0
# --- gli script: si riscaricano dal repo
for f in keccak.py pescatore.py in_acqua.py sentinella.py invia_pacchetto.py \
         prepara_vendite.py conferma_e_avvisa.py avvisa.py lista_corta.py \
         composizione_posizioni.py metrica.py metrica_pagina.py istantanea.py \
         prima_bolla.py guarda_la_cassa.py raccogli_debitori.py \
         prezzi_dall_oracolo.py pubblica_file.py; do
  if [ ! -f "agents/$f" ]; then
    if curl -sfL -o "agents/$f" "$REPO/agents/$f"; then
      echo "$(date -u '+%F %T') ripristinato agents/$f dal repo" >> "$LOG"
      ripristinati=$((ripristinati+1))
    else
      echo "$(date -u '+%F %T') MANCA agents/$f e NON e' sul repo" >> "$LOG"
    fi
  fi
done
# --- i prezzi: si RIGENERANO, che e' meglio di una copia vecchia.
# Si rigenerano se MANCANO *oppure* se sono VECCHI. Trovato il 3/11: qui
# c'era solo il controllo "il file manca", e il file aveva 40 ORE. In un
# crollo del 9% un file di 40 ore e' il pezzo piu' pericoloso del sistema:
# ogni quantita' da vendere viene calcolata su prezzi di prima del crollo.
# Rigenerarli costa 67 letture all'oracolo, cioe' niente: si fa ogni giro.
# 300 e non 600: il giro del laghetto dura 420 secondi, quindi con 600 i
# prezzi potevano restare vecchi fino a 17 minuti. Con 300 si rinfrescano a
# ogni giro. Costa 67 letture all'oracolo ogni sette minuti, cioe' niente.
VECCHI_SECONDI=300
rigenera=0
if [ ! -f data/liquidazioni/prezzi_oracolo.json ]; then
  rigenera=1; motivo="mancanti"
else
  eta=$(( $(date +%s) - $(stat -f %m data/liquidazioni/prezzi_oracolo.json) ))
  if [ "$eta" -gt "$VECCHI_SECONDI" ]; then rigenera=1; motivo="vecchi ${eta}s"; fi
fi
if [ "$rigenera" = "1" ]; then
  echo "$(date -u '+%F %T') prezzi $motivo: li rigenero dall'oracolo" >> "$LOG"
  .venv_bot2/bin/python agents/prezzi_dall_oracolo.py >> "$LOG" 2>&1 \
    && ripristinati=$((ripristinati+1))
fi
# --- i dati che non si rigenerano: dal repo
for f in tetti.json da_sorvegliare.json novanta_giorni.json ogni_quanto.json \
         avrebbe_pagato.json la_gara.json accorgersi.json; do
  if [ ! -f "data/liquidazioni/$f" ]; then
    if curl -sfL -o "data/liquidazioni/$f" "$REPO/data/liquidazioni/$f"; then
      echo "$(date -u '+%F %T') ripristinato data/liquidazioni/$f" >> "$LOG"
      ripristinati=$((ripristinati+1))
    fi
  fi
done
printf '{"quando":"%s","ripristinati":%d}\n' "$(date -u '+%F %T')" "$ripristinati" \
  > data/liquidazioni/ripristino.json
[ "$ripristinati" -gt 0 ] && echo "   RIPRISTINATI $ripristinati file essenziali"
exit 0
