# Revisione Grok — 2026-09-25 15:57 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 679s

---

Il confronto che citi è annidato: prima di giudicare la stabilità ricalcolo cosa deve essere successo nel pezzo nuovo, poi ti dico il test che può far crollare il risultato.Il progetto ha già una definizione operativa di trappola e di iniziatore. La leggo prima di attaccare il numero, così il test che ti do è sul tuo dato e non su una ricostruzione.Il calo dal 29,1% al 22,0% è la persistenza dell'attività, letta con soglie così basse che il campo `from` non ha ancora dimostrato di aggiungere nulla al numero di swap. La stabilità fra 3.454 e 4.732 è l'inerzia di un campione annidato: il 73% del secondo è il primo, e questo confronto non è in grado di far sgonfiare un effetto del tipo che ti ha già ucciso le tre strategie precedenti. Il valore atteso di chi passa il filtro è −18,3%. Con i sani a +4,3% e le trappole a −98%, il pareggio sta sotto il 4,2% di trappole.

La riga «>8 venditori e trap rate ancora 21%» dice già una cosa precisa: i venditori distinti non sono contati sulle stesse vendite che definiscono la trappola. Se lo fossero, otto venditori distinti implicherebbero almeno otto vendite e la riga sarebbe a zero. Quella tautologia grossolana è già esclusa dai tuoi numeri. Restano le altre.

## 1. Il confronto che ti tiene in vita il risultato non può farlo morire

**(a)** La stabilità fra 3.454 e 4.732 è il comportamento meccanico di due campioni annidati, e la sola fetta nuova ha già un tasso di base diverso.

**(b)** Il secondo campione contiene il primo. L'incremento è 1.278 pool, il 27%. Un effetto misurato sul cumulato si muove solo in proporzione a quel 27%: anche una scomparsa totale dell'effetto nei dati nuovi sposta il cumulato di una frazione, non lo dimezza. Le tre volte precedenti il segnale è morto perché il campione nuovo era abbastanza grande da trascinare la media. Qui non lo è. «Non si è sgonfiato» è la proprietà del disegno.

Il tasso di base della fetta nuova si recupera dalla tabella:

\[
\frac{4732 \times 0{,}291 - 3454 \times 0{,}303}{1278} = 25{,}9\%
\]

contro il 30,3% del primo blocco. L'arrotondamento a un decimale lo confina fra il 25,5% e il 26,2%. Il «identico» nasconde già quattro punti di tasso di base.

Il tasso filtrato della fetta nuova non è nella tabella, perché manca quanti pool teneva il filtro sui 3.454. Sotto l'ipotesi che la quota trattenuta sia la stessa dei 4.732 (3.316/4.732 = 70%), il divario nella fetta nuova risulta circa −4 punti, contro −8 punti nel primo blocco: il dimezzamento c'è già, e il cumulato (22,2% → 22,0%) lo copre. È un'ipotesi, non una misura. Va sostituita coi conteggi veri prima di crederci.

**(c)** Congela la regola annunciata, «più di 2 venditori e più di 3 compratori», e non toccarla più. Parti dagli identificativi della fotografia a 3.454. Sulla sola differenza (i 1.278) riporta, in due righe: pool, quota trattenuta, tasso di trappole di tutti, tasso di trappole dei trattenuti, tasso di trappole degli scartati, media, R dei sani. La quantità è

\[
\Delta = p(\text{trappola}\mid\text{trattenuto}) - p(\text{trappola}).
\]

Intervallo con bootstrap a blocchi di ora di lancio. Poi lo stesso conto su un blocco di giorni successivo, mai usato per scegliere la regola.

**(d)** Se il cumulato ti ha ingannato, nei 1.278 \(\Delta\) è molto più piccolo di −8 punti, oppure l'intervallo a blocchi copre sia −8 sia valori vicini a zero. Se il disegno annidato era innocuo, \(\Delta\) dei 1.278 sta vicino a −7 punti e l'intervallo a blocchi esclude qualsiasi cosa sopra −3 punti. Anche in quel caso hai una associazione ripetuta: i punti 2 e 3 dicono che cosa non è.

## 2. Il test che può far crollare il risultato

**(a)** Con soglie a 2 e a 3, nel primo mezz'ora, il numero di `from` distinti e il numero di swap sono quasi lo stesso numero, e la persistenza dell'attività prevede da sola «meno di 5 vendite nelle 24 ore successive».

**(b)** I distinti non possono superare gli swap. «Più di 3 compratori distinti» è un sottoinsieme di «più di 3 swap di acquisto». I due insiemi divergono solo dove gli stessi indirizzi ripetono lo swap: il riciclo, il wash, il bot. È l'unico margine su cui il campo nuovo può valere qualcosa. Il resto del calo dal 29% al 22% è «un pool che ha già scambiato ne avrà altri», che è il fatto più vecchio della microstruttura e spiega la firma che ti ha colpito: un dummy grossolano non si sgonfia aggiungendo il 27% di dati, a differenza di un 12× o di un AUC 0,92, che avevano gradi di libertà abbastanza da adattarsi al rumore. Spiega anche perché stringendo la soglia il tasso di trappole si ferma intorno al 21%: hai già separato i pool morti da quelli vivi, e i rug che hanno avuto attività iniziale restano dentro.

Il 50% di indirizzi visti una volta sola e l'86% visti in un solo pool scagiona il router condiviso. È anche la distribuzione di wallet usa-e-getta. Non distingue le due cose, e per questo test non serve ancora distinguerle.

C'è un secondo canale, nel codice di raccolta. `iniziatori.py` ha `ORE_UTILI = 3` ore come finestra di default, mentre l'ingresso è a 0,5 ore. Se il conteggio ha usato tutto ciò che è stato raccolto, 2,5 ore di scambi successivi all'ingresso entrano nel filtro. La riga degli 8 venditori esclude solo il caso estremo (conteggio sulle stesse 24 ore della trappola). Non esclude questa sovrapposizione.

**(c)** Su ogni pool fissa \(t_0\) come primo swap e taglia i conteggi a `ts <= t0 + 1800`, indipendentemente da cosa ha raccolto lo script. Due regole, stessi pool, stessa etichetta:

- A: `from` distinti in acquisto > 3 e in vendita > 2
- B: swap di acquisto > 3 e swap di vendita > 2, ignorando `from`

Riporta il tasso di trappole di A, di B, e di A dentro i quintili di (swap di acquisto, swap di vendita). L'effetto specifico delle persone è solo quello dentro i quintili, ed è da calcolare sui 1.278, non sull'unione. Se dentro i quintili resta un divario, e solo allora, ripeti A dopo aver fuso gli indirizzi che condividono il finanziatore del primo finanziamento nativo.

**(d)** Se ho ragione, B riproduce il tasso di trappole di A entro circa un punto, e dentro i quintili il divario di A è circa zero: il risultato sopravvive come attività e muore come risultato sulle persone. Se ho torto, dentro i quintili, sui 1.278, con il taglio a 30 minuti, i distinti abbassano ancora le trappole di diversi punti. Quello sarebbe il primo numero di questa ricerca che riguarda le persone. Il punto 3 gli si applica lo stesso.

## 3. Il filtro non ha un uso che eviti di comprare

**(a)** Spostare massa da un atomo a −98% lascia un valore atteso di −18,3%, e rispetto a non comprare questo valore è una perdita.

**(b)** La media è una mistura, e torna al centesimo coi numeri pubblicati:

\[
0{,}291\times(-0{,}98)+0{,}709\times 0{,}049 = -0{,}250
\]
\[
0{,}220\times(-0{,}98)+0{,}780\times 0{,}043 = -0{,}183
\]

Dei +6,7 punti fra −25,0% e −18,3%, circa +7,3 vengono dal minor peso dell'atomo a −98% e circa −0,5 dal peggioramento dei sani. Il pareggio, a questi rendimenti, è

\[
p < \frac{0{,}043}{0{,}98+0{,}043} = 4{,}2\%.
\]

La griglia si ferma al 21% e, oltre la prima soglia, la media peggiora. Stringere non è una strada verso il 4%.

Sul libro scartato (1.416 pool) il tasso di trappole è circa il 46% e la media circa −41%. I sani scartati rendono circa +6,9%, più dei sani trattenuti (+4,3%). Il filtro trattiene il rendimento condizionato peggiore. Ordina «ci saranno vendite», e lo paga con la coda destra.

Un veto vale qualcosa solo contro una decisione che qualcuno prenderebbe comunque e che ha già valore atteso positivo. Contro la liquidità, evitare un libro a −18% vale zero: anche il libro scartato, messo a confronto con non fare nulla, non va corto da solo. A mezz'ora di vita un memecoin nuovo non ha prestito. Vendere il filtro a chi compra gli trasferisce il −18%.

**(c)** Non c'è un test che apra un uso. L'unico che avrebbe senso è un veto in ombra su un flusso di decisioni già fissato, indipendente da questo filtro, col capitale rifiutato lasciato liquido, e l'intervallo della differenza di P&L sopra zero su un blocco di giorni successivo. Quel flusso, con valore atteso positivo fuori campione, non c'è.

**(d)** Se ho ragione, ogni uso che scrivi ha valore atteso negativo, oppure domanda nulla nel momento in cui il −18% residuo viene detto. Se ho torto, quel flusso esiste già, il veto ne alza il P&L dopo i costi e dopo le occasioni sane bloccate, e il risultato regge su giorni non usati per costruire il filtro.

## 4. Il crollo di R dei sani è il prezzo del filtro, e il «+4,3%» è una mistura

**(a)** All'ingresso fisso di 0,5 ore, più controparte distinta all'inizio coincide con un rendimento successivo peggiore dei pool ancora vendibili, e il +4,3% è la media fra una fetta moderata molto positiva e una fetta affollata a zero.

**(b)** Le due curve sono monotone e di segno opposto sulla media. Il tasso di trappole scende e si ferma (29 → 22 → 21). R dei sani scende (+4,9 → +4,3 → −0,3). La media, che è la loro somma, ha un fondo piatto. I quattro decimi di punto fra −18,7%, −19,2% e −18,3% stanno sotto l'errore plausibile di una media di memecoin. Quel fondo non identifica un ottimo.

Sulla tabella arrotondata, la fetta che passa «2 e 3» e non passa «8 e 10» (926 pool) ha tasso di trappole circa 25%, R dei sani circa +17%, media ancora circa −11%. La fetta che passa «8 e 10» ha R dei sani −0,3%. Il restringimento butta via l'unica fetta in cui il condizionato è largamente positivo, e anche quella fetta perde perché un quarto è l'atomo a −98%. In microstruttura il segno è quello dell'adverse selection: a 30 minuti la breadth è la folla già arrivata, e tu sei la sua liquidità di uscita.

L'esito è il prezzo mediano dei soli swap di vendita. Per un pool attivo quel mediano cade dove sono avvenute le vendite, spesso molto prima delle 24 ore. Il numero «uscita a 24 ore» e il numero «mediano delle vendite nella finestra» sono due politiche diverse. Se le vendite si concentrano nella fase viva e il prezzo poi decade, il +4% descrive la fase viva.

**(c)** Ricalcola sui dati non arrotondati le tre fette (scartati dal filtro lasco, fascia intermedia, filtro stretto): mediana, frazione di rendimenti positivi, quota della media dovuta all'1% migliore. Accanto, il rendimento da \(t_0\) all'ingresso, che è il movimento a cui non partecipi. Poi ricalcola R dei sani col prezzo all'ultimo scambio con `ts <= t0+24h`, stessa size, e mettilo di fianco al mediano delle vendite. Intervallo a blocchi di ora di lancio.

**(d)** Se ho ragione, la fetta stretta ha un rialzo pre-ingresso più alto della fascia intermedia, il +17% intermedio è trainato dall'1% migliore con mediana vicina a zero, e il R dei sani a 24 ore secche sta sotto il mediano delle vendite. Se ho torto, i rendimenti pre-ingresso sono simili fra le fette, la mediana della fascia intermedia sta vicina alla sua media, e R dei sani non scende con la breadth dentro i bin di numero di swap. In quel caso il calo è la composizione della griglia: si smette di cercare la soglia, perché non c'è un parametro da ottimizzare.

## 5. Il campione al 95% va misurato, e l'ordine dei file non è un hash casuale

**(a)** L'inclusione è un prefisso dell'ordine di directory tagliato dal budget di raccolta, e con soglie a 2 e a 3 un indirizzo mancante è l'intera classificazione.

**(b)** La raccolta cammina `os.listdir` e si ferma a `BUDGET_SEC`. I pool incontrati prima mettono le loro transazioni in coda prima. «Completo al 95%» seleziona quel prefisso. L'ordine di directory di una cartella scritta nel corso dei giorni segue l'ingestione, e l'ingestione segue quando il pool è stato scoperto. L'hash dell'indirizzo sarebbe casuale. La camminata che esegue lo script è un'altra cosa.

Il buco del 5% pesa poco sul conteggio globale: con il 50% degli indirizzi visti una sola volta, e quelle transazioni che sono circa 50.000 su 458.000, cancellare il 5% delle transazioni a caso toglie circa il 2,5% dei distinti, perché un indirizzo con due o più scambi non scompare. Sul singolo pool, nella prima mezz'ora, i conteggi stanno a 2, 3, 4. Lì una transazione mancante fa cambiare lato al filtro. Il segno del bias dipende da se le mancanze si concentrano sui contratti strani, che sono anche i rug.

**(c)** Tre conti, su tutti i pool candidati e non solo sui completi. Primo: ordina i pool per posizione nella camminata del collector, o per data di modifica del file, e confronta i quintili su giorno di lancio, chain, numero di swap e tasso di trappole. Secondo: sui pool risolti al 100%, cancella il 5% delle transazioni pre-ingresso, duecento volte, prima in modo uniforme e poi col profilo empirico delle mancanze (ora dal lancio, chiamata da contratto contro EOA, batch RPC fallito); misura la quota che attraversa la soglia 2/3 e di quanto si sposta \(\Delta\). Terzo: confronta \(\Delta\) sulla fascia di completezza [95%, 99%) con \(\Delta\) sui completi al 100%.

**(d)** Se ho ragione, i quintili della camminata differiscono per giorno di lancio o per tasso di trappole, e la cancellazione sposta \(\Delta\) di più di un punto. Se ho torto, i quintili coincidono e la cancellazione sposta \(\Delta\) di una frazione di punto: il criterio del 95% non è la sorgente dei 7 punti. Il campione resta comunque la coda dei pool che hai finito di leggere, non la popolazione dei memecoin nati.

Domani, in quest'ordine: la tabella dei 1.278 con la regola congelata, poi A contro B dentro i quintili di swap, con il taglio a 30 minuti. Se B riproduce A, la raccolta degli iniziatori ha misurato un fatto che il numero di swap già conteneva, e il risultato si chiude.
