"""BUCO — i pool del registro di cui non abbiamo una riga (si chiamava BUCO BASE).

VALE PER TUTTE E DUE LE CHAIN (19/09): si sceglie con CHAIN=base|robinhood. I limiti del nodo sono
diversi e misurati, non assunti: base accetta finestre da 2.000 blocchi e gruppi da 10, robinhood
20.000 e 100.

COME SONO STATI TROVATI (18/09). Scomponendo l'assenza di eventi, i 128 che mancavano davvero in
una finestra che falliva appartenevano TUTTI a pool per cui non avevamo un solo record: zero
cadeva in un tratto di blocchi che stavamo gia' leggendo. Non un archivio troncato: pool interi
mai cominciati.
Poi ho chiesto al nodo, per ognuno, se avesse mai scambiato. Su base: 101 id V4 su 102 SI', 40
indirizzi su 44 no (quelli sono voci sporche del registro, in quarantena). I 101 sono il buco vero.

PERCHE' LO SCAVO A FASCE NON LI PRENDE. Il collettore storico setaccia fasce di blocchi e tiene
quello che vi trova; quei pool sono nati fuori dalle fasce coperte finora, quindi nessuna pala e'
mai passata sopra la loro nascita. Aspettare che ci arrivi vuol dire aspettare che lo scavo copra
tutta la storia della chain — settimane, per 101 pool che sappiamo gia' nominare.
Qui si va DRITTI alla nascita di ognuno, che conosciamo dalla catena, e si prendono le sue prime
ore. E' l'unico agente che parte dai pool invece che dai blocchi.

GLI ISTANTI SONO VERI. I timestamp si chiedono al nodo per i blocchi che servono davvero, a
gruppi. Interpolare da un riferimento preso a inizio corsa e' quello che il 16/09 ha prodotto
istanti falsi fino a 84 minuti, e con essi una finestra di vita sbagliata per ogni pool.
"""
import gzip
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storico_evm import SWAP_V2, SWAP_V3, SWAP_V4, firma, scarica_su_disco  # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
URL = {"base": "https://mainnet.base.org",
       "robinhood": "https://rpc.mainnet.chain.robinhood.com"}[CHAIN]
AMPIEZZA = 2000 if CHAIN == "base" else 20000   # misurato: base rifiuta oltre, con qualunque filtro
# QUANTI BLOCCHI PER VOLTA: MISURATO, NON SCELTO (21/09). Su robinhood chiedevo gruppi da 100 e il
# nodo rispondeva 429 a intermittenza — due volte si', poi no — e le attese di cortesia mangiavano
# tutto: 164 secondi per UN pool. Provate le alternative a parita' di condizioni:
#     gruppi da 100 -> [100, 100, 429]     gruppi da 50 -> [429, 429, 429]
#     gruppi da  20 -> [20, 20, 20]        gruppi da 10 -> [10, 10, 10]
# e con gruppi da 20 e mezzo secondo scarso di pausa: 12 richieste su 12 riuscite, ZERO rifiuti,
# 30 blocchi al secondo.
# Stavo curando il sintomo (aspettare dopo il rifiuto) invece della causa (chiedere troppo insieme).
LOTTO = 10 if CHAIN == "base" else 20
ORE = float(os.environ.get("ORE_VITA", 8))
# secondi per blocco, misurati sulle due chain (servono a leggere l'arco del censimento)
SEC_BLOCCO = 2.0 if CHAIN == "base" else 0.106
BUDGET = int(os.environ.get("BUDGET_SEC", 900))
ELENCO = f"data/{CHAIN}_mai_letti.json"
# LE FETTE (19/09): il nodo limita per INDIRIZZO IP, misurato ieri sulle coppie (un filo 0,24
# pool/s, tre fili 0,22, sei fili zero). Da una macchina sola non si accelera. Ma ogni lavoro di
# GitHub ha un IP proprio: con 23.079 pool da prendere a ~60 secondi l'uno, una corsia sola impiega
# giorni e sei fette li dividono per sei.
FETTA = os.environ.get("FETTA")
N_FETTE = int(os.environ.get("N_FETTE", 6))
CK = (f"data/multichain/{CHAIN}/buco_ckpt_f{FETTA}.json" if FETTA is not None
      else f"data/multichain/{CHAIN}/buco_ckpt.json")


def ha_qualcosa(pl):
    """Questo pool ha DAVVERO dei record, o solo un file?

    LA DIMENSIONE NON E' IL CONTENUTO (21/09, rilievo della revisione esterna verificato e
    quantificato). Il controllo era «il file esiste e supera 40 byte». Ma un file gzip VUOTO pesa
    81 byte — solo intestazione, zero record — e supera quella soglia.
    Misurato: 2.698 pool su base e 184 su robinhood avevano esattamente quel file. Risultavano
    «gia' pieni» e non sarebbero MAI tornati in coda: duemilaottocento pool che credevamo raccolti
    e di cui non avevamo una sola riga.
    E' la stessa famiglia di errore di tutta la settimana — un controllo che assolve invece di
    verificare — e la conferma che «esiste» e «contiene» sono due domande diverse.

    Si legge il contenuto solo dei file piccoli: sopra i 200 byte un file compresso ha per forza
    dei record, e aprire undicimila file a ogni giro costerebbe piu' del problema che risolve."""
    for c in ("storico", "vivo"):
        p = f"data/multichain/{CHAIN}/{c}/{pl}.jsonl.gz"
        if not os.path.exists(p):
            continue
        try:
            dim = os.path.getsize(p)
        except Exception:
            continue
        if dim > 200:
            return True
        try:
            for riga in gzip.open(p, "rt"):
                if riga.strip():
                    return True
        except Exception:
            # UN FILE ILLEGGIBILE NON E' UN FILE PIENO: torna in coda, non viene assolto.
            continue
    return False


def mia(pool):
    """True se questo pool tocca a questa fetta. Senza fetta, tocca tutto a noi."""
    if FETTA is None:
        return True
    try:
        return int(pool[-6:], 16) % N_FETTE == int(FETTA)
    except Exception:
        return True
t0 = time.time()


def rpc(metodo, params, to=60):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    for k in range(3):
        try:
            r = urllib.request.Request(URL, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=to) as x:
                d = json.load(x)
            if "error" in d:
                return None, str(d["error"])[:60]
            return d.get("result"), None
        except Exception as e:
            if k < 2:
                time.sleep(2 * (k + 1))
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "esauriti"


def istanti(blocchi):
    """I timestamp veri dei blocchi chiesti, a gruppi. Mai interpolati."""
    fuori = {}
    b = sorted(blocchi)
    for i in range(0, len(b), LOTTO):
        gruppo = b[i:i + LOTTO]
        corpo = json.dumps([{"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                             "params": [hex(n), False], "id": n} for n in gruppo]).encode()
        # SI RIPROVA, PERCHE' SENZA ISTANTE LA RIGA SI BUTTA (21/09). Chi chiama scarta ogni record
        # per cui manca il timestamp: se qui ci si arrende al primo rifiuto — e il nodo di robinhood
        # ne manda di continuo — si scaricano i log dalla catena e poi si gettano via.
        # Misurato sul cloud: tre fette hanno visitato 344, 406 e 422 pool scrivendo 7, 172 e 4
        # righe. I log c'erano tutti (verificato a mano: 266, 180, 133 log, esattamente quanti ne
        # dichiara il censimento): mancavano i TEMPI.
        # E' lo stesso difetto che ieri teneva 2.255 pool a zero righe, in un altro punto dello
        # stesso agente: il 429 non e' una risposta, e' una richiesta di aspettare.
        if time.time() - t0 > BUDGET * 1.3:
            break                     # il budget comanda anche sulle riprove (21/09): una prova con
                                      # 150 secondi di budget ne ha impiegati 600, perche' le attese
                                      # non guardavano l'orologio.
        for _k in range(4):
            try:
                r = urllib.request.Request(URL, data=corpo,
                                           headers={"Content-Type": "application/json",
                                                    "User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(r, timeout=60) as x:
                    for d in json.load(x):
                        if d.get("result"):
                            fuori[int(d["result"]["number"], 16)] = int(d["result"]["timestamp"], 16)
                break
            except Exception:
                time.sleep(2 * (_k + 1))
        time.sleep(0.2)
    return fuori


def main():
    # I BERSAGLI SI CALCOLANO OGNI VOLTA, NON SI LEGGONO DA UNA LISTA FISSA (19/09).
    # La prima versione leggeva i 105 pool di un elenco scritto a mano il giorno prima. Li ha presi
    # tutti — e il giorno dopo ce n'erano ALTRI 66, con la stessa identica malattia: nel registro,
    # mai raccolti, e vecchi fino a 900 ore. Controllati uno per uno: 25 su 25 sono POOL VERI, non
    # voci sporche. Il buco non era un incidente chiuso: e' una falla che si riapre, perche' il
    # registro cresce di continuo e lo scavo a fasce non passa dove quei pool sono nati.
    # Una lista fissa cura il sintomo una volta sola. Calcolare i bersagli a ogni giro cura la falla.
    # I BERSAGLI SONO LA POPOLAZIONE DEFINITA, NON SOLO IL REGISTRO (19/09).
    # Con le coppie finalmente risolte (base 98%, robinhood 100%) la definizione di DEFINIZIONE.md
    # si puo' finalmente APPLICARE, e dice che la popolazione da studiare e' 7.084 pool su base e
    # 15.995 su robinhood. Ne avevamo 228 e 227: il 3,2% e l'1,4%.
    # La condizione 1 del cancello chiede >=95% di QUELLA popolazione. Non ci si arriva raccogliendo
    # meglio i pool che gia' abbiamo: bisogna prendere gli altri ventiduemila.
    # Perche' proprio qui: questo agente parte dai POOL invece che dai blocchi, va dritto alla
    # nascita di ognuno e ne prende le prime ore. E' esattamente il lavoro che serve, gia' scritto e
    # gia' verificato contro la catena (istanti esatti al secondo, blockhash giusti, zero duplicati).
    # E IL CRITERIO NON GUARDA IL FUTURO. Si entra per «ha almeno 20 scambi nell'intervallo
    # dichiarato e ha una valuta di base da un lato»: entrambe cose vere al momento in cui si
    # decide. Il vecchio registro invece chiedeva almeno 5 candele e un minimo di volume — cioe'
    # ESSERE SOPRAVVISSUTI — ed escludeva cosi' il 52% dei pool proprio perche' erano andati male.
    # Quella e' la selezione che gonfia qualunque percentuale il loop 1 andra' a misurare.
    reg = {}
    try:
        reg = json.load(open(f"data/multichain/{CHAIN}/righe.json")).get("pool", {})
    except Exception:
        pass
    voluti = dict(reg)
    if os.environ.get("POPOLAZIONE", "1") == "1":
        try:
            basi = set(json.load(open("data/valute_base.json"))[CHAIN])
            cop = {k.lower(): v for k, v in
                   json.load(open(f"data/multichain/{CHAIN}/coppie.json")).get("coppie", {}).items()}
            n_pop = 0
            with gzip.open(f"data/multichain/{CHAIN}/censimento.jsonl.gz", "rt") as fo:
                for l in fo:
                    if not l.strip():
                        continue
                    d0 = json.loads(l)
                    if d0.get("scambi", 0) < 20:
                        continue
                    v = cop.get(d0["pool"])
                    if not v:
                        continue
                    t_0 = (v.get("t0") or "").lower()
                    t_1 = (v.get("t1") or "").lower()
                    if (t_0 in basi) == (t_1 in basi):
                        continue                  # o nessuno o entrambi: non e' la nostra popolazione
                    # QUANTO E' CONCENTRATA L'ATTIVITA' (19/09). Il censimento conta gli scambi su
                    # TUTTO l'intervallo dichiarato, che e' di settimane: un pool con 23 scambi
                    # sparsi su 1,4 milioni di blocchi soddisfa «>=20 scambi» ed e' un pool
                    # dormiente, non un evento. Misurato su sei pool a caso: quelli con arco stretto
                    # rendono 201 e 239 righe nelle prime ore, quelli con arco largo UNA.
                    # E qui c'e' la scoperta che conta: i pool che GIA' abbiamo sono in maggioranza
                    # i diluiti (14,2% di copertura), mentre dei concentrati abbiamo il 4,0%. Ha una
                    # causa — il vecchio registro sceglieva i sopravvissuti con almeno 5 candele,
                    # cioe' i longevi — e una conseguenza: il picco breve, che e' come si presenta
                    # una memecoin che pompa, nel nostro archivio quasi non c'e'.
                    # Non cambio la definizione (quella si registra in DEFINIZIONE.md, non si sposta
                    # in un agente): cambio l'ORDINE, e prendo prima quelli concentrati.
                    arco_ore = (d0.get("ultimo", 0) - d0.get("primo", 0)) * SEC_BLOCCO / 3600.0
                    # L'ANCORA SUL BORDO NON E' UNA NASCITA (19/09). Il censimento vede un pool per
                    # la prima volta quando il suo intervallo comincia: se il pool scambiava GIA'
                    # prima, quel blocco non e' la sua nascita ma il bordo della nostra finestra, e
                    # raccogliere otto ore da li' da' una fetta arbitraria di mezza vita — utile
                    # quanto aprire un libro a caso e leggerne una pagina.
                    # Misurato: capita al 36% della popolazione di base e all'8% di robinhood.
                    # Non li scarto (i dati servono comunque, e sono marcati «ancora: censimento»),
                    # ma vanno DOPO: prima si prendono quelli di cui vediamo davvero l'inizio.
                    try:
                        _da = int((d0.get("intervallo") or "0-0").split("-")[0])
                    except Exception:
                        _da = 0
                    sul_bordo = 1 if (_da and d0.get("primo", 0) - _da < 2000) else 0
                    voluti.setdefault(d0["pool"], {"ent": None, "t0": None,
                                                   "arco_ore": round(arco_ore, 2),
                                                   "bordo": sul_bordo})
                    n_pop += 1
            print(f"BUCO | {CHAIN}: popolazione definita {n_pop} pool "
                  f"(registro {len(reg)}, da cercare in tutto {len(voluti)})", flush=True)
        except Exception as e:
            print(f"BUCO | {CHAIN}: popolazione non leggibile ({type(e).__name__}), "
                  f"resto sul registro", flush=True)
    reg = voluti
    bersagli = []
    sporche = set()
    try:
        for x in json.load(open("data/quarantena_registro.json"))["non_sono_pool"].get(CHAIN, []):
            sporche.add(x.lower())
    except Exception:
        pass
    for p in reg:
        pl = p.lower()
        if pl in sporche:
            continue                      # gia' verificato che non e' un pool: non si ritenta
        # BASTA SAPERE SE IL FILE C'E', NON QUANTE RIGHE HA (19/09). Qui si aprivano e si
        # DECOMPRIMEVANO tutti i file per contarne le righe: con 8.778 bersagli vuol dire leggere
        # un centinaio di megabyte a ogni giro, e infatti il budget finiva nel censimento invece che
        # nella raccolta — un pool visitato in tre minuti. La domanda e' «di questo pool abbiamo
        # qualcosa?», e a quella risponde l'esistenza di un file non vuoto.
        if not mia(pl):
            continue
        if not ha_qualcosa(pl):
            bersagli.append(pl)
    # l'elenco storico resta come semenza, se c'e' ancora qualcosa dentro che non abbiamo preso
    if os.path.exists(ELENCO):
        try:
            for p in json.load(open(ELENCO)).get("buco_vero", []):
                if p not in bersagli and p not in sporche:
                    bersagli.append(p)
        except Exception:
            pass
    # I CONCENTRATI PER PRIMI: rendono righe utili subito, i diluiti ne rendono una a testa.
    bersagli.sort(key=lambda p: ((reg.get(p) or {}).get("bordo", 0),
                                 (reg.get(p) or {}).get("arco_ore") or 1e9))
    if not bersagli:
        print(f"BUCO | {CHAIN}: nessun pool del registro e' senza righe. Niente da recuperare.",
              flush=True)
        return
    print(f"BUCO | {CHAIN}: {len(bersagli)} pool nel registro senza una riga", flush=True)
    nasc = {}
    try:
        for p, d in json.load(open(f"data/multichain/{CHAIN}/nascita_vera.json"))["nascite"].items():
            if d.get("fonte") == "catena" and (d.get("bn") or d.get("ts")):
                nasc[p.lower()] = d
    except Exception:
        pass
    punta, _ = rpc("eth_blockNumber", [])
    if not punta:
        print("BUCO | il nodo non risponde", flush=True)
        return
    punta = int(punta, 16)
    b1, _ = rpc("eth_getBlockByNumber", [hex(punta), False])
    b0, _ = rpc("eth_getBlockByNumber", [hex(punta - 100000), False])
    if not b1 or not b0:
        print("BUCO | non riesco a leggere il ritmo dei blocchi", flush=True)
        return
    ora = int(b1["timestamp"], 16)
    sec = (ora - int(b0["timestamp"], 16)) / 100000.0

    fatti = set()
    vuoti = set()
    if os.path.exists(CK):
        try:
            _ck = json.load(open(CK))
            fatti = set(_ck.get("fatti", []))
            # VUOTO VERIFICATO E' DIVERSO DA MAI LETTO (20/09). Un pool che il nodo ci ha lasciato
            # leggere per intero e che in quella finestra non aveva scambi e' una RISPOSTA, non un
            # fallimento: va ricordata, altrimenti lo si ritenta a ogni giro per sempre.
            # Senza questa distinzione le fette riaprivano 505 pool a testa ogni volta e ci
            # bruciavano dentro il budget invece di andare avanti.
            vuoti = set(_ck.get("vuoti", []))
        except Exception:
            fatti = set(); vuoti = set()
    # UN POOL SEGNATO «FATTO» MA SENZA DATI TORNA IN CODA (19/09). Il segnalibro dice cosa abbiamo
    # VISITATO, non cosa abbiamo OTTENUTO: finche' le due cose venivano confuse, 3.287 pool chiusi
    # da una lettura fallita erano persi per sempre. Qui il segnalibro si rilegge alla luce di cio'
    # che c'e' davvero su disco, quindi i giri vecchi si correggono da soli senza toccare i file.
    _riaperti = 0
    for _p in list(fatti):
        _n = 0
        for _c in ("storico", "vivo"):
            _f = f"data/multichain/{CHAIN}/{_c}/{_p}.jsonl.gz"
            if os.path.exists(_f):
                try:
                    _n += sum(1 for _l in gzip.open(_f, "rt") if _l.strip())
                except Exception:
                    pass
        # SI RIAPRE SOLO CHI NON HA PROPRIO NIENTE (20/09, notte — correzione di una mia modifica
        # di ieri). La soglia era «meno di 20 righe», cioe' la stessa che uso per dire «usabile».
        # Ma un pool con 5 righe e' stato letto benissimo: in quella finestra aveva cinque scambi.
        # Riaprirlo a ogni giro significa rifare sempre gli stessi pool poveri — e siccome sono
        # ordinati per primi (arco stretto), le fette ci restavano dentro e ai pool nuovi non
        # arrivavano mai. Misurato: +108 pool usabili in mezz'ora invece dei ~1.500 attesi dal
        # ritmo di scrittura osservato.
        # Zero righe vuol dire «non l'abbiamo mai letto davvero»; da una a diciannove vuol dire
        # «letto, e tanto c'era». Confondere le due cose e' la stessa famiglia di errori di questi
        # giorni: scambiare una misura riuscita per un tentativo fallito.
        if _n == 0 and _p not in vuoti:
            fatti.discard(_p)
            _riaperti += 1
    if _riaperti:
        print(f"BUCO | {CHAIN}: {_riaperti} pool erano segnati fatti senza avere dati: li riapro",
              flush=True)

    # dove il censimento ha visto ogni pool la prima e l'ultima volta: la prima e' l'ancora di
    # ripiego, l'ultima dice fin dove vale la pena scavare
    primo_censimento = {}
    ultimo_censimento = {}
    fine_intervallo = {}
    try:
        with gzip.open(f"data/multichain/{CHAIN}/censimento.jsonl.gz", "rt") as fo:
            for l in fo:
                if l.strip():
                    d0 = json.loads(l)
                    if d0.get("primo"):
                        primo_censimento[d0["pool"]] = int(d0["primo"])
                    if d0.get("ultimo"):
                        ultimo_censimento[d0["pool"]] = int(d0["ultimo"])
                    try:
                        fine_intervallo[d0["pool"]] = int((d0.get("intervallo") or "0-0").split("-")[1])
                    except Exception:
                        pass
    except Exception:
        pass

    per_pool = {}
    presi = saltati = 0
    for pool in bersagli:
        if time.time() - t0 > BUDGET:
            break
        if pool in fatti:
            continue
        d = nasc.get(pool)
        if not d:
            # L'ANCORA DI RIPIEGO VIENE DAL CENSIMENTO (19/09). Senza, questo agente saltava 6.434
            # bersagli su 6.536: la nascita risolta dalla catena ce l'ha solo il vecchio registro, e
            # la popolazione definita e' fatta quasi tutta di pool che il registro non ha mai visto.
            # Il censimento pero' sa in quale blocco li ha visti scambiare la PRIMA VOLTA dentro
            # l'intervallo dichiarato. Non e' la nascita — se il pool e' nato prima dell'intervallo,
            # il suo vero inizio e' altrove — ma e' un punto di partenza onesto, e le righe raccolte
            # cosi' vengono marcate «ancora: censimento» invece di spacciarsi per nascita.
            # nascita_vera.py potra' raffinarle dopo; intanto i dati entrano, invece di non entrare.
            b0 = primo_censimento.get(pool)
            if not b0:
                saltati += 1
                continue
            d = {"bn": b0, "ripiego": True}
        # la nascita in blocchi: quella dichiarata se c'e', altrimenti dal suo istante vero
        bn0 = int(d["bn"]) if d.get("bn") else int(punta - (ora - int(d["ts"])) / max(0.01, sec))
        fine = bn0 + int(ORE * 3600 / max(0.01, sec))
        # NON SI SCAVA OLTRE DOVE IL POOL HA SMESSO (20/09). Scansionavamo sempre otto ore piene —
        # su robinhood sono 271.000 blocchi, cioe' 14 chiamate — anche per pool che il censimento
        # ha visto scambiare per venti minuti e poi piu' nulla. Le chiamate dopo l'ultimo scambio
        # tornano vuote per costruzione: sono tempo speso a farsi dire che non c'e' niente.
        # Il censimento sa gia' in quale blocco il pool e' stato visto l'ultima volta. Ci si ferma
        # li', con un margine per non tagliare la coda.
        # MA SOLO SE QUELL'«ULTIMO» E' DAVVERO LA FINE. Il censimento vede fino a dove arriva il
        # suo intervallo: se il pool stava ancora scambiando quando l'intervallo e' finito, il suo
        # «ultimo» e' il bordo della nostra finestra, non la fine della sua attivita' — e tagliare
        # li' vorrebbe dire buttare via dati veri per andare piu' veloci.
        # Si accorcia solo per i pool che hanno smesso BEN PRIMA del bordo.
        _ult = ultimo_censimento.get(pool)
        _fin_iv = fine_intervallo.get(pool)
        if (_ult and _fin_iv and _ult + 4 * AMPIEZZA < _fin_iv
                and _ult + 2 * AMPIEZZA < fine):
            fine = _ult + 2 * AMPIEZZA
        righe = []
        rotto = False
        attese = 0
        ampiezza = AMPIEZZA
        cur = bn0
        # NESSUN POOL SI MANGIA IL BUDGET DI TUTTI (21/09). Misurato: una fetta visitava UN pool in
        # 196 secondi, mentre leggere i suoi log costa 0,6s e i suoi istanti altrettanto. Il tempo
        # se ne andava in una scansione enorme — un pool con nascita lontana fa centinaia di
        # finestre — e gli altri tremila bersagli non venivano nemmeno guardati.
        # Con un tetto di finestre per giro il pool resta aperto e riprende dal punto in cui si e'
        # fermato, mentre gli altri hanno la loro occasione. La raccolta e' un lavoro a turni, non
        # una gara a chi finisce per primo.
        _finestre = 0
        while cur < fine and time.time() - t0 < BUDGET and _finestre < 40:
            _finestre += 1
            a = min(fine, cur + ampiezza)
            f = {"fromBlock": hex(cur), "toBlock": hex(a)}
            if len(pool) == 66:
                f["topics"] = [SWAP_V4, pool]
            else:
                f["address"] = pool
                f["topics"] = [[SWAP_V2, SWAP_V3, SWAP_V4]]
            log, err = rpc("eth_getLogs", [f])
            if log is None and err and ("429" in str(err) or "Too Many" in str(err)):
                # 429 NON E' «TROPPO LARGO», E' «TROPPO IN FRETTA» (20/09, notte).
                # Qui si stringeva la finestra a ogni rifiuto, che contro un limite di FREQUENZA
                # non serve a nulla: dopo quattro dimezzamenti il pool veniva dichiarato illeggibile
                # e lasciato aperto, per poi essere ritentato al giro dopo e fallire di nuovo.
                # E' cosi' che 2.255 pool concentrati sono rimasti a zero righe pur avendo centinaia
                # di scambi sulla catena, e che le fette bruciavano il budget rifacendo sempre gli
                # stessi. Misurato: lo stesso pool rifiutato a 20.000 blocchi risponde con 68 log a
                # 5.000 — non perche' la finestra sia troppo larga, ma perche' nel frattempo e'
                # passato mezzo secondo.
                # La stessa lezione era gia' scritta nel collettore storico il 14/09: aspettare e'
                # gratis, perdere un evento no. Non l'avevo applicata qui.
                attese += 1
                if attese > 8:
                    rotto = True
                    break
                time.sleep(min(30, 3 * attese))
                continue                      # STESSA finestra, solo piu' tardi
            if log is None:
                # UN RIFIUTO DEL NODO NON E' UN POOL VUOTO (19/09). Qui si usciva dal ciclo e subito
                # sotto, non avendo righe, il pool veniva ARCHIVIATO COME FATTO: mai piu' ritentato.
                # Misurato su robinhood: 3.287 pool concentrati chiusi con mediana ZERO righe,
                # mentre il censimento ne dichiarava 96 scambi. Non erano vuoti, era la lettura a
                # fallire — e il segnalibro li ha sepolti.
                # E' la stessa famiglia di difetti di questi giorni: «non tentato» scambiato per
                # «verificato». Adesso prima si stringe la finestra e si riprova, e se proprio non
                # si legge il pool resta APERTO per il giro prossimo.
                if ampiezza > 500:
                    ampiezza = max(500, ampiezza // 2)
                    continue
                rotto = True
                break
            righe.extend(log)
            cur = a + 1
            time.sleep(0.15)
        if not righe:
            if not rotto:
                fatti.add(pool)      # letto davvero, e davvero non c'era niente
                vuoti.add(pool)      # e lo si ricorda, per non ritentarlo in eterno
            continue
        # IL TETTO SI APPLICA PRIMA DI CHIEDERE I TEMPI, NON DOPO (21/09). Qui si chiedeva l'istante
        # di OGNI log trovato nella finestra — che possono essere migliaia — e solo in scrittura se
        # ne tenevano 300 per via del tetto per pool. Cronometrato: 141 secondi sugli istanti contro
        # 13 sulla scansione, per UN pool.
        # I log arrivano gia' in ordine di blocco dalla catena, e il tetto tiene i PRIMI: quindi
        # tutto cio' che sta oltre il trecentesimo non verra' scritto comunque, e chiederne il tempo
        # e' lavoro pagato per essere buttato.
        righe.sort(key=lambda l: (int(l["blockNumber"], 16), int(l.get("logIndex", "0x0"), 16)))
        _gia = 0
        for _c in ("storico", "vivo"):
            _f = f"data/multichain/{CHAIN}/{_c}/{pool}.jsonl.gz"
            if os.path.exists(_f):
                try:
                    _gia += sum(1 for _l in gzip.open(_f, "rt") if _l.strip())
                except Exception:
                    pass
        # CENTOVENTI RIGHE, NON TRECENTO (21/09, per il solo popolatore). Misurato sul campo: la
        # mediana e' 82 righe per pool e solo il 28% arriva al tetto — quindi abbassarlo tocca poco
        # piu' di un pool su quattro, e proprio quelli che costano di piu' in tempo.
        # La domanda a cui questo archivio deve rispondere e' «CHI E' ENTRATO PRIMA, e in che
        # ordine»: i primi centoventi scambi la esauriscono. Tutto il resto e' tempo speso a
        # chiedere istanti per righe che nessuna analisi d'entrata guardera'.
        # Sul cloud le fette si contendono lo stesso nodo e ogni pool costa 250 secondi: a 300
        # righe i 4.059 concentrati mancanti di robinhood sono cinque giorni, a 120 circa tre.
        # Lo storico mantiene il suo tetto di 300: qui si abbassa solo la soglia con cui il
        # POPOLATORE decide quanto scaricare per un pool nuovo.
        _spazio = max(0, int(os.environ.get("TETTO_BUCO", 120)) - _gia)
        if not _spazio:
            fatti.add(pool)
            continue
        righe = righe[:_spazio]
        _blocchi = {int(l["blockNumber"], 16) for l in righe}
        ts = istanti(_blocchi)
        # SI SCRIVE QUELLO CHE HA IL TEMPO, E IL POOL RESTA APERTO PER IL RESTO (21/09).
        # Prima scartavo l'intero pool se mancava piu' di un decimo degli istanti: con un nodo che
        # rifiuta a intermittenza — misurato: gruppi da 100 passano due volte e poi no, da 50 mai,
        # da 20 sempre — quasi nessun pool superava quella soglia, e si buttavano via log gia'
        # scaricati. Tre fette hanno visitato 1.172 pool scrivendo 183 righe.
        # Le righe si deduplicano per (transazione, indice di log), quindi scriverne una parte ora e
        # il resto al giro prossimo non crea doppioni: e' solo un pool che si completa in due volte.
        _completo = len(ts) >= len(_blocchi)
        for l in righe:
            bn = int(l["blockNumber"], 16)
            if bn not in ts:
                continue                      # senza istante vero non si scrive: meglio mancante
            fi = firma(l["topics"][0], l.get("data", "0x"), l["topics"])
            if not fi:
                continue
            per_pool.setdefault(pool, []).append(
                {"acq": int(time.time()), "ts": ts[bn], "blocco": bn,
                 "tx": l.get("transactionHash"), "bh": l.get("blockHash"),
                 "ti": int(l.get("transactionIndex", "0x0"), 16),
                 "li": int(l.get("logIndex", "0x0"), 16),
                 "classe": "recupero-buco",
                 # gli istanti qui sono chiesti al nodo, non interpolati: lo si dichiara nel record
                 # cosi' la riparazione sa che non c'e' niente da fare (20/09)
                 "orario": "catena",
                 # LA VERIFICA SI TIMBRA QUANDO AVVIENE (22/09). Finora l'unica prova che un
                 # istante venisse dalla catena era l'etichetta «orario: catena» — che pero'
                 # la scriveva anche il codice vecchio che interpolava. Misurato contro la
                 # catena: il 17% dei record di base era sbagliato PUR portando quell'etichetta.
                 # Da qui in avanti chi chiede davvero l'orario al nodo lo dichiara con una
                 # data. Cio' che non ha la data non e' verificato: e' soltanto etichettato.
                 "ver": int(time.time()),
                 "ancora": "censimento" if d.get("ripiego") else "nascita", "w": fi["w"], "w_sem": fi.get("w_sem"),
                 "a0": fi["a0"], "a1": fi["a1"], "dex": fi["v"],
                 "mgr": l.get("address", "").lower(), "fonte": "catena"})
        if not rotto and _completo:
            fatti.add(pool)
        presi += 1

    nuovi = scarica_su_disco(CHAIN, per_pool) if per_pool else 0
    try:
        os.makedirs(os.path.dirname(CK), exist_ok=True)
        json.dump({"fatti": sorted(fatti), "vuoti": sorted(vuoti),
                   "quando": int(time.time())}, open(CK, "w"))
    except Exception:
        pass
    print(f"BUCO | {presi} pool visitati, {nuovi} righe nuove scritte | "
          f"{len(fatti)}/{len(bersagli)} dell'elenco chiusi"
          + (f" | {saltati} senza nascita dalla catena: non li tocco" if saltati else ""), flush=True)


if __name__ == "__main__":
    main()
