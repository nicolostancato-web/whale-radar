# Il piano da qui — con le date e il punto in cui si smette

**1 ottobre. Scritto ADESSO, prima di avere i risultati, perché una regola decisa dopo non è
una regola.**

## Dove siamo, in una riga

Sedici ipotesi provate, sedici morte. L'ultima — la sola che avesse prodotto un numero positivo
— è morta per la latenza: **compravamo a un prezzo che non si può avere**. La macchina ora
misura il prezzo che si paga davvero, e tutto va rimisurato su quello.

## 1. Il ciclo accumula (1 → 8 ottobre)

Il ciclo gira **ogni tre ore**, ruotando su sei configurazioni (due chain × tre livelli di
latenza e momento d'ingresso). Fa **otto prove al giorno**: in una settimana ogni configurazione
viene provata nove-dieci volte.

Ogni prova finisce nel registro, **anche quando non trova niente** — senza il denominatore un
successo non significa nulla.

### La regola che dice cos'è un segnale, fissata ora

Una configurazione conta **solo se**:

1. dà «segnale» in **almeno tre ripetizioni su cinque**, non una;
2. il margine supera la soglia, che **sale col numero di prove** (già nel codice);
3. vale su **tutte e due le chain**.

Una sola ripetizione positiva su cinque è esattamente ciò che il caso produce. **Non si
promuove niente che non si ripeta.**

## 2. La prova in avanti (verdetto intorno al 10-15 ottobre)

Il contatore è **ripartito da zero** l'1/10, perché misurava un prezzo irraggiungibile. Serve
di nuovo: **5.000 pool nuovi per chain**, nati dopo il 30/09, misurati col prezzo ottenibile.

Il giudice non mostra il rendimento prima del traguardo, e scrive il verdetto **una volta sola**.

## 3. Il punto in cui si smette — e questa è la parte che conta

**Se al 20 ottobre, dopo circa 150 prove registrate, nessuna configurazione si è ripetuta tre
volte su cinque su entrambe le chain**, allora la risposta non è la configurazione numero 151.

La risposta è: **questo mercato, entrato dopo il quinto scambio e con un'esecuzione realistica,
non paga.** E lo diremo così, con il registro in mano a dimostrarlo.

A quel punto la domanda diventa un'altra, e la decisione è di Nicolò: **dove portiamo la
macchina?** Perché la macchina — raccolta, misura onesta, due revisori, verdetti che sanno dire
no, memoria che non si perde — **funziona, ed è indipendente da cosa misura.**

Non sarebbe un fallimento: sarebbe aver speso venti giorni per sapere con certezza una cosa che
molti credono senza misurarla, con **zero euro rischiati**.

## 4. Cosa serve dalle mani di Nicolò (gratis, dieci minuti)

1. **healthchecks.io**, piano gratuito senza carta: un osservatore in un dominio di guasto
   diverso. Finché i guardiani girano tutti su GitHub Actions, sono un guardiano solo — provato
   sul campo l'1/10, morti tutti e tre insieme per quattro ore.
2. **Una regola sul repository** che chieda la sua revisione per `.github/workflows/`: finché il
   mio token può modificare il guardiano, tre guardiani sono un file.

*(La chiave di Astra è stata messa fra i segreti l'1/10: quella corsia ora è autonoma.)*
