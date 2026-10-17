# Dentro il recinto liquido non c'e' niente, e il +15% era il futuro

*5 ottobre 2026 · chiusura dei due filoni della notte*

## La domanda di stanotte

Se il vantaggio dei bravi vive dove la liquidita' non ci sta (`IL_LORO_VANTAGGIO_E_LA_SOTTIGLIEZZA.md`),
allora: **esiste qualcuno che e' bravo dove ci stiamo anche noi?**

## Risposta: no. A parita' di liquidita' i bravi fanno PEGGIO del mercato

Recinto: solo pool dove il nostro ordine d'uscita da 500$ si riempie almeno al 90%.

| | mercato (medio / mediana) | pool dei bravi (medio / mediana) |
|---|---|---|
| base, 12.734 pool | +27,6% / **+15,2%** | +5,8% / **−1,8%** |
| robinhood, 34.862 pool | +41,8% / **+11,6%** | +2,0% / **−1,9%** |

**Due chain su due.** Il vantaggio dei bravi era la sottigliezza: dentro il recinto liquido non
ne resta nulla. **Il filone «seguire i vincenti» si chiude qui.**

## E il +15,2% del mercato non e' una strategia: e' informazione dal futuro

Sembrava enorme — una MEDIANA positiva del 15% a cinquecento dollari di taglia. Ma il recinto
e' costruito su `_riempito_500`, cioe' **se il nostro ordine d'uscita si riempie** — e questo
dipende dalla liquidita' **dopo** il nostro acquisto. Una pool che resta liquida e' una pool che
non e' morta.

E' la stessa famiglia del +16% svanito a zero il 1/10 (scegliere i pool che avevano uno scambio
successivo archiviato). Quella volta ci ho messo un giorno; stavolta l'ho fermato **prima di
riportarlo**.

## La versione onesta: liquidita' nota PRIMA di comprare. Non c'e' niente.

| quinto di liquidita' pre-acquisto | base: nostro esito mediano | robinhood |
|---|---|---|
| 1o (meno liquide) | −98,0% | −15,8% |
| 3o | −93,9% | −9,7% |
| 5o (piu' liquide) | −93,7% | −8,1% |

Tutti i quinti profondamente negativi, **nessun gradiente utile**. Il vantaggio era interamente
nel futuro.

## E un difetto nei dati, annotato dove nasce

`_liq_prima` e' in **unita' grezze del gettone**, non in dollari e non diviso per i decimali: i
quinti risultano «da 40.212.582.413.327.208$», che non e' una cifra. Mescolando gettoni con
decimali diversi, anche l'**ordinamento** fra pool e' senza senso — quindi la tabella qui sopra
e' valida solo come «nessun segnale», non come misura della liquidita'.

E' la famiglia dei sedici milioni di dollari del 2/10: un'unita' mai convertita che viaggia
dentro un campo dal nome innocente. Annotato in `agents/insieme.py` nel punto che lo produce,
con la riparazione da fare e il divieto di filtrare su quel campo finche' non e' fatta.
Copertura comunque bassa: noto per il 4-5% delle pool.

## Dove resta il lavoro

Due filoni chiusi stanotte, e nessuno dei due per stanchezza: entrambi con una misura su due
chain. Resta in piedi una cosa sola, e con numeri piccoli: **il passato di chi lancia la
moneta** raddoppia il tasso di morte (19,2% contro 38,9%, 375 pool). Quello e' noto prima di
comprare, non dipende dalla taglia, e la corsia accumula da sola.
