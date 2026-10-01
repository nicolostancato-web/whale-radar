# H6 e H6b — morte in quattro ore, e la ragione vale più delle due ipotesi

*Notte del 26 settembre. Nessun euro rischiato. Verso dei prezzi corretto poche ore prima.*

## H6b muore per la taglia, non per il prezzo

H6b comprava col filtro di H6 e vendeva a un bersaglio alto. Fuori campione dava media **+11,05%**,
positiva anche togliendo l'1% più alto (+2,02%), con intervallo tutto sopra zero. Era il primo
numero del genere da agosto.

Avevo scritto, prima di guardare: *«un prezzo alto non è una quantità»*. Ho misurato la quantità.
**Sopra il 10x, nei quindici pool che lo toccano, la valuta passata è in mediana 32 dollari.**

| | valuta passata sopra 10x |
|---|---|
| mediana | **32 $** |
| pool sotto 100 $ | **12 su 15** |
| massimo | 5.754 $ |

Quel +11% si incassa vendendo dentro trentadue dollari di domanda. Con una posizione da cento euro
sei tu il mercato; con una vera non esiste. **È la stessa illusione di agosto** — il paper da
323 mila euro fatto di prezzi non incassabili — riconosciuta stavolta in quaranta minuti invece che
in tre settimane, e *prima* di costruirci sopra.

## H6 muore per la coda

Il filtro fa una cosa vera: porta i pool da cui non si esce dal 20% al **7,2%**, e questo resta in
piedi anche tolta la coda. Ma la media positiva (+4,3%) dipende da una decina di token su 987:
tolto l'1% più alto è **−3,7%**, e l'intervallo attraversa lo zero. Non è un vantaggio.

## La ragione che vale più delle due ipotesi

Ho misurato dove stanno i soldi e dove stanno i multipli. La risposta, sui pool giudicabili di
robinhood, **condizionando su un volume misurato dopo l'entrata** (quindi NON una strategia — è
guardare il futuro, e lo dichiaro perché stavo per citarlo come se lo fosse):

| venduto in 24h | pool | tocca 2x | tocca 10x | senza uscita | valore atteso |
|---|---|---|---|---|---|
| 0–100 $ | 2.808 | 3,8% | 0,8% | **38,2%** | −28,9% |
| 100–1.000 $ | 1.577 | 4,5% | 0,3% | 0,0% | +3,7% |
| 1.000–10.000 $ | 1.669 | 7,5% | 0,5% | 0,0% | +5,7% |
| oltre 10.000 $ | 519 | 14,5% | 1,3% | 0,0% | **+24,9%** |

Sembra una miniera. **Non lo è**: quel volume si conosce solo dopo. Rifatta con ciò che si sa al
momento di comprare — numero di compratori nelle prime due ore, fuori campione:

| compratori prima | pool | senza uscita | media | senza l'1% alto |
|---|---|---|---|---|
| 0–4 | 591 | 29,9% | −18,1% | −24,9% |
| 6–10 | 1.071 | 18,1% | −7,7% | −14,1% |
| oltre 15 | 422 | **10,4%** | **−2,9%** | −9,4% |

**Monotono, pulito, e negativo in ogni fascia.** Tutto il +24,9% era sopravvivenza travestita da
previsione.

## Cosa resta scritto

1. **Un prezzo non è un'uscita finché non gli metti accanto una taglia.** Implementato:
   `_valuta_sopra_2x/5x/10x` in `agents/insieme.py`.
2. **Le unità grezze non si confrontano fra pool con valute diverse.** Su robinhood USDG ha 6
   decimali e WETH 18: la prima versione del campo mescolava numeri che differivano di mille
   miliardi di volte. Verificato sulla catena, non assunto.
3. **Se una fascia che rende bene è definita da qualcosa misurato dopo l'entrata, non è una
   strategia.** La forma dell'errore: *«i sopravvissuti sopravvivono»*.
4. **La capienza va misurata prima.** Avevamo trentatré caratteristiche e nessuna diceva quanti
   soldi fossero passati. Aggiunto `_valuta_prima`: è la prima domanda del prossimo giro.
