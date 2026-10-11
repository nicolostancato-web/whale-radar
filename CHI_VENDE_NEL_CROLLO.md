# Chi vende quando crolla: è folla, non regia

**L'idea era di Nicolò** (10 ottobre): *«se dampa forte vuol dire che qualcuno vende forte, o
qualcuno ha comprato anche forte all'inizio. Chi è che sta vendendo lì? Magari possiamo prendere
spunto.»* Domanda ben posta, perché falsificabile. La risposta è no, ed è solida.

## I numeri, su 28 crolli con i venditori identificati davvero

| misura | mediana | minimo | massimo |
|---|---|---|---|
| quota del venditore più grosso | **10,3%** | 6,9% | 51,5% |
| quota dei primi tre | 23,8% | 14,1% | 100% |
| venditori distinti nel crollo | **~90** | — | 120 (il nostro tetto) |
| quota del venduto che viene da chi aveva comprato nel primo minuto | **2,0%** | 0% | 49,8% |

**Un solo venditore fa più del 40% in 3 crolli su 28. In 27 su 28 i venditori distinti sono
almeno dieci, e in mediana sono novanta.**

E il tetto rafforza la conclusione invece di indebolirla: chiediamo l'identità di al massimo 150
transazioni per crollo, quindi i 90 venditori sono un **minimo** e la quota del più grosso è
**sovrastimata**. La concentrazione vera è ancora più bassa di così.

## Cosa vuol dire

Non c'è una regia da cui prendere spunto. I crolli non sono un grande venditore che scarica: sono
novanta indirizzi che vendono insieme, e i compratori del primo minuto non c'entrano quasi niente
(il 2% del venduto). Quindi **nessun segnale anticipato** da questa strada: non esiste un wallet
da sorvegliare che ci dica «sta per crollare».

Resta un fatto utile: i gettoni venduti nel crollo **non arrivano dal primo minuto**. Vengono
da altrove — la curva prima del pool, o acquisti intermedi. Dove, è la domanda successiva, e si
risponde seguendo i trasferimenti, non le vendite.

## Il mio errore, e perché lo scrivo qui

Un'ora prima avevo detto a Nicolò il contrario: *«il venditore più grosso fa il 51% del venduto,
quindi è concentrato»*. Era calcolato su **4 crolli su 27**, perché negli altri 23 la ricerca
dell'identità falliva — chiedevo 150 transazioni in una chiamata e il nodo rifiutava in silenzio.

I 4 che rispondevano non erano un campione: erano i crolli con **pochi** scambi, cioè proprio
quelli dove un venditore solo pesa tanto per costruzione. **Il guasto tecnico selezionava i casi
che confermavano l'ipotesi.** È la stessa famiglia di «da dove viene il campione» (30/09): un
campione preso da ciò che è riuscito è un campione di ciò che riesce, non del mondo.

Due cose sono cambiate nel codice, non nella mia memoria:
1. l'identità si chiede a pacchetti da 25, non da 150;
2. il record porta il campo `attendibile`, e il referto stampa **su quanti casi** è calcolato —
   perché la riga precedente diceva «su 27 crolli» un numero che veniva da 4.

E i 23 record che dicevano «0 venditori» sono stati cancellati: **«zero» e «non l'ho potuto
sapere» sono due cose diverse, e scrivere la prima al posto della seconda mette una bugia nel
database — peggio di un buco, perché un buco si vede e una bugia no.**
