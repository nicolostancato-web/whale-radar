# Ricerca Grok — 2026-10-06 17:10 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 616s

---

Il piano va attaccato sui numeri, non sull'intenzione. Prima verifico se nel lavoro c'è la definizione esatta di «capitale onesto» e della posizione in fila: da quella dipende se la tabella è un edge o un artefatto di selezione.La nota interna contraddice il brief su un punto decisivo: il gas. Controllo nel codice come è stato costruito il conto onesto e la coda delle 10x, prima di giudicare.Il piano, nella forma «chi ha fatto tante X più volte, copiamolo», è sbagliato alla radice. La tabella che hai già in mano è una perdita contro il cash in ogni riga. La classifica dei ripetitori va costruita solo se vuoi fabbricare un nome. L'unica misura che può riaprire qualcosa è un numero solo, prestabilito, e se esce sotto 1 si chiude.

## 1. Come la ricerca di «chi ripete» si illude

Il modo più probabile è questo: ordini i portafogli per **quante volte** hanno preso una X grossa, e quel conteggio è quasi interamente il conteggio di **quanti tentativi** hanno fatto, più gli indirizzi che il lanciatore ha scritto nella lista dei 32 esentati. La fortuna, a parità di tentativi, è il residuo piccolo. La classifica mette in cima il residuo grande.

Non esiste un intero K oltre il quale «ha ripetuto» smette di essere caso. K senza il numero di tentativi \(n_i\) è la classifica dei bot.

Definizione stretta, l'unica che si calcola coi tuoi conteggi senza inventare una distribuzione: successo = essere l'unico primo compratore di una moneta che poi gradua. Sono 5.169 eventi. Se li assegni a caso, in modo uniforme, sui 146.000 portafogli (media 0,035 a testa):

| volte | portafogli attesi | probabilità che ne esista almeno uno |
|---|---:|---:|
| 2 | 89 | ~1 |
| 3 | 1,05 | 65% |
| 4 | 0,01 | 0,9% |
| 5 | ~0 | ~0 |

Due volte è il rumore di fondo. Quattro volte è dove questo null, il più gentile possibile verso la tesi, si esaurisce. Gentilissimo, perché assume che un portafoglio fermo e un bot che compra per primo mille volte abbiano la stessa probabilità. Appena l'esposizione è storta, il null si sposta di un ordine di grandezza. Scenario illustrativo, non una stima dei tuoi dati: ~60.000 portafogli, ~95.000 primi acquisti, una coda di pochi indirizzi con centinaia o migliaia di tentativi, probabilità di graduazione del primo acquisto 5,27% (5.169 / 98.025). Senza nessuna abilità ti aspetti circa 15 portafogli con almeno 10 graduzioni prese da primi, e circa 4 con almeno 50. Quei quattro, in una classifica per conteggio, sono il risultato.

La soglia che regge il confronto multiplo (5% di probabilità di anche un solo falso positivo su 146.000 portafogli, un solo test deciso prima) è un p-value ≤ 3,4×10⁻⁷ **per portafoglio**, cioè un numero di successi che dipende da \(n_i\) e da \(p\):

| tentativi \(n\) | successi minimi se \(p\)=5,27% (graduazione del primo acquisto; la media è fra parentesi) | se \(p\)=0,3% (ordine della coda ≥10x del primo posto) |
|---:|---:|---:|
| 20 | 9 (media 1,1) | 4 (media 0,06) |
| 100 | 20 (media 5,3) | 7 (media 0,3) |
| 400 | 47 (media 21) | 11 (media 1,2) |
| 1.500 | 126 (media 79) | 19 (media 4,5) |
| 5.000 | 346 (media 264) | 39 (media 15) |

Un bot con 1.500 primi acquisti che «ne ha prese 80» è sotto la media. Un portafoglio con 20 tentativi e 6 prese da 10x è fuori dal caso. La classifica per conteggio mette in cima il primo e butta il secondo.

Due cose alzano ancora l'asticella. I lanci si raggruppano nel tempo, quindi i successi di uno stesso portafoglio non sono estrazioni indipendenti: la binomiale dichiara significativo troppo presto. E 32 esenzioni sullo stesso lancio, finanziate dallo stesso indirizzo, sono un operatore contato trentadue volte: 146.000 non è il numero di prove indipendenti.

La misura che la uccide prima, e che puoi calcolare senza finire l'attribuzione dei pool: prendi la classifica per numero di X, togli ogni moneta in cui quell'indirizzo è il lanciatore o sta nella lista `snipeTaxExemptions` della transazione di creazione, e sostituisci il conteggio con l'eccesso rispetto ai portafogli con **lo stesso numero di tentativi**. Poi congeli i nomi usando solo ciò che era noto a una data T e, dopo T, simuli il copiatore: stesso segnale, primo blocco in cui un indirizzo non esentato riesce davvero a comprare, **tutte** le monete segnalate comprese quelle che non graduano, inventario a fine periodo valutato a quello che si incassa vendendo. Il numero è il patrimonio finale del copiatore diviso il capitale messo, con una cassa finita.

Se i nomi continuano a fare X e quel patrimonio è sotto 1, la frase del fondatore è già falsa. Su questa chain la versione precedente della stessa frase, sui pool, era già ridotta a trenta portafogli con intervalli che si toccano (80,5% contro 77,8%) e con una fetta del divario dovuta al periodo. Ripeterla sulla curva senza il divisore dei tentativi rigenera quel quasi-segnale.

## 2. La cosa che non stai misurando

La colonna «solo chi ha venduto» non contiene un vantaggio. Contiene la formula della curva.

1,2063 / 0,9568 = 1,2608. Il vantaggio di gettoni che hai misurato a parte, primo contro decimo, è 1,26. Lo scarto è 0,001. Tutto il gradiente di chi riesce a vendere, dal primo al decimo, è il prezzo meccanico d'ingresso. Non c'è residuo per l'abilità, per il timing, per la selezione del portafoglio.

Le tre colonne non sono la stessa media, e la prosa le tratta come se lo fossero. 1,2063 × (1 − 0,395) = 0,730, mentre il conto onesto è 0,854. Il 39,5% è una quota di **posizioni**. Il 0,854 è capitale uscito su capitale entrato, solo valuta nativa. La quota di capitale che non torna è 1 − 0,854/1,2063 = **29%**, non 39%. Il biglietto che resta bloccato al primo posto pesa il 63% del biglietto che esce: sono soldi veri, non polvere. Dal decimo posto in giù il capitale bloccato crolla al 4% e poi al 2%, mentre la quota di posizioni bloccate resta intorno al 20%: lì a non vendere è polvere.

| posto | capitale che esce | capitale bloccato | posizioni bloccate | biglietto bloccato / biglietto uscito |
|---|---:|---:|---:|---:|
| 1 | 71% | 29% | 39,5% | 0,63 |
| 2 | 88% | 12% | 20,3% | 0,51 |
| 3 | 92% | 8% | 23,1% | 0,31 |
| 10 | 96% | 4% | 19,4% | 0,16 |
| 50 | 98% | 2% | 19,5% | 0,08 |

Il primo posto è l'unico in cui il denaro grosso resta dentro. È anche l'unico posto che esiste sulle monete che non ricevono mai un secondo compratore: per essere decimi, nove persone sono già entrate. Questo lo hai già scritto. La conseguenza che non hai tirato è che il secondo e il terzo posto ripetono lo stesso filtro un gradino più in là. Non sono una strategia nuova.

Il decimo di punto tra 0,938 e 0,948 è più piccolo dell'ambiguità di definizione della colonna (12 punti, tra 0,730 e 0,854). Il terzo posto «vince» sul secondo pur avendo multiplo di vendita peggiore e più posizioni senza vendita, perché il capitale bloccato lì è più piccolo. È la mistura delle taglie storiche, non un'aspettativa che ottieni decidendo di arrivare terzo con la tua taglia. E 0,948 batte il primo posto e perde contro tenere la valuta ferma, che rende 1. La cassa non usata non trasforma 0,95 in un guadagno: il capitale che schieri torna 0,95.

La cella che indica davvero un'altra direzione è la coda, e indica un buco di misura. Tra chi vende, il primo posto sta sopra 10x circa lo 0,3%, il secondo circa l'1,7%. Con un ingresso del 14% più conveniente il primo dovrebbe superare la soglia 10x più spesso del secondo, a parità di prezzo d'uscita. L'inversione ha la taglia giusta per essere le uscite che non vedi. Su ~59.000 primi posti che vendono, 0,3% sono ~180 eventi da 10x; per arrivare all'1,7% ne mancano ~830. Le monete graduate sono 5.169. Basta che un sesto di quei primi compratori abbia realizzato ≥10x nel pool, e che quel realizzo sia contato come «non ha mai venduto», e la coda del primo posto sparisce dalla colonna sbagliata e va a pesare zero nel conto onesto. È lo stesso meccanismo del 0,29x che hai già scartato. Qui è dentro il 0,854, in una quota che a oggi hai quantificato in numero di casi (sotto i 50 nel campione dei candidati) e non in capitale.

Il buco, in una formula. Sia \(g\) la quota di capitale del primo posto che sta su monete graduate ed è oggi nel mucchio azzerato (\(g\) ≤ 0,29). Il conto vero è

\[
0{,}854 + g \times R_{\text{graduati}}
\]

Se i biglietti sulle graduate hanno la stessa taglia degli altri e ogni primo compratore di una graduate è oggi a zero, \(g \approx 0{,}053\) e servi un realizzo di circa 2,8x su **tutto** quel capitale solo per tornare a 1. A 10x il conto salirebbe a circa 1,38. A 2x resterebbe una perdita. Lo 0,8% dei lanci non entra in questo conto: entra \(g\), che è capitale. Finché pubblichi la quota di monete, lo sportello di fuga non ha un prezzo.

Quel \(R\) inoltre è il realizzo di chi era già dentro, spesso esentato dalla tassa che parte al 99% nei primi 5 secondi. L'anticipo mediano di 41 minuti e la tenuta mediana di 5,5 ore, letti insieme, dicono che chi compra sulla curva ha il tempo di vendere dentro il pool nuovo. Il copiatore che scopre la moneta quando il pool nasce è il bid in cui quello vende. Un indirizzo vergine accettato 10 volte su 10 dimostra che il mercato è aperto. L'esenzione, che è l'unico modo di non pagare il 99%, è una nomina del lanciatore. Aprire e poter copiare sono due fatti diversi.

Il secondo e il terzo posto sono il segnale, e il segnale dice di misurare il prezzo della conferma, non di cercarci dentro le persone. Il taglio che manca, e che è già nei dati della transazione di creazione: rifare il conto onesto del primo posto spezzato in esentato-nei-primi-5-secondi contro tutti gli altri, e solo sulle monete che poi ricevono un secondo compratore che non è nella lista dei 32. Se dopo quel taglio il primo posto torna sopra gli altri della misura del prezzo della curva (~1,26 contro il decimo, meno sui posti vicini), la classifica attuale è la tassa più le monete morte in arrivo. Se non ci torna, l'anticipo è una perdita anche condizionando sulla domanda successiva, e la caccia ai ripetitori non ha un oggetto.

Io quel taglio lo farei, e pubblicherei \(g\) e il realizzo del copiatore non esentato, con la regola di uscita scritta prima. Non costruirei la classifica. Se quel realizzo, contando anche le monete che la regola compra e che non graduano, è ≤ 1, il risultato è smettere.
