"""Costruisce l'insieme di dati ricco: una riga per pool, 33 caratteristiche + l'esito.

Sostituisce le cinque misure grezze del cercatore. Tutto e' calcolato a `ORE_ATTESA` dal primo
scambio osservato, usando SOLO cio' che si sapeva allora.
"""
import gzip
import json
import os
import sys
import time
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caratteristiche as K                                   # noqa: E402
import verso as V                                             # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
CAMPIONE = int(os.environ.get("CAMPIONE", 1))
ORE_ATTESA = float(os.environ.get("ORE_ATTESA", 2))
ORIZZONTE_ORE = float(os.environ.get("ORIZZONTE_ORE", 6))
ENTRATA_SCAMBIO = int(os.environ.get("ENTRATA_SCAMBIO", 0))
PREZZO_MEDIANO = os.environ.get("PREZZO_INGRESSO", "") == "mediano"  # 0 = si usa il tempo
CAMMINO_PUNTI = 80          # quanti punti del cammino si tengono per pool
MIN_VITA = int(os.environ.get("MIN_VITA", 10))
COSTO = float(os.environ.get("COSTO_GIRO", 0.018))
RITARDO_MINIMO = int(os.environ.get("RITARDO_MINIMO_S", 60))   # l'esito non puo' essere simultaneo
MIN_DOPO = int(os.environ.get("MIN_DOPO", 5))       # meno di cosi' e il prezzo non e' misurabile
MIN_VENDITE = int(os.environ.get("MIN_VENDITE", 5))  # meno di cosi' e l'uscita non e' misurabile


# IL PREZZO NON ESISTE SENZA SAPERE DOV'E' IL MEMECOIN (25/09). Qui c'era `a0/a1` fisso, che e'
# valuta-per-memecoin solo dove la valuta e' token0 e l'inverso altrove — e `a0 > 0` per «vendita»,
# che nel 73% dei pool e' un ACQUISTO. Vedi `agents/verso.py` per la misura e il perche'.
# Ora il verso arriva per pool e le due funzioni stanno li'.


def _persone():
    """La mappa hash della transazione -> chi ha FIRMATO davvero.

    Vuota se il file non c'e': in quel caso gli attributi `pers_*` semplicemente NON compaiono,
    invece di comparire finti a zero. Un attributo assente si vede; uno finto a zero no — ed e'
    lo stesso errore del segnaposto 1.0 che ha prodotto il falso titolo del 30/09.
    """
    p = f"data/multichain/{os.environ.get('CHAIN', 'robinhood')}/iniziatori.json.gz"
    if not os.path.exists(p):
        print(f"INSIEME | manca {p}: gli attributi sulle PERSONE non verranno calcolati "
              f"(restano quelli sui router, che misurano porte)", flush=True)
        return {}
    try:
        d = json.load(gzip.open(p, "rt")).get("da", {})
    except Exception as e:
        print(f"INSIEME | non riesco a leggere {p}: {type(e).__name__}", flush=True)
        return {}
    print(f"INSIEME | {len(d):,} transazioni con la persona che ha firmato davvero", flush=True)
    return {k.lower(): v for k, v in d.items()}


PERSONE = _persone()

# QUANTI SCAMBI SERVONO PERCHE' GLI ATTRIBUTI SIGNIFICHINO QUALCOSA (2/10).
# Cinque, per gli attributi di microstruttura. Ma per entrare PRIMA — che e' il punto dopo aver
# trovato che il segnale degli insider esiste — serve poter costruire un insieme a due scambi,
# con il solo sottoinsieme di attributi che a due scambi ha senso (vedi PRECOCI in
# agents/caratteristiche.py). Chi lo abbassa sa cosa perde: lo dichiara qui, non lo scopre dopo.
MIN_SCAMBI = int(os.environ.get("MIN_SCAMBI", 5))


def costruisci():
    righe = []
    verso = V.carica(CHAIN)
    senza_verso = [0]
    import collections as _c
    scartati = _c.Counter()
    for sub in ("storico", "vivo"):
        d = f"data/multichain/{CHAIN}/{sub}"
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if CAMPIONE > 1 and zlib.crc32(fn.encode()) % CAMPIONE:
                continue
            try:
                rr = [json.loads(l) for l in gzip.open(os.path.join(d, fn), "rt") if l.strip()]
            except Exception:
                continue
            rr = [x for x in rr if x.get("ts") and x.get("a0") and x.get("a1") and x.get("w")]
            # ESCLUSIONE SILENZIOSA, E GUARDA IL FUTURO (5/10, trovata da Astra).
            # Questa riga scartava i pool con meno di MIN_VITA scambi SENZA CONTARLI, in un
            # file che dieci righe piu' sotto scrive «OGNI ESCLUSIONE VA CONTATA».
            # Ma il difetto grosso e' un altro, e l'ha nominato Astra: **alla nascita non si sa
            # quali pool arriveranno a dieci scambi**. Quelli che muoiono prima sono
            # esattamente le PERDITE di una strategia sulle monete appena nate, e li stavamo
            # togliendo dall'universo. Sono il 43% su base e il 76% su robinhood.
            # Un universo definito con informazione successiva descrive un mondo filtrato:
            # ogni misura fatta dentro parla di quel mondo, non del mercato.
            # Ora si conta, e con MIN_VITA=1 l'universo e' onesto (variante «_onesto»).
            if len(rr) < MIN_VITA:
                scartati[f"meno di {MIN_VITA} scambi in tutta la vita (soglia MIN_VITA: "
                         f"GUARDA IL FUTURO, alla nascita non si sa chi ci arrivera')"] += 1
                continue
            rr.sort(key=lambda x: x["ts"])
            meme_t0 = verso.get(fn.split(".")[0].lower())
            if meme_t0 is None:
                # NON SI TIRA A INDOVINARE: senza sapere quale dei due token e' il memecoin, il
                # prezzo e' l'inverso di se stesso e le vendite sono acquisti. Meglio un pool in
                # meno che una riga sbagliata in piu'.
                senza_verso[0] += 1
                continue
            prezzo = lambda x: V.prezzo(x, meme_t0)
            # L'ASSE GIUSTO PER «CHI ARRIVA PRIMA» E' IL NUMERO DI SCAMBI, NON I MINUTI (29/09).
            # Coi minuti, l'entrata a zero dava zero pool: l'ingresso cadeva sul primo scambio e
            # sotto il sesto non si puo' scendere, perche' le caratteristiche del pool si calcolano
            # sulla storia PRECEDENTE all'acquisto. Ma il tempo e' comunque una misura povera qui:
            # un pool fa cento scambi in un minuto e un altro tre in un'ora, e «tre minuti» vuol
            # dire due cose diverse. Con ENTRATA_SCAMBIO si compra all'N-esimo scambio, che e'
            # la domanda vera: quanti sono passati prima di me?
            if ENTRATA_SCAMBIO:
                i = ENTRATA_SCAMBIO if ENTRATA_SCAMBIO < len(rr) else None
            else:
                lim = rr[0]["ts"] + ORE_ATTESA * 3600
                i = None
                for k, x in enumerate(rr):
                    if x["ts"] >= lim:
                        i = k
                        break
            # OGNI ESCLUSIONE VA CONTATA (30/09). Qui si scartavano in silenzio i pool con
            # troppi pochi scambi — e sono i fallimenti totali. Escluderli senza dirlo e'
            # sopravvivenza travestita: il risultato migliora e nessuno sa di quanto.
            if i is None:
                scartati["nessuno scambio al momento d'ingresso"] += 1
                continue
            # LA QUARTA SOGLIA, E UN'ETICHETTA CHE MENTIVA (2/10). Qui c'era `if i < 5` con il
            # contatore «meno di 6 scambi in tutta la vita». Non e' quello che misura: scarta i
            # pool il cui MOMENTO D'INGRESSO cade prima del quinto scambio. Con ingresso 2
            # scartava TUTTO — 47.617 pool — e il log diceva che il problema erano i dati.
            # Ho cercato un problema di dati per due giri per colpa di quella etichetta: e' la
            # lezione del 28/09 scritta in pubblica.sh, «le diagnosi imprecise costano piu' del
            # difetto che descrivono», ripresentata altrove.
            # La soglia ora e' la stessa dichiarata per gli attributi: chi abbassa MIN_SCAMBI sa
            # cosa perde, e il contatore dice la verita'.
            if i < MIN_SCAMBI:
                scartati[f"ingresso prima del {MIN_SCAMBI}o scambio (soglia MIN_SCAMBI)"] += 1
                continue
            # IL PREZZO D'INGRESSO E' UN SINGOLO SCAMBIO, E QUESTO PUO' MENTIRE (29/09).
            # In un mercato automatico una VENDITA lascia il prezzo piu' basso e un ACQUISTO piu'
            # alto. Se l'ingresso cade su una vendita, il prezzo di riferimento e' depresso e il
            # ritorno successivo e' in parte solo il rientro da quell'impatto: un guadagno finto.
            # Con PREZZO_INGRESSO=mediano si usa la mediana degli ultimi cinque prezzi, che non
            # dipende da quale lato fosse l'ultimo scambio. Se il vantaggio sparisce, era questo.
            if PREZZO_MEDIANO:
                vicini = [prezzo(x) for x in rr[max(0, i - 4):i + 1]]
                vicini = sorted(v for v in vicini if v)
                p0 = vicini[len(vicini) // 2] if vicini else None
            else:
                p0 = prezzo(rr[i])
            if not p0:
                continue
            t0 = rr[i]["ts"]
            c = K.estrai(rr[:i + 1], prezzo, PERSONE, MIN_SCAMBI, meme_t0=meme_t0)
            if not c:
                continue
            # IL «DOPO» DEVE ESSERE DAVVERO DOPO (23/09 notte). Prendendo rr[i+1:] finivano
            # nell'esito anche gli scambi con lo STESSO identico secondo dell'ingresso: per circa
            # un pool su cinque il «dopo» era il «durante», e l'esito si misurava su prezzi
            # simultanei all'entrata. Ora serve almeno RITARDO_MINIMO secondi di distacco.
            dopo = [x for x in rr[i + 1:]
                    if t0 + RITARDO_MINIMO <= x["ts"] <= t0 + ORIZZONTE_ORE * 3600]
            pp = [prezzo(x) for x in dopo]
            pp = [x for x in pp if x]
            if len(pp) < MIN_DOPO:
                # NON si butta: chi entra e non trova piu' mercato ha perso, e toglierlo sarebbe
                # la selezione che premia i casi migliori (rilievo di Astra, 23/09).
                rend = -0.98
            else:
                # IL PREZZO MEDIANO DELLA FINESTRA, NON L'ULTIMO (23/09 notte).
                # Misurare sull'ULTIMO scambio ha prodotto la piu' grande illusione della giornata:
                # un modello a 33 caratteristiche dava 0,92 di capacita' predittiva e un decimo
                # migliore al 92% con mediana +66%. Rifatto lo STESSO calcolo col prezzo mediano:
                # capacita' 0,60, decimo migliore 21%, mediana −2,5% e il 56% in perdita.
                # Il modello non prevedeva i guadagni: sceglieva i pool con POCHI scambi dopo
                # l'ingresso (mediana 8 contro 37), dove l'ultimo prezzo e' una singola stampa
                # ballerina. Un prezzo mediano non si lascia spostare da una stampa sola.
                # E' anche la vera ragione per cui la regola «11 compratori e 73 scambi» sembrava
                # buona: misurata su tutta la popolazione e con questo prezzo fa 0,5x, cioe' PEGGIO
                # di non fare niente — esattamente quello che aveva detto la prova sul futuro.
                pp.sort()
                rend = pp[len(pp) // 2] / p0 - 1
                if not (-0.99 < rend < 20):
                    continue
            # SI PUO' USCIRE DA QUESTO POOL? (24/09) Senza questo controllo la ricerca trova
            # sempre le stesse cose: pool dove un solo portafoglio compra a ripetizione lungo una
            # curva e NESSUNO vende mai. Misurato: l'86% di quei pool non ha una sola vendita nelle
            # 24 ore dopo l'ingresso, a fronte di 166 scambi. Il loro «+77%» e' aritmetica della
            # curva, non un guadagno: ci si entra e non si esce.
            # Non si SCARTANO — toglierli sarebbe una selezione che premia i casi buoni — ma si
            # registra il dato, cosi' ogni analisi puo' separare il vendibile dall'illusorio.
            # L'USCITA SI MISURA SUI PREZZI DI CHI HA VENDUTO (24/09, rilievo di Grok).
            # Il prezzo mediano di TUTTI gli scambi e' quanto gli ALTRI pagano per entrare, non
            # quanto io incasso per uscire. Misurato sullo stesso campione: con tutti i prezzi la
            # media e' −0,4%, con i soli prezzi di vendita e' **−22,9%**.
            # La differenza sta nella coda: il 26% dei pool che l'etichetta chiamava «vendibili»
            # (bastava UNA vendita in 24 ore) non ha abbastanza vendite per misurare un'uscita.
            # Chi non ha almeno MIN_VENDITE prezzi di vendita vale perdita totale: non e' un caso
            # da scartare, e' il caso peggiore.
            prezzi_vendita = []
            vend = 0
            # LA TAGLIA ACCANTO AL PREZZO (26/09). `_max_vendibile` diceva che QUALCUNO ha venduto a
            # 10x, non che ci stesse dentro una posizione. Su pool sottili quei prezzi sono spesso
            # polvere: e' la forma esatta dell'illusione che ci ha ingannati in agosto, quando un
            # paper da 323 mila euro si e' rivelato fatto di prezzi che non si potevano incassare.
            # Qui si registra QUANTA VALUTA e' passata sopra ogni soglia: un bersaglio vale solo se
            # a quel prezzo e' passato abbastanza da contenere un ordine vero.
            valuta_sopra = {2.0: 0.0, 5.0: 0.0, 10.0: 0.0}
            valuta_tot = 0.0
            # IL CAMMINO, NON SOLO IL PUNTO D'ARRIVO (29/09). Per dodici ipotesi abbiamo variato
            # SOLO quale pool comprare, mai QUANDO USCIRE: ogni misura era «compra e tieni fino
            # alla fine», cioe' resta dentro anche mentre il pool muore sotto gli occhi.
            # Una regola d'uscita non e' un trucco di selezione: usa quello che si sa IN QUEL
            # MOMENTO, non dopo. Ma per provarla serve il cammino, e nel dato non c'era.
            # Si salvano le vendite in ordine: ore dall'ingresso, prezzo rispetto all'ingresso,
            # valuta passata. Al massimo CAMMINO_PUNTI, prese a passo regolare per non gonfiare
            # il file: bastano a simulare un'uscita, non a rifare l'analisi da capo.
            cammino = []
            for x in dopo:
                if V.e_vendita(x, meme_t0):
                    vend += 1
                    v = prezzo(x)
                    if v:
                        prezzi_vendita.append(v)
                        q = V.valuta(x, meme_t0)
                        valuta_tot += q
                        cammino.append([round((x["ts"] - t0) / 3600, 3),
                                        round(v / p0, 6), q])
                        for s in valuta_sopra:
                            if v / p0 >= s:
                                valuta_sopra[s] += q
            # SI ACCORPA, NON SI SCARTA (29/09). La prima versione teneva un punto ogni N e
            # buttava gli altri: per una mediana va bene, per simulare un riempimento no — i
            # soldi scartati sono soldi che al momento di vendere non ci sarebbero piu'.
            # Accorpando, il prezzo diventa la media pesata per la valuta e la valuta si SOMMA:
            # il totale resta intero e il cammino resta leggibile.
            if len(cammino) > CAMMINO_PUNTI:
                passo = len(cammino) / CAMMINO_PUNTI
                gruppi = [[] for _ in range(CAMMINO_PUNTI)]
                for k, punto in enumerate(cammino):
                    gruppi[min(CAMMINO_PUNTI - 1, int(k / passo))].append(punto)
                accorpato = []
                for g in gruppi:
                    if not g:
                        continue
                    peso = sum(max(1e-12, x[2]) for x in g)
                    # LISTA, non tupla: la conversione in dollari piu' sotto scrive dentro il
                    # punto. Con le tuple sarebbe esplosa al primo pool con la valuta nota.
                    accorpato.append([g[0][0],
                                      round(sum(x[1] * max(1e-12, x[2]) for x in g) / peso, 6),
                                      sum(x[2] for x in g)])
                cammino = accorpato
            c["_cammino"] = cammino
            # LA CAPIENZA VA MISURATA PRIMA DI COMPRARE (26/09). Avevamo trentatre caratteristiche
            # e nessuna diceva quanti SOLDI erano passati: solo quanti scambi e quanti portafogli.
            # Il 26/09 ho trovato che i pool dove passano oltre 10.000$ rendono +24,9% — ma quel
            # volume e' misurato DOPO l'entrata, quindi e' guardare il futuro: e' la stessa cosa
            # che dire «i sopravvissuti sopravvivono».
            # Qui si registra la valuta passata nella finestra di OSSERVAZIONE, che a quel momento
            # si conosce. Solo con questa la domanda «la capienza si vede in anticipo?» ha una
            # risposta onesta.
            c["_valuta_prima"] = sum(V.valuta(x, meme_t0) for x in rr[:i + 1])
            # LA PROFONDITA', QUANDO C'E' (26/09). Da stanotte la raccolta tiene `liq` sui protocolli
            # V3 e V4 (il 91,5% degli scambi); prima la buttava. Qui si porta fino all'analisi, che
            # e' il passaggio dove oggi la catena si e' rotta tre volte: chi produce il dato lo
            # cambiava e chi lo scriveva non lo copiava, o chi lo scriveva lo salvava e chi lo
            # leggeva non lo cercava.
            # Resta None sui pool vecchi e su V2: **un campo assente e' meglio di uno finto a zero**,
            # perche' uno zero finto entra in una media e la sposta senza farsi vedere.
            liq = [float(x["liq"]) for x in rr[:i + 1] if x.get("liq")]
            # ATTENZIONE, DIFETTO NOTO (5/10): questo numero e' in UNITA' GREZZE del gettone,
            # non in dollari, e non e' diviso per i decimali. Misurato stanotte: i quinti
            # risultano «da 40.212.582.413.327.208$», che non e' una cifra — e mescolando
            # gettoni con decimali diversi anche l'ORDINAMENTO fra pool e' senza senso.
            # Chi lo usa come filtro sta filtrando sul nulla. E' la famiglia dei sedici
            # milioni di dollari del 2/10: un'unita' mai convertita che viaggia dentro un
            # campo dal nome innocente.
            # Da riparare dividendo per i decimali del lato valuta e moltiplicando per il
            # prezzo, come fa verso.valuta_lato(); finche' non e' fatto, NON si filtra su
            # questo campo. Copertura attuale comunque bassa: noto per il 4-5% delle pool.
            c["_liq_prima"] = sorted(liq)[len(liq) // 2] if liq else None
            c["_liq_copertura"] = round(len(liq) / max(1, i + 1), 3)
            c["_valuta_venduta"] = valuta_tot
            for s, q in valuta_sopra.items():
                c[f"_valuta_sopra_{int(s)}x"] = q
            c["_scambi_dopo"] = len(dopo)
            c["_vendite_dopo"] = vend
            if len(prezzi_vendita) >= MIN_VENDITE:
                prezzi_vendita.sort()
                u = prezzi_vendita[len(prezzi_vendita) // 2] / p0 - 1 - COSTO
                c["_uscita"] = u if -0.99 < u < 20 else -0.98
            else:
                c["_uscita"] = -0.98
            # IL DECRETO VA SEPARATO DALLA MISURA (25/09, rilievo di Grok verificato).
            # La regola «meno di cinque vendite vale -98%» non e' una misura: e' un'etichetta. E
            # pesa quasi tutto. Misurato sui pool giudicabili: il 42,4% (robinhood) e il 53,2%
            # (base) prende -98% per decreto, e vale -41,5 punti su -41,2 di portafoglio. Fra i
            # pool con un prezzo DAVVERO misurato, quelli sotto -90% sono lo 0,4% e su base ZERO.
            # Cioe': il numero che per giorni ho chiamato «tasso di trappole» era la frequenza di
            # una mia regola, non una proprieta' del mercato.
            # Il decreto puo' anche essere giusto — chi non trova compratori non esce davvero — ma
            # va potuto CONTARE a parte. Qui si registrano tutte e due le cose:
            #   `_uscita`          come prima, col decreto, per non cambiare sotto ai piedi i
            #                      numeri gia' pubblicati;
            #   `_uscita_min1`     la mediana delle vendite che ci sono, anche se sono una o due,
            #                      e None quando non ce n'e' NESSUNA (li' non c'e' uscita, punto).
            # Con `_vendite_dopo` accanto, ogni analisi puo' scegliere la soglia e dichiararla,
            # invece di ereditarne una nascosta.
            if prezzi_vendita:
                pv = sorted(prezzi_vendita)
                um = pv[len(pv) // 2] / p0 - 1 - COSTO
                c["_uscita_min1"] = um if -0.99 < um < 20 else -0.98
            else:
                c["_uscita_min1"] = None
            # IL MASSIMO INCASSABILE, NON IL MASSIMO SEGNATO (25/09). Serve alla sola domanda
            # rimasta aperta su questa direzione: se l'uscita mediana rende +0,9% sui pool sani,
            # esiste una coda che paga abbastanza da giustificare il 43% di trappole?
            # Ma il massimo del PREZZO e' un prezzo a cui qualcuno COMPRAVA, non uno a cui io
            # potevo vendere. Si prende il massimo dei soli prezzi di VENDITA: stesso metro
            # dell'uscita, cosi' i due numeri si possono confrontare senza trucchi.
            # Resta un limite superiore ottimistico — presuppone di aver venduto nel punto esatto —
            # e va letto come «il meglio che si poteva fare», non come un rendimento.
            if len(prezzi_vendita) >= MIN_VENDITE:
                mv = max(prezzi_vendita) / p0 - 1 - COSTO
                c["_max_vendibile"] = mv if mv < 20 else 20
            else:
                c["_max_vendibile"] = -0.98
            # L'USCITA PESATA PER IL DENARO — la taglia che entra nel calcolo (28/09).
            #
            # `_uscita` e' la mediana dei prezzi di vendita: conta ogni vendita uguale, che sia da
            # trenta dollari o da tremila. E' cosi' che un 10x fatto di polvere passa per un'uscita
            # vera — il difetto che ha ucciso H6b e che avevamo misurato ma non ancora USATO:
            # `_valuta_sopra_10x` aveva uno scrittore e zero lettori.
            #
            # Qui il prezzo si pesa per i SOLDI passati: e' il prezzo a cui e' uscita meta' della
            # valuta, non meta' delle stampe. Una vendita da tremila dollari conta cento volte una
            # da trenta, che e' esattamente il peso che ha nella realta'.
            #
            # PERCHE' NON SOSTITUISCO `_uscita`, che sarebbe la cosa ovvia: **H7 e' gia' in corso e
            # le sue condizioni di morte sono scritte su `_uscita`.** Cambiare il metro adesso
            # invaliderebbe una prova registrata prima di vedere i dati — cioe' distruggerei la sola
            # cosa che rende quella prova credibile. Il metro nuovo affianca il vecchio e servira'
            # dall'ipotesi successiva.
            if prezzi_vendita:
                coppie = []
                for x in dopo:
                    if V.e_vendita(x, meme_t0):
                        pr, q = prezzo(x), V.valuta(x, meme_t0)
                        if pr and q > 0:
                            coppie.append((pr, q))
                if coppie:
                    coppie.sort()
                    meta = sum(q for _, q in coppie) / 2
                    corso = 0.0
                    for pr, q in coppie:
                        corso += q
                        if corso >= meta:
                            up = pr / p0 - 1 - COSTO
                            c["_uscita_pesata"] = up if -0.99 < up < 20 else -0.98
                            break
                else:
                    c["_uscita_pesata"] = -0.98
            else:
                c["_uscita_pesata"] = -0.98
            # SI SIMULA DI VENDERE DAVVERO (29/09) — la sostituzione della convenzione.
            #
            # Il numero su cui abbiamo chiuso questa direzione dipendeva quasi tutto dalla regola
            # «meno di cinque vendite = hai perso tutto». Misurato il 28/09: quella regola vale
            # CINQUANTACINQUE punti di fondale. Non e' una misura, e' una scelta — e una scelta che
            # decide il verdetto e' il posto peggiore dove lasciare un'assunzione.
            #
            # Qui non si sceglie una soglia: si SIMULA. Si prende il flusso delle vendite in ordine
            # di tempo e si prova a piazzarci dentro una posizione da N dollari, prendendo i prezzi
            # come arrivano. Quello che non si riesce a vendere entro l'orizzonte vale zero.
            # E' la domanda vera — «con N dollari, quanto avrei ripreso?» — e la risposta e' diversa
            # per ogni N: un mercato che regge cento dollari puo' non reggerne duemila.
            #
            # Si registra solo dove la valuta e' nota (decimali verificati sulla catena): altrimenti
            # i dollari sarebbero inventati, e un numero inventato e' peggio di un numero assente.
            val = V.valuta_del_pool(CHAIN, fn.split(".")[0])
            if val:
                # IL CAMMINO PARLA IN DOLLARI (29/09): senza conversione, una soglia da $500
                # sarebbe in unita' di token, cioe' un numero inventato. Dove la valuta non e'
                # nota il cammino resta in unita' grezze e chi legge lo deve sapere.
                _dec, _pusd = val
                for punto in c.get("_cammino", []):
                    punto[2] = round(punto[2] / 10 ** _dec * _pusd, 2)
                c["_cammino_in_dollari"] = True
            else:
                c["_cammino_in_dollari"] = False
            if val and prezzi_vendita:
                dec, prezzo_usd = val
                flusso = []                       # (prezzo, valuta in dollari), in ordine di tempo
                for x in dopo:
                    if V.e_vendita(x, meme_t0):
                        pr = prezzo(x)
                        q = V.valuta(x, meme_t0) / 10 ** dec * prezzo_usd
                        if pr and q > 0:
                            flusso.append((pr, q))
                # DOVE SI FERMA IL VANTAGGIO DELLA TAGLIA (29/09). L'ordine $100 < $500 < $2000
                # regge su otto epoche su otto: piu' piccolo e' sempre meglio. Ma se anche a
                # venticinque dollari il fondale resta negativo, il mercato e' a somma negativa
                # e nessuna taglia lo salva. E' la domanda che chiude o apre tutto il progetto,
                # e costava due numeri in piu' in questa riga.
                # IL PREZZO CHE VEDI NON E' QUELLO CHE PAGHI (30/09 notte, la correzione piu'
                # importante del progetto). `p0` e' il prezzo dello scambio a cui entriamo: uno
                # scambio realmente avvenuto. Ma quel qualcuno non possiamo essere noi — per
                # comprare si manda una transazione, che viene eseguita DOPO quelle davanti.
                # Il prezzo ottenibile e' quello dello scambio SUCCESSIVO.
                # Misurato: sui pool a raffica il primo scambio dopo il nostro costa il 38% in
                # piu' in mediana. Tutto il vantaggio del +17,6% e del +193% stava in quel salto:
                # a un solo scambio di ritardo diventano −11,4% e +0,9%.
                # Da qui ogni taglia si misura DUE volte: col prezzo osservato (`_uscita_N`, che
                # resta per confronto) e col prezzo ottenibile (`_uscita_N_ritardo`), che e'
                # l'unico su cui si decide.
                p_reale = flusso[0][0] if flusso else None
                for taglia in (25, 50, 100, 500, 2000):
                    riempito = incassato = 0.0
                    for pr, q in flusso:
                        if riempito >= taglia:
                            break
                        quota = min(q, taglia - riempito)
                        riempito += quota
                        incassato += quota * (pr / p0)    # quanto rende quella fetta, in multipli
                    if riempito <= 0:
                        c[f"_uscita_{taglia}"] = -0.98
                    else:
                        # la parte non venduta entro l'orizzonte vale zero: e' il costo di essere
                        # entrati in un mercato che non ti fa uscire tutto
                        u = (incassato + 0.0 * (taglia - riempito)) / taglia - 1 - COSTO
                        c[f"_uscita_{taglia}"] = u if -0.99 < u < 20 else -0.98
                    c[f"_riempito_{taglia}"] = round(riempito / taglia, 3)
                    # e ora lo stesso conto col prezzo che si paga davvero
                    if p_reale and p_reale > 0 and len(flusso) > 1:
                        riemp2 = inc2 = 0.0
                        for pr, q in flusso[1:]:
                            if riemp2 >= taglia:
                                break
                            quota = min(q, taglia - riemp2)
                            riemp2 += quota
                            inc2 += quota * (pr / p_reale)
                        if riemp2 <= 0:
                            c[f"_uscita_{taglia}_ritardo"] = -0.98
                        else:
                            u2 = inc2 / taglia - 1 - COSTO
                            c[f"_uscita_{taglia}_ritardo"] = (
                                u2 if -0.99 < u2 < 20 else -0.98)
                    else:
                        c[f"_uscita_{taglia}_ritardo"] = -0.98
            # QUANTO ABBIAMO GUARDATO, E COME SI MISURA DAVVERO (25/09, in due tempi).
            #
            # PRIMO TEMPO, la mattina. Misuravo esiti a fine orizzonte su pool di cui avevamo poche
            # ore di dati: chi non aveva vendite perche' non avevamo GUARDATO finiva fra le
            # trappole. Vero, e va corretto.
            #
            # SECONDO TEMPO, la sera: **la correzione della mattina era peggio del difetto.**
            # Avevo definito «giudicabile» come «abbiamo visto sei ore di scambi SU QUESTO POOL».
            # Ma un pool muore smettendo di scambiare: le ore osservate sono poche PROPRIO PERCHE'
            # e' morto. Quel criterio non toglieva i pool poco osservati — toglieva i morti, cioe'
            # esattamente le trappole. Sopravvivenza travestita da rigore.
            # Misurato sullo stesso insieme, orizzonte 24h:
            #     robinhood  ore viste 35,2% di trappole  |  eta' vera **42,6%**
            #     base       ore viste 47,4%              |  eta' vera **53,0%**
            # Il criterio sbagliato buttava via meta' del campione e migliorava il risultato di
            # sette punti. Avevo perfino annunciato la buona notizia prima di verificarla.
            #
            # IN POSITIVO: **un pool e' giudicabile se e' NATO abbastanza prima della fine della
            # raccolta** — una proprieta' del calendario, che non sa nulla di come e' andata. Se poi
            # e' morto in dieci minuti, quello e' il suo esito, non un motivo per escluderlo.
            # `_ore_osservate` resta scritto, ma come descrizione del pool, non come filtro.
            c["_ore_osservate"] = (rr[-1]["ts"] - t0) / 3600
            c["_t"] = t0
            c["_pool"] = fn.split(".")[0]
            c["_rend"] = rend - COSTO
            righe.append(c)
    # LA FRONTIERA SI CONOSCE SOLO DOPO AVER LETTO TUTTO: l'ultimo scambio visto sull'intera chain
    # e' il momento fino a cui la raccolta arriva. Un pool nato prima di quel momento meno
    # l'orizzonte e' giudicabile — sia che abbia scambiato per giorni, sia che sia morto subito.
    if scartati:
        tot = sum(scartati.values())
        print(f"   {tot} pool esclusi dalla misura (e sapere QUANTI e' la meta' del mestiere):",
              flush=True)
        for k, n in scartati.most_common():
            print(f"      {n:6d}  {k}", flush=True)
    if senza_verso[0]:
        print(f"   {senza_verso[0]} pool saltati: non si capisce quale token e' il memecoin",
              flush=True)
    fine = max((x["_t"] + x["_ore_osservate"] * 3600 for x in righe), default=0)
    for x in righe:
        x["_giudicabile"] = (fine - x["_t"]) >= ORIZZONTE_ORE * 3600
    return righe


if __name__ == "__main__":
    r = costruisci()
    # SI SCRIVE COMPRESSO (25/09). Da oggi questo file lo rifa' una corsia ogni due ore invece
    # delle mie mani una volta al giorno: in chiaro sarebbero venti megabyte riscritti dodici
    # volte al giorno dentro un repository che era gia' arrivato al limite.
    # una variante (entrata/orizzonte diversi) finisce in un file suo e NON tocca quello ufficiale
    suf = os.environ.get("SUFFISSO", "").strip()
    fuori = f"data/loop1/insieme_{CHAIN}{('_' + suf) if suf else ''}.jsonl.gz"
    os.makedirs(os.path.dirname(fuori), exist_ok=True)
    with gzip.open(fuori, "wt") as f:
        for x in r:
            f.write(json.dumps(x) + "\n")
    # L'ELENCO CHE TAPPAVA TUTTO (2/10). `data/loop1/decisioni_{CHAIN}.json` dice a
    # `agents/iniziatori.py` per QUALI pool risolvere chi ha firmato, e fino a quale istante.
    # NESSUNO lo scriveva: era un residuo di un giro vecchio, congelato a 9.009 pool su
    # robinhood e 4.137 su base — il 22% e il 21% dell'insieme. Ed e' esattamente la copertura
    # del passato dei compratori (20% e 26%): il limite del filone insider non era nei dati,
    # era una lista ferma che nessuno rigenerava.
    # SI FONDE, NON SI SOSTITUISCE, E CONTRIBUISCONO TUTTE LE VARIANTI (2/10).
    # Prima scrivevo questo elenco solo dalla variante UFFICIALE, pensando che fosse la piu'
    # completa. Non lo e': l'ufficiale ha 5.082 pool su base, mentre la variante `sc5` — quella
    # su cui faccio TUTTE le misure — ne ha 20.083. Scrivendo dall'ufficiale la lista restava
    # della stessa taglia di prima (8.712 contro 9.009) e il tetto non si alzava di un dito.
    # Qui ogni variante AGGIUNGE i suoi pool e si tiene il momento di decisione piu' TARDI fra
    # quelli visti: un taglio piu' tardi fa risolvere piu' transazioni, mai meno. Cosi' la
    # lista e' l'unione di tutto cio' che conosciamo e non puo' rimpicciolirsi.
    f_dec = f"data/loop1/decisioni_{CHAIN}.json"
    dec = {}
    if os.path.exists(f_dec):
        try:
            dec = json.load(open(f_dec))
        except Exception:
            dec = {}
    prima_n = len(dec)
    for x in r:
        if x.get("_pool") and x.get("_t"):
            p_ = x["_pool"]
            dec[p_] = max(int(x["_t"]), int(dec.get(p_, 0)))
    with open(f_dec, "w") as f:
        json.dump(dec, f)
    print(f"INSIEME | elenco per gli iniziatori: {prima_n:,} -> {len(dec):,} pool "
          f"(variante «{suf or 'ufficiale'}» ha aggiunto {len(dec)-prima_n:,})", flush=True)

    vecchio_chiaro = f"data/loop1/insieme_{CHAIN}.jsonl"
    if os.path.exists(vecchio_chiaro):
        os.remove(vecchio_chiaro)   # due copie della stessa cosa divergono e si legge la sbagliata
    # UN TIMBRO DENTRO IL DATO (26/09). La corsia deve sapere quanto e' vecchio l'insieme per
    # decidere se rifarlo. Il primo tentativo leggeva la data dell'ultimo commit su questo file —
    # e su una copia superficiale (`--depth 1`) esiste una sola cronologia, datata ADESSO: il
    # controllo rispondeva «ha 2 minuti» qualunque fosse la verita', e la corsia non avrebbe
    # ricostruito mai piu'. Un giro andato a vuoto che dichiara «riuscito».
    # IN POSITIVO: **un controllo non deve dipendere da qualcosa che l'ambiente potrebbe non
    # avere.** La cronologia si pota, il contenuto no: il timbro vive nel dato.
    timbro = "data/loop1/insieme_timbro.json" if not suf else "/tmp/timbro_variante.json"
    try:
        tutti = json.load(open(timbro)) if os.path.exists(timbro) else {}
    except Exception:
        tutti = {}
    tutti[CHAIN] = int(time.time())
    json.dump(tutti, open(timbro, "w"))
    n50 = sum(1 for x in r if x["_rend"] >= 0.5)
    print(f"INSIEME | {CHAIN}: {len(r)} pool, {len(r[0])-3 if r else 0} caratteristiche, "
          f"{n50} fanno +50% ({100*n50/max(1,len(r)):.1f}%) -> {fuori}", flush=True)
