# H8 — previsione sbagliata, meccanismo trovato, e il fondale non lo conosciamo

*28 settembre 2026, sera. Ipotesi registrata prima di guardare; previsione dichiarata e smentita.*

## Cosa avevo previsto e cosa è successo

**Prevedevo che il fondale peggiorasse** col metro pesato per il denaro: le stampe a prezzo alto
sono piccole, quindi pesarle meno doveva abbassare il risultato.

**È migliorato, e di molto:** su robinhood la media passa da **−31,5% a −8,8%**, e i pool sotto il
−90% dal 38,7% al 18,9%.

La regola scritta un'ora prima diceva: *«un miglioramento senza spiegazione è quasi sempre un
difetto di misura — non trattarlo come buona notizia finché non capisci il meccanismo»*.
Questa volta la regola ha fatto il suo lavoro.

## Il meccanismo: il merito non è del peso

Le due misure differiscono in **due cose**, non in una:
il peso (metà del denaro invece di metà delle stampe) **e** cosa fanno quando le vendite sono poche.

| | mediana stampe | metà del denaro | differenza |
|---|---|---|---|
| dove **entrambe misurano** (≥5 vendite), robinhood | +10,10% | +12,66% | **+2,6** |
| dove la prima **decreta −98%**, robinhood | −98,00% | −43,26% | **+54,7** |
| dove entrambe misurano, base | +2,51% | +3,90% | +1,4 |
| dove la prima decreta, base | −98,00% | −66,60% | +31,4 |

**Il peso vale due punti. Il decreto ne vale cinquantacinque.**

Stavo per attribuire l'effetto alla cosa sbagliata — lo stesso errore del 24/09, confrontare due
cose che differiscono in piu' di un modo e raccontarne una sola.

## Cosa impariamo davvero, ed è scomodo

**Il numero su cui abbiamo chiuso la direzione è dominato da una nostra convenzione.**

Il 26/09 avevo scritto che il fondale era −9,5% e il premio +0,9%, e da lì la conclusione: nemmeno
un filtro perfetto basterebbe. Ma quel numero dipende quasi tutto dalla regola *«meno di cinque
vendite = perdita totale»*, che **non è una misura: è una scelta**. Cambiarla di poco sposta il
fondale di cinquanta punti.

**Non significa che ci sia un vantaggio.** Significa che **non conosciamo il fondale**, e che
entrambe le versioni sono difendibili:
- il decreto dice: con meno di cinque vendite non saresti uscito davvero;
- la misura dice: qualcuno ha venduto, quindi uscire era possibile — solo sottile.

La verità sta in mezzo e dipende da una cosa che sappiamo misurare: **se a quei prezzi è passato
abbastanza denaro da contenere la nostra posizione.** È la stessa domanda della taglia, applicata
ai pool sottili invece che ai 10x.

## Cosa NON faccio, e perché

**Non riapro le strategie morte.** Sono morte per ragioni misurate, e ripescarle una per una finché
una passa è il modo più sicuro di trovare rumore.

**Non scelgo la misura che conviene.** Passare al metro che fa sembrare il mondo migliore, senza
una ragione indipendente, è esattamente ciò che il critic esiste per impedire.

## Il prossimo passo, che nasce da qui

Sostituire il decreto con una misura della **capienza reale** nei pool sottili: quanta valuta è
passata in vendita, e se basta a contenere una posizione. Il dato per farlo esiste già
(`_valuta_venduta`), e da stanotte esiste anche la profondità (`liq`).

Finché quel numero non c'è, **ogni affermazione sul fondale è provvisoria — compresa quella con cui
ho chiuso la direzione due giorni fa.**
