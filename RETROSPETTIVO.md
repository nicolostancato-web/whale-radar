# 🔬 ESPERIMENTO RETROSPETTIVO — l'attenzione su X anticipa il prezzo?

*16 settembre 2026 · primo campione · nessun trading, nessun capitale*

## Il disegno, in tre righe

Si sceglie un **giorno passato**. Si chiede a Grok, **con la vista tappata a quel giorno**
(`from_date`/`to_date` su X), quali memecoin mostravano segnali precoci di attenzione. Poi si
guarda cosa e' successo **davvero** nelle ore successive, sui prezzi reali.

Chiedere del presente costringe ad aspettare giorni per sapere se la risposta era buona. Chiedere
del passato rende la verifica immediata: il ciclo impara-correggi passa da giorni a minuti.

## Il risultato, su 27 token nominati

| misura | valore |
|---|---|
| verificabili | **19 su 27** (70%) |
| picco mediano | **1,19** (+19%) |
| «partiti» (picco ≥ 1,5x) | **5 su 19** (26%) |
| **chiusi sopra il prezzo d'ingresso** | **2 su 19** (11%) |
| **chiusura mediana** | **0.570** |
| chiusura media | 0.531 |

**Il token mediano tocca +19% e chiude a −43%.** Con la stessa firma su diciannove casi.

### I casi piu' estremi

| token | giorno | chain | verdetto | picco | chiusura |
|---|---|---|---|---|---|
| $BLFT | 2026-09-02 | solana | PARTITO | 7.275 | 0.708 |
| $SHRIMP | 2026-09-04 | solana | PARTITO | 2.589 | 0.802 |
| $STK | 2026-09-10 | robinhood | PARTITO | 2.528 | 0.357 |
| $COPYCAT | 2026-09-09 | solana | PARTITO E CROLLATO | 1.712 | 0.133 |
| $GTA | 2026-09-09 | robinhood | PARTITO | 1.548 | 1.107 |
| $SLINK | 2026-09-04 | solana | non partito | 1.391 | 0.137 |
| $TESTICLE | 2026-09-10 | solana | non partito | 1.249 | 0.004 |
| $POOH | 2026-09-04 | solana | non partito | 1.24 | 0.3 |

## Cosa dice, e cosa NON dice

**Dice** che l'attenzione social selezionata cosi' trova cose che *si muovono* — un quarto supera
il +50% — ma che **tenerle non funziona**: i picchi evaporano entro 24 ore. Se un vantaggio esiste,
sta nell'**uscita**, non nell'ingresso.

**Non dice** che esiste un edge. Diciannove casi non sono una statistica, e su questo progetto
abbiamo gia' imparato cosa costa entusiasmarsi su campioni piccoli.

**E' un risultato sul MERCATO, non sul prompt.** Il prompt e' migliorato davvero durante la notte
(v2: zero risposte usabili; alla fine sette su dieci). Proprio per questo il risultato e' credibile:
non stiamo guardando il fallimento dello strumento.

## Come il prompt si e' affinato da solo

| versione | esito |
|---|---|
| v0 — JSON a otto campi | **zero token**: Grok si blocca |
| v1 — una riga per token | 7 token con chain e contratti |
| v2 — forense, tutte le prove insieme | **«nessun candidato»**: scarta token che HA VISTO |
| v3 — prove parziali ammesse, dichiarando cosa manca | primo successo |
| v5+ — con fase di scoperta esplicita | 2 su 2, poi 6 e 7 token al giorno |

Il ciclo: Grok risponde → un **metro automatico** scritto prima decide se e' usabile → ChatGPT legge
le risposte vere col punteggio gia' fatto e riscrive → si ricomincia. ChatGPT capisce **perche'**,
non decide **se**: senza un metro direbbe qualcosa di plausibile su qualunque risposta.

## I due errori che sono costati di piu'

**`to_date` e' ESCLUSIVO.** Con `from_date = to_date = giorno` chiedevo un intervallo **vuoto**:
dieci chiamate buttate, e per dieci volte ho letto «nessun candidato» dando la colpa al prompt.

**Il mio metro cercava la parola «zero» ignorando le maiuscole.** Una risposta buona che dicesse
«zero red flags» sarebbe stata marcata come rifiuto: il ciclo si sarebbe **addestrato sul rumore
del proprio giudice**, riscrivendo il prompt per un problema inesistente.

## Costo

**$1,61 in totale**, dentro il tetto di €2 fissato dal fondatore. Il verificatore usa solo fonti
gratuite.

## Il limite che resta

**8 token su 27 non sono verificabili** (30%): pool che non esistevano ancora, o senza candele.
Non e' un dettaglio — e finche' resta cosi', un terzo di quello che Grok dice non lo sappiamo
giudicare.
