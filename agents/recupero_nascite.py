"""RECUPERO NASCITE — va a prendere le prime ore di vita dei pool che ce le hanno perse.

PERCHE' ESISTE (16/09). Le fette filtrano per righe.json NEL MOMENTO in cui passano. Quando una
fetta e' transitata dal blocco in cui un pool e' nato, se quel pool non era ancora nella lista i
suoi scambi sono stati scartati — e le fette non tornano indietro. Cosi' ogni pool scoperto tardi
(tipicamente dalla coda viva, che lavora alla punta) resta senza la sua storia per sempre.

Misurato quando e' saltato fuori:
    base       1841 su 1906 hanno le prime ore =  97%   -> sta bene
    robinhood   414 su  768                    =  54%   -> 320 pool con ZERO record
Il 16% di finestre identiche dell'audit era dominato da questi.

Non e' una fetta in piu': le fette scavano all'indietro senza sapere cosa cercano, e non tornano
mai sui propri passi. Qui si sa esattamente cosa manca e dove sta, quindi si va solo li'.
Raggruppando i pool per fascia di sei ore di nascita, 354 pool stanno in 75 fasce.

IL COSTO VERO, dopo averlo sbagliato di undici volte (16/09). Avevo stimato 21.600 blocchi per
fascia dando per buono un blocco al secondo: robinhood ne fa DIECI al secondo, quindi una fascia e'
di ~245.000 blocchi. Non 4.050 chiamate in 1,4 ore ma ~45.900 in cinque o sei. Sono gratis — sono
minuti di runner su repo pubblico — ma non si prendono in un colpo solo: si lavora a morsi, con
il segnalibro delle fasce gia' fatte, dentro la corsia che gia' gira.
Provata anche la strada furba — chiedere al nodo un pool solo su tutto l'intervallo, filtrando per
indirizzo — e NON funziona: il nodo pubblico deve comunque scandire e la chiamata non torna entro
dieci minuti. Meglio saperlo qui che scoprirlo fra un mese.

L'ISTANTE SI CONVERTE IN BLOCCO COI NOSTRI DATI, NON CHIEDENDOLO. Abbiamo gia' decine di migliaia
di coppie (blocco, istante) nei file: si interpola fra le due piu' vicine, che e' esatto quanto
serve e non costa una chiamata. Si allarga poi il tratto di mezz'ora per parte, perche' sbagliare
in difetto qui vuol dire ricominciare da capo domani.
"""
import gzip
import json
import os
import time
import urllib.request

SWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
SWAP_V4 = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
RPC = {"base": ("https://mainnet.base.org", 100),
       "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 400)}
CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = int(os.environ.get("BUDGET_SEC", 600))
PAUSA = float(os.environ.get("PAUSA", 1.2))
ORE_VITA = int(os.environ.get("ORE_VITA", 6))
MARGINE = 1800                      # mezz'ora per parte: meglio raccogliere un po' troppo
CK = f"data/multichain/{CHAIN}/recupero_ckpt.json"
t0 = time.time()

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storico_evm import firma, salva_e_spingi   # noqa: E402  stessa lettura del log, stesso salvataggio


def rpc(url, metodo, params, tentativi=3):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    attesa = 3
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=45) as x:
                d = json.load(x)
            if "error" in d:
                return None, str(d["error"])[:70]
            return d.get("result"), None
        except Exception as e:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "tentativi esauriti"


def nascite(chain):
    """Quando e' nato ogni pool, secondo le candele."""
    out = {}
    for d in ("candles", "pulse"):
        dd = f"data/multichain/{chain}/{d}"
        if not os.path.isdir(dd):
            continue
        for fn in os.listdir(dd):
            a = fn.split(".")[0].lower()
            if a in out:
                continue
            try:
                for l in gzip.open(os.path.join(dd, fn), "rt"):
                    if l.strip():
                        d0 = json.loads(l)
                        v = d0.get("t0") or d0.get("ts")
                        if v:
                            out[a] = int(v)
                        break
            except Exception:
                pass
    return out


def primo_nostro(chain, pool):
    """Il record piu' vecchio che abbiamo per quel pool, se c'e'."""
    p = None
    for cart in ("storico", "vivo"):
        f = f"data/multichain/{chain}/{cart}/{pool}.jsonl.gz"
        if not os.path.exists(f):
            continue
        try:
            for l in gzip.open(f, "rt"):
                if l.strip():
                    ts = json.loads(l).get("ts")
                    if ts:
                        p = ts if p is None else min(p, ts)
        except Exception:
            pass
    return p


def mappa_tempo_blocco(chain, quanti_file=300):
    """Coppie (istante, blocco) prese dai nostri file: servono a convertire senza chiamare."""
    coppie = []
    for cart in ("storico", "vivo"):
        d = f"data/multichain/{chain}/{cart}"
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d)[:quanti_file]:
            try:
                for l in gzip.open(os.path.join(d, fn), "rt"):
                    if not l.strip():
                        continue
                    r = json.loads(l)
                    if r.get("ts") and r.get("blocco"):
                        coppie.append((r["ts"], r["blocco"]))
            except Exception:
                pass
    coppie.sort()
    return coppie


def tempo_di(per_blocco, blocco):
    """L'istante di un blocco, interpolato sugli stessi dati. SERVE: un record senza istante e'
    invisibile al controllo che decide quali pool mancano, e il recupero rifarebbe all'infinito
    gli stessi pool credendo di non averli mai presi."""
    if not per_blocco:
        return None
    import bisect
    i = bisect.bisect_left(per_blocco, (blocco, 0))
    if i <= 0 or i >= len(per_blocco):
        return None
    (b1, t1), (b2, t2) = per_blocco[i - 1], per_blocco[i]
    if b2 == b1:
        return t1
    return int(t1 + (t2 - t1) * (blocco - b1) / (b2 - b1))


def blocco_a(url, quando, punta, chiamate=None):
    """Il primo blocco con istante >= quando, chiesto alla catena per bisezione.

    INTERPOLARE SUI NOSTRI DATI NON BASTA (16/09, misurato prima di fidarsene). Provato: errori da
    19 minuti a 15 ORE E MEZZA rispetto al blocco vero, contro un margine di mezz'ora. Motivo: una
    parte dei nostri istanti e' a sua volta stimata, e interpolare su stime e' costruire sulla
    sabbia. Il primo giro di prova ha infatti raccolto ZERO scambi in 34 chiamate: stava guardando
    i blocchi sbagliati.
    Venticinque chiamate per fascia sono il prezzo giusto per non sprecarne quattromila altrove."""
    lo, hi = 1, punta
    ris = None
    for _ in range(40):
        if lo > hi:
            break
        mid = (lo + hi) // 2
        b, _e = rpc(url, "eth_getBlockByNumber", [hex(mid), False])
        if chiamate is not None:
            chiamate[0] += 1
        if not b:
            return None
        ts = int(b["timestamp"], 16)
        if ts >= quando:
            ris = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return ris


def main():
    url, ampiezza = RPC.get(CHAIN, (None, None))
    if not url:
        print(f"RECUPERO | {CHAIN}: nessun nodo", flush=True)
        return
    rf = f"data/multichain/{CHAIN}/righe.json"
    if not os.path.exists(rf):
        print(f"RECUPERO | {CHAIN}: manca righe.json", flush=True)
        return
    righe = {k.lower() for k in json.load(open(rf)).get("pool", {})}
    nasc = nascite(CHAIN)
    limite = ORE_VITA * 3600

    da_fare = []
    for p in righe:
        n0 = nasc.get(p)
        if not n0:
            continue
        pr = primo_nostro(CHAIN, p)
        if pr is None or pr > n0 + limite:
            da_fare.append((n0, p))
    if not da_fare:
        print(f"RECUPERO | {CHAIN}: nessun pool senza le sue prime ore", flush=True)
        return

    # NIENTE SECCHI: L'UNIONE DEGLI INTERVALLI VERI (16/09, dopo aver visto il difetto).
    # Prima raggruppavo i pool in secchi da sei ore e scandivo il secchio. Ma un pool nato a fine
    # secchio ha la sua finestra di vita che sborda di ore oltre il tratto scandito: di quelli
    # raccoglievo solo l'inizio. Si vedeva dal conto — i «tardivi» SALIVANO mentre lavoravo, da 34
    # a 41: pool che ricevevano record, ma non quelli delle prime ore.
    # Il secchio era una comodita' mia, non una proprieta' dei dati. Adesso ogni pool porta il suo
    # intervallo vero [nascita, nascita + ore di vita] e si scandisce l'UNIONE: gli intervalli che
    # si toccano si fondono, quindi i pool nati vicini continuano a costare una scansione sola, ma
    # nessuno resta tagliato a meta'.
    grezze = sorted((n0 - MARGINE, n0 + limite + MARGINE, p) for n0, p in da_fare)
    tratti = []
    for a, b, p in grezze:
        if tratti and a <= tratti[-1][1]:
            tratti[-1][1] = max(tratti[-1][1], b)
            tratti[-1][2].add(p)
        else:
            tratti.append([a, b, {p}])
    bande = {f"{a}-{b}": pool for a, b, pool in tratti}
    durate = [(b - a) / 3600 for a, b, _ in tratti]

    ck = {}
    if os.path.exists(CK):
        try:
            ck = json.load(open(CK))
        except Exception:
            ck = {}
    fatte = set(ck.get("fatte", []))
    coppie = mappa_tempo_blocco(CHAIN)
    per_blocco = sorted((b, ts) for ts, b in coppie)
    pp, _e = rpc(url, "eth_blockNumber", [])
    if not pp:
        print(f"RECUPERO | {CHAIN}: il nodo non risponde", flush=True)
        return
    punta = int(pp, 16)
    print(f"RECUPERO | {CHAIN}: {len(da_fare)} pool senza le prime ore, in {len(bande)} tratti "
          f"({len(fatte)} gia' fatti) | durata mediana {sorted(durate)[len(durate)//2]:.1f}h, "
          f"totale {sum(durate):.0f}h", flush=True)

    per_pool = {}
    presi = chiamate = bande_fatte = 0
    ultimo_salvataggio = time.time()

    for banda in sorted(bande, key=lambda k: -int(k.split("-")[0])):   # dai piu' recenti: valgono di piu'
        if time.time() - t0 > BUDGET:
            break
        if str(banda) in fatte:
            continue
        cerco = bande[banda]
        t_da, t_a = (int(x) for x in banda.split("-"))
        cc = [0]
        b_da = blocco_a(url, t_da, punta, cc)
        b_a = blocco_a(url, t_a, punta, cc)
        chiamate += cc[0]
        if not b_a:
            # L'ESTREMO OLTRE LA PUNTA NON E' UN ERRORE, E' DOMANI (16/09). Il tratto piu' recente
            # arriva fino a ore che la catena non ha ancora prodotto: la bisezione torna a mani
            # vuote. Prima lo segnavo «fatto» e quei pool sparivano per sempre senza che nessuno
            # se ne accorgesse — il modo piu' silenzioso di perdere lavoro.
            # Si scandisce fino a dove la catena arriva; il resto sara' di domani, e il tratto
            # resta aperto apposta.
            b_a = punta
        if not b_da or b_a <= b_da:
            print(f"RECUPERO | tratto {banda}: non convertibile, lo lascio APERTO", flush=True)
            continue
        # IL SEGNALIBRO VA DENTRO IL TRATTO, NON SOLO FRA I TRATTI (16/09). Il tratto piu' lungo
        # e' di 266 ore — undici giorni, ~24.000 chiamate — perche' gli intervalli dei pool nati
        # vicini si fondono. Senza cursore salvato, ogni interruzione lo fa ricominciare da zero:
        # si lavorerebbero due ore per ritrovarsi al punto di partenza, all'infinito.
        cur = int(ck.get("cursori", {}).get(str(banda), b_da))
        if cur <= b_da or cur >= b_a:
            cur = b_da
        while cur < b_a and time.time() - t0 <= BUDGET:
            fine = min(cur + ampiezza, b_a)
            log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(cur), "toBlock": hex(fine),
                                                 "topics": [[SWAP_V2, SWAP_V3, SWAP_V4]]}])
            chiamate += 1
            if log is None:
                if "429" in str(err) or "500" in str(err):
                    time.sleep(6)
                    ampiezza = max(50, ampiezza // 2)
                    continue
                cur = fine + 1
                time.sleep(PAUSA)
                continue
            for l in log:
                tp = l.get("topics") or []
                pool = (tp[1].lower() if (tp and tp[0] == SWAP_V4 and len(tp) > 1)
                        else l["address"].lower())
                if pool not in cerco:
                    continue
                f = firma(tp[0], l.get("data", "0x"), tp)
                if not f:
                    continue
                bn = int(l["blockNumber"], 16)
                per_pool.setdefault(pool, []).append(
                    {"acq": int(time.time()), "ts": tempo_di(per_blocco, bn), "blocco": bn,
                     "tx": l.get("transactionHash"), "bh": l.get("blockHash"),
                     "ti": int(l.get("transactionIndex", "0x0"), 16),
                     "li": int(l.get("logIndex", "0x0"), 16),
                     "classe": "ricostruzione-storica",
                     "w": f["w"], "w_sem": f.get("w_sem"), "a0": f["a0"], "a1": f["a1"],
                     "dex": f["v"], "fonte": "catena"})
                presi += 1
            cur = fine + 1
            time.sleep(PAUSA)
            if time.time() - ultimo_salvataggio > 600:
                n = scarica(per_pool)
                per_pool = {}
                ck["fatte"] = sorted(fatte)
                ck.setdefault("cursori", {})[str(banda)] = cur
                try:
                    json.dump(ck, open(CK, "w"))
                except Exception:
                    pass
                salva_e_spingi(f"recupero {CHAIN} +{n}")
                ultimo_salvataggio = time.time()
        ck.setdefault("cursori", {})[str(banda)] = cur
        if cur >= b_a:
            fatte.add(str(banda))
            ck["cursori"].pop(str(banda), None)
            bande_fatte += 1

    n = scarica(per_pool)
    ck["fatte"] = sorted(fatte)
    try:
        json.dump(ck, open(CK, "w"))
    except Exception:
        pass
    print(f"RECUPERO | {CHAIN}: {chiamate} chiamate, {presi} scambi, {n} nuovi su disco, "
          f"{bande_fatte} fasce completate ({len(fatte)}/{len(bande)})", flush=True)


def scarica(per_pool):
    """Scrive nello storico, senza doppioni. L'istante si mette dopo: qui conta non perdere il log."""
    nuovi = 0
    for pool, righe in per_pool.items():
        p = f"data/multichain/{CHAIN}/storico/{pool}.jsonl.gz"
        os.makedirs(os.path.dirname(p), exist_ok=True)
        visti = set()
        if os.path.exists(p):
            try:
                for l in gzip.open(p, "rt"):
                    if l.strip():
                        try:
                            d = json.loads(l)
                            visti.add((d.get("tx"), d.get("li")))
                        except Exception:
                            pass
            except Exception:
                pass
        da = [r for r in righe if (r.get("tx"), r.get("li")) not in visti]
        if not da:
            continue
        try:
            with gzip.open(p, "at") as fo:
                for r in sorted(da, key=lambda x: (x["blocco"], x.get("li", 0))):
                    fo.write(json.dumps(r) + "\n")
            nuovi += len(da)
        except Exception:
            pass
    return nuovi


if __name__ == "__main__":
    main()
