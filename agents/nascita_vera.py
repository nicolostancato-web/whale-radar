"""NASCITA VERA — quando un pool e' nato davvero, chiesto alla catena.

IL PROBLEMA (17/09, notte, dopo sei accertamenti a vuoto sul recupero). Tutto il database usa come
«nascita» di un pool il primo istante delle sue CANDELE. Ma le candele cominciano quando
GeckoTerminal SI ACCORGE del pool, non quando il pool nasce.

Misurato su sei pool, confrontando candele ed evento `Initialize` della catena:
    +3,1h   +9,7h   0,0h   +8,5h   +3,4h   0,0h
    scarto mediano **+3,26 ore**, e DUE SU SEI sforano completamente la finestra di sei ore.

Noi teniamo «le prime sei ore di vita». Calcolate da un istante in ritardo di tre ore, quella
finestra e' spostata in avanti: per una parte dei pool le vere prime sei ore sono gia' finite
prima che la nostra finestra si apra. Ecco perche' il recupero faceva 16.837 chiamate senza
raccogliere niente — cercava ogni pool nel posto sbagliato.

E NON RIGUARDA SOLO IL RECUPERO. La stessa nascita da candele la usano l'audit di integrita', la
classificazione delle esclusioni e la misura «nascite possedute». Sono tutte spostate.

LA FONTE GIUSTA. Per i pool V4 l'evento `Initialize` dice l'istante esatto, ed e' cosi' selettivo
che una sola chiamata copre l'intera catena. Per i pool con indirizzo (V2/V3) l'evento equivalente
va ancora trovato: per quelli resta la candela, dichiarata come stima.

SI SCRIVE DA DOVE VIENE. Ogni nascita porta `fonte`: «catena» quando e' l'istante vero, «candele»
quando e' la stima. Un dato che non dice da dove viene costringe chi lo usa a fidarsi, ed e'
esattamente cosi' che abbiamo passato due giorni a inseguire numeri che sembravano sensati.
"""
import gzip
import json
import os
import time
import urllib.request

INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
RPC = {"base": "https://mainnet.base.org",
       "robinhood": "https://rpc.mainnet.chain.robinhood.com"}
CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = int(os.environ.get("BUDGET_SEC", 400))
OUT = f"data/multichain/{CHAIN}/nascita_vera.json"
t0 = time.time()


def rpc(url, metodo, params, tentativi=4, to=120):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    attesa = 4
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=to) as x:
                d = json.load(x)
            if "error" in d:
                return None, str(d["error"])[:60]
            return d.get("result"), None
        except Exception as e:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "esauriti"


def main():
    url = RPC.get(CHAIN)
    rf = f"data/multichain/{CHAIN}/righe.json"
    if not url or not os.path.exists(rf):
        print(f"NASCITA | {CHAIN}: manca il nodo o il registro", flush=True)
        return
    voluti = {k.lower() for k in json.load(open(rf)).get("pool", {})}
    note = {}
    if os.path.exists(OUT):
        try:
            note = json.load(open(OUT)).get("nascite", {})
        except Exception:
            note = {}
    # SI PULISCE DA SOLO, PERCHE' DA FUORI NON SI PUO' (17/09). Avevo tolto a mano 18 nascite
    # prodotte dalla versione che non distingueva i cammini troncati. Sono tornate al primo giro:
    # la corsia spinge con `-X ours`, quindi la SUA copia dei file dati vince sempre sui conflitti,
    # e ogni correzione fatta da fuori viene annullata.
    # Non e' un difetto della corsia — e' giusto che vinca chi raccoglie. Ma vuol dire che una
    # riparazione dei dati, per durare, deve stare DENTRO l'agente che quei dati li scrive.
    # Qui: i record col metodo «primo scambio» che non dichiarano se il cammino si e' concluso
    # vengono dalla versione vecchia. Non sono sbagliati per certo: sono ingiudicabili, e una cosa
    # ingiudicabile ti fa credere di sapere. Si buttano e si rifanno.
    ingiudicabili = [p for p, d in note.items()
                     if d.get("metodo") == "primo scambio" and "confermato" not in d]
    for p in ingiudicabili:
        del note[p]
    if ingiudicabili:
        print(f"NASCITA | {CHAIN}: buttate {len(ingiudicabili)} nascite ingiudicabili "
              f"(prodotte prima del controllo sul troncamento), verranno rifatte", flush=True)
    manca = [p for p in voluti if p not in note and len(p) == 66]
    print(f"NASCITA | {CHAIN}: {len(voluti)} pool, {len(note)} nascite vere note, "
          f"mancano {len(manca)} pool V4", flush=True)
    ind_da_fare = [x for x in voluti if x not in note and len(x) == 42]
    if not manca and not ind_da_fare:
        print(f"NASCITA | {CHAIN}: tutte le nascite risolte", flush=True)
        return
    # NON USCIRE PERCHE' UN SOLO TIPO E' FINITO (17/09). L'uscita anticipata guardava solo i pool
    # V4: finiti quelli, l'agente se ne andava e la sezione dei pool con indirizzo — meta' del
    # lavoro rimasto su robinhood — non veniva mai raggiunta. Il messaggio diceva «mancano 0 pool
    # V4», che era vero e completamente fuorviante.
    print(f"NASCITA | {CHAIN}: mancano anche {len(ind_da_fare)} pool con indirizzo", flush=True)
    punta, err = rpc(url, "eth_blockNumber", [])
    if not punta:
        print(f"NASCITA | {CHAIN}: il nodo non risponde ({err})", flush=True)
        return
    punta = int(punta, 16)

    # la cache degli istanti di blocco: molti pool nascono nello stesso blocco
    istante = {}
    nuovi = scarti = 0
    somma_scarto = []
    # la nascita secondo le candele, per misurare quanto sbagliava
    candele = {}
    for d in ("candles", "pulse"):
        dd = f"data/multichain/{CHAIN}/{d}"
        if not os.path.isdir(dd):
            continue
        for fn in os.listdir(dd):
            a = fn.split(".")[0].lower()
            if a in candele:
                continue
            try:
                for l in gzip.open(os.path.join(dd, fn), "rt"):
                    if l.strip():
                        d0 = json.loads(l)
                        v = d0.get("t0") or d0.get("ts")
                        if v:
                            candele[a] = int(v)
                        break
            except Exception:
                pass

    # DUE STRADE, PERCHE' I DUE NODI NON SONO UGUALI (17/09, misurato).
    #   robinhood accetta il filtro Initialize+id su TUTTA la catena in una chiamata: una query
    #   per pool, semplice e precisa.
    #   base risponde 413 su qualunque intervallo largo, anche col filtro piu' selettivo, ma regge
    #   2.000 blocchi. Una query per pool costerebbe migliaia di chiamate a pool.
    # Quindi su base si fa il contrario: UNA scansione all'indietro che raccoglie le nascite di
    # TUTTI i pool insieme. Lo stesso mestiere dello scopritore, esteso indietro nel tempo.
    # Adattare la strategia al nodo invece di forzare la stessa ovunque e' quello che mi ha fatto
    # perdere mezza giornata sulle coppie di token, quando avevo dedotto «base non fa i lotti» da
    # un solo tentativo.
    ck_scan = f"data/multichain/{CHAIN}/nascita_scan_ckpt.json"
    if CHAIN == "base":
        voluti_v4 = {p for p in manca}
        cur = punta
        if os.path.exists(ck_scan):
            try:
                cur = int(json.load(open(ck_scan)).get("cur") or punta)
            except Exception:
                cur = punta
        ampiezza = 2000
        # LA SCANSIONE NON SI MANGIA TUTTO IL TEMPO (17/09). Girava finche' c'era budget, quindi
        # su base non finiva MAI e la sezione dei pool con indirizzo — 328 pool — non veniva mai
        # raggiunta: zero tentativi, giro dopo giro, in silenzio.
        # Non era un blocco: era fame. Un pezzo che lavora bene e senza limite affama gli altri, e
        # dal di fuori sembra che gli altri non funzionino. Adesso la scansione ha il 60% del
        # tempo, il resto resta a chi viene dopo.
        while cur > 1 and time.time() - t0 < BUDGET * 0.6:
            da = max(1, cur - ampiezza)
            log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(cur),
                                                 "topics": [INIT]}])
            if log is None:
                if ampiezza > 250:
                    ampiezza //= 2
                    continue
                cur = da - 1
                time.sleep(1)
                continue
            for l in log:
                tp = l.get("topics") or []
                if len(tp) < 2:
                    continue
                pid = tp[1].lower()
                if pid not in voluti_v4 or pid in note:
                    continue
                bn = int(l["blockNumber"], 16)
                if bn not in istante:
                    b, _e = rpc(url, "eth_getBlockByNumber", [hex(bn), False])
                    if not b:
                        continue
                    istante[bn] = int(b["timestamp"], 16)
                vero = istante[bn]
                stima = candele.get(pid)
                note[pid] = {"acq": int(time.time()), "fonte": "catena", "ts": vero, "blocco": bn,
                             "ts_candele": stima,
                             "scarto_ore": round((stima - vero) / 3600, 2) if stima else None}
                if stima:
                    somma_scarto.append((stima - vero) / 3600)
                    if abs(stima - vero) > 6 * 3600:
                        scarti += 1
                nuovi += 1
            cur = da - 1
            try:
                json.dump({"cur": cur, "acq": int(time.time())}, open(ck_scan, "w"))
            except Exception:
                pass
            time.sleep(0.3)
        manca = []          # su base si e' fatta la scansione, non la lista

    for p in manca:
        if time.time() - t0 > BUDGET:
            break
        # UNA CHIAMATA SOLA SU TUTTA LA CATENA: il filtro Initialize+id e' selettivo al massimo
        log, err = rpc(url, "eth_getLogs", [{"fromBlock": "0x1", "toBlock": hex(punta),
                                             "topics": [INIT, p]}])
        if log is None:
            time.sleep(2)
            continue
        if not log:
            note[p] = {"acq": int(time.time()), "fonte": "assente",
                       "motivo": "nessun Initialize: non e' un pool V4 di questo PoolManager"}
            continue
        bn = int(log[0]["blockNumber"], 16)
        if bn not in istante:
            b, _e = rpc(url, "eth_getBlockByNumber", [hex(bn), False])
            if not b:
                time.sleep(2)
                continue
            istante[bn] = int(b["timestamp"], 16)
        vero = istante[bn]
        stima = candele.get(p)
        note[p] = {"acq": int(time.time()), "fonte": "catena", "ts": vero, "blocco": bn,
                   "ts_candele": stima,
                   "scarto_ore": round((stima - vero) / 3600, 2) if stima else None}
        if stima:
            somma_scarto.append((stima - vero) / 3600)
            if abs(stima - vero) > 6 * 3600:
                scarti += 1
        nuovi += 1
        time.sleep(0.6)

    # --- I POOL CON INDIRIZZO (V2/V3): niente Initialize, si cerca il PRIMO SCAMBIO ---
    #
    # PERCHE' ANCHE QUI (17/09). Avevo provato quattro pool con indirizzo: tre avevano la candela
    # esatta e uno sforava di 24 minuti, e stavo per dichiarare «per questi le candele vanno bene».
    # Poi ne ho provati dodici: SETTE su dodici hanno scambi PRIMA della candela, scarto mediano
    # +16,5 ore, cinque oltre la finestra. La conclusione su quattro casi era sbagliata — la terza
    # volta in ventiquattro ore che estrapolo da un campione minuscolo e prendo un granchio.
    #
    # COME. Questi pool non hanno un evento di creazione che sappiamo leggere, ma hanno gli scambi:
    # si parte dal blocco del nostro record piu' vecchio e si cammina ALL'INDIETRO a tratti, finche'
    # un tratto non torna vuoto. Il primo scambio trovato e' la nascita — o almeno il primo istante
    # in cui quel pool e' esistito per il mercato, che e' quello che ci serve.
    # Si parte dai NOSTRI blocchi e non dalla candela per non pagare una bisezione a pool: il
    # blocco ce l'abbiamo gia' su disco, esatto, gratis.
    ind = [p for p in voluti if p not in note and len(p) == 42]
    for p in ind:
        if time.time() - t0 > BUDGET:
            break
        nostro_blocco = None
        for cart in ("storico", "vivo"):
            f = f"data/multichain/{CHAIN}/{cart}/{p}.jsonl.gz"
            if not os.path.exists(f):
                continue
            try:
                for l in gzip.open(f, "rt"):
                    if l.strip():
                        b_ = json.loads(l).get("blocco")
                        if b_ and (nostro_blocco is None or b_ < nostro_blocco):
                            nostro_blocco = b_
            except Exception:
                pass
        if not nostro_blocco:
            continue
        # IL PASSO RADDOPPIA, NON RESTA UGUALE (17/09). Camminavo all'indietro a tratti fissi da
        # centomila blocchi, con un tetto di ventiquattro: due milioni e quattro. Su robinhood, che
        # fa dieci blocchi al secondo, sono SESSANTASETTE ORE — e un pool che scambia da settimane
        # tronca sempre. Infatti: zero conferme su tutti i tentativi.
        # Raddoppiando il passo a ogni giro, dieci chiamate coprono cento milioni di blocchi invece
        # di un milione. Stessa ricerca, stesso risultato, costo che cresce col logaritmo invece
        # che con la distanza.
        primo = nostro_blocco
        cur = nostro_blocco
        confermato = False
        tratti = 0
        passo = 50_000
        for _ in range(16):
            da = max(1, cur - passo)
            passo = min(passo * 2, 8_000_000)
            log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(cur),
                                                 "address": p, "topics": [[SWAP_V2, SWAP_V3]]}])
            tratti += 1
            if log is None:
                break                       # il nodo non ha risposto: non si conclude niente
            if not log:
                confermato = True
                break                       # tratto VUOTO: prima di qui il pool non scambiava
            primo = min(int(l["blockNumber"], 16) for l in log)
            cur = da - 1
            if cur <= 1:
                confermato = True
                break                       # inizio della catena: piu' indietro non si va
            time.sleep(0.4)
        if primo not in istante:
            b, _e = rpc(url, "eth_getBlockByNumber", [hex(primo), False])
            if not b:
                continue
            istante[primo] = int(b["timestamp"], 16)
        vero = istante[primo]
        stima = candele.get(p)
        # SI DICHIARA SE IL CAMMINO E' FINITO O E' STATO TRONCATO (17/09). Il cammino all'indietro
        # si ferma quando un tratto torna vuoto — li' il pool non scambiava ancora, e la nascita e'
        # certa. Ma si ferma anche quando finiscono i tratti concessi: in quel caso quello che
        # chiamo «primo scambio» e' soltanto il bordo della MIA ricerca, non l'inizio del pool.
        # E' esattamente il difetto della candela, in versione mia: un numero che sembra una
        # nascita e invece e' il punto in cui ho smesso di guardare. Se non lo dichiarassi, fra un
        # mese nessuno saprebbe distinguere i due casi — e ci costruirebbe sopra.
        note[p] = {"acq": int(time.time()),
                   "fonte": "catena" if confermato else "catena-non-confermata",
                   "ts": vero, "blocco": primo, "ts_candele": stima,
                   "metodo": "primo scambio", "confermato": confermato, "tratti": tratti,
                   "scarto_ore": round((stima - vero) / 3600, 2) if stima else None}
        if not confermato:
            continue                        # non entra nelle statistiche: non e' una nascita
        if stima:
            somma_scarto.append((stima - vero) / 3600)
            if abs(stima - vero) > 6 * 3600:
                scarti += 1
        nuovi += 1
        time.sleep(0.4)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"acq": int(time.time()), "n": len(note), "nascite": note}, open(OUT, "w"))
    if somma_scarto:
        somma_scarto.sort()
        mediano = somma_scarto[len(somma_scarto) // 2]
        print(f"NASCITA | {CHAIN}: +{nuovi} nascite vere ({len(note)} in tutto) | "
              f"le candele sbagliavano di {mediano:+.2f} ore (mediana) | "
              f"oltre la finestra di 6 ore: {scarti}/{len(somma_scarto)}", flush=True)
    else:
        print(f"NASCITA | {CHAIN}: +{nuovi} nascite vere ({len(note)} in tutto)", flush=True)


if __name__ == "__main__":
    main()
