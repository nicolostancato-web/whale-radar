#!/usr/bin/env python3
"""
STORICO_EVM — lo storico COMPLETO degli scambi, dalla catena, gratis.

IL PROBLEMA CHE RISOLVE, ed e' vecchio di mesi. Le fonti gratuite (GeckoTerminal) restituiscono solo
gli ultimi ~300 scambi di un pool: per un token maturo i primi acquisti — quelli che dicono CHI e'
entrato per primo, in che ordine, con che tempi — non esistono piu'. Su questo limite ci siamo
arenati per mesi, e l'audit del 14/09 ha mostrato che e' esattamente il dato che ci manca per
cercare l'edge dove potrebbe essere.

LA SCOPERTA (14/09): quel limite e' della FONTE, non della catena. Sulla catena c'e' tutto, per
sempre. Sbagliavamo la domanda: chiedevamo **un pool alla volta** — e cosi' il nodo pubblico rifiuta
(413) perche' deve cercare in milioni di blocchi. Chiedendo invece **una fascia di blocchi per tutti
i pool insieme**, filtrando per tipo di evento, risponde subito e restituisce OGNI scambio di OGNI
pool in quella fascia.

I NUMERI MISURATI:
  Base       100 blocchi in 0,9s -> 2.175 swap da 460 pool | un mese di storia = 3,4 ore
  Robinhood  500 blocchi in 1,0s -> 2.312 swap da 298 pool | un mese di storia = 14,5 ore
Con sei corsie in parallelo: Base 36 minuti, Robinhood 2,4 ore. **A costo zero.**

COSA CATTURA, e cosa no. Cattura i fatti che non si possono ricostruire dopo: istante, pool, wallet,
direzione e quantita' grezze dei due lati. NON calcola il valore in dollari: per quello servirebbe il
prezzo del token quotato a quell'istante, e preferisco lasciare il campo vuoto piuttosto che riempirlo
con una stima travestita da misura. Le domande che l'audit indica come importanti — chi compra, in
che ordine, con che tempi, quanto concentrato — si rispondono senza i dollari.

Scrive in data/multichain/<chain>/storico/<pool>.jsonl.gz, separato dagli scambi della fonte
gratuita: due origini diverse non si mescolano senza dirlo.
"""
import json, gzip, os, time, urllib.request

SWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
# SWAP STILE V4 (15/09). Su Robinhood quasi tutti i pool vivono dentro UN SOLO contratto (il
# "PoolManager"), quindi il mittente del log e' sempre lo stesso e il pool NON si legge da li':
# sta dentro l'evento, in topics[1]. Per questo lo scavo trovava 158 pool e nessuno era fra quelli
# che sappiamo valutare — cercavo l'identita' nel posto sbagliato.
# La firma non l'ho presa da una documentazione: l'ho trovata guardando i log. Un solo mittente,
# 1.107 eventi in 300 blocchi, topics[1] che coincide con i nostri pool, e due quantita' con segno
# opposto nei dati — cioe' uno scambio.
SWAP_V4 = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
RPC = {"base": ("https://mainnet.base.org", 100), "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 500)}
CHAIN = os.environ.get("CHAIN", "base")
BUDGET = int(os.environ.get("BUDGET_SEC", 600))
FETTA = int(os.environ.get("FETTA", 0))       # quale porzione di storia tocca a questa corsia
FETTE = int(os.environ.get("FETTE", 1))       # in quante corsie e' divisa
GIORNI_FETTA = float(os.environ.get("GIORNI_FETTA", 3))   # quanti giorni di storia separano una fetta dall'altra
TETTO_POOL = int(os.environ.get("TETTO_POOL", 300))   # primi N scambi per pool: bastano a dire chi e' entrato prima
CK = lambda c: f"data/multichain/{c}/storico_ckpt.json"
t0 = time.time()


def rpc(url, metodo, params, tentativi=3):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    attesa = 2
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=45) as x:
                d = json.load(x)
            if "error" in d: return None, str(d["error"])[:80]
            return d.get("result"), None
        except Exception as e:
            if k < tentativi - 1: time.sleep(attesa); attesa *= 2; continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "esauriti i tentativi"


def firma(topic0, dati, topics):
    """Dal log grezzo ai fatti. Niente dollari: si tengono le quantita' dei due lati, cosi' come sono.

    LA SEMANTICA DEL WALLET VA DICHIARATA (15/09, imposto dalla revisione). Dire "wallet presenti al
    100%" misura la NON-NULLITA', non l'identita' economica: quel campo puo' essere un router, un
    aggregatore, un contratto, il destinatario o chi incassa le commissioni — non necessariamente
    chi ha DECISO lo scambio. E cambia significato fra le versioni del protocollo.
    Finche' non lo si dichiara, meta' delle variabili nuove poggia su un'identita' non giudicabile.
    Qui ogni record porta scritto da quale campo viene, cosi' chi analizza lo sa senza dedurlo."""
    w = "0x" + topics[-1][-40:] if len(topics) > 1 else None
    sem = {SWAP_V2: "v2:to", SWAP_V3: "v3:recipient", SWAP_V4: "v4:sender"}.get(topic0, "ignota")
    d = dati[2:] if dati.startswith("0x") else dati
    campi = [d[i:i + 64] for i in range(0, len(d), 64)]
    def i256(h):
        v = int(h, 16)
        return v - (1 << 256) if v >= (1 << 255) else v
    try:
        if topic0 == SWAP_V2 and len(campi) >= 4:
            a0i, a1i, a0o, a1o = (int(campi[i], 16) for i in range(4))
            # verso: se entra token0 ed esce token1, qualcuno ha venduto token0
            return {"w": w, "w_sem": sem, "a0": a0i - a0o, "a1": a1i - a1o, "v": 2}
        # SI TENGONO ANCHE IL PREZZO DEL POOL E LA SUA PROFONDITA' (26/09).
        # L'evento Swap di V3 e V4 porta, subito dopo le due quantita', `sqrtPriceX96` e
        # `liquidity`. Li decodificavamo e li buttavamo, e ci sono mancati per un mese:
        #  · `sq` e' il prezzo DEL POOL dopo lo scambio — uno solo, uguale per tutti, indipendente
        #    da chi ha colpito. Con questo l'uscita si puo' misurare a orologio («il prezzo due ore
        #    dopo») invece che sulla mediana delle stampe, che dipende da chi ha scambiato e quando.
        #  · `liq` e' la PROFONDITA': quanto il pool puo' assorbire. La notte del 26/09 ho scoperto
        #    che i prezzi a 10x scambiavano in mediana 32 dollari — una posizione vera non ci entra.
        #    Avevamo 33 caratteristiche e nessuna diceva quanto il pool potesse contenere, perche'
        #    il dato lo scartavamo qui, in questa funzione, due campi dopo quelli che tenevamo.
        # Vale solo per la raccolta da qui in avanti: lo storico andrebbe riletto, e costa chiamate.
        if topic0 == SWAP_V3 and len(campi) >= 2:
            r = {"w": w, "w_sem": sem, "a0": i256(campi[0]), "a1": i256(campi[1]), "v": 3}
            if len(campi) >= 4:
                r["sq"] = int(campi[2], 16)
                r["liq"] = int(campi[3], 16)
            return r
        if topic0 == SWAP_V4 and len(campi) >= 2:
            # stessa forma del V3 nei primi due campi: le due quantita' con segno
            r = {"w": w, "w_sem": sem, "a0": i256(campi[0]), "a1": i256(campi[1]), "v": 4}
            if len(campi) >= 4:
                r["sq"] = int(campi[2], 16)
                r["liq"] = int(campi[3], 16)
            return r
    except Exception:
        return None
    return None


def salva_e_spingi(etichetta):
    """SI SALVA STRADA FACENDO (14/09). La prima versione committava solo alla fine di tre ore: se
    il lavoro moriva — e nella prima notte sono morti tutti e sei dopo un minuto — spariva tutto.
    Chi raccoglie per ore e salva una volta sola scommette tre ore su un istante."""
    import subprocess
    subprocess.run('git config user.name "whale-radar-bot"; git config user.email '
                   '"bot@users.noreply.github.com"', shell=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if subprocess.run(f'git add -A && git commit -m "storico {etichetta}"', shell=True,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        return False                                    # niente di nuovo: non e' un errore
    for _ in range(8):
        subprocess.run('git pull --no-rebase --no-edit -X ours origin main', shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.run('git push origin main', shell=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return True
        time.sleep(6)
    print("STORICO_EVM | ATTENZIONE: non sono riuscito a spingere, i dati restano sul runner", flush=True)
    return False


def pota(CHAIN, quanti=400):
    """Riporta al tetto i file gia' scritti oltre misura.

    PERCHE' SERVE (14/09). Il tetto per pool e' arrivato DOPO che il primo salvataggio aveva gia'
    portato 780.000 scambi: una regola nuova non ripara il passato da sola. Qui si riscrivono i file
    troppo grassi tenendo i PRIMI scambi — quelli che dicono chi e' entrato per primo — e buttando
    la coda, che non risponde a nessuna domanda nostra.
    Si pota poco per volta: riscrivere migliaia di file in un giro solo bloccherebbe la raccolta."""
    import glob as _g
    fatti = tolti = 0
    for f in _g.glob(f"data/multichain/{CHAIN}/storico/*.jsonl.gz"):
        if fatti >= quanti: break
        try:
            righe = []
            for l in gzip.open(f, "rt"):
                if l.strip():
                    try: righe.append(json.loads(l))
                    except Exception: pass
            # UN SOLO FORMATO, NON DUE (15/09). I record raccolti prima di oggi non hanno il block
            # hash ne' l'indice della transazione: non si possono ordinare con precisione (piu'
            # scambi condividono lo stesso secondo) ne' si puo' accorgersi di una riorganizzazione
            # della catena. Tenerli sarebbe un database di cui bisogna RICORDARSI le eccezioni, e le
            # eccezioni che si ricordano oggi sono quelle che si dimenticano fra un mese.
            # Si buttano: la catena li ha ancora, e il collettore li riprende col formato completo.
            righe = [r for r in righe if r.get("bh")]
            # prima i doppioni, poi il tetto: un file puo' essere oltre misura PERCHE' e' doppio
            unici = {}
            for r in righe:
                unici.setdefault((r.get("tx"), r.get("li")), r)
            righe = sorted(unici.values(), key=lambda r: r.get("ts", 0))
            # Si riscrive se c'e' da tagliare OPPURE se c'erano doppioni: un file puo' essere
            # dentro il tetto e comunque sporco.
            originali = sum(1 for _ in gzip.open(f, "rt"))
            if len(righe) <= TETTO_POOL and len(righe) == originali:
                continue      # gia' pulito: stesso numero di righe, tutte col formato completo
            tenute = righe[:TETTO_POOL]
            tmp = f + ".tmp"
            with gzip.open(tmp, "wt") as fo:
                for r in tenute: fo.write(json.dumps(r) + "\n")
            os.replace(tmp, f)
            tolti += len(righe) - len(tenute); fatti += 1
        except Exception: pass
    if fatti:
        print(f"STORICO_EVM | potati {fatti} file, tolti {tolti} scambi oltre il tetto", flush=True)
    return fatti


def scarica_su_disco(CHAIN, per_pool, url=None, lotto=100):
    """Svuota il raccolto sui file. Torna quante righe nuove ha scritto.

    QUESTA FUNZIONE HA CHIAMATO SE STESSA (14/09). Avevo sostituito il blocco finale con una chiamata
    a questa funzione, ma la stessa sostituzione a stringa ha centrato anche il CORPO della funzione
    appena creata: sei lavori morti dopo dodici minuti con RecursionError. La prova locale durava
    45 secondi e non arrivava mai fin qui — ha superato senza toccare la riga rotta.
    Una modifica a stringa cieca e una prova che non percorre il tratto modificato sono due errori
    che si coprono a vicenda."""
    nuovi = 0
    for pool, righe in per_pool.items():
        p = f"data/multichain/{CHAIN}/storico/{pool}.jsonl.gz"
        visti = set(); esistenti = []
        if os.path.exists(p):
            try:
                for l in gzip.open(p, "rt"):
                    if l.strip():
                        try:
                            d0 = json.loads(l)
                            visti.add((d0.get("tx"), d0.get("li")))
                            esistenti.append(d0)
                        except Exception: pass
            except Exception: pass
        # SI RIPARA QUELLO CHE SI TOCCA (20/09). La riparazione degli istanti aveva una corsia sua,
        # e le sue correzioni NON SOPRAVVIVEVANO: misurato, ZERO file su tremila portavano il suo
        # marchio, su entrambe le chain. Il motivo e' strutturale — due corsie possiedono gli stessi
        # file, e chi raccoglie spinge con «-X ours» da un checkout vecchio, riscrivendo sopra le
        # riparazioni appena fatte. Quella gara una corsia separata non puo' vincerla.
        # Qui il file e' gia' in mano a chi lo possiede: gli istanti vecchi si correggono nello
        # stesso momento in cui si aggiungono i nuovi, e nessuno puo' sovrascriverli.
        # I record da riparare sono quelli senza «orario»: il loro ts veniva interpolato dalla punta
        # della catena e su robinhood sbagliava di ORE.
        # E SI RIPARA SOLO FINCHE' C'E' TEMPO (20/09). Senza questo limite la riparazione dentro
        # la scrittura ignora il budget: una prova con 120 secondi di budget ha girato oltre DIECI
        # MINUTI, perche' ogni file toccato chiedeva al nodo gli istanti di tutti i suoi record
        # vecchi. Un rimedio che sfonda il tempo del lavoro non e' un rimedio: e' un blocco.
        # La raccolta viene prima; la riparazione usa quello che avanza e riprende al giro dopo.
        riparati = 0
        if url and time.time() - t0 < BUDGET * 1.5:
            vecchi = [r for r in esistenti if not r.get("orario") and r.get("blocco")]
            if vecchi:
                veri_v = istanti_veri(url, {r["blocco"] for r in vecchi}, lotto)
                for r in vecchi:
                    v = veri_v.get(r["blocco"])
                    if v is None:
                        continue
                    r["ts"] = v
                    r["orario"] = "catena"
                    riparati += 1
        da_scrivere = [r for r in righe if (r.get("tx"), r.get("li")) not in visti]
        if not da_scrivere and not riparati: continue
        # IL TETTO PER POOL (14/09). Il primo salvataggio ha portato 780.000 scambi in dodici minuti:
        # a quel ritmo il repo supera il gigabyte prima dell'alba e muore. Ma la domanda dell'audit e'
        # "CHI e' entrato per primo, in che ordine": per rispondere bastano i PRIMI scambi di ogni
        # pool. Tutto quello che viene dopo e' peso che non risponde a niente.
        # Si tengono i primi TETTO per pool, e non si scrive oltre.
        gia = len(visti)
        if gia >= TETTO_POOL: continue
        da_scrivere = sorted(da_scrivere, key=lambda x: x["ts"])[:TETTO_POOL - gia]
        try:
            if riparati:
                # riscrittura intera: le correzioni stanno nei record vecchi, non in coda
                tmp = p + ".tmp"
                with gzip.open(tmp, "wt") as f:
                    for r in sorted(esistenti + da_scrivere,
                                    key=lambda x: (x.get("ts", 0), x.get("blocco", 0),
                                                   x.get("ti", 0), x.get("li", 0))):
                        f.write(json.dumps(r) + "\n")
                os.replace(tmp, p)
            elif da_scrivere:
                with gzip.open(p, "at") as f:
                    for r in sorted(da_scrivere, key=lambda x: (x["ts"], x.get("blocco", 0), x.get("ti", 0), x.get("li", 0))):
                        f.write(json.dumps(r) + "\n")
            nuovi += len(da_scrivere)
        except Exception: pass
    return nuovi


def istanti_veri(url, blocchi, lotto):
    """Gli istanti VERI dei blocchi chiesti, a gruppi. Mai interpolati (20/09).

    Qui l'istante si calcolava cosi':  ts = t_now - (ultimo - bn) * sec_blocco
    cioe' partendo dalla punta della catena e tornando indietro col tempo MEDIO per blocco. Su base
    l'errore restava piccolo; su robinhood, dove un blocco dura un decimo di secondo e si torna
    indietro di milioni di blocchi, si accumula in ORE.
    Misurato oggi su quattro file appena scritti dallo scavo: istanti sbagliati di 3.031, 3.055,
    8.235 e 8.439 secondi, e righe non piu' ordinate nel tempo.
    E' lo stesso difetto che il 16/09 avevo corretto nella coda viva (istanti falsi fino a 84
    minuti) e nel recuperatore: lo stesso errore, lasciato in piedi nel terzo raccoglitore, che da
    stamattina e' il principale produttore di righe su robinhood.
    L'ordine temporale non e' un dettaglio estetico: e' cio' che permette di chiedersi CHI E'
    ENTRATO PRIMA, che e' la domanda su cui si regge tutta l'analisi d'entrata."""
    fuori = {}
    b = sorted(blocchi)
    for i in range(0, len(b), lotto):
        gruppo = b[i:i + lotto]
        corpo = json.dumps([{"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                             "params": [hex(x), False], "id": x} for x in gruppo]).encode()
        # SI RIPROVA, PERCHE' UN GRUPPO PERSO E' UN GRUPPO DI RIGHE BUTTATE. Chi chiama scarta le
        # righe senza istante: se qui ci si arrende al primo rifiuto (e il nodo ne manda di
        # continuo), il rimedio all'istante inventato diventa la perdita silenziosa del dato — un
        # difetto peggiore di quello che sto correggendo.
        for _k in range(3):
            try:
                r = urllib.request.Request(url, data=corpo,
                                           headers={"Content-Type": "application/json",
                                                    "User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(r, timeout=60) as x:
                    for d in json.load(x):
                        if isinstance(d, dict) and d.get("result"):
                            fuori[int(d["result"]["number"], 16)] = int(d["result"]["timestamp"], 16)
                break
            except Exception:
                time.sleep(2 * (_k + 1))
        time.sleep(0.15)
    return fuori


def main():
    url, ampiezza = RPC.get(CHAIN, (None, None))
    AMPIEZZA_MAX = ampiezza
    if not url:
        print(f"STORICO_EVM | {CHAIN} non e' una chain EVM che sappiamo interrogare"); return
    ultimo, err = rpc(url, "eth_blockNumber", [])
    if not ultimo:
        print(f"STORICO_EVM | il nodo non risponde: {err}"); return
    ultimo = int(ultimo, 16)

    # l'ancora per gli istanti: si prende UNA volta e si interpola. I blocchi arrivano a ritmo
    # regolare, quindi l'errore e' di qualche secondo — e chiedere l'istante di ogni blocco
    # costerebbe piu' chiamate del lavoro vero.
    b_now, _ = rpc(url, "eth_getBlockByNumber", [hex(ultimo), False])
    b_pre, _ = rpc(url, "eth_getBlockByNumber", [hex(ultimo - 20000), False])
    if not b_now or not b_pre:
        print("STORICO_EVM | non riesco a fissare l'ancora degli istanti"); return
    t_now = int(b_now["timestamp"], 16); t_pre = int(b_pre["timestamp"], 16)
    sec_blocco = (t_now - t_pre) / 20000.0

    # SI TIENE SOLO CIO' CHE SERVE (14/09). La prima prova ha raccolto 108.092 scambi da 4.382 pool
    # in cinquanta secondi — piu' di tre volte tutto il nostro archivio storico. Bellissimo, e
    # insostenibile: un mese di catena cosi' sarebbe piu' di un gigabyte, e il repo morirebbe.
    # Teniamo due cose sole: i pool che sappiamo valutare, e SOLO le loro prime ore di vita. Sono
    # esattamente i dati che l'audit indica come mancanti — chi entra per primo, in che ordine — e
    # tutto il resto e' peso che non risponde a nessuna domanda.
    # SOLO I POOL CHE DIVENTANO UNA RIGA (15/09). Il filtro prendeva tutto il registro — 20.000 pool
    # — e cosi' abbiamo raccolto la storia di 2.969 pool di cui solo 242 diventano righe analizzabili:
    # il 92% dello scavo non serviva a nessuna domanda. Una riga nasce solo dove c'e' una SERIE DI
    # PREZZO: senza prezzo non c'e' esito, senza esito non c'e' niente da imparare.
    # Il registro resta come ripiego se le serie mancassero, ma viene dopo.
    import glob as _g
    nostri = set()
    # PRIMA L'ELENCO ESATTO: i pool che diventano davvero una riga analizzabile (agents/elenco_righe.py).
    # Filtrare sulle serie di prezzo lasciava passare 4.671 pool su Base, ma solo 1.711 diventano righe:
    # il resto non ha abbastanza candele o e' stato preso troppo tardi per avere un'entrata. A parita'
    # di chiamate al nodo, scavare qui dentro vale tre volte tanto.
    try:
        el = json.load(open(f"data/multichain/{CHAIN}/righe.json"))
        nostri = {k.lower() for k in (el.get("pool") or {})}
    except Exception:
        nostri = set()
    if len(nostri) < 50:                      # ripiego: se l'elenco manca, le serie di prezzo
        for d in ("candles", "pulse"):
            for f in _g.glob(f"data/multichain/{CHAIN}/{d}/*.jsonl.gz"):
                nostri.add(os.path.basename(f).replace(".jsonl.gz", "").lower())
    # LA NASCITA VIENE DALLA CATENA, NON DALLA PRIMA CANDELA (18/09). Qui la vita del pool si
    # contava dalla prima candela che AVEVAMO — cioe' dal momento in cui abbiamo cominciato a
    # guardare, non da quando il pool e' nato. Per ogni pool preso in ritardo la finestra partiva
    # tardi, e gli scambi veri precedenti venivano scartati dal filtro qui sotto come "oltre le
    # prime ore". Misurato il 18/09 su una finestra che falliva: 617 eventi su 2.083 scartati cosi',
    # e **306 su 306 verificabili venivano da una nascita di ripiego, zero da una nascita risolta
    # sulla catena**. Era la seconda causa di assenza, dopo i pool fuori registro.
    # Adesso comanda nascita_vera.json dove la nascita e' confermata dalla catena (85% dei pool su
    # entrambe le chain), e la candela resta solo come ripiego per il resto.
    nascita = {}
    da_catena = 0
    try:
        for p, d in json.load(open(f"data/multichain/{CHAIN}/nascita_vera.json"))["nascite"].items():
            if d.get("fonte") == "catena" and d.get("ts"):
                nascita[p.lower()] = int(d["ts"]); da_catena += 1
    except Exception: pass
    for f in _g.glob(f"data/multichain/{CHAIN}/candles/*.jsonl.gz") + _g.glob(f"data/multichain/{CHAIN}/pulse/*.jsonl.gz"):
        a = os.path.basename(f).replace(".jsonl.gz", "").lower()
        if a in nascita: continue
        try:
            with gzip.open(f, "rt") as fo:
                for l in fo:
                    if not l.strip(): continue
                    d0 = json.loads(l)
                    v0 = d0.get("t0") or d0.get("ts")
                    if v0: nascita[a] = int(v0); break
        except Exception: pass
    print(f"STORICO | nascite: {da_catena} dalla catena, {len(nascita) - da_catena} di ripiego "
          f"dalla prima candela", flush=True)
    FINESTRA = int(os.environ.get("ORE_VITA", 8)) * 3600     # solo le prime ore di vita del pool

    os.makedirs(f"data/multichain/{CHAIN}/storico", exist_ok=True)
    pota(CHAIN)
    try: ck = json.load(open(CK(CHAIN)))
    except Exception: ck = {}
    # ogni corsia scava una porzione diversa della storia: non si pestano i piedi
    # LE FETTE VANNO DISTANZIATE IN GIORNI, NON IN BLOCCHI (15/09). Con uno scarto fisso di 200.000
    # blocchi le tre fette di Robinhood partivano tutte entro le ultime 11 ore — mentre i pool che
    # sappiamo valutare sono nati giorni fa. Scavavamo con tre pale nello stesso metro quadrato.
    # Il numero di blocchi in un giorno cambia moltissimo fra le chain (Base 43.200, Robinhood
    # 847.000): lo scarto si calcola dal TEMPO, non dai blocchi.
    blocchi_al_giorno = 86400 / max(0.05, sec_blocco)
    scarto = int(FETTA * GIORNI_FETTA * blocchi_al_giorno)
    partenza = ck.get(f"fetta{FETTA}") or (ultimo - scarto)
    cursore = int(partenza)

    per_pool = {}
    chiamate = scambi = 0
    senza_istante = 0
    pausa_429 = 0
    guai = 0
    # IL RITMO. 79 chiamate in 65 secondi (1,2/s) sono bastate a farci bloccare. Si parte piano e si
    # rallenta ancora a ogni rifiuto: una corsia che va piano e non si ferma scava piu' di sei corsie
    # che si arrendono dopo un minuto.
    rallenta = [float(os.environ.get("PAUSA", 1.6))]
    fermato = "budget"
    ultimo_salvataggio = [time.time()]
    totale_nuovi = [0]
    # OGNI FETTA HA IL SUO TRATTO, E SI FERMA LI' (15/09). Le fette partivano a 0, 6, 12, 18, 24 e 30
    # giorni indietro e poi scavavano all'INDIETRO SENZA FINE: la fetta dei 30 giorni finiva per
    # rifare il lavoro di quella dei 24, che rifaceva quello dei 18. Sei pale che scavano la stessa
    # trincea da punti diversi, e nessuna arriva in fondo al proprio tratto.
    # Adesso ognuna copre esattamente la sua fascia di giorni e si ferma: sei tratti affiancati
    # coprono tutto, una volta sola.
    fine_tratto = int(partenza - GIORNI_FETTA * blocchi_al_giorno)
    while time.time() - t0 < BUDGET:
        da = cursore - ampiezza
        if da <= fine_tratto: fermato = "tratto completato"; break
        if da <= 0: fermato = "inizio della catena"; break
        log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(cursore),
                                             "topics": [[SWAP_V2, SWAP_V3, SWAP_V4]]}])
        chiamate += 1
        if log is None:
            if err and "limit" in err.lower():
                ampiezza = max(20, ampiezza // 2)      # il nodo dice troppo: si stringe e si riprova
                continue
            if err and ("429" in err or "Too Many" in err):
                # NON E' UNA MORTE, E' UNA RICHIESTA DI RALLENTARE (14/09). La prima notte questa
                # riga diceva "break" e sei corsie si sono arrese dopo un minuto ciascuna, dopo 79
                # chiamate. Avevo gia' imparato due giorni fa, su un altro agente, che aspettare e'
                # gratis e perdere un evento no — e qui non l'avevo applicato.
                rallenta[0] = min(6.0, rallenta[0] * 1.6 + 0.4)
                pausa_429 += 1
                time.sleep(min(60, 5 * pausa_429))
                if pausa_429 > 12:
                    fermato = "il nodo continua a rifiutare dopo 12 attese"; break
                continue
            # OGNI ALTRO ERRORE: si stringe e si riprova, non si muore (14/09). Il 500 dei nodi
            # pubblici vuol dire "fascia troppo densa per me", non "arrenditi": la stessa fascia,
            # divisa in due, passa. Un collettore che muore al primo intoppo raccoglie quanto uno
            # spento — e la prima notte e' successo esattamente questo, sei volte.
            guai += 1
            ampiezza = max(10, ampiezza // 2)
            time.sleep(min(30, 2 * guai))
            if guai > 25:
                fermato = f"il nodo continua a rifiutare dopo 25 tentativi: {err}"; break
            continue
        veri = istanti_veri(url, {int(l["blockNumber"], 16) for l in log},
                            100 if CHAIN != "base" else 10)
        for l in log:
            tp = l.get("topics") or []
            # nei pool stile V4 l'identita' e' dentro l'evento, non nel mittente
            pool_a = (tp[1].lower() if (tp and tp[0] == SWAP_V4 and len(tp) > 1)
                      else l["address"].lower())
            if pool_a not in nostri:
                continue                                  # pool che non sappiamo valutare: non serve
            f = firma(l["topics"][0], l.get("data", "0x"), l["topics"])
            if not f: continue
            bn = int(l["blockNumber"], 16)
            ts = veri.get(bn)
            if ts is None:
                senza_istante += 1
                continue          # senza istante vero non si scrive: meglio mancante che inventato
            n0 = nascita.get(pool_a)
            if n0 and ts > n0 + FINESTRA:
                continue                                  # oltre le prime ore: non e' la domanda nostra
            # SI SALVA CON L'IDENTITA' CHE SI E' APPENA CALCOLATA (15/09). Qui c'era
            # l["address"], cioe' il MITTENTE del log. Per i pool con contratto proprio coincide col
            # pool ed era giusto per caso; per quelli dentro un contratto unico il mittente e' sempre
            # lo stesso, e tutti i loro scambi finivano in un unico file da 6,9 MB intestato al
            # contratto — 1.414 pool schiacciati in uno, e la loro identita' persa nello scrivere.
            # Tre filtri sopra usavano pool_a, e solo l'ultima riga no: il pezzo piu' facile da non
            # guardare e' quello dopo il punto in cui hai gia' verificato tutto.
            per_pool.setdefault(pool_a, []).append(
                # L'IDENTITA' DI UNO SCAMBIO NON E' LA TRANSAZIONE (15/09). Una sola transazione puo'
                # contenere PIU' scambi — succede ogni volta che un ordine passa per piu' pool. Con
                # la sola transazione come chiave se ne perdevano di legittimi e se ne tenevano di
                # doppi: 1.014 duplicati su 28.271 scambi campionati. La posizione nel log li separa.
                # I CAMPI CHE C'ERANO GIA' E BUTTAVAMO (15/09). Piu' scambi possono avere lo STESSO
                # istante — sono nello stesso blocco — quindi una variabile che si chiama "in che
                # ordine sono arrivati" non puo' ordinare con la precisione del secondo. Servono
                # numero di blocco, indice della transazione e indice del log: insieme danno
                # l'ordine esatto. E il block hash e' l'unico modo per accorgersi che la catena e'
                # stata riorganizzata sotto di noi.
                # Arrivavano tutti nella stessa risposta. Non costavano niente. Li scartavo.
                {"acq": int(time.time()), "ts": ts, "blocco": bn, "tx": l.get("transactionHash"),
                 "bh": l.get("blockHash"),
                 "ti": int(l.get("transactionIndex", "0x0"), 16),
                 "li": int(l.get("logIndex", "0x0"), 16),
                 "classe": "ricostruzione-storica",
                 # DA DOVE VIENE L'ISTANTE, SCRITTO NEL RECORD (20/09). Senza questo campo un
                 # record giusto e uno sbagliato sono indistinguibili, e la riparazione deve
                 # riesaminare TUTTO a ogni passaggio invece di saltare cio' che e' gia' a posto.
                 # Misurato: le righe scritte da stamattina hanno errore 0 secondi e quelle vecchie
                 # 7.510, ma nessuna delle due lo dichiara — quindi la riparazione non sapeva da
                 # dove cominciare e non partiva.
                 "orario": "catena",
                 # LA VERIFICA SI TIMBRA QUANDO AVVIENE (22/09). Finora l'unica prova che un
                 # istante venisse dalla catena era l'etichetta «orario: catena» — che pero'
                 # la scriveva anche il codice vecchio che interpolava. Misurato contro la
                 # catena: il 17% dei record di base era sbagliato PUR portando quell'etichetta.
                 # Da qui in avanti chi chiede davvero l'orario al nodo lo dichiara con una
                 # data. Cio' che non ha la data non e' verificato: e' soltanto etichettato.
                 "ver": int(time.time()),
                 "w": f["w"], "w_sem": f.get("w_sem"), "a0": f["a0"], "a1": f["a1"],
                 # prezzo del pool e profondita' (26/09): vedi `coda_viva.py`.
                 **({"sq": f["sq"], "liq": f["liq"]} if "sq" in f else {}),
                 "dex": f["v"], "mgr": l.get("address", "").lower(), "fonte": "catena"})
            scambi += 1
        cursore = da
        # GLI INTOPPI SI DIMENTICANO DOPO UN SUCCESSO (15/09). Il contatore non si azzerava mai: in
        # una corsa di tre ore i 25 intoppi tollerati si accumulano per forza, e il lavoro muore
        # anche se sta andando benissimo. Una fetta aveva gia' raccolto 105.068 scambi quando e'
        # stata uccisa dal ventiseiesimo intoppo, sparso su 551 chiamate RIUSCITE.
        # Un guasto va contato quando e' CONSECUTIVO: altrimenti non misura la salute, misura la
        # durata — e piu' a lungo lavori, piu' e' sicuro che ti ammazzi.
        guai = 0
        if time.time() - ultimo_salvataggio[0] > 720:          # ogni 12 minuti si mette al sicuro
            n = scarica_su_disco(CHAIN, per_pool, url, 100 if CHAIN != "base" else 10)
            totale_nuovi[0] += n
            per_pool.clear()
            ck[f"fetta{FETTA}"] = cursore; ck["ultimo_visto"] = ultimo
            try: json.dump(ck, open(CK(CHAIN), "w"))
            except Exception: pass
            salva_e_spingi(f"{CHAIN} fetta{FETTA} +{n} {time.strftime('%H:%MZ', time.gmtime())}")
            ultimo_salvataggio[0] = time.time()
        if ampiezza < AMPIEZZA_MAX:
            # si riallarga dopo OGNI successo, non solo quando la fascia e' magra: in una zona densa
            # restava a 10 blocchi per sempre e scavava dieci volte piu' piano di quanto poteva.
            ampiezza = min(AMPIEZZA_MAX, int(ampiezza * 1.3) + 5)
        time.sleep(rallenta[0])

    nuovi = 0
    # IL SECONDO PUNTO DI SCRITTURA CHIAMA IL PRIMO (20/09). Qui c'era una COPIA della
    # stessa logica di scarica_su_disco: due posti che scrivono i file nello stesso modo, e
    # ogni correzione fatta in uno andava ricordata anche nell'altro. La riparazione degli
    # istanti che sto aggiungendo sarebbe finita in meta' dei casi.
    # (E una sostituzione a stringa su due blocchi identici e' esattamente cio' che il 14/09
    #  ha prodotto una funzione che chiamava se stessa: sei lavori morti per RecursionError.)
    nuovi += scarica_su_disco(CHAIN, per_pool, url, 100 if CHAIN != "base" else 10)
    ck[f"fetta{FETTA}"] = cursore
    ck["ultimo_visto"] = ultimo
    try: json.dump(ck, open(CK(CHAIN), "w"))
    except Exception: pass
    try:
        import registro_pit as R
        R.annota("storico_evm", "catena", CHAIN, nuovi,
                 {"chiamate": chiamate, "blocchi": ultimo - cursore if cursore < ultimo else 0, "fetta": FETTA})
    except Exception: pass
    coperti = (int(partenza) - cursore) / max(1, 86400 / max(0.1, sec_blocco))
    print(f"STORICO_EVM | {CHAIN} fetta{FETTA}: {chiamate} chiamate, {scambi} swap, {nuovi} nuovi, {senza_istante} SCARTATI senza istante vero, "
          f"{len(per_pool)} pool | scavati {coperti:.2f} giorni di catena | "
          f"pausa {rallenta[0]:.1f}s, rifiuti {pausa_429}, intoppi {guai}, fascia {ampiezza} | "
          f"fine: {fermato}", flush=True)


if __name__ == "__main__":
    main()
