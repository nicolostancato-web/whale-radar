"""RISERVE — quanto c'e' davvero dentro il pool, momento per momento.

Attributo che mancava al database, trovato il 22/09 dal loop di ricerca su GitHub.

COME E' SALTATO FUORI, perche' il percorso conta. La ricerca ha segnalato che chi sorveglia questi
mercati guarda i MOVIMENTI DI LIQUIDITA': quando chi ha creato il token toglie i soldi dal pool,
chi e' dentro resta con un prezzo che non vale niente. Noi quel momento non lo vedevamo.
Prima di scrivere codice con firme di evento prese a memoria ho guardato cosa emette davvero un
nostro pool — e accanto a ogni scambio c'era un evento SYNC che porta le RISERVE.

QUELLO CHE AVEVO DETTO LA MATTINA STESSA, E CHE ERA SBAGLIATO. Avevo scartato le librerie di
matematica degli AMM scrivendo: «partono dalle riserve, che noi non abbiamo». Le riserve ci sono,
emesse sulla catena dopo ogni singolo scambio. Non le avevamo mai raccolte — che e' una cosa
diversa da non averle.

COSA CI DANNO, in ordine di importanza:

  1. L'IMPATTO ESATTO DI UN ORDINE DI QUALUNQUE DIMENSIONE. Con le riserve, quanto muove il prezzo
     un ordine si CALCOLA, anche per ordini piu' grandi di tutti quelli mai visti in quel pool.
     La misura costruita stamattina (`impatto_reale.py`) sa parlare solo delle dimensioni gia'
     osservate, e sopra quelle deve dire «non misurato». Resta utile come CONTROLLO: se il calcolo
     e la misura non concordano sugli ordini osservati, e' il calcolo a essere sbagliato.

  2. LA LIQUIDITA' CHE SPARISCE, VISTA invece che indovinata. Un crollo delle riserve senza uno
     scambio corrispondente e' una rimozione. Ieri avevamo stimato «un pool su undici finisce in
     cima», ma quel numero andava da 2,3% a 9,2% a seconda di come si misurava il picco: stavamo
     indovinando una fuga dall'impronta. Qui si vede.

  3. LA LIQUIDITA' AL MOMENTO DELLA DECISIONE, che e' una condizione osservabile e quindi
     ammissibile nel loop 1 — a differenza di quasi tutto cio' che sappiamo solo dopo.

NON TOCCA I RACCOGLITORI ESISTENTI. Scrive in una cartella sua. In questo progetto riavviare un
raccoglitore che funziona per aggiungergli qualcosa ha gia' fatto perdere piu' lavoro di quanto la
novita' valesse.
"""
import gzip
import json
import os
import time
import urllib.request

SYNC = "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
RPC = {"base": ("https://mainnet.base.org", 2000),
       "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 2000)}
CHAIN = os.environ.get("CHAIN", "base")
BUDGET = int(os.environ.get("BUDGET_SEC", 1200))
CART = f"data/multichain/{CHAIN}/riserve"
# DUE VERSI: AVANTI TIENE IL PRESENTE, INDIETRO RIPRENDE IL PASSATO (22/09 sera).
# Avevo scritto che il passato delle riserve era «perso comunque, come per le nascite». SBAGLIATO,
# e me l'ha fatto notare il fondatore invece dei dati: gli eventi di liquidita' sono sulla catena
# da sempre, basta chiederli. Provato su un pool di SETTE GIORNI FA: 56 letture, riserve esatte.
# Avevo scambiato «non l'abbiamo raccolto» con «non si puo' avere» — sulla cosa piu' importante,
# e dopo due giorni passati a inseguire esattamente questo errore negli altri.
#
# Perche' conta: col passato ricostruito, il loop 1 puo' cercare uno schema su giorni e giorni
# invece di aspettare che il presente si accumuli. Aspettare e' giusto per COLLAUDARE una
# strategia, non per trovarla.
NOSTRI = set()
VERSO = os.environ.get("VERSO", "avanti")          # avanti | indietro
CK = (f"data/multichain/{CHAIN}/riserve_ckpt.json" if VERSO == "avanti"
      else f"data/multichain/{CHAIN}/riserve_ckpt_indietro.json")
t0 = time.time()


def frenata(err):
    """Il nodo ci sta frenando? Allora i blocchi NON sono illeggibili: siamo noi ad andare forte.

    Il 23/09 la corsia riserve saltava blocchi con «illeggibili, LI SALTO (HTTPError 429)». 429
    vuol dire «troppe richieste»: quei blocchi si leggono benissimo un attimo dopo. Li stavamo
    buttando per sempre, ed e' esattamente l'errore di LEZIONE_IMPOSSIBILE.md — un limite nostro
    registrato come un fatto del mondo. Su robinhood la copertura era al 6%.
    """
    e = str(err or "")
    return ("429" in e or "503" in e or "502" in e or "504" in e
            or "timeout" in e.lower() or "TimeoutError" in e)


def rpc(url, metodo, params, tentativi=5):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    attesa = 3
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=b,
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=60) as x:
                d = json.load(x)
            if "error" in d:
                return None, str(d["error"])[:80]
            return d.get("result"), None
        except Exception as e:
            etichetta = f"{type(e).__name__} {getattr(e, 'code', '')}"
            if k < tentativi - 1:
                # se e' una frenata, si aspetta MOLTO di piu': insistere subito la peggiora
                time.sleep(attesa * (4 if frenata(etichetta) else 1))
                attesa *= 2
                continue
            return None, etichetta
    return None, "esauriti"


def pool_nostri():
    """I pool di cui teniamo gli scambi: gli unici per cui la liquidita' ci serve."""
    fuori = set()
    for sub in ("storico", "vivo"):
        d = f"data/multichain/{CHAIN}/{sub}"
        if os.path.isdir(d):
            fuori |= {fn.split(".")[0].lower() for fn in os.listdir(d)}
    return fuori


def main():
    global NOSTRI
    NOSTRI = pool_nostri()
    if not NOSTRI:
        print(f"RISERVE | {CHAIN}: non conosco nessun pool, non raccolgo niente", flush=True)
        return
    print(f"RISERVE | {CHAIN}: raccolgo solo per i {len(NOSTRI)} pool che seguiamo", flush=True)
    url, ampiezza = RPC.get(CHAIN, (None, None))
    if not url:
        print(f"RISERVE | {CHAIN}: nessun nodo", flush=True)
        return
    punta, err = rpc(url, "eth_blockNumber", [])
    if not punta:
        print(f"RISERVE | {CHAIN}: il nodo non risponde ({err})", flush=True)
        return
    punta = int(punta, 16)

    try:
        ck = json.load(open(CK))
    except Exception:
        ck = {}
    # SI PARTE DA DOVE SIAMO ARRIVATI, e la prima volta da poco indietro: non si rincorre tutta
    # la storia, si comincia a tenere il presente. Il passato delle riserve e' perso comunque —
    # come per le nascite, e per lo stesso motivo: non c'eravamo.
    cur = int(ck.get("cur") or (punta - 3000 if VERSO == "avanti" else punta - 3000))
    os.makedirs(CART, exist_ok=True)

    per_pool = {}
    chiamate = 0
    frenate = 0
    while time.time() - t0 < BUDGET:
        if VERSO == "avanti":
            if cur >= punta:
                break
            da, a = cur, min(punta, cur + ampiezza)
        else:
            if cur <= 1:
                break
            da, a = max(1, cur - ampiezza), cur
        log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(a),
                                             "topics": [[SYNC]]}])
        chiamate += 1
        if log is None:
            if frenata(err):
                # NON si salta e NON si stringe: stringere non serve contro una frenata, e saltare
                # lascia un buco permanente. Si aspetta; se non basta, si ESCE lasciando `cur` dov'e',
                # cosi' il giro successivo riprende esattamente da qui. Meglio lenti che bucati.
                frenate += 1
                if frenate <= 6:
                    time.sleep(min(60, 5 * frenate))
                    continue
                print(f"RISERVE | il nodo ci frena da {frenate} tentativi: mi fermo a {da}, "
                      f"il prossimo giro riprende da qui (NESSUN buco)", flush=True)
                break
            if ampiezza > 100:
                ampiezza = max(100, ampiezza // 2)
                continue                      # si stringe, non si salta
            print(f"RISERVE | blocchi {da}-{a} illeggibili, LI SALTO ({err})", flush=True)
            cur = (a + 1) if VERSO == "avanti" else (da - 1)
            continue
        frenate = 0
        for l in log:
            d = (l.get("data") or "0x")[2:]
            if len(d) < 128:
                continue
            pool = l["address"].lower()
            # SOLO I POOL CHE SEGUIAMO (22/09 sera, correzione entro l'ora).
            # Chiedendo gli eventi di liquidita' per topic si riceve TUTTA la chain: in un'ora
            # erano arrivati 240.349 pool, di cui il 97,5% non li seguiamo nemmeno — un gigabyte
            # di dati inutili, spinti sul repository a ogni giro.
            # E' lo stesso difetto che il 20/09 ha portato il repo a 3.162 MB: raccogliere tutto
            # cio' che il nodo offre invece di cio' che serve. La domanda giusta non e' «cosa posso
            # avere» ma «cosa mi serve» — ed e' il rovescio esatto dell'errore che ho fatto
            # stasera, quando avevo dichiarato irrecuperabile cio' che bastava chiedere.
            if pool not in NOSTRI:
                continue
            per_pool.setdefault(pool, []).append({
                "blocco": int(l["blockNumber"], 16),
                "li": int(l.get("logIndex", "0x0"), 16),
                "r0": int(d[:64], 16),
                "r1": int(d[64:128], 16),
                "acq": int(time.time()),
                "ver": int(time.time()),      # chiesto alla catena adesso: si timbra, come ovunque
            })
        cur = (a + 1) if VERSO == "avanti" else (da - 1)
        ck["cur"] = cur
        time.sleep(0.15)

    scritti = 0
    for pool, righe in per_pool.items():
        p = f"{CART}/{pool}.jsonl.gz"
        try:
            with gzip.open(p, "at") as f:
                for r in sorted(righe, key=lambda x: (x["blocco"], x["li"])):
                    f.write(json.dumps(r) + "\n")
            scritti += len(righe)
        except Exception as e:
            # UNA SCRITTURA FALLITA NON E' UN SUCCESSO: si dice.
            print(f"RISERVE | non sono riuscito a scrivere {pool[:14]}…: {e}", flush=True)
    try:
        json.dump(ck, open(CK, "w"))
    except Exception:
        pass
    if VERSO == "avanti":
        dist = (punta - cur) if cur < punta else 0
        print(f"RISERVE | {CHAIN} avanti: {chiamate} chiamate, {scritti} letture su "
              f"{len(per_pool)} pool | indietro di {dist} blocchi dalla punta", flush=True)
    else:
        giorni = (punta - cur) * (2 if CHAIN == "base" else 0.2) / 86400
        print(f"RISERVE | {CHAIN} indietro: {chiamate} chiamate, {scritti} letture su "
              f"{len(per_pool)} pool | recuperati fino a {giorni:.1f} giorni fa", flush=True)


if __name__ == "__main__":
    main()
