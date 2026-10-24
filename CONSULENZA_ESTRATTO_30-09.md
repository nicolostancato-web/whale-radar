# Cosa prendo dalla consulenza di Astra del 30/09

**Costo reale: $0,09.** Il fascicolo era costruito su documenti vecchi (alcuni del 17-21/09),
quindi parte dei rilievi riguarda uno stato gia' superato. Questi tre no: colpiscono il lavoro
di oggi in pieno.

## 1. La correttezza degli SCAMBI non e' mai stata misurata (rilievo n. 7)

> «La correttezza dei timestamp sta occupando il posto della correttezza degli scambi. Non c'e'
> una misura di concordanza per quantita', decimali, direzione dello scambio, identita' dei
> token, prezzo o duplicati. Potreste arrivare al 100% dei timestamp richiesti alla catena e
> avere ancora un database inutilizzabile per cercare un vantaggio.»

**Perche' brucia:** il +17,6% dipende interamente da importi e direzione. Abbiamo verificato
i **decimali** sulla catena (USDG=6, WETH=18) e il **verso** (`agents/verso.py`, provato dal
banco degli incidenti). Non abbiamo mai confrontato evento per evento **quantita' e prezzo**
con il registro della catena.

**Azione:** un controllo che prenda un campione casuale di scambi, li rilegga dal nodo e
confronti quantita', direzione, token e prezzo derivato. Da fare PRIMA del 10 ottobre: se il
dato e' storto, il verdetto misura un'illusione.

## 2. La dichiarazione di aver corretto non e' la correzione (rilievo n. 5)

> «Tre riparazioni perse integralmente con log "success". Ne' il marchio ne' il log sono prove
> attendibili di avvenuta riparazione. E 0,0% arrotondato non equivale a zero record.»

E' la stessa famiglia che ho inseguito tutto il giorno — il silenzio scambiato per salute —
vista da fuori e detta meglio. **«Provare l'interruzione forzata: il lavoro deve risultare o
conservato e verificabile, o esplicitamente incompleto, mai falsamente riuscito.»**

## 3. Un documento vecchio che da' ordini (rilievo n. 9)

> «Al 30/09 20:29, `STAFFETTA.md` e' calcolato al 17/09 19:10: tredici giorni prima. Dice che
> non vale se vecchio di piu' di pochi minuti. Eppure prescrive «Riaccendere» il motore.»

Coerente con quello che ho trovato oggi da solo: trentatre corsie ferme dal 27 agosto. Ma qui
il rischio e' peggiore: **un documento obsoleto che impartisce istruzioni operative.**

**Azione:** la staffetta o si rigenera, o dichiara in testa che e' scaduta e non vale.

## Cosa NON prendo, e perche'

I rilievi 1, 2, 4, 6 riguardano il congelamento della popolazione e le percentuali di copertura
di un lavoro di settembre che oggi non e' piu' il perno: la scoperta di oggi ha spostato la
domanda da «quali pool includere» a «con quanti soldi e quanto tempo per uscire».

**Ma il rilievo 3 resta vivo e va guardato ogni volta:** «dichiarare una soglia prima
dell'analisi non la rende osservabile al momento della decisione». Per la nostra regola —
comprare al 5° scambio — l'ho verificata: chi non arriva al 6° scambio non viene comprato, non
e' una perdita nascosta. Ma e' il controllo da rifare a ogni regola nuova.
