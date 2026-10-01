# RECOVERY — whale-radar (29/09/2026, sera)

## Cosa stiamo facendo, in una frase
Cerchiamo se esiste un modo di guadagnare sui memecoin appena nati; oggi abbiamo scoperto che
per quindici ipotesi avevamo misurato tutto con lo strumento tarato male.

## La scoperta del giorno (la piu' importante da mesi)
Il «fondale» di −53% **non era il mercato: era il nostro ordine**. La simulazione vendeva $500
dentro sei ore, e cio' che non riusciva a vendere valeva zero: a quella taglia e in quel tempo
si piazzava solo il 58% della posizione.

Tolto l'artefatto, il mercato a +2h e' **un gioco equo**: chi compra a caso con una taglia da
cui si esce incassa circa zero prima dei costi, e perde l'1,8% di commissione.

## La classifica delle leve (misurata oggi, stessi pool, stesso metro)
| leva | valore |
|---|---|
| taglia della posizione ($2000 → $25) | 15–35 punti |
| finestra per uscire (6h → un mese) | 14–17 punti |
| momento d'ingresso (60° → 25° scambio) | 3–5 punti |
| **scelta di quale pool comprare** | **negativa: peggio del caso** |

Per settimane avevamo lavorato solo sull'ultima riga.

## Ipotesi chiuse oggi
- **H10** (pattern di H9 su finestra lunga): morta. Il modello addestrato sul PREZZO sceglieva
  i pool illiquidi — decimo migliore −69% contro fondale −27%.
- **H11** (stesso modello, ma addestrato sull'INCASSO): morta, ma **+52 punti** per una riga.
- **H13** (uscire sul crollo): morta, e fa DANNI. I crolli rientrano: lo stop e' una tassa.
  Conferma misurata dell'intuizione di Nicolo' di luglio.
- **H14** (prendere il guadagno a 2x): non promossa. +24 punti su robinhood, zero su base.
- **H15** (entrare prima): morta. Gobba al 25° scambio, mai sopra zero. E chi compra ai
  primissimi scambi guadagna MENO.

## Stato della macchina
- **Guasto risolto**: `segnali.jsonl` a 104,8 MB superava il limite GitHub e **impediva ogni
  spinta a chiunque** per tre ore. Compresso a 5,6 MB, 175.845 righe intatte.
- Due guardie nuove: `agents/file_troppo_grandi.py` (avvisa a 60 MB, blocca a 90) e il
  pubblicatore che scarta i file oltre soglia da qualunque pacco arrivino.
- Cinque corsie convertite da «spingo» a «consegno»: previsioni, scoperta, censimento, hook,
  coppie. **NON convertire vivo e storico** senza fusione: accumulano su file condivisi.
- `agents/fondi_consegna.py`: il pubblicatore fonde cio' che si accumula, sostituisce cio' che
  si ricalcola.
- Timeout insieme portato a 170 minuti: tre varianti erano state CANCELLATE a 60 minuti, in
  silenzio (una cancellazione non manda email e non conta come fallimento).

## Strumenti nuovi di oggi
- L'insieme accetta parametri: `ore_attesa`, `orizzonte_ore`, `entrata_scambio`, `suffisso`.
  Si lanciano varianti a mano senza toccare quella ufficiale.
- `_cammino`: il percorso del pool durante la tenuta, in dollari, per provare le regole d'uscita.
- Taglie misurate: $25, $50, $100, $500, $2000.
- `agents/chiavi_doppie.py`: rifiuta le chiavi doppie come fa GitHub (il mio controllo le
  perdonava e GitHub rifiutava il file intero).

## Prossimo passo previsto
Le tre leve strutturali valgono dieci volte la selezione. Cercare li', non nel «quale comprare».
Domanda aperta: esiste una combinazione taglia+finestra+momento che porti sopra lo zero su
TUTTE E DUE le chain? Oggi il meglio senza selezione e' −5,4% (robinhood) e −14,9% (base).

## Come riprendere
Nuova chat: «leggi RECOVERY_whale-radar.md dal repo nicolostancato-web/whale-radar».
Documenti chiave di oggi: VERDETTO_TAGLIA.md, VERDETTO_TAGLIA_LIMITE.md, CORREZIONE_FONDALE.md,
VERDETTO_H15_COMPLETO.md, VERDETTO_H13_H14.md, VERDETTO_H10_H11.md.
