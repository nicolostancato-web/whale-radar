# Gli insider esistono: +16/+20 punti che sopravvivono a due attacchi

*1 ottobre 2026 · 22.424 pool su robinhood e 15.128 su base, con i compratori VERI*

## Da dove nasce

Nicolò, stasera: «sono ancora convinto che ci sia della gente che faccia molti soldi a livello
di insider. Partiamo dalla 3 e andiamo in insider mode.»

Il materiale c'era già e **non è costata una chiamata**: `iniziatori.json.gz` tiene 624.340
transazioni su robinhood e 336.014 su base con il nome di **chi ha firmato davvero**. Serviva
solo incrociarlo con i file degli scambi, pool per pool. Lo fa `agents/insider.py`.

**E dentro c'era una cosa più grave di quella che cercavo.** Quel file esiste dal 25/09 perché
il campo che usavamo come «chi ha fatto lo scambio» registra nell'81% dei casi il **router**, non
la persona — un solo indirizzo faceva il 42,6% degli scambi. Quindi cinque dei nostri attributi
(compratori distinti, portafogli nuovi, scambi per portafoglio, concentrazione, peso del primo)
misurano **porte, non gente**. Il file di correzione non è mai stato unito all'insieme: la
ricerca ha girato sei giorni sugli attributi sbagliati, compresa la strategia bocciata stasera.

## Il primo risultato, e perché non andava creduto

Ordinando le monete per **come erano andate le monete precedenti dei loro primi compratori**:

| passato dei compratori | robinhood | base |
|---|---|---|
| il quinto peggiore | −44,8% | −60,8% |
| il quinto migliore | **+16,1%** | **+7,5%** |

Monotono su tutti e cinque i gradini, su entrambe le chain, positivo in assoluto. Mai visto
prima in questo progetto — che è precisamente il motivo per attaccarlo.

## Attacco 1: il passato deve essere CHIUSO

Se la moneta precedente è di dieci minuti prima, **il suo esito non lo sapevamo ancora**. Usarlo
è informazione dal futuro. Pretendendo che il passato sia chiuso da almeno 6 ore:

| | 0h (sbagliato) | 6h | 24h |
|---|---|---|---|
| robinhood, quinto migliore | +16,1% | **−0,3%** | −2,8% |
| base, quinto migliore | +7,5% | **−3,7%** | −4,8% |
| robinhood, scarto | +61 punti | **+24** | +20 |
| base, scarto | +68 punti | **+44** | +42 |

**Il positivo era futuro.** Lo scarto invece sopravvive, e resta uguale fra 6 e 24 ore: stabile,
non un residuo che si consuma.

## Attacco 2: è la gente o è il momento?

Si rifà tutto usando la storia dei compratori di **un'altra moneta della stessa ora**. Se lo
scarto resta, non stiamo misurando le persone: stiamo misurando il momento.

| | scarto vero (6h) | con donatori della stessa ora | **attribuibile alle persone** |
|---|---|---|---|
| robinhood | +24 punti | +8 | **+16 punti** |
| base | +44 punti | +24 | **+20 punti** |

Una parte buona era il momento — su base più della metà. Ma **sedici e venti punti restano**, e
restano su due chain indipendenti.

## Il verdetto, in due frasi che vanno tenute insieme

**Gli insider esistono.** Il passato chiuso di chi compra predice la moneta successiva oltre le
condizioni di mercato, per sedici-venti punti, su entrambe le chain. È la prima cosa del
progetto che sopravvive a una prova costruita per ucciderla.

**Non si incassa ancora.** Anche il quinto migliore è negativo (−0,3% e −3,7%): è «perdere molto
meno», non guadagnare. È la trappola per cui esiste la seconda porta — il rendimento assoluto
sopra zero — scritta oggi stesso.

## Rimisurato il 2/10 con piu' copertura: si STRINGE

La mappa delle persone e' passata da 624.340 a 691.514 transazioni, e i pool coi compratori veri
da 8.222 a 21.791 su robinhood. Rifatta la stessa misura, con lo stesso criterio:

| | scarto vero (passato chiuso 6h) | di cui momento | **attribuibile alle persone** |
|---|---|---|---|
| robinhood | +24 punti | +6 | **+19** (era +16) |
| base | +60 punti | +41 | **+18** (era +20) |

**Le due chain convergono**: +19 e +18, misurate su popolazioni indipendenti. E su base la
progressione e' monotona su tutti e cinque i gradini: −64,0 → −53,1 → −33,4 → −16,1 → **−4,4**.

Questo e' il comportamento di un effetto vero: con piu' dati la stima si stringe invece di
sfumare. Resta un FILTRO — anche il quinto migliore e' negativo (−0,3% e −4,4%) — ma e' l'unico
risultato del progetto che migliora quando gli si danno piu' dati.

## Dove guardare adesso, e perché

Il senso di un insider è che **è in anticipo**. Noi entriamo al quinto scambio: se lui compra per
primo, al quinto scambio potremmo essere già tardi. Il segnale c'è, quindi la domanda non è più
*se* esiste un vantaggio ma **quando entrare perché diventi incassabile**.

Tre cose, in ordine:
1. **Entrare prima**, sulle sole monete i cui primi compratori hanno un passato chiuso buono:
   oggi non esiste un insieme costruito a un ingresso più precoce del quinto scambio.
2. **Alzare la copertura**: oggi conosciamo i compratori veri del 20% di robinhood e del 26% di
   base. Il resto è pronto da risolvere, e costa chiamate alla catena, non denaro nuovo.
3. **Risalire a chi finanzia**: un insider cambia portafoglio, ma chi lo finanzia spesso no. È
   il livello sopra, e serve per non perderlo quando cambia indirizzo.

E una cosa da fare in ogni caso, indipendente dal vantaggio: **unire i compratori veri
all'insieme**, perché cinque attributi su trentaquattro oggi misurano router.
