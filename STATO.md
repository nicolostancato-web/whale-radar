================================================================================
LEGGIMI PRIMA — ISTRUZIONI PER L'AI CHE STA LEGGENDO QUESTO FILE
================================================================================

Ciao. Questo file e' il riassunto completo di un progetto di Nicolo'. Lui te lo
carica per parlarne CON LA VOCE. Non sa nulla di quello che c'e' scritto qui piu'
di quanto ci sia scritto: il progetto lo esegue un altro assistente (Claude Code).

IL TUO RUOLO:
Sei un quant senior, esperto di trading crypto, backtest e validazione statistica.
Parli in italiano, in modo diretto, senza gergo inutile. Se una cosa e' sbagliata
lo dici chiaramente. Nicolo' NON vuole incoraggiamenti: vuole che gli trovi gli
errori prima che gli costino soldi.

COME COMPORTARTI:
- Rispondi corto. E' una conversazione a voce, non un report scritto.
- Se ti fa una domanda vaga, chiedi cosa vuole sapere davvero.
- Se noti un errore di ragionamento nel progetto, dillo subito, anche se non
  te l'ha chiesto. E' il motivo per cui ti carica questo file.
- Non inventare numeri. Se una cosa non e' in questo file, di' che non la sai.
- Ricorda il contesto: founder solo, budget stretto, nessun euro ancora speso.
  Ogni consiglio che costa soldi va giustificato.

LE DOMANDE APERTE SU CUI SERVE IL TUO PARERE (sezione 11 in fondo).

SE PUOI LEGGERE GITHUB: questo file e' il PUNTO D'INGRESSO, tienilo come mappa.
Il repo ha 25.000 file e 229 MB di dati grezzi: NON provare a leggerlo tutto.
Se vuoi approfondire, apri solo questi, in quest'ordine:
  DECISIONS.md        le decisioni prese e perche' (append-only)
  ISPEZIONE.md        stato di salute della macchina, aggiornato ogni ora
  COSTO_MODELLO.md    il costo vero di entrare e uscire
  CREATOR_GATE.md     la pista del creator — CHIUSA il 4/9, tenuta come storico
  agents/metro.py     il metro con cui si giudica tutto (leggi i commenti)
Tutto il resto sono dati grezzi o agenti: ignorali salvo richiesta esplicita.
Questo file viene riscritto dal sistema: se la data in cima e' vecchia di piu'
di un giorno, dillo a Nicolo'.

GLOSSARIO VELOCE (per capire il resto del file):
  EDGE       = vantaggio statistico vero, non fortuna
  BACKTEST   = provare una strategia sui dati del passato
  HOLDOUT    = fetta di dati messa da parte e MAI guardata, serve a non barare
  MEMECOIN   = crypto senza prodotto, pura speculazione
  HONEYPOT   = token che puoi comprare ma NON vendere. Truffa.
  RUG        = quando il creatore ritira i soldi e il token va a zero
  SLIPPAGE   = quanto perdi fra il prezzo che vedi e quello che ottieni
  POOL       = la riserva di liquidita' dove avviene lo scambio
  CREATOR    = chi ha creato il token (spesso e' anche chi truffa)
  LORDO      = prima dei costi. NETTO = dopo i costi.

================================================================================
STATO PROGETTO — WHALE RADAR
Aggiornato: 2026-09-04 11:30
Comando per aggiornare questo file: scrivi "gpt" in chat
================================================================================

--------------------------------------------------------------------------------
1. COS'E' IL PROGETTO (in una frase)
--------------------------------------------------------------------------------
Un sistema autonomo che cerca un vantaggio statistico ("edge") sui memecoin,
gira da solo su GitHub Actions, costa ZERO EURO, e accumula un proprio database.
Obiettivo: trovare una percentuale positiva PROVATA prima di mettere un euro.

Repo: github.com/nicolostancato-web/whale-radar (PUBBLICO — mai segreti dentro)
Credenziali: ~/Documents/b2b-finder-credentials.txt (mai in chat, mai nel codice)

--------------------------------------------------------------------------------
2. LA STRUTTURA A TRE LOOP (nomenclatura decisa da Nicolo')
--------------------------------------------------------------------------------
LOOP 0 = ISPEZIONE   -> non si ferma mai. Controlla che ogni agente lavori.
LOOP 1 = PERCENTUALE -> uno per chain. Cerca il vantaggio. E' dove siamo ora.
LOOP 2 = DEMO LIVE   -> uno per chain. TUTTI FERMI. Si apre solo se LOOP 1
                        e' positivo in modo robusto.

Chain seguite: Solana, Base, BSC, Robinhood.

--------------------------------------------------------------------------------
3. DOVE SIAMO OGGI (3 settembre 2026)
--------------------------------------------------------------------------------
STATO MACCHINA: verde. Il motore gira, l'ispezione non trova guasti.
STATO EDGE:     NON TROVATO. Nessuna strategia confermata, NESSUNA PISTA VIVA.
                Quattro provate, quattro chiuse (dettaglio in sezione 6).

Numeri del database (crescono da soli):
  - 2.279 token con creator identificato
  - 212 misure REALI del costo di uscita (su Jupiter, gratis)
  - 81 token marcati come "trappole" (non si esce)
  - fascia di validazione (dati mai visti): nata il 31/08, ha pochi giorni

--------------------------------------------------------------------------------
4. LA COSA PIU' IMPORTANTE SUCCESSA (2-3 settembre)
--------------------------------------------------------------------------------
Abbiamo scoperto che GIUDICAVAMO TUTTO CON UN METRO SBAGLIATO.

Il backtest assumeva un costo di uscita del 33% (mai misurato). Quel numero
diceva che un token doveva salire del 50% solo per pareggiare. Con quel metro
avevamo dichiarato morte tutte e quattro le chain.

Poi l'abbiamo MISURATO davvero, su 212 token: il costo vero e' il 4%.
Otto volte piu' basso.

DECISIONE PRESA (approvata da Nicolo' il 3/9):
  Il costo misurato diventa il metro primario. Il vecchio 33% resta come
  "stress test", cioe' scenario pessimistico. Scritto in DECISIONS.md.
  Un solo posto nel codice: agents/metro.py

EFFETTO (stesso codice, stessi dati, cambia solo il metro):
  robinhood: da -20,9%  a  +3,5%   <-- CAMBIA SEGNO
  base:      da -27,2%  a  -11,1%
  solana:    -31%       (invariato)
  bsc:       -31%       a  -33,3%

ATTENZIONE — quel +3,5% NON E' UN EDGE:
  E' la migliore di 39 configurazioni provate. Con 39 tentativi il rumore
  da selezione atteso e' +9-14 punti. Quindi +3,5% e' compatibile con un
  vantaggio VERO NEGATIVO. Vale zero finche' non passa dall'holdout sigillato.

--------------------------------------------------------------------------------
5. L'AUDIT ESTERNO (Fable 5.1, 3 settembre)
--------------------------------------------------------------------------------
Abbiamo fatto attaccare la decisione sui costi da un modello piu' potente.
Verdetto: "giusto misurare, applicato in modo ingenuo". Quattro correzioni:

  [FATTO] 1. Gambe separate. Non dividere il costo a meta' fra entrata e
             uscita: misurarle. A $25 -> acquisto 2,76%, vendita 1,07%
             (l'opposto di quello che avevamo dedotto).

  [FATTO] 2. Uscita "in fuga". Lo stop scatta quando tutti vendono e il pool
             si prosciuga: li' il costo e' ~3 volte quello misurato in calma.
             Misurare il costo di uscire NON e' misurare il costo di uscire
             QUANDO VUOI USCIRE TU.

  [FATTO] 3. Trappole a -100%. Un honeypot tiene il prezzo su: il backtest
             vedeva uno stop a -40% e registrava -40%, quando la realta' e'
             -100%. Ora forzato, ma SOLO se la serie non lo mostra gia'
             (niente doppio conteggio).

  [DA FARE] 4. Costo come FUNZIONE della liquidita' al momento dell'uscita,
             invece del moltiplicatore fisso x3. Curva calibrata sui nostri
             dati storici. E' l'ultima cosa che separa il metro da qualcosa
             di cui fidarsi davvero.

--------------------------------------------------------------------------------
6. LE PISTE PROVATE E COME SONO FINITE
--------------------------------------------------------------------------------
ATTENZIONE: al 4 settembre NON ABBIAMO NESSUNA PISTA VIVA. Quattro provate,
quattro chiuse. Questo e' il dato piu' importante del file.

CHIUSA  Copy-trading ("ha azzeccato 2 token = e' bravo")
        Su Solana rende -46% LORDO, peggio che comprare a caso.
        Un wallet che indovina 2 volte su decine di migliaia e' fortuna.

CHIUSA  Flusso di capitale "indipendente"
        Sembrava +4,4%. Il controllo all'indietro ha mostrato +307% PRIMA del
        segnale: arrivavamo a festa gia' cominciata. Tolto il momentum: +0,1%.

CHIUSA  Reputazione del creator ("un grafico non causa un rug, una persona si")
        Il 3/9 sembrava fortissima: 91% di disastri fra i creator marchiati
        contro 57% fra i puliti. 33 punti.
        Il 4/9, con i dati cresciuti (840 puliti contro 73 marchiati): 8 punti.
        Il criterio di morte era stato scritto PRIMA. Chiusa.
        NON era una pista sbagliata: era un campione piccolo.

CHIUSA  Secondo stadio (cosa comprare fra i sopravvissuti)
        Quattro candidati: accelerazione del volume, ampiezza dei compratori,
        squilibrio compra/vendi, facce nuove. Tre mostravano +70% di MEDIA con
        MEDIANA +0,0% (pochi mostri, caso tipico a zero = lotteria), il quarto
        e' risultato momentum al controllo all'indietro.

Due volte in tre giorni un numero forte si e' sciolto appena i dati sono
cresciuti. Non e' sfortuna: e' quello che succede quando smetti di illuderti.

7. GUASTI TROVATI E RIPARATI (2-3 settembre)
--------------------------------------------------------------------------------
- META' DATABASE INSERVIBILE: prezzi salvati per "pool", sicurezza per "token",
  e indirizzi scritti con maiuscole da una parte e minuscole dall'altra.
  Su BSC si agganciavano ZERO token su 265. Riparato.

- 6 AGENTI CANCELLATI DAL MOTORE (errore mio, Claude): avevo pubblicato
  partendo da una copia vecchia del repo. Guardiano credenziali, CFO, memoria,
  proposte, segretario, ispezione: non erano rotti, NON VENIVANO PIU' CHIAMATI.
  Ripristinati. Ora LOOP 0 controlla anche la LISTA DEI CONVOCATI.

- TASSAMETRO CHE GIRAVA A VUOTO: rimisurava sempre gli stessi 24 token.
  Un contatore che non sale non e' sempre un motore fermo. Riparato:
  ora ruota e ha superato le 200 misure.

- BIAS DEI SOPRAVVISSUTI: il cancello dei creator trovava l'1% di disastri
  mentre la mortalita' ne misura il 12-24%. I token spariti senza lasciare
  un prezzo non entravano nel conto. Riparato.

- IL GC CANCELLAVA I DATI CHE SERVONO: potava i token senza prezzo proprio
  mentre il cancello li usa come "caso peggiore". Ora lascia una "lapide"
  (traccia di cosa ha potato) e l'analisi li esclude invece di contarli morti.

--------------------------------------------------------------------------------
8. IL METODO (quello che vale piu' dei risultati)
--------------------------------------------------------------------------------
Due segnali positivi sono morti in due giorni, per lo stesso motivo:
sembravano funzionare finche' non li abbiamo confrontati con la cosa giusta.

Regole ora dentro la macchina:
  - CONFRONTO APPAIATO: non "ha guadagnato?", ma "ha guadagnato piu' di quello
    che potevi comprare comunque, a parita' di eta' e liquidita'?"
  - PLACEBO ALL'INDIETRO: se il segnale "spiega" anche il PASSATO, non sta
    prevedendo niente. E' cosi' che e' morto il flusso dei cluster.
  - ORIZZONTI FISSATI PRIMA di guardare i dati (5m/30m/2h/6h/24h)
  - CRITERIO DI MORTE scritto PRIMA di vedere i numeri
  - Quando i dati non bastano, l'agente scrive "NON ANCORA GIUDICABILE"
    invece di inventare una risposta
  - Le decisioni vivono in DECISIONS.md, non nella chat

--------------------------------------------------------------------------------
9. COSA SI FA ADESSO
--------------------------------------------------------------------------------
1. Finire la correzione 4 (costo funzione della liquidita' all'uscita)
2. Far girare il GIUDICE su Robinhood con il metro nuovo, sulla fascia
   MAI VISTA. Una sola lettura. Serve t-stat >= 2 per crederci.
3. Continuare ad accumulare: servono ~7 giorni di fascia di validazione
   perche' i test rigorosi diano un verdetto vero.

COSA NON SI FA:
  - Niente LOOP 2 / soldi veri. Il cancello evita disastri ma non genera
    rendimento: manca il secondo stadio.
  - Niente spese. Il CT Signal Scout (momentum su X) e' l'idea migliore
    vista di recente, ma serve X Premium o un VPS. Non si spende un euro
    finche' LOOP 1 non trova una percentuale positiva.
  - Niente piste nuove finche' il metro non e' finito.

--------------------------------------------------------------------------------
10. FILE IMPORTANTI NEL REPO
--------------------------------------------------------------------------------
DECISIONS.md          registro decisioni, append-only, mai cancellare
ISPEZIONE.md          LOOP 0: il team sta lavorando?
COSTO_MODELLO.md      quanto costa DAVVERO entrare e uscire
CREATOR_GATE.md       pista CHIUSA il 4/9 (33 punti -> 8 al crescere dei dati)
WALLET_SKILL.md       l'ultimo test sui wallet
FLUSSO_CLUSTER.md     il segnale morto per momentum
agents/metro.py       IL METRO: un posto solo per il costo
agents/controlli.py   confronti appaiati, placebo, cluster
agents/trappole.py    i token da cui non si esce

Fuori dal repo:
~/n8n builder/whale-radar/CONSULENZA_WALLET_TRACKING_2026-09-02.md
~/n8n builder/LEARNINGS.md  (sezione 9 = video "how to find crypto with AI")

--------------------------------------------------------------------------------
11. DOMANDE APERTE — SU QUESTE SERVE IL PARERE DI CHI LEGGE
--------------------------------------------------------------------------------
Se sei un'AI a cui Nicolo' ha caricato questo file, queste sono le domande vere.
Rispondi a queste anche se lui te ne fa altre, se pensi che contino di piu'.

D0. LA DOMANDA PIU' URGENTE (4/9): STIAMO SCAVANDO NEL POSTO SBAGLIATO?
    Abbiamo chiuso QUATTRO piste su quattro. La macchina che le giudica ora e'
    severa e onesta: costi misurati, controlli appaiati, placebo all'indietro,
    criteri di stop scritti prima. Il metodo funziona — quello che non troviamo
    e' il segnale.
    Con la scadenza del 3 ottobre e nessuna pista viva: continuiamo a cercare
    qui, o il dato vero e' che questo mercato non offre un edge sfruttabile
    con il nostro approccio? Se pensi la seconda, dillo chiaramente.

D1. IL PROGETTO HA SENSO?
    Con un pareggio a 1,16x, il 9% dei token che sono trappole, e tre chain su
    quattro a -30%, esiste davvero una strategia sistematica positiva sui
    memecoin per chi mette 25-100 dollari a posizione? O il banco ha gia' vinto
    e la mossa razionale e' cambiare mercato?

D2. IL +3,5% DI ROBINHOOD.
    E' la migliore di 39 configurazioni. Che soglia dovremmo pretendere prima
    di crederci? E quanti trade servono per una conclusione onesta?

D3. IL CANCELLO DEI CREATOR.
    Funziona su Base (91% contro 57%) ma non su BSC (85% contro 85%).
    Un filtro che funziona su una chain sola e' un segnale o e' rumore?
    E come si costruisce un "secondo stadio" che generi rendimento, dato che
    un filtro anti-truffa da solo non fa guadagnare?

D4. IL COSTO DELLA FUGA.
    Stiamo assumendo che uscire in stop costi 3 volte piu' che uscire con calma
    (perche' il pool si prosciuga quando tutti scappano). Quel 3x e'
    un'assunzione. Come lo misureresti davvero con dati gratuiti?

D5. CI STIAMO PERDENDO QUALCOSA?
    Abbiamo: candele al minuto, ogni trade con wallet e importo, dati honeypot,
    grafo dei creator, costi di uscita misurati. Che domanda NON ci stiamo
    facendo e dovremmo farci?

--------------------------------------------------------------------------------
12. COME RIPRENDERE SE TUTTO SI PERDE
--------------------------------------------------------------------------------
Il codice e i dati sono su GitHub, non sul Mac. Se il computer si rompe:
  1. apri il repo nicolostancato-web/whale-radar
  2. leggi DECISIONS.md (le decisioni) e ISPEZIONE.md (lo stato di salute)
  3. il motore riparte da solo ogni 6 ore, non serve fare niente

================================================================================
FINE — per aggiornare: scrivi "gpt"
================================================================================
