"""IL MERCATO PRIMA DEL POOL: gli acquisti che ci mancavano, sulla curva di Pons.

== PERCHE' ESISTE ==

Dal 5/10 avevamo un fatto misurato e senza spiegazione: il 45-48% delle posizioni risulta
«comprata e mai venduta», un'altra fetta comparabile «venduta senza acquisto», e sulle sole
posizioni verificabili il multiplo mediano e' 1,05X e 0,99X. Cioe': la maggior parte di chi vende
questi gettoni NON li ha comprati sui mercati che leggiamo.

Il 6/10 Grok (abbonamento, costo zero) ha indicato il meccanismo con la documentazione in mano:
su robinhood il 92,9% delle commissioni dei lanci passa da Pons, e Pons vende i gettoni su una
CURVA, prima che il pool Uniswap esista. Fonte: https://docs.ponsfamily.com/v2

VERIFICATO SULLA CHAIN il 6/10, non creduto sulla parola:
 · chain id 4663, la fabbrica 0x7eD5…EC7e ha 48.356 caratteri di codice e sta lanciando adesso;
 · l'evento della fabbrica e' `TokenLaunched(address,address,address,address,uint256,uint256)`
   e quello della curva e' `CurveBuy(address,address,uint256,uint256,uint256,uint256)` —
   riconosciuti col keccak (agents/firma_evento.py), NON a occhio sulla forma dei dati;
 · su 9 lanci negli ultimi 6000 blocchi: 33 acquisti e 17 vendite sulla curva, con importi e
   indirizzi veri.

Questo NON e' un vantaggio da copiare: chi compra sulla curva paga. E' la META' MANCANTE della
contabilita'. Senza questi acquisti ogni multiplo che calcoliamo e' un numero senza il costo.

== LA LEZIONE CHE QUESTO FILE DEVE RICORDARE ==

**Chi compra non e' chi detiene.** Nell'evento `CurveBuy` il primo indirizzo e' il `buyer` e il
secondo il `recipient`. Nei dati veri sono DIVERSI: l'indirizzo 0xe33e9e47… compare come
compratore in 4 lanci su 9, ogni volta per un destinatario diverso, e in un caso il destinatario
era il creatore del gettone. E' il router `launchAndBuy`, che crea e compra nella stessa
transazione. Attribuire la posizione al compratore significherebbe dare tutto al router.
E' la STESSA famiglia di errore del 5/10 sui pool (dove l'uscita va al `recipient`, mai al
firmatario): la terza volta che la incontriamo. Qui si attribuisce al DESTINATARIO.

== I LIMITI DELL'RPC, MISURATI IL 6/10 (non assunti) ==

Stavo per costruire un crawler a finestre di 2000 blocchi: 34.096 chiamate per la nostra finestra
storica. Poi ho MISURATO cosa accetta l'RPC, e i limiti sono due, diversi:
 · con un filtro `address`:  fino a 10.000.000 di blocchi per chiamata  → l'elenco dei lanci
   (filtrato sulla fabbrica) sta in 7 chiamate, non 34.096;
 · senza filtro `address`:   30.000 blocchi  → la spazzata per tipo di evento costa
   68.000.000/30.000 = ~2.273 chiamate.

Quindi: i lanci si prendono per indirizzo (7 chiamate), gli scambi si prendono PER TIPO DI EVENTO
su tutta la chain (2.273 chiamate). Andare curva per curva costerebbe ~600.000 chiamate
(300.000 lanci x 2): trenta volte peggio.

E' la lezione «non dedurre i limiti della realta' dai propri» applicata: misurare invece di
assumere ha risparmiato un giorno di lavoro e il 97% delle chiamate.

== LA VALUTA DI QUOTAZIONE NON E' SEMPRE LA STESSA (misurato il 6/10) ==

Ogni curva si paga in un asset scelto da chi lancia. Su 413 lanci misurati: 349 usano la valuta
NATIVA della chain (18 decimali), 16 usano USDG che ha **6 decimali**, e altri usano gettoni vari.

Dividere tutto per 10**18 sottostima gli importi a 6 decimali di **mille miliardi di volte**, e
sommare importi in asset diversi da' un numero che non significa niente. E' esattamente la
famiglia dell'errore che il 3/10 produsse un valore di 16 milioni di dollari inesistente.

Quindi, qui: ogni scambio porta il SIMBOLO e i DECIMALI del suo asset, e **non si somma mai fra
asset diversi**. Dove l'asset non si riconosce, l'importo resta GREZZO (il numero intero come
sta sulla chain) e si dichiara `asset_ignoto`. Un importo grezzo e dichiarato e' usabile; un
importo convertito con il divisore sbagliato e' una bugia con la virgola al posto giusto.

== COSTO ==

ZERO. RPC pubblico della chain, nessuna chiave, nessun conto a consumo. Dichiarato perche' la
regola CFO chiede di dirlo, non di darlo per scontato.
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from firma_evento import firma  # noqa: E402

RPC = "https://rpc.mainnet.chain.robinhood.com"
FABBRICA = "0x7eD598BcEf8bd9Edd8C97A195C6d13f40801EC7e"
CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = int(os.environ.get("BUDGET_SEC", "600"))
FASE = os.environ.get("FASE", "scambi")        # "lanci" | "scambi"
FIN_IND = int(os.environ.get("FIN_INDIRIZZO", "10000000"))   # col filtro address
FIN_TOP = int(os.environ.get("FIN_TOPIC", "30000"))          # senza filtro address
INDIETRO = int(os.environ.get("BLOCCHI_INDIETRO", "69000000"))
FUORI = os.environ.get("FUORI", f"data/multichain/{CHAIN}/curva_acquisti.json")

T_LANCIO = firma("TokenLaunched(address,address,address,address,uint256,uint256)")
T_COMPRA = firma("CurveBuy(address,address,uint256,uint256,uint256,uint256)")
T_VENDE = firma("CurveSell(address,address,uint256,uint256,uint256,uint256)")

_H = {"Content-Type": "application/json",
      "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"),
      "Origin": "https://robinhoodchain.blockscout.com",
      "Referer": "https://robinhoodchain.blockscout.com/"}


_ERRORI = []            # gli ultimi messaggi di errore dell'RPC, per poterli STAMPARE


def chiama(metodo, par=None, tentativi=7):
    """Una chiamata all'RPC, che insiste sui guasti TRANSITORI.

    PERCHE' SETTE TENTATIVI E NON QUATTRO (misurato il 6/10). Con dieci fette in parallelo l'RPC
    risponde `429 Too Many Requests` e chiude la connessione. Con quattro tentativi a 1,5-6
    secondi la finestra veniva ABBANDONATA: una fetta ha letto lo 0,4% della sua parte, con 453
    finestre perse. Un limite di frequenza e' temporaneo, ma saltare una finestra e' definitivo —
    e un'assenza nei dati si legge «non ha comprato», non «non ho guardato».
    Quindi: sul 429 e sulla connessione chiusa si aspetta fino a ~30 secondi, non 6.
    """
    corpo = json.dumps({"jsonrpc": "2.0", "id": 1, "method": metodo,
                        "params": par or []}).encode()
    for t in range(tentativi):
        try:
            q = urllib.request.Request(RPC, corpo, _H)
            r = json.load(urllib.request.urlopen(q, timeout=90))
            # UN ERRORE JSON-RPC NON E' UN'ECCEZIONE. Il 6/10 questo e' costato due giri interi:
            # `.get("result")` su una risposta di errore da None, e la finestra veniva saltata
            # SENZA UNA RIGA DI LOG. Una fetta ha perso 416 finestre con zero messaggi: il
            # contatore diceva «416 fallite» e non c'era modo di sapere perche'.
            # Un guasto silenzioso e' peggio di un guasto rumoroso.
            if isinstance(r, dict) and r.get("error"):
                msg = str(r["error"].get("message", r["error"]))[:200]
                _ERRORI.append(msg)
                # NIENTE RITENTATIVI SU UN ERRORE DI DIMENSIONE. Misurato il 6/10: la finestra
                # troppo densa veniva ritentata 7 volte con attese fino a 30 secondi, cioe' fino
                # a due minuti buttati per finestra — e al settimo tentativo e' densa come al
                # primo. Con 54 rifiuti in un giro, il budget finiva prima della fine e una
                # finestra su sette restava fuori. Qui si torna SUBITO, cosi' chi chiama puo'
                # dimezzare, che e' l'unica cosa che funziona.
                # Aspettare ha senso sul 429 e sulla connessione chiusa; su «troppi risultati»
                # e' solo tempo regalato.
                return None
            return r.get("result")
        except Exception as e:
            msg = str(e)
            if t == tentativi - 1:
                print(f"CURVA | {metodo} fallito dopo {tentativi} tentativi: {msg[:90]}",
                      flush=True)
                return None
            lento = ("429" in msg or "Too Many" in msg or "reset" in msg.lower()
                     or "timed out" in msg.lower())
            time.sleep(min(30.0, (4.0 if lento else 1.5) * (t + 1)))


def _indirizzo(topic):
    return "0x" + topic[-40:]


def _numeri(dati):
    d = dati[2:] if dati.startswith("0x") else dati
    return [int(d[i * 64:(i + 1) * 64], 16) for i in range(len(d) // 64)]


def _riga(x, verso, valute=None):
    """Un evento della curva in forma piatta. Attribuzione a CHI RICEVE: vedi lezione in testa."""
    n = _numeri(x["data"])
    if len(n) < 2:
        return None
    cur = x["address"].lower()
    # I DECIMALI VENGONO DALLA CURVA, non da una costante. Su 1.987 lanci ci sono 28 asset di
    # quotazione: USDG ha 6 decimali, e dividere il suo importo per 10**18 lo sottostima di
    # mille miliardi di volte. Dove non so l'asset, l'importo resta GREZZO e lo dichiaro:
    # un numero grezzo e dichiarato si puo' usare, uno convertito male e' una bugia precisa.
    sim, dec = (valute or {}).get(cur, (None, None))
    div = 10 ** dec if dec is not None else 1
    return {"verso": verso,
            "curva": cur,
            "valuta_simbolo": sim,
            "grezzo": dec is None,
            "chi_compra": _indirizzo(x["topics"][1]),
            "chi_riceve": _indirizzo(x["topics"][2]),
            # I CAMPI SONO INVERTITI FRA ACQUISTO E VENDITA (verificato sulla chain il 6/10).
            #   CurveBuy  : campo 0 = valuta che ENTRA, campo 1 = gettoni che ESCONO
            #   CurveSell : campo 0 = gettoni che ENTRANO, campo 1 = valuta che ESCE
            # Avevo assunto lo stesso ordine per entrambi, ed e' la STESSA assunzione di
            # simmetria che il 5/10 ci aveva fatto invertire acquisti e vendite sul 67-78% dei
            # pool. Due eventi con la stessa firma non hanno per forza lo stesso significato
            # nello stesso posto.
            # LA PROVA: in una vendita il campo 0 valeva 24.326.879.850.071.016.010.754.537, e
            # nella stessa transazione c'e' un trasferimento di ESATTAMENTE quella quantita' di
            # memecoin dal venditore alla curva; il campo 1 valeva 43.198.716.754.653.951, e
            # c'e' un trasferimento di esattamente quella quantita' di valuta verso il
            # venditore. Non e' un'interpretazione: sono due trasferimenti che combaciano.
            "valuta": (n[1] if verso == "vende" else n[0]) / div,
            "gettoni": (n[0] if verso == "vende" else n[1]) / 1e18,
            "commissione": n[2] / div if len(n) > 2 else 0.0,
            "tassa": n[3] / div if len(n) > 3 else 0.0,
            "blocco": int(x["blockNumber"], 16),
            # L'ORDINE DENTRO IL BLOCCO. Su una chain da 10 blocchi al secondo, decine di
            # acquisti cadono nello stesso blocco: senza questo, «chi e' arrivato prima» sarebbe
            # deciso a caso dall'ordine di lettura. Con un blocco solo di granularita' la
            # domanda di Nicolo' («chi entra all'inizio all'inizio») non e' rispondibile.
            "ordine": int(x.get("logIndex", "0x0"), 16),
            "tx": x["transactionHash"]}


def fase_lanci(bn, t0):
    """L'elenco dei lanci: gettone -> curva, creatore, blocco. Col filtro address: 10M per volta."""
    fuori = f"data/multichain/{CHAIN}/curva_lanci.json.gz"
    lanci, b, chiamate = {}, max(1, bn - INDIETRO), 0
    while b < bn and time.time() - t0 < BUDGET:
        # -1 come per le finestre degli scambi: l'RPC conta gli estremi INCLUSI, quindi
        # b..b+10.000.000 sono 10.000.001 blocchi e il limite scatta. Avevo corretto questo
        # fuori-di-uno stamattina per gli scambi e NON qui: la stessa lezione in due posti
        # vale una volta se la applico a uno solo.
        fine = min(b + FIN_IND - 1, bn)
        # COL DIMEZZAMENTO ANCHE QUI. Il 6/10 ho creduto che col filtro sull'indirizzo bastasse
        # restare sotto i 10 milioni di blocchi. Falso: vale ANCHE il tetto di 10.000 risultati,
        # e in 10 milioni di blocchi ci sono ~47.000 lanci. Tutte e 7 le finestre sono state
        # rifiutate e il giro ha scritto ZERO lanci. La prova di stamattina su una finestra da
        # 10 milioni era fallita per un fuori-di-uno: quel caso non era MAI riuscito, quindi
        # **avevo dedotto il limite da una prova che non era passata.**
        lg = log_di_finestra(T_LANCIO, b, fine, indirizzo=FABBRICA)
        chiamate += 1
        if lg is None:
            print(f"   finestra {b:,}-{fine:,} non letta: la segno, non la invento", flush=True)
            b = fine + 1
            continue
        for ev in lg:
            ind = [_indirizzo(t) for t in ev["topics"][1:]]
            if len(ind) < 2:
                continue
            # il quarto indirizzo della firma non e' indicizzato: sta nei dati, ed e' l'ASSET DI
            # QUOTAZIONE, cioe' con cosa si paga su quella curva. Senza di lui gli importi sono
            # numeri senza unita'.
            d = ev.get("data", "0x")[2:]
            quote = ("0x" + d[24:64]) if len(d) >= 64 else None
            lanci[ind[0]] = {"curva": ind[1], "creatore": ind[2] if len(ind) > 2 else None,
                             "blocco": int(ev["blockNumber"], 16), "quote": quote}
        print(f"   {b:,}-{fine:,}: {len(lg):,} lanci (totale {len(lanci):,})", flush=True)
        b = fine + 1
    os.makedirs(os.path.dirname(fuori), exist_ok=True)
    import gzip
    # "at", non "wt": con la ripartenza, troncare butterebbe le righe grezze dei giri precedenti,
    # cioe' proprio le prove che Nicolo' deve poter aprire a mano. Nessun doppione: le finestre
    # in `fatte` non si rileggono. Il contatore e il file delle somme si scrivono insieme, quindi
    # restano coerenti fra loro.
    if _ERRORI:
        from collections import Counter
        print(f"CURVA | motivi dei rifiuti ({len(_ERRORI)}):", flush=True)
        for _m, _q in Counter(_ERRORI).most_common(3):
            print(f"   x{_q}  {_m[:140]}", flush=True)
    # LA GUARDIA CHE AVEVO SCRITTO E POI PERSO. Il 5/10 avevo messo «zero lanci: non scrivo un
    # file che direbbe che nessun acquisto esiste». Poi il 6/10 ho riscritto l'agente in due
    # fasi e la guardia e' rimasta nel pezzo buttato: il giro dopo ha scritto un file VUOTO
    # sopra uno con 1.987 lanci e 28 valute. **Una riscrittura non eredita le lezioni da sola.**
    if not lanci:
        print("CURVA | ZERO lanci: NON scrivo. Un file vuoto qui si legge «non esistono "
              "acquisti sulla curva», che e' la conclusione opposta a quella vera, e "
              "cancellerebbe un file buono. Uno zero ripetuto non e' un dato.", flush=True)
        return
    # I DECIMALI DI OGNI ASSET DI QUOTAZIONE, chiesti una volta per asset (sono pochi: su 1.994
    # lanci quattro coprono quasi tutto). Senza, gli importi sono numeri senza unita'.
    assets = {}
    for _L in lanci.values():
        _q = _L.get("quote")
        if not _q or _q in assets:
            continue
        if _q == "0x" + "0" * 40:
            assets[_q] = {"simbolo": "NATIVO", "decimali": 18}
            continue
        _dec = chiama("eth_call", [{"to": _q, "data": "0x313ce567"}, "latest"])   # decimals()
        _sim = chiama("eth_call", [{"to": _q, "data": "0x95d89b41"}, "latest"])   # symbol()
        _nome = None
        if _sim and len(_sim) > 130:
            try:
                _nome = bytes.fromhex(_sim[130:]).decode().strip("\x00").strip()
            except Exception:
                _nome = None
        assets[_q] = {"simbolo": _nome, "decimali": int(_dec, 16) if _dec else None}
    _ign = sum(1 for a in assets.values() if a["decimali"] is None)
    print(f"CURVA | {len(assets)} asset di quotazione distinti, {_ign} senza decimali leggibili "
          f"(per quelli l'importo resta grezzo, non convertito col divisore sbagliato)",
          flush=True)
    # "wt" e NON "at": questo file e' UN documento JSON, non un flusso di righe. Il 6/10 una mia
    # sostituzione pensata per il file degli scambi ha colpito ANCHE questo, e i giri successivi
    # accodavano un secondo documento che nessuno leggeva: i dati nuovi scomparivano in silenzio.
    # Avevo verificato che la modifica ci FOSSE, non QUANTE volte. Ora conto sempre.
    with gzip.open(fuori, "wt") as f:
        json.dump({"acq": int(time.time()), "chain": CHAIN, "fabbrica": FABBRICA, "assets": assets,
                   "blocco_fino_a": bn, "blocchi_indietro": INDIETRO,
                   "chiamate": chiamate, "da": lanci}, f)
    print(f"CURVA | {len(lanci):,} lanci in {chiamate} chiamate -> {fuori}", flush=True)


def log_di_finestra(topic, da, a, prof=0, indirizzo=None, secondo=None):
    """I log di un tipo di evento fra due blocchi, dimezzando la finestra se e' troppo densa.

    PERCHE'. Le fette centrali perdevano il 99% delle finestre, e non per la frequenza delle
    chiamate: per la DENSITA'. Dove ci sono ~9.500 eventi per finestra l'RPC rifiuta la risposta
    (troppi risultati), dove ce ne sono ~4.500 risponde. Aspettare non serve a niente: la finestra
    sara' densa anche al tentativo dopo. Si dimezza, e si dimezza di nuovo, finche' entra.
    Fino a 6 dimezzamenti: una finestra da 30.000 blocchi scende a ~470, cioe' ~47 secondi di
    chain. Sotto non si va: a quel punto non e' piu' densita', e il None va segnalato.
    """
    quanti = len(_ERRORI)
    # `secondo` e' il SECONDO argomento indicizzato dell'evento. Serve per gli scambi Uniswap
    # v4, dove il pool non ha un indirizzo e il suo id sta li': filtrando sull'indirizzo del
    # gestore PIU' l'id si leggono gli scambi di un solo pool, e col filtro per indirizzo la
    # finestra consentita sale a 10 milioni di blocchi.
    q = {"topics": [topic] + ([secondo] if secondo else []),
         "fromBlock": hex(da), "toBlock": hex(a)}
    if indirizzo:
        q["address"] = indirizzo
    lg = chiama("eth_getLogs", [q])
    if lg is not None:
        return lg
    denso = any(("more than" in e or "too many" in e.lower() or "limit" in e.lower()
                 or "exceed" in e.lower()) for e in _ERRORI[quanti:])
    if (denso or prof == 0) and prof < 12 and a > da:
        meta = da + (a - da) // 2
        s1 = log_di_finestra(topic, da, meta, prof + 1, indirizzo, secondo)
        if s1 is None:
            return None
        s2 = log_di_finestra(topic, meta + 1, a, prof + 1, indirizzo, secondo)
        if s2 is None:
            return None
        return s1 + s2
    return None


def fase_scambi(bn, t0):
    """Gli acquisti e le vendite, spazzati PER TIPO DI EVENTO: senza address, 30.000 per volta.

    A fette: ogni fetta prende la sua porzione di blocchi e scrive il suo pezzo. Le finestre sono
    indipendenti, quindi dividere per blocchi e' corretto senza bisogno di unire niente a mano.
    """
    import gzip
    try:
        from a_fette import quale_fetta
        i_f, n_f = quale_fetta()
    except Exception:
        i_f, n_f = 0, 1
    # GRIGLIA ANCORATA, non relativa al blocco attuale.
    # Il 6/10 la ripartenza sembrava funzionare e non funzionava: le finestre partivano da
    # `bn - INDIETRO`, e `bn` avanza di ~10 blocchi al secondo. Al giro dopo ogni inizio di
    # finestra era spostato, quindi nessuno combaciava con quelli segnati e si rileggeva tutto.
    # Dichiarava «riprendo: 12 finestre gia' lette» e ne rifaceva 14.
    # Con la griglia agganciata ai multipli di FIN_TOP gli inizi sono gli STESSI a ogni giro,
    # qualunque sia il blocco attuale, e il contatore serve davvero a qualcosa.
    # Lezione: una ripartenza si prova facendola due volte, non leggendola.
    dal = max(FIN_TOP, ((bn - INDIETRO) // FIN_TOP) * FIN_TOP)
    al = (bn // FIN_TOP) * FIN_TOP
    passi = max(1, (al - dal) // FIN_TOP)
    per_fetta = max(1, passi // n_f)
    mio_da = dal + i_f * per_fetta * FIN_TOP
    mio_a = al if i_f == n_f - 1 else mio_da + per_fetta * FIN_TOP
    fuori = f"data/multichain/{CHAIN}/curva_scambi_pezzo_{i_f}.jsonl.gz"
    os.makedirs(os.path.dirname(fuori), exist_ok=True)
    print(f"CURVA | fetta {i_f+1}/{n_f}: blocchi {mio_da:,}-{mio_a:,} "
          f"({(mio_a-mio_da)//FIN_TOP:,} finestre previste)", flush=True)

    # PERCHE' AGGREGO. La finestra intera sono ~7,4 milioni di eventi (misurato: 32.657 in
    # 300.000 blocchi): grezzi fanno ~1,8 GB, e il repo non e' il posto giusto. Ma la domanda
    # non ha bisogno dei singoli eventi: ha bisogno di QUANTO ha pagato ogni indirizzo per ogni
    # gettone, che e' una somma. Tengo le righe grezze SOLO per i candidati, perche' quelle
    # Nicolo' le deve poter aprire a mano e ritrovare sulla chain.
    # LA MAPPA CURVA -> (simbolo, decimali), dal file dei lanci. Serve prima di leggere un solo
    # scambio: senza, ogni importo e' un numero senza unita'.
    valute = {}
    pl = f"data/multichain/{CHAIN}/curva_lanci.json.gz"
    if os.path.exists(pl):
        try:
            _dl = json.load(gzip.open(pl, "rt"))
            _as = _dl.get("assets", {})
            for _t, _L in _dl.get("da", {}).items():
                _a = _as.get(_L.get("quote")) or {}
                valute[_L["curva"].lower()] = (_a.get("simbolo"), _a.get("decimali"))
        except Exception as e:
            print(f"CURVA | lanci illeggibili ({str(e)[:60]}): gli importi resteranno grezzi",
                  flush=True)
    print(f"CURVA | valuta nota per {len(valute):,} curve", flush=True)
    cand = set()
    pc = "data/candidati_vincenti.json"
    if os.path.exists(pc):
        try:
            cand = set(x.lower() for x in json.load(open(pc))["da"].get(CHAIN, []))
        except Exception:
            pass
    print(f"CURVA | {len(cand)} candidati: per loro tengo anche le righe grezze", flush=True)

    # RIPARTENZA. Il 6/10 il primo giro ha coperto il 72,7% in media, con una fetta allo 0,4%:
    # senza memoria, il giro dopo ricomincerebbe dall'inizio e perderebbe le stesse finestre.
    # Con la memoria i giri CONVERGONO: ogni passaggio ripara solo i buchi rimasti.
    pf = f"data/multichain/{CHAIN}/curva_fatte_pezzo_{i_f}.json"
    VERSIONE = 4        # 4 = ogni voce porta la sua unita' (grezzo/simbolo) (6/10)
    fatte = set()
    if os.path.exists(pf):
        try:
            _c = json.load(open(pf))
            if int(_c.get("versione", 1)) < VERSIONE:
                # BUTTO quello che c'e'. Fino alla versione 1 ogni importo era diviso per 10**18
                # anche quando l'asset aveva 6 decimali, e le somme mescolavano asset diversi:
                # un totale senza unita' non e' un dato parziale, e' un dato FALSO. Rileggere
                # costa un giro; tenerlo costa una conclusione sbagliata.
                print(f"CURVA | contatore di versione {_c.get('versione', 1)}: lo butto e "
                      f"rileggo, perche' quegli importi avevano il divisore sbagliato",
                      flush=True)
                fatte = set()
            else:
                fatte = set(_c["fatte"])
        except Exception:
            fatte = set()
    ps = f"data/multichain/{CHAIN}/curva_somme_pezzo_{i_f}.json.gz"
    # LA FILA DEI PRIMI ARRIVATI, per curva. Tenerne 50 basta: la domanda e' se chi entra per
    # primo guadagna piu' di chi entra dopo, e oltre il cinquantesimo non e' piu' «l'inizio».
    # Non e' deducibile dalle somme (che aggregano e perdono l'ordine), e il file grezzo lo
    # teniamo solo per i candidati: senza questo, l'ordine di arrivo sarebbe perso per sempre.
    PRIMI = 50
    fila = {}
    pfi = f"data/multichain/{CHAIN}/curva_fila_pezzo_{i_f}.json.gz"
    somme = {}
    if os.path.exists(ps) and fatte:
        try:
            somme = json.load(gzip.open(ps, "rt")).get("da", {})
        except Exception:
            somme = {}
        if os.path.exists(pfi):
            try:
                fila = json.load(gzip.open(pfi, "rt")).get("da", {})
            except Exception:
                fila = {}
    if fatte or somme:
        print(f"CURVA | riprendo: {len(fatte):,} finestre gia' lette, "
              f"{len(somme):,} coppie gia' in archivio", flush=True)
    b, n, nb, nv, saltate, lette, blocchi_letti = mio_da, 0, 0, 0, 0, 0, 0
    # "at", non "wt": con la ripartenza, troncare butterebbe le righe grezze dei giri precedenti,
    # cioe' proprio le prove che Nicolo' deve poter aprire a mano. Nessun doppione: le finestre
    # in `fatte` non si rileggono. Il contatore e il file delle somme si scrivono insieme, quindi
    # restano coerenti fra loro.
    with gzip.open(fuori, "at") as f:
        while b < mio_a:
            if time.time() - t0 >= BUDGET:
                print(f"   budget speso a {b:,} ({100*(b-mio_da)/max(1,mio_a-mio_da):.1f}% "
                      f"della fetta): salvo quello che ho", flush=True)
                break
            # -1 perche' l'RPC conta gli estremi INCLUSI: b..b+FIN_TOP sono FIN_TOP+1 blocchi,
            # e il limite di 30.000 scatta a 30.001. Il 6/10 questo fuori-di-uno ha fatto
            # fallire 18 chiamate su 20 SENZA che si vedesse: vedi la nota sulla copertura.
            fine = min(b + FIN_TOP - 1, mio_a)
            if b in fatte:          # gia' letta in un giro precedente: non si rifa'
                blocchi_letti += fine - b + 1
                b = fine + 1
                continue
            ok_qui = 0
            for topic, verso in ((T_COMPRA, "compra"), (T_VENDE, "vende")):
                lg = log_di_finestra(topic, b, fine)
                if lg is None:
                    saltate += 1
                    continue
                ok_qui += 1
                lette += 1
                for x in lg:
                    r = _riga(x, verso, valute)
                    if not r:
                        continue
                    n += 1
                    if verso == "compra":
                        nb += 1
                    else:
                        nv += 1
                    if verso == "compra":
                        # `fl` e NON `f`: dentro questo blocco `f` e' il FILE aperto in
                        # scrittura. Chiamando la fila `f` l'ho ombreggiato e la corsia e'
                        # morta alla prima riga con «'list' object has no attribute 'write'».
                        # Trovato facendola girare: un file che compila non e' un file che gira.
                        fl = fila.setdefault(r["curva"], [])
                        fl.append([r["blocco"], r["ordine"], r["chi_riceve"],
                                   round(r["valuta"], 12), round(r["gettoni"], 4)])
                        if len(fl) > PRIMI * 3:         # si pota ogni tanto, non a ogni riga
                            fl.sort(key=lambda z: (z[0], z[1]))
                            del fl[PRIMI:]
                    k = r["chi_riceve"] + "|" + r["curva"]
                    # L'UNITA' VIAGGIA CON IL NUMERO (6/10). Le somme non dicevano se
                    # l'importo era grezzo (asset ignoto, diviso per 1) o convertito: due
                    # numeri identici all'occhio e diversi di 10^18. Mescolandoli ho ottenuto
                    # multipli da 5 miliardi di miliardi. Un numero senza la sua unita' e'
                    # indistinguibile da uno con l'unita' sbagliata: e' «una descrizione che
                    # mente», ed e' peggio di una mancante.
                    # Chi legge DEVE poter rifiutare di sommare: percio' `grezzo` e `simbolo`
                    # stanno dentro ogni voce, non in una nota a margine del file.
                    d = somme.setdefault(k, {"compra_valuta": 0.0, "compra_gettoni": 0.0,
                                             "grezzo": bool(r.get("grezzo")),
                                             "simbolo": r.get("valuta_simbolo"),
                                             "vende_valuta": 0.0, "vende_gettoni": 0.0,
                                             "n_compra": 0, "n_vende": 0,
                                             "primo": None, "ultimo": None,
                                             "tx_compra": [], "tx_vende": []})
                    # le PROVE (gli hash) solo per i candidati. Per tutti gli altri bastano
                    # i numeri. Il 6/10 le somme con le prove per tutti pesavano 290 MB per
                    # giro, consegnati a OGNI giro allo scrittore unico del ramo: tenere una
                    # prova per 600.000 coppie che nessuno verifichera' e' peso per gli altri.
                    # Chi serve davvero verificare e' nella lista dei candidati.
                    suo = r["chi_riceve"] in cand or r["chi_compra"] in cand
                    if verso == "compra":
                        d["compra_valuta"] += r["valuta"]; d["compra_gettoni"] += r["gettoni"]
                        d["n_compra"] += 1
                        if suo and len(d["tx_compra"]) < 3:
                            d["tx_compra"].append(r["tx"])
                    else:
                        d["vende_valuta"] += r["valuta"]; d["vende_gettoni"] += r["gettoni"]
                        d["n_vende"] += 1
                        if suo and len(d["tx_vende"]) < 3:
                            d["tx_vende"].append(r["tx"])
                    bl = r["blocco"]
                    d["primo"] = bl if d["primo"] is None else min(d["primo"], bl)
                    d["ultimo"] = bl if d["ultimo"] is None else max(d["ultimo"], bl)
                    if cand and (r["chi_riceve"] in cand or r["chi_compra"] in cand):
                        f.write(json.dumps(r) + "\n")
            # un blocco conta come letto solo se ENTRAMBI i tipi di evento sono arrivati:
            # con uno solo dei due avrei gli acquisti senza le vendite, cioe' la meta' della
            # contabilita' — esattamente il difetto che questo file nasce per riparare
            if ok_qui == 2:
                blocchi_letti += fine - b + 1
                fatte.add(b)
            b = fine + 1
    # quanto ho coperto DAVVERO: senza questo numero, un file corto sembra "pochi scambi"
    # invece di "poco letto". E' l'errore che il 5/10 ci ha fatto chiamare "impossibile"
    # una cosa che era solo non guardata.
    coperto = 100 * blocchi_letti / max(1, mio_a - mio_da)
    attraversato = 100 * (min(b, mio_a) - mio_da) / max(1, mio_a - mio_da)
    print(f"CURVA | fetta {i_f+1}/{n_f}: {n:,} eventi ({nb:,} acquisti, {nv:,} vendite), "
          f"LETTO {coperto:.1f}% (attraversato {attraversato:.1f}%), "
          f"{lette} chiamate buone, {saltate} fallite -> {fuori}", flush=True)
    if _ERRORI:
        from collections import Counter
        c = Counter(_ERRORI)
        print(f"CURVA | motivi dei rifiuti dell'RPC ({len(_ERRORI)} in tutto):", flush=True)
        for m, q in c.most_common(3):
            print(f"   x{q}  {m[:150]}", flush=True)
    if saltate and coperto < 95:
        print(f"CURVA | ATTENZIONE: {saltate} finestre non lette. Questo file e' PARZIALE e "
              f"chi lo usa deve saperlo: un'assenza qui si legge come «non ha comprato», "
              f"che e' la conclusione sbagliata.", flush=True)
    json.dump({"acq": int(time.time()), "fetta": i_f,
               "da_blocco": mio_da, "a_blocco": mio_a, "passo": FIN_TOP,
               "versione": VERSIONE, "fatte": sorted(fatte)}, open(pf, "w"))
    with gzip.open(ps, "wt") as g:
        json.dump({"acq": int(time.time()), "fetta": i_f, "fette": n_f,
                   "da_blocco": mio_da, "a_blocco": mio_a, "coperto_pct": coperto,
                   "attribuzione": "chi_riceve (il router compra per altri: 25,8% degli eventi)",
                   "da": somme}, g)
    for fl in fila.values():
        fl.sort(key=lambda z: (z[0], z[1]))
        del fl[PRIMI:]
    with gzip.open(pfi, "wt") as g:
        json.dump({"acq": int(time.time()), "fetta": i_f, "primi": PRIMI,
                   "campi": ["blocco", "ordine_nel_blocco", "chi_riceve", "valuta", "gettoni"],
                   "da": fila}, g)
    print(f"CURVA | {len(fila):,} curve con la fila dei primi {PRIMI} -> {pfi}", flush=True)
    print(f"CURVA | {len(somme):,} coppie (chi riceve x curva) -> {ps}", flush=True)
    json.dump({"acq": int(time.time()), "fetta": i_f, "fette": n_f,
               "da_blocco": mio_da, "a_blocco": mio_a, "arrivato_a": min(b, mio_a),
               "coperto_pct": coperto, "attraversato_pct": attraversato,
               "blocchi_letti": blocchi_letti, "chiamate_buone": lette,
               "finestre_non_lette": saltate,
               "acquisti": nb, "vendite": nv},
              open(f"data/multichain/{CHAIN}/curva_copertura_pezzo_{i_f}.json", "w"))


def main():
    if CHAIN != "robinhood":
        print(f"CURVA | Pons e' la fabbrica di robinhood: su {CHAIN} non c'e' niente da leggere. "
              f"Su base i lanci passano da o1/Bankr/Clanker, che mettono la supply nel pool: "
              f"meccanismo diverso, va misurato a parte e NON con questo file.")
        return
    t0 = time.time()
    bn = chiama("eth_blockNumber")
    if not bn:
        raise SystemExit("CURVA | l'RPC non risponde: non invento un blocco")
    bn = int(bn, 16)
    print(f"CURVA | chain id {int(chiama('eth_chainId'), 16)}, blocco {bn:,}, fase {FASE}",
          flush=True)
    if FASE == "lanci":
        fase_lanci(bn, t0)
    else:
        fase_scambi(bn, t0)


if __name__ == "__main__":
    main()
