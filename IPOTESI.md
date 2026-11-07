# 📋 Ipotesi — scritte prima di misurarle

*Aperto il 22 settembre 2026, sera. Ogni riga qui dentro e' stata scritta PRIMA di conoscerne
l'esito. È l'unica cosa che rende una previsione diversa da un ricordo.*

---

## Le regole di questo registro

**1. Si scrive prima, sempre.** Una riga aggiunta dopo aver visto i dati va marcata `ESPLORATIVA`
e non potra' mai, da sola, sostenere una promozione: dovra' essere riconfermata da zero su dati
mai visti.

**2. Ogni ipotesi porta la sua condizione di morte.** Non «poco convincente»: *morta*. Senza quella
riga l'ipotesi non entra — perche' un'ipotesi senza condizione di morte si puo' sempre
razionalizzare restringendo una soglia o spostando una finestra.
*(regola presa il 22/09 da un metodo di analisi esterno)*

**3.bis Si contano i POOL DISTINTI, non le righe.** Lo stesso pool osservato tre volte a venti
minuti di distanza non e' tre prove: e' una prova guardata tre volte. Ogni condizione di morte
parla di pool distinti. *(aggiunto il 22/09, misurando: 391 previsioni su 332 pool)*

**3. Si contano le domande fatte.** Il numero di ipotesi provate va riportato accanto a qualunque
risultato. Senza quel numero, «ha funzionato» non significa niente.

**4. Niente si cancella.** Un'ipotesi morta resta scritta, con la data e il motivo. E' cosi' che si
evita di riprovarla fra due mesi credendo che sia nuova.

---

## Perche' partono adesso, prima che la macchina sia rifinita

Le previsioni **non si accumulano da sole**: si accumulano da quando si comincia a scriverle. Ogni
giorno passato ad aspettare la macchina perfetta e' un giorno di previsioni che non avremo mai.

Il rigore non cambia — si scrive prima e si giudica dopo. Cambia solo **quando parte l'orologio**.

---

## Ipotesi aperte

### H1 — La liquidita' al momento dell'entrata conta

**Scritta il:** 22/09/2026, sera · **Stato:** aperta · **Tipo:** dichiarata prima

**Cosa dice:** fra i pool su cui potremmo entrare, quelli con liquidita' piu' alta al momento della
decisione danno un rendimento di portafoglio migliore, dopo i costi, di quelli con liquidita' piu'
bassa.

**Perche' e' plausibile:** i costi di esecuzione scendono con la liquidita' — lo abbiamo misurato
(impatto mediano 0,45%, ma il novantesimo percentile e' dieci volte tanto). Se il vantaggio lordo
fosse simile, resterebbe piu' netto dove si paga meno per entrare e uscire.

**Perche' potrebbe essere falsa:** la liquidita' alta attira anche chi e' piu' veloce di noi. Il
guadagno potrebbe essere gia' stato preso da altri prima che arriviamo — e noi arriviamo con
secondi di ritardo.

**CONDIZIONE DI MORTE:** se dopo 300 POOL DISTINTI con previsione chiusa il gruppo «liquidita' alta» non batte quello
«liquidita' bassa» di almeno 1 punto percentuale di rendimento di portafoglio dopo i costi,
l'ipotesi e' **morta**. Non ridotta, non da approfondire: morta.

**Finestra di valutazione:** 6 ore dalla decisione.

---

### H2 — Il numero di compratori distinti conta piu' del numero di scambi

**Scritta il:** 22/09/2026, sera · **Stato:** aperta · **Tipo:** dichiarata prima

**Cosa dice:** a parita' di scambi, i pool con piu' INDIRIZZI DISTINTI che comprano danno un
rendimento migliore di quelli dove gli stessi pochi indirizzi scambiano molte volte.

**Perche' e' plausibile:** molti indirizzi diversi somigliano a interesse vero; pochi indirizzi che
scambiano molto somigliano a una persona sola che si fa volume da sola. La seconda cosa non ha
nessuna ragione di continuare.

**Perche' potrebbe essere falsa:** molti indirizzi possono essere una persona sola con molti
portafogli — e la tecnica per riconoscerlo l'abbiamo provata oggi e non reggeva (campioni piccoli,
direzioni opposte fra le chain).

**CONDIZIONE DI MORTE:** se dopo 300 POOL DISTINTI con previsione chiusa la differenza fra i due gruppi e' inferiore a
1 punto percentuale dopo i costi, **morta**.

**Finestra di valutazione:** 6 ore.

---

### H3 — La vendibilita' dimostrata protegge piu' di quanto costa

**Scritta il:** 22/09/2026, sera · **Stato:** aperta · **Tipo:** dichiarata prima

**Cosa dice:** escludere i pool da cui nessuno e' ancora riuscito a USCIRE migliora il rendimento
di portafoglio dopo i costi, anche tenendo conto delle occasioni che ci fa perdere.

**Perche' e' plausibile:** oggi abbiamo misurato che un pool su sei e' uno da cui praticamente
nessuno esce, e nel nostro conteggio quelli risultavano guadagni normali. Se anche solo una parte
fossero trappole, evitarli vale piu' di quello che costa.

**Perche' potrebbe essere falsa:** «nessuno e' ancora uscito» puo' semplicemente voler dire «e'
troppo presto». Se il filtro scarta soprattutto i pool giovani, potrebbe togliere proprio quelli
dove il guadagno e' maggiore.

**CONDIZIONE DI MORTE:** se dopo 300 POOL DISTINTI con previsione chiusa il gruppo filtrato non batte quello non
filtrato — cioe' se il filtro non paga cio' che ci fa perdere — **morta**.

**Finestra di valutazione:** 6 ore.

---

## Domande fatte finora

**3.** Conteggio aperto il 22/09. Ogni ipotesi nuova lo aumenta, e il numero va riportato accanto a
qualunque risultato: e' il denominatore della fortuna.

## Ipotesi morte

*(nessuna, per ora — e quando ce ne saranno resteranno scritte qui)*

---

## H4 — la successione di pattern (scritta 23/09 04:25, prima di qualunque esito in avanti)

**L'ipotesi:** a due ore dal primo scambio, un pool con **almeno 11 compratori distinti e almeno 73
scambi** (robinhood; su base 8 e 71) ha una probabilita' sensibilmente piu' alta di fare un colpo
grosso rispetto ai pool contemporanei che non soddisfano le condizioni.

**Misurata sullo storico:** 18,4% dei pool scelti fa +25% contro il 6,8% del caso; 9,5% fa +50%
contro 3,4%; 4,8% fa +100% contro 1,4%. Su 400 mescolate casuali nessuna eguaglia le prime due
soglie. 147 pool scelti su 1.004.

**Perche' si misura una frequenza e non un rendimento medio:** su questi mercati la media e'
dominata da singoli token (uno solo fa +1.972% e sposta la media di 63 pool di quaranta punti).
Togliendo i 3 migliori, il risultato medio di base passa da +80% a −9,4%. Una frequenza non si
lascia spostare cosi'.

**Si annotano anche i pool NON scelti**, come gruppo di controllo: senza, la prova non dimostrerebbe
nulla, perche' la quota di token che salgono oscilla fra il 20% e il 60% da un'ora all'altra e un
numero assoluto sarebbe illeggibile.

**CONDIZIONE DI MORTE, scritta ora:** su **150 pool scelti distinti** annotati in avanti, se la
quota che fa +50% non arriva almeno al **7%**, oppure se non supera di almeno **due volte** la quota
dei pool di controllo nelle stesse ore, **H4 e' morta e si butta.**

**Non e' stabilita su base:** 37 pool scelti, due soli colpi, e sulla misura robusta base va peggio
del non fare niente. Su base H4 si annota ma non si conclude finche' i pool scelti non arrivano a 150.
