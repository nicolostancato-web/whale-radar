#!/bin/bash

# «OGNI N PASSATE» NON E' UNA FREQUENZA (riparato il 5/11).
# I commenti qui sotto dicevano "ogni 8 giri (~1 ora)" perche' una passata
# durava sette minuti. Misurato stasera: una passata dura circa UN'ORA
# (la lista corta e le vendite sono cresciute), quindi ogni guardia
# periodica scattava OTTO VOLTE MENO SPESSO di quanto credevamo -- e in
# silenzio, che e' il modo peggiore. Il tabellone risultava vecchio di 2,5
# ore pur girando "a ogni giro".
# Adesso ogni passo periodico si misura sull'OROLOGIO, non sul contatore:
# se la passata rallenta, le guardie restano alla loro frequenza.
scaduto() {   # scaduto <nome> <minuti>
  local f="data/liquidazioni/.ultimo_$1"
  [ -f "$f" ] || return 0
  local ora q
  ora=$(date +%s); q=$(cat "$f" 2>/dev/null || echo 0)
  [ $((ora - q)) -ge $(( $2 * 60 )) ]
}
segna() { date +%s > "data/liquidazioni/.ultimo_$1" 2>/dev/null || true; }
# ALLARGA IL LAGHETTO: raccoglie debitori, li controlla, aggiorna la lista
# che il pescatore sorveglia. Gira da solo, piano, senza bruciare le fonti.
#
# Ciclo:
#   1. raccoglie 5 finestre di debitori da Blockscout (max consentito)
#   2. ogni 4 giri, ricontrolla la salute di tutti e rifa' la lista corta
#   3. ogni 8 giri, ricalcola la composizione delle nuove vicine
cd "$(dirname "$0")/.."
# IL BATTITO SI SCRIVE A OGNI PASSO, non una volta per ciclo.
# DIFETTO di misura trovato l'1/11: il battito usciva una volta per ciclo, e
# il ciclo lungo (composizione + metrica su 860 posizioni) dura 15 minuti.
# Quindi un battito vecchio di 15 minuti era indistinguibile fra «lavora» e
# «bloccato», e mi ha fatto dare un falso allarme.
# La regola: il battito deve essere piu' frequente della cosa che deve
# rilevare. Se il passo piu' lungo dura 15 minuti, un battito ogni ciclo non
# serve a niente -- serve uno per passo, col NOME del passo.
G=0
battito() {
  printf '{"quando":"%s","giro":%d,"passo":"%s","fa_vendite":true}\n' \
    "$(date -u '+%F %T')" "$G" "$1" > data/liquidazioni/laghetto_vivo.json
}
while true; do
  G=$((G+1))
  # BATTITO. DIFETTO TROVATO l'1/11: questo loop ha girato per ore col
  # CODICE VECCHIO -- avevo aggiunto le vendite al suo ciclo ma bash non
  # rilegge uno script gia' in esecuzione. Zero chiamate alle vendite, e da
  # fuori sembrava che lavorasse: il log si riempiva di «202/202 finestre».
  # Un loop che gira col codice vecchio e' indistinguibile da uno che
  # lavora. Il battito registra COSA fa, non solo che e' vivo.
  battito "raccolgo debitori"
  echo "$(date -u '+%F %T') giro $G: raccolgo debitori" >> /tmp/laghetto.log
  .venv_bot2/bin/python agents/raccogli_debitori.py >> /tmp/laghetto.log 2>&1
  # LE VENDITE PRONTE, a ogni giro: e' la cosa che ci rende competitivi.
  # Preparare il preventivo PRIMA della caduta porta la composizione da
  # 990 ms a 90 ms (misurato sul percorso vero), e le liquidazioni grosse
  # si prendono nello stesso blocco. Le piu' malate si rifanno per prime;
  # quelle gia' fresche vengono saltate, quindi il cassetto scorre.
  # L'ISTANTANEA di chi sorvegliamo, a ogni giro. Serve a misurare la
  # copertura IN AVANTI: confrontare la lista di oggi con le cadute di ieri
  # da' un numero storto (dava 20,6% e era strutturalmente sbagliato, perche'
  # chi e' caduto e' stato liquidato e la liquidazione gli ha alzato la
  # salute, facendolo uscire dalla lista). Da qui ogni caduta e' una prova.
  # LA CASSA, a ogni giro. E' il controllo che non dipende da nessuno dei
  # nostri strumenti: la sentinella potrebbe non accorgersi di un'inclusione,
  # il pescatore potrebbe non scrivere il flag, l'email potrebbe non partire
  # -- tutti guasti che ho trovato davvero oggi. Ma se i soldi sono arrivati,
  # il saldo lo dice, e non c'e' niente da credere.
  # PRIMO PASSO DI OGNI GIRO: ripristinare cio' che la cartella temporanea
  # ha cancellato. Il 2/11 e' sparito prezzi_oracolo.json, che pescatore.py
  # legge ALL'IMPORT: il sistema armato era a un riavvio dalla morte totale
  # e tutti i battiti dicevano OK. Questo passo va PRIMA di tutto, perche'
  # ogni altro passo dipende da quei file.
  # LE COPIE SUL REPO SONO QUELLE GIUSTE? Il ripristino scarica da la', e una
  # copia vecchia reintrodurrebbe un difetto corretto -- invisibilmente.
  # Al primo giro di questo controllo ho scoperto che conferma_e_avvisa.py
  # (il pezzo che verifica la cassa e manda l'email) NON era sul repo: una
  # cancellazione l'avrebbe perso per sempre.
  battito "controllo le copie"
  ./agents/copie_allineate.sh >> /tmp/laghetto.log 2>&1
  battito "ripristino i file"
  ./agents/ripristina.sh >> /tmp/laghetto.log 2>&1
  battito "guardo la cassa"
  .venv_bot2/bin/python agents/guarda_la_cassa.py >> /tmp/laghetto.log 2>&1
  battito "istantanea"
  .venv_bot2/bin/python agents/istantanea.py >> /tmp/laghetto.log 2>&1
  battito "preparo vendite"
  # VENTI per giro, non ottanta. Misurato il 4/11: con 80 la fonte ci
  # rifiutava il 36% delle passate e il rinnovo degli ordini era FERMO
  # (0,0,0,2,0,0,2,0,0,0 nelle ultime dieci). Servono 13 per giro per
  # tenere 650 ordini freschi entro sei ore: 20 basta e non si viene
  # cacciati. Un rifiuto costa tutta la passata, non una richiesta.
  # OTTANTA per giro. I venti erano la dose giusta quando ogni preventivo
  # passava dall'aggregatore e chiederne troppi ci faceva cacciare. Con la
  # strada Uniswap un preventivo costa qualche lettura della catena (e le
  # vasche stanno in cache per un giorno), quindi il limite non c'e' piu'.
  # Serve recuperare: 170 ordini erano scaduti e il gruppo in caduta cresce.
  # DUECENTO per giro. Il conto: 684 ordini validi sei ore vogliono 114
  # rinnovi all'ora, e con 80 per giro il blocco 5 e' tornato indietro da
  # solo (95% -> 91%, 223 in ritardo). Senza la pausa inutile un preventivo
  # costa 389 ms, quindi duecento sono circa 80 secondi: si puo'.
  .venv_bot2/bin/python agents/prepara_vendite.py 200 >> /tmp/laghetto.log 2>&1
  # Quante posizioni cadrebbero a ogni profondita' di dump e quante hanno
  # l'ordine FRESCO. Gira ogni giro, subito dopo le vendite: il numero deve
  # stare sullo schermo di Nicolo', non in una chat che si perde.
  battito "pronti al crollo"
  .venv_bot2/bin/python agents/pronti_al_crollo.py >> /tmp/laghetto.log 2>&1
  # LA TABELLA DEI BLOCCHI, calcolata dalle verifiche del C-check e non
  # stimata a occhio: cosi' un blocco che torna indietro si vede da solo.
  battito "tabella dei blocchi"
  # LA PROVA CHE ATTRAVERSA TUTTO (27 secondi, quindi non a ogni passata).
  # Prende l'ordine VERO piu' vicino a cadere, fa scendere il prezzo finche'
  # cade, e pretende che in cassa arrivino soldi. E' l'unica prova che
  # avrebbe visto il selettore sbagliato.
  if scaduto daCapoAFondo 180; then
    $PY agents/da_capo_a_fondo.py 2>&1 | tail -1
    segna daCapoAFondo
  fi

  # I PREMI VERI, riletti dal protocollo. Mancava proprio il passo che li
  # aggiorna: il file scadeva a 6 ore e tutti i gettoni ripiegavano sul
  # 4,50% di difetto, rendendo la soglia di resa troppo severa su USDe
  # (8,50%) e facendoci rifiutare rotte che guadagnavano.
  if scaduto premi 120; then
    $PY agents/premi.py 2>&1 | tail -2
    segna premi
  fi

  # IL TABELLONE: cosa e' successo nel mondo e chi ha preso i premi.
  # E' il blocco 6, e il suo mestiere e' insegnare agli altri cinque.
  battito "tabellone"
  ORE=6 .venv_bot2/bin/python agents/tabellone.py >> /tmp/laghetto.log 2>&1
  # LO STORICO DEI VINCITORI, ogni 24 giri (~3 ore): il vivo dice chi ha
  # vinto adesso, lo storico dice SE SONO SEMPRE GLI STESSI -- e quella e'
  # la domanda che decide la strategia. Con due campioni avevo concluso
  # "gente di passaggio"; con trenta giorni si prendono il 99,8% in 35.
  if scaduto storicoVincitori 180; then
    battito "storico dei vincitori"
    GIORNI=30 .venv_bot2/bin/python agents/storico_vincitori.py >> /tmp/laghetto.log 2>&1
    segna storicoVincitori
  fi
  # LO SPAZIO NEL BLOCCO, ogni 24 giri (~3 ore): chi costruisce i blocchi
  # dove avvengono le liquidazioni che valgono, e se gli consegniamo.
  if scaduto spazioNelBlocco 180; then
    battito "spazio nel blocco"
    .venv_bot2/bin/python agents/spazio_nel_blocco.py >> /tmp/laghetto.log 2>&1
    segna spazioNelBlocco
  fi
  # IL CONSULTO ESTERNO, due volte al giorno (due Astra + due Grok).
  # Il giro dura ~7 minuti, quindi 100 giri sono circa 12 ore: due volte al
  # giorno. La domanda la GENERA il sistema dallo stato del momento, non e'
  # scritta a mano -- altrimenti fra una settimana chiederei le cose di oggi.
  # L'agente ha il suo tetto di spesa dentro (massimo 2 consulti e $0,60 al
  # giorno, contati su file). Credito PREPAGATO: nessuna sorpresa.
  # Perche' vale: il 4/11 i cinque blocchi erano al 100% mentre perdevamo
  # $422.496 di premio, e il buco l'hanno trovato Nicolo' e i revisori --
  # non le 90 verifiche interne.
  if scaduto consulto 360; then
    battito "consulto esterno"
    .venv_bot2/bin/python agents/domanda_per_fuori.py >> /tmp/laghetto.log 2>&1
    .venv_bot2/bin/python agents/consulto_esterno.py /tmp/domanda_per_fuori.txt stato >> /tmp/laghetto.log 2>&1
    segna consulto
  fi
  .venv_bot2/bin/python agents/blocchi.py >> /tmp/laghetto.log 2>&1
  # RILEGGE le coppie delle piu' vicine alla caduta, ogni 8 giri (~1 ora).
  # Il costruttore della composizione non rilegge mai le vecchie, e il 4/11
  # una delle piu' vicine aveva cambiato garanzia senza che lo sapessimo.
  if scaduto composizione 60; then
    battito "rileggo le coppie"
    .venv_bot2/bin/python agents/composizione_riletta.py 25 >> /tmp/laghetto.log 2>&1
    segna composizione
  fi
  # SONDA FUORI DAL RECINTO, ogni 8 giri (~1 ora), sfasato rispetto alle
  # coppie per non caricare lo stesso giro. Nessun preventivo: sono letture
  # della catena, gratuite.
  if scaduto fuoriDalRecinto 60; then
    battito "sondo fuori dal recinto"
    .venv_bot2/bin/python agents/fuori_dal_recinto.py 40 >> /tmp/laghetto.log 2>&1
    segna fuoriDalRecinto
  fi
  # I TETTI MISURATI, ogni 16 giri (~2 ore). Trovare il tetto per
  # dimezzamenti col Quoter costa solo letture, ma sono molte: si fa con
  # calma e si taranno 25 coppie per volta, le piu' ricche prima.
  # Nascono il 4/11: i tetti scritti a mano invecchiano e non distinguono
  # wstETH->WETH (due milioni al 99,96%) da wstETH->cbBTC (cinquantamila).
  if scaduto tettiMisurati 120; then
    battito "taro i tetti"
    QUANTE=25 .venv_bot2/bin/python agents/tetti_misurati.py >> /tmp/laghetto.log 2>&1
    segna tettiMisurati
  fi
  # L'ESECUZIONE VERA su copia della catena, ogni ~50 giri (circa 6 ore).
  # Rara di proposito: chiede preventivi, e quella fonte e' gratuita.
  if scaduto provaInCatena 240; then
    battito "prova in catena"
    .venv_bot2/bin/python agents/prova_in_catena.py >> /tmp/laghetto.log 2>&1
    segna provaInCatena
  fi
  # IL C-CHECK, ogni quattro giri (fa chiamate in rete). Nato il 3/11: il
  # guasto piu' grave trovato finora -- 660 pacchetti spediti a salve per
  # una chiave cancellata -- aveva TUTTI gli altri indicatori verdi, e l'ho
  # visto solo perche' Nicolo' ha chiesto un controllo. Non deve dipendere
  # da una richiesta: ogni stadio della catena vuole la sua guardia.
  if scaduto ccheck 999999; then   # ora gira in agents/guardie.sh, ogni 15 minuti
    battito "c-check"
    .venv_bot2/bin/python agents/check_finale.py >> /tmp/laghetto.log 2>&1
    if grep -q "C-CHECK: .* [1-9][0-9]* da sistemare" /tmp/laghetto.log; then
      echo "$(date -u '+%F %T') !!! C-CHECK HA TROVATO QUALCOSA" >> /tmp/laghetto.log
    fi
    segna ccheck
  fi
  # LA POPOLAZIONE, ogni 20 minuti. RIACCESA il 5/11 dopo 15 ORE DI MORTE.
  #
  # Questo ramo era disattivato (999999) con la nota «ora gira in
  # guardie.sh». FALSO, e l'errore e' nel NOME: la chiave del timer si
  # chiamava "blocchi", guardie.sh esegue blocchi.py -- ma questo ramo non
  # esegue blocchi.py, esegue lista_corta.py. Ho spento il rinfresco della
  # popolazione credendo di spegnere un doppione.
  # COSTO MISURATO: la nona e la decima liquidazione (blocchi 26351313 e
  # 26351314) hanno colpito posizioni che NON ERANO NEL NOSTRO LIBRO -- ne'
  # fra gli ordini, ne' nella lista corta -- pur essendo a salute 1,0047 e
  # 1,0068, in piena fascia. Non ci e' sfuggita la campanella: ci e' sfuggito
  # che quelle posizioni esistessero.
  # LA REGOLA: la chiave di un timer porta il nome di CIO' CHE ESEGUE. Due
  # nomi diversi per la stessa cosa sono un guasto che aspetta.
  if scaduto listaCorta 20; then
    echo "$(date -u '+%F %T') rifaccio la lista corta" >> /tmp/laghetto.log
    battito "rifaccio la lista corta"
    .venv_bot2/bin/python agents/lista_corta.py >> /tmp/laghetto.log 2>&1
    segna listaCorta
  fi
  # ogni 4 giri, non 8: da quando la composizione usa getUserConfiguration
  # costa ~60 secondi per 250 posizioni invece di 10 minuti per 25, e il
  # laghetto cresce piu' in fretta di quanto lei componesse. Una posizione
  # non composta e' invisibile al pescatore: la composizione e' il collo
  # fra «trovata» e «sorvegliata».
  # LE COMPOSIZIONI, ogni 30 minuti. RIACCESE il 5/11 per lo stesso errore di
  # nome: chiave "tabellone", guardie.sh esegue tabellone.py, ma qui si
  # esegue composizione_posizioni.py. E una posizione non composta e'
  # INVISIBILE al pescatore -- e' il collo fra «trovata» e «sorvegliata»,
  # come dice il commento due righe sopra. Spenta anche questa in silenzio.
  if scaduto composizioni 30; then
    echo "$(date -u '+%F %T') ricalcolo le composizioni" >> /tmp/laghetto.log
    battito "compongo le posizioni"
    .venv_bot2/bin/python agents/composizione_posizioni.py >> /tmp/laghetto.log 2>&1
    # la metrica si rigenera dopo ogni ricomposizione: quando il laghetto
    # cresce, cresce anche la pagina. Nessun numero scritto a mano.
    battito "rifaccio la metrica"
    .venv_bot2/bin/python agents/metrica.py >> /tmp/laghetto.log 2>&1
    battito "chi pende in bolla"
    .venv_bot2/bin/python agents/prima_bolla.py >> /tmp/laghetto.log 2>&1
    .venv_bot2/bin/python agents/metrica_pagina.py >> /tmp/laghetto.log 2>&1
    segna composizioni
  fi
  battito "in pausa"
  sleep 420   # sette minuti fra un giro e l'altro: non si brucia la fonte
done
