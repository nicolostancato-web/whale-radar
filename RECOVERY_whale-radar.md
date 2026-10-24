# RECOVERY — whale-radar / crypto

Aggiornato: 24 ottobre 2026, pomeriggio.

## Cosa stiamo facendo, in una frase

Cerchiamo un modo misurabile di guadagnare in crypto partendo da **€52**; la
fase di misura è **chiusa** e resta una decisione da prendere.

## Lo stato, in tre righe

1. **Sedici strade chiuse** sul lato di chi paga il pedaggio. Due sole cause
   ripetute: il lordo non copre il pedaggio, oppure la torta intera vale €40-94
   al giorno.
2. **Verdetto di due revisori indipendenti (Astra e Grok, stesso dossier,
   separatamente):** €500/giorno su €52 sono il **962% al giorno**, cioè 15.000
   volte il miglior rendimento misurato. Cercare ancora nel trading pubblico è
   l'errore.
3. **Una porta aperta e verificata sulla chain:** il 47% delle transazioni dal
   router di Uniswap su Base porta già una commissione d'app, mediana 0,206%.
   **€500/giorno = €243.000 di volume al giorno** attraverso qualcosa di
   proprio. Le sei app che lo fanno oggi prendono €20-200 al giorno.

## Gli ultimi passi fatti

- chiusa la strada del mercante (liquidità concentrata: −2,9% ± 0,4)
- chiuse le liquidazioni Morpho su due chain (€1/giorno alla nostra taglia)
- ritirato il +18,9% e poi il +1,5%: entrambi erano errori nostri
- misurate le tariffe vere che un'app può applicare, e verificate sulla chain
- chiuse le azioni tokenizzate: 1 scambio ogni mezz'ora a New York aperta

## Il prossimo passo

**Non è una misura.** È la decisione di Nicolò fra tre opzioni, tutte con i
numeri accanto: continuare a scavare (due revisori lo chiamano errore),
accumulare capitale (€15.700 per €10/giorno), oppure costruire qualcosa che
incassa il pedaggio (€243.000 di volume al giorno per €500).

## Strumenti costruiti, che restano

- `agents/keccak.py` — firme degli eventi **calcolate**, non ricordate
- `agents/dato_obbligatorio.py` — un dato mancante **alza eccezione**, mai un
  ripiego (nato dal falso 0,30% che resse quattro misure)
- i contatori di fallimento nelle query: un rifiuto dell'RPC non è più uno zero

## Come riprendere

Leggere, nel repo pubblico `nicolostancato-web/whale-radar`:
`STATO_FINALE_MISURE_24OTT.md`, `IL_VERDETTO_24OTT.md`,
`LA_TARIFFA_VERA_24OTT.md`, `QUANTO_FA_UNAPP_24OTT.md`.

Cassa: **€52,16**, invariata. Nessun euro speso, nessun capitale esposto.
