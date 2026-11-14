# RECOVERY — liquidazioni Aave ("prima bolla")
aggiornato 2026-10-31 20:30 UTC

## Cosa stiamo facendo (1 frase)
Macchina armata che liquida posizioni Aave v3 in perdita, incassa il premio del
7,00% con un prestito lampo, e manda un'email a Nicolo' SOLO dopo aver
verificato che i soldi sono arrivati nella cassa.

## Stato: ARMATO su 302 posizioni, 0 prese, 24 centesimi spesi
## COPERTURA DEL PREMIO REALE: 98,7% (stamattina era 10%)
- contratto `Liquidatore` live: `0xE30b58692FB7a1a417d3e0F1F5585a8Bc4D51212`
- cassa (riceve il profitto, chiave MAI da me): tiene il test da 0,00009 ETH
- wallet operativo: ~0,016 ETH
- `in_acqua.py` armato, sorveglia 18 posizioni, rilegge la lista ogni 150 giri

## Il mercato, MISURATO il 31/10 su 9 giorni veri (93 liquidazioni)
- 10,3 liquidazioni/giorno, 7,4/giorno sopra EUR 50
- premio MEDIANO per liquidazione: **EUR 134** (non 100.000)
- premio lordo del mercato: EUR 13.568/giorno
- ...ma solo il **10%** e' su garanzie che sappiamo vendere
- le 3 piu' grosse (39.862/17.122/12.319) erano TUTTE invendibili
- vediamo il 31% dei caduti -> il laghetto e' la leva sulla COPERTURA
- la gara (6,47s di finestra MEV-Share vs 1,1s nostri) e' la leva sulla
  CONVERSIONE, e resta IGNOTA finche' non arriva la prima presa

## Asset PROVATI su posizione vera (ProvaVera.t.sol, blocco attuale)
GARANZIA: WETH $25.578 | USDT $5.130 | USDC $288 | weETH (OggiVera) $881
DEBITO (prestito lampo): WETH, USDT, USDC, GHO (1.077 GHO in cassa)
RAMO STESSO-GETTONE: PROVATO e ARMATO l'1/11. 0x18a95d14 (WETH/WETH),
  0,0912 WETH in cassa. Provato facendo passare 630 giorni di interessi sulla
  copia locale -- e' il meccanismo vero con cui cadono queste coppie, non un
  prezzo falsificato. La prova dimostra il MECCANISMO, non la taglia (il warp
  distorce gli importi). Ultimo buco noto chiuso.
APERTO: il contratto non ha uno spazzino per la polvere di garanzia che resta
  quando la sovrascrittura dell'importo non si propaga (0,5%). Serve un nuovo
  deploy; non urgente, non perde soldi, li lascia fermi.

## Serata del 31/10 — le tre cose grosse
1. WETH ARMATO: il 60% delle liquidazioni vere (53 su 93) e' su garanzia WETH e
   non era ammessa. Tetto misurato $2M, prova WethVera.t.sol PASSA con $25.225
   in cassa su posizione vera al blocco attuale. USDT/USDC hanno il tetto ma
   NON la prova: non armati.
2. DIFETTO sul sistema armato: POSIZIONE_IMPORTO=132 era misurata su una rotta
   sola; su 0x46c67b6d l'importo sta a 68 e il 132 cadeva sull'importo atteso
   in uscita -> si annullava invece di incassare, in silenzio. Ora si CERCA e
   si rifiuta di tirare se non appare esattamente una volta.
3. PROBABILITA' MISURATA al posto del modello: il modello dava EUR 311.878 di
   atteso contro un mercato vendibile intero di EUR 41.000/mese -> impossibile.
   Causa: i debitori DIFENDONO. Misurato prima/dopo su 300 posizioni fra il
   blocco di 9 giorni fa e oggi (agents/difendono.py):
     coppia uguale  0,7% [0,1-3,7] di caduta in 9 giorni (n=148)
     coppia diversa 11,2% [7,1-17,2] di caduta in 9 giorni (n=152)
   Gli intervalli non si sovrappongono: la distinzione e' vera, 16x.

## Ultimi 5 step fatti
1. metrica pubblicata (artifact 537f7951-fdc6-4998-9582-2970425820f1), si
   rigenera da sola a ogni giro del laghetto
2. misurato il mercato vero: `chi_e_caduto.py` + `quanto_avrebbe_pagato.py`
3. DIFETTO corretto: `composizione_posizioni.py` prendeva i primi 25 e
   SOVRASCRIVEVA -> ora accumula e ruota sulle non-composte
4. DIFETTO corretto: `in_acqua.py` leggeva la lista una volta sola all'avvio
   -> ora ricarica ogni 150 giri. 11 -> 18 sorvegliate
5. composte 45 su 277 candidati con debito vero

## Prossimo step
1. FATTO: USDT e USDC provate e armate. Copertura 98,7%.
   FATTO anche il ramo stesso-gettone. TUTTI i percorsi noti sono provati
   su posizione vera. Da qui e' ATTESA: non c'e' altro da costruire prima
   della prima presa, solo da sorvegliare che i processi restino vivi.
2. Aspettare la PRIMA USCITA MERCI. Parole di Nicolo' (31/10): la presa da
   EUR 500 conta PIU' delle bombe da 100.000, perche' e' la conferma che il
   flusso intero funziona in produzione. Il documento, non l'importo.
3. Composizione: ora fa 150 per giro in ~60 secondi (era 25 in 10 minuti):
   getUserConfiguration dice in 1 chiamata quali asset usa un utente, invece
   di interrogarne 67. Verificato 4/4 contro il metodo lento prima di usarlo.

## Processi che devono essere vivi
    agents/in_acqua.py            pescatore armato
    agents/guardia.sh in_acqua    guardia PROVATA (rialza in 45s)
    agents/guardia.sh quaderno    guardia del registro
    agents/allarga_laghetto.sh    raccolta + lista corta + composizione + metrica
    agents/quaderno.py            registro posizioni

## COME SI CONTROLLA CHE SIA DAVVERO VIVO (non basta contare i processi)
    data/liquidazioni/guardia_in_acqua.json  <- battito, si aggiorna ogni 45s
       se "quando" e' vecchio -> la GUARDIA e' il problema
    data/liquidazioni/pescatore_vivo.json    <- cosa VEDE il pescatore
       "viste"/"mute" e "piu_malata": se mute sale o piu_malata e' immobile,
       il pescatore e' cieco. L'1/11 e' stato giu' mezz'ora sembrando sano
       perche' pgrep trovava il suo ZOMBIE. Vedi feedback_guardia_mai_provata.

## Fonti RPC che reggono eth_getLogs su 4.000 blocchi con archivio
    https://gateway.tenderly.co/public/mainnet
    https://rpc.mevblocker.io
  (drpc da 400, publicnode 403 dopo 2 giri, 1rpc max 50 blocchi)

## Come riprendere
Nuova chat: "leggi RECOVERY_liquidazioni.md". Credenziali in
~/Documents/b2b-finder-credentials.txt e CLAUDE.md. Repo: nicolostancato-web/whale-radar.
