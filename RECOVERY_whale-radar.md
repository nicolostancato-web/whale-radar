# RECOVERY — whale-radar (13-14 ottobre 2026, notte)

## Cosa stiamo facendo (una frase)
Siamo LIVE con capitale ristretto: un bot compra e vende dentro la curva Pons su Robinhood
Chain seguendo la regola 50-5, 2 euro a posizione, tetto cumulato 40 euro.

## Dove siamo
- **Strategia**: entra quando la riserva netta supera 1,5 nativi, vende a +50%, taglia a -5%.
  Resa misurata: **+9,8% per operazione** su 232 chiusure della prova, costo vero 5,91% incluso.
  Fuori campione: +8,7%. Sopravvissuta a 7 attacchi.
- **Fattibilita'**: 7 attacchi al tool, 6 falliti. Niente ostacoli strutturali (velocita', gas,
  priorita', rifiuti, limiti del nodo, blocchi del contratto, impatto). Unico requisito emerso:
  un portafoglio per posizione (ce ne sono 6, ~10$ l'uno).
- **Live**: acceso il 13/10 sera. Alle 00:45 del 14/10: processo vivo, **0 euro spesi**,
  1 sola occasione vista e **rifiutata correttamente** (prezzo gia' a +29% dall'entrata).

## Il limite vero scoperto stanotte
Il bot vede una posizione solo dopo che il cervello ha finito di elaborare la sua finestra:
a quel punto il prezzo e' gia' mosso. Mediana **+3,5%**, il 25% sopra +6,3%, il 10% oltre 2,8x.
Dentro la finestra d'acquisto 0,97-1,05 resta il **51%** delle occasioni.
Allargare la finestra NON si fa: entrare piu' in alto perde (dimostrato sulle entrate a 3,6).
**Prossimo passo proposto**: fondere cervello e mani in un processo solo, che agisce
nell'istante del rilevamento invece di passare da un file.

## Ultimi 5 passi fatti
1. Recuperate 36 ore perse: campione da 60 a 700+ operazioni, la candidata diventa leggibile
2. Attaccata 7 volte la percentuale: regge (39 regole su 49 positive -> il vantaggio e' nell'entrata)
3. Cambiato bersaglio: attaccata la fattibilita' del bot invece della percentuale
4. Costruito il bot, checklist di 19 voci tutte verdi, acceso il live
5. Corretti: costo contato due volte, scritture non atomiche, orologio sostituito dal prezzo

## File importanti
- `agents/prova_nella_curva.py` — il cervello (decide)
- `agents/bot_curva.py` — le mani (eseguono)
- `agents/live_curva.py` — il processo continuo
- `agents/controllo_pre_live.py` — la checklist, 19 voci
- `.github/workflows/prova_curva.yml` — la corsia che accumula lo storico
- `SI_PUO_FARE_IL_BOT_13OTT.md`, `LA_FAMIGLIA_E_POSITIVA_13OTT.md`, `IL_RITARDO_UCCIDE_13OTT.md`

## Risorse
- Chain: `https://rpc.mainnet.chain.robinhood.com` (pubblico, gratis)
- Chiavi: `~/Documents/b2b-finder-credentials.txt`, sezione `=== WHALE RADAR BOT ===` (6 chiavi)
- Repo: `nicolostancato-web/whale-radar` (pubblico, 7 GB su 10)

## Come riprendere
Leggere questo file, poi `agents/controllo_pre_live.py` per verificare che tutto sia a posto,
poi `.venv_bot/bin/python agents/live_curva.py --vero` per riaccendere il live.
Per fermarlo: `rm /tmp/live_curva.marcia`.
