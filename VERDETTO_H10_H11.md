# Verdetto H10 e H11 — due morti, trentasei punti recuperati

**29/09. Regole fissate in IPOTESI_H10.md prima di guardare. Nessuna e' stata toccata dopo.**

## Esito

**Muoiono tutte e due.** Serviva il decimo migliore sopra zero su tutte e due le chain:

| | robinhood | base |
|---|---|---|
| H10 — pattern di H9, finestra lunga | −69,2% | −39,0% |
| H11 — stesso, ma imparando sull'incasso | **−17,1%** | **−20,7%** |
| serviva | sopra 0% | sopra 0% |

## Cosa hanno insegnato, che vale piu' della loro morte

### 1. Il bersaglio sbagliato sceglieva il veleno (52 punti)

H10 addestrava il modello a prevedere «questo raddoppiera' di prezzo». Il suo decimo migliore
incassava **−69% contro un fondale di −27%**: peggio del caso, e non per poco.

Il motivo e' che i pool che raddoppiano di prezzo sono i piu' **sottili** — schizzano proprio
perche' dentro non c'e' nessuno. Cercando il prezzo che sale, il modello cercava con precisione
i pool da cui non si esce.

Cambiando una riga — impara su quanto si **incassa** vendendo $500 veri — lo stesso modello,
sugli stessi pool, passa da −69,2% a −17,1%. **Cinquantadue punti in una riga.**

> **Un modello impara a cercare esattamente quello che gli chiedi di prevedere. Se gli chiedi
> il prezzo, ti trova i pool illiquidi con la massima efficienza.**

### 2. La finestra che nessuno aveva scelto (14 punti)

Per dieci ipotesi si e' misurato tutto tenendo **sei ore**, perche' cosi' era scritto nella
corsia. Sugli stessi identici pool, tenendo una settimana: fondale da −37,5% a −23,0%,
trappole dal 37,0% al 21,4%.

Non era una scelta sbagliata: era una scelta **mai fatta**, ereditata e mai guardata.

### 3. Un'etichetta rovesciata (nessun punto, ma per un pelo)

Avevo stampato i cinque gruppi con scritto «dal peggiore al migliore». Erano ordinati al
contrario. Per qualche minuto ho letto un ordinamento sano come se fosse rovesciato.

> **Un asse etichettato male non e' un dettaglio di stampa: e' un risultato sbagliato.**

## Dove siamo, in un numero

Il fondale di stamattina, vendendo $500 veri, era **−53%**. La combinazione trovata oggi —
finestra lunga, bersaglio sull'incasso, decimo migliore — vale **−17%**.

**Trentasei punti recuperati in un giorno. E siamo ancora sotto zero.**

Sotto zero vuol dire: non si rischia un euro. Ma per la prima volta la distanza dalla pari e'
di diciassette punti e non di cinquantatre', e i due punti guadagnati sono **strutturali** —
riguardano come si misura e cosa si chiede al modello, non una fortuna del campione.
