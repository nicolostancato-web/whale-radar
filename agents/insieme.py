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
MIN_VITA = int(os.environ.get("MIN_VITA", 10))
COSTO = float(os.environ.get("COSTO_GIRO", 0.018))
RITARDO_MINIMO = int(os.environ.get("RITARDO_MINIMO_S", 60))   # l'esito non puo' essere simultaneo
MIN_DOPO = int(os.environ.get("MIN_DOPO", 5))       # meno di cosi' e il prezzo non e' misurabile
MIN_VENDITE = int(os.environ.get("MIN_VENDITE", 5))  # meno di cosi' e l'uscita non e' misurabile


# IL PREZZO NON ESISTE SENZA SAPERE DOV'E' IL MEMECOIN (25/09). Qui c'era `a0/a1` fisso, che e'
# valuta-per-memecoin solo dove la valuta e' token0 e l'inverso altrove — e `a0 > 0` per «vendita»,
# che nel 73% dei pool e' un ACQUISTO. Vedi `agents/verso.py` per la misura e il perche'.
# Ora il verso arriva per pool e le due funzioni stanno li'.


def costruisci():
    righe = []
    verso = V.carica(CHAIN)
    senza_verso = [0]
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
            if len(rr) < MIN_VITA:
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
            lim = rr[0]["ts"] + ORE_ATTESA * 3600
            i = None
            for k, x in enumerate(rr):
                if x["ts"] >= lim:
                    i = k
                    break
            if i is None or i < 5:
                continue
            p0 = prezzo(rr[i])
            if not p0:
                continue
            t0 = rr[i]["ts"]
            c = K.estrai(rr[:i + 1], prezzo)
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
            for x in dopo:
                if V.e_vendita(x, meme_t0):
                    vend += 1
                    v = prezzo(x)
                    if v:
                        prezzi_vendita.append(v)
                        q = V.valuta(x, meme_t0)
                        valuta_tot += q
                        for s in valuta_sopra:
                            if v / p0 >= s:
                                valuta_sopra[s] += q
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
    fuori = f"data/loop1/insieme_{CHAIN}.jsonl.gz"
    os.makedirs(os.path.dirname(fuori), exist_ok=True)
    with gzip.open(fuori, "wt") as f:
        for x in r:
            f.write(json.dumps(x) + "\n")
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
    timbro = "data/loop1/insieme_timbro.json"
    try:
        tutti = json.load(open(timbro)) if os.path.exists(timbro) else {}
    except Exception:
        tutti = {}
    tutti[CHAIN] = int(time.time())
    json.dump(tutti, open(timbro, "w"))
    n50 = sum(1 for x in r if x["_rend"] >= 0.5)
    print(f"INSIEME | {CHAIN}: {len(r)} pool, {len(r[0])-3 if r else 0} caratteristiche, "
          f"{n50} fanno +50% ({100*n50/max(1,len(r)):.1f}%) -> {fuori}", flush=True)
