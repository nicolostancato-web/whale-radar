# Verdetto H13 e H14 — i crolli rientrano, i rialzi no

**29/09. Soglia scelta sulla prima meta' dei pool per data di nascita, giudizio sulla seconda,
mai vista. Nessuna regola toccata dopo aver visto il risultato.**

## Esito

| regola | robinhood | base |
|---|---|---|
| **H13** — si esce se il prezzo crolla sotto una soglia | **−3,3 punti** | −1,7 punti |
| **H14** — si vende al primo scambio sopra un bersaglio | **+5,6 punti** | +1,1 punti |

**H13 muore.** Serviva +10 punti su tutte e due; ha fatto danni su tutte e due. E non per un
pelo: sulla meta' d'apprendimento **ogni** soglia provata era peggiore del non fare niente, in
ordine — piu' stretto lo stop, peggio il risultato.

**H14 non e' promossa**, per il motivo scritto sotto. Ma la sua direzione e' l'opposto esatto
di H13, e le due cose insieme dicono una cosa sola sulla forma di questo mercato.

## Cosa hanno insegnato

### I crolli rientrano, i rialzi no

Un pool che scende sotto il 30% dell'ingresso spesso risale: uscire li' trasforma uno scossone
in una perdita vera. Un pool che fa 2x quasi mai lo rifa': non incassare li' significa
restituirlo.

E' la stessa cosa che Nicolo' aveva detto a luglio guardando le balene — *«tieni sui dip
−50/60%, esci quando escono loro, non su stop di prezzo»*. Allora era un'intuizione. Adesso e'
misurata, su 10.176 pool, fuori campione, con la soglia scelta prima di guardare.

> **Su questo mercato lo stop di prezzo e' una tassa, non una protezione.**

### Perche' H14 non si promuove (la trappola di stamattina, di nuovo)

Il bersaglio a 2x scatta sul **12% dei pool**: quelli che fanno scatti violenti. E gli scatti
violenti, su questo mercato, sono il segno di un pool **sottile** — schizza proprio perche'
dentro non c'e' nessuno.

Il +5,6 e' misurato sul **prezzo**. Stamattina abbiamo appena imparato, pagando 52 punti, che
il prezzo e l'incasso non sono la stessa cosa e che chi insegue il prezzo trova i pool da cui
non si esce. Promuovere H14 senza rimisurarla su quanto si **incassa** sarebbe ripetere lo
stesso errore lo stesso giorno.

**Prossimo passo, gia' deciso:** la simulazione di riempimento va portata dentro la regola
d'uscita, dove vivono i dollari veri. Se i +5,6 punti sopravvivono li', H14 vale. Se svaniscono,
era di nuovo polvere.

## Nota di metodo

Il cammino del pool e' entrato nel dato oggi. Prima non c'era, e per questo dodici ipotesi di
fila hanno variato **solo cosa comprare**. Non era una scelta di strategia: era un limite dello
strumento che nessuno aveva nominato.
