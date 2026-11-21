# Prima la prova, poi il numero — 7 ottobre 2026

## Cosa mi ha detto Nicolò

> «non puoi sempre sbagliare e darmi dei risultati sbagliati»
> «è da 3 giorni che tipo ti inventi le cose»
> «mi dai dei wallet che non fanno soldi. come fai a sbagliare??»

Ha ragione, e la risposta non è una scusa: è **l'ordine delle operazioni**.

Producevo un numero → glielo comunicavo → lo verificavo **dopo**, quando lo contestava lui.
Il 7/10 ha aperto un portafoglio su un sito: dentro c'erano **11 euro**, dove io avevo detto
**7.740 dollari**. La chain dice che quella vendita ha incassato **3,36 dollari**: aveva chiuso in
pari. Sbagliato di **2.300 volte**, e il controllo che lo smentiva costava due minuti.

Tre giorni di numeri usciti senza prova, perché la prova era una mia abitudine invece di un
meccanismo. Le abitudini saltano quando c'è fretta.

## Le tre cause, tutte chiuse con una misura

| causa | cosa faceva | come è chiusa | provato |
|---|---|---|---|
| **righe di due generazioni** mescolate nello stesso file | il 27,4% erano in formato vecchio e i miei conti le sommavano alle nuove | ogni riga porta `"v"`; chi legge **rifiuta** l'insieme misto invece di scegliere | file finto con 300 nuove + 100 vecchie → `RIFIUTO`, nessun numero prodotto |
| **fette per posizione** | l'elenco delle monete cresce ogni giro, le posizioni slittano, la stessa moneta cambia fetta e viene scritta due volte (30.016 duplicati misurati) | la fetta si assegna per **identità** della moneta (hash dell'indirizzo), mai per posizione | con +1, +3, +7, +301 monete: per posizione **il 100%** cambia fetta, per identità **0%** |
| **nessuna prova dentro la riga** | per controllare un numero dovevo rifare il lavoro a mano, quindi il controllo arrivava dopo | ogni riga porta **hash e importo** dei propri scambi; chi misura pesca un campione e lo chiede alla chain **prima** di scrivere | file finto con importi gonfiati: l'agente ha calcolato `1,6662x` e **si è rifiutato di scriverlo** |

### Nota su un errore dentro la verifica stessa

Il primo test della fetta diceva «0% cambia fetta» — cioè **mi smentiva**. Avevo aggiunto 300
monete, e 300 è multiplo di 4: le posizioni restavano le stesse per caso. Rifatto con +1, +3,
+7, +301: il difetto c'era, ed era al 100%.
**Un test che passa per caso è peggio di un test che manca**, perché chiude l'indagine.

## Cosa cambia da ora

L'agente che misura il mercato pubblico ha tre cancelli in fila, e ognuno **non scrive niente**
se non è soddisfatto: versioni mescolate → rifiuto; duplicati → scartati e dichiarati; campione
non verificato sulla chain → verdetto bloccato e si scrive il referto del fallimento, perché un
fallimento che non lascia traccia si ripete.

**Conseguenza pratica: non porto più nessun numero sul mercato pubblico** finché un campione
pescato a caso non combacia con la chain. Il `1,0622x`, le fasce `22-25x` e il copiatore `9,275x`
sono **ritirati**: venivano da file contaminati.

## Il prezzo

I dati si rifanno da zero (versione 8 butta da sé contatore e righe). Perdo la copertura
accumulata — 235 monete su 5.268 — e riparto. È il prezzo giusto: un file che sembra pieno ed è
misto è peggio di un file vuoto.
