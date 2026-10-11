# 🚨 IL REPERTO CENTRALE: l'entrata avviene prima che i dati esistano

*14/09/2026 · audit del database · misurato, non ipotizzato*

## Il fatto

| | valore |
|---|---|
| momento d'entrata (`ENTRY_H`) | **+3 ore** dalla nascita del token |
| ritardo con cui i dati arrivano DA NOI (`RITARDO_OSS`) | **35,4 ore** |
| finestra utile per le feature sugli scambi | **−32,4 ore** |

Una finestra **negativa**. Il codice seleziona gli scambi con
`t <= entrata − 127.586 secondi`, cioè scambi avvenuti **32 ore prima che il token esistesse**.

## La conseguenza, verificata sulle righe vere

Su **1.710** token di Base, **1.577 (92,2%)** hanno le quattro feature sugli scambi bloccate sul
valore neutro di ripiego `[0.5, 0.0, 0.0, 1.0]` — cioè **nessuno scambio è stato usato**.

> **Il modello che credevamo avesse dieci variabili ne ha avute sei per tutta la sua vita.**
> Le quattro sugli scambi — rapporto vendite/acquisti, quanto comprato, quanti compratori,
> accelerazione — erano costanti su 9 righe su 10.

Ogni esperimento che dipendeva dal flusso degli scambi misurava una costante.

## Da dove vengono le 35,4 ore

`_ritardo()` prende il **massimo fra le chain**:

| chain | ritardo misurato | campione |
|---|---|---|
| robinhood | **3,8 h** | 400 |
| solana | 10,6 h | 400 |
| base | 10,7 h | 400 |
| **bsc** | **35,4 h** | 342 |

Il massimo è **BSC — la chain che abbiamo abbandonato il 9 settembre**. Il suo ritardo continua a
paralizzare le tre chain attive. La scelta «nel dubbio il peggiore» era prudente quando le chain
erano quattro e tutte vive; oggi fa decidere una chain morta per tutte le altre.

## Ma togliere BSC non basta

Anche con il ritardo della sola chain: **base 10,7h, solana 10,6h**, contro un'entrata a **+3h**.
La finestra resta negativa (−7,7h). Solo Robinhood (3,8h) ci va vicino, e comunque non ci arriva.

> **Non è un parametro da ritoccare: è una contraddizione di progetto.** Diciamo di comprare tre ore
> dopo la nascita, ma i dati per decidere ci arrivano dieci ore dopo. Quell'entrata non esiste.

## E c'è un'asimmetria che rende il quadro peggiore

Le feature dalle **candele** usano tutto fino all'entrata, **senza sottrarre il ritardo**. Le feature
dagli **scambi** sottraggono 35,4 ore. Stessa decisione, stesso istante, due trattamenti opposti:

- le candele fanno finta che i dati arrivino istantaneamente → **ottimismo**
- gli scambi fanno finta che arrivino con 35 ore → **paralisi**

Nessuno dei due è il mondo vero. E la parte penalizzata è **proprio quella dove l'audit di stanotte
dice che potrebbe vivere il segnale**.

## Cosa NON dico

Non dico che riparando questo comparirà un edge. Dico che **finora non è stato possibile cercarlo**
nella metà del database che riguarda chi compra, in che ordine e con che tempi — e che i test fatti
su quella metà non misuravano ciò che credevamo.

## Stato delle affermazioni

| affermazione | tipo |
|---|---|
| RITARDO_OSS = 35,4h e ENTRY_H = 3h | **MISURATO** (letto dal codice e dal file) |
| il 92,2% delle righe Base ha le feature-scambi neutre | **MISURATO** |
| le 35,4h vengono da BSC, chain abbandonata | **MISURATO** |
| le candele non sottraggono il ritardo | **MISURATO** (lettura di `load_rows`) |
| gli scambi nelle prime 3h esistono per il 79-84% dei token | **MISURATO** su 210-222 campioni |
| riparando comparirà un vantaggio | **NON GIUDICABILE** |
