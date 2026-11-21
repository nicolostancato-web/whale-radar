# -*- coding: utf-8 -*-
"""VENDERE SU CURVE, per le monete che su Uniswap non hanno compratore.

Perche' esiste (4/11). Con l'aggregatore bloccato, 265 posizioni (sUSDe,
osETH, rsETH, syrupUSDT) restavano senza strada: la loro liquidita' sta su
Curve. Non serve per il dump -- quelle sono coppie uguali e cadono piano --
serve per le grosse e lente: la piu' vicina ha $1,7M di premio a 1,0107.

COME SI TROVANO LE VASCHE, e questa e' la parte che ho dovuto imparare.
Ho chiesto a `find_pool_for_coins` del MetaRegistry, di tutte e nove le
fabbriche che Curve dichiara, con due firme diverse, e anche con ETH
NATIVO invece di WETH. Tutte hanno detto che la vasca osETH non esiste.
Non era vero: la vasca c'era.
Il metodo che funziona e' GIRATO: invece di chiedere a Curve dove sono le
vasche, si chiede AL GETTONE CHI LO POSSIEDE. Si leggono i trasferimenti
recenti, si prendono le controparti che sono contratti con un saldo
grosso, e si guarda chi risponde a coins(0)/coins(1) -- chi SI COMPORTA
da vasca. Cosi' e' uscita 0xe080027b..., osETH/rETH, 3.006 osETH dentro.
LEZIONE: «non si puo'» va provato con un ALTRO strumento, non con lo
stesso strumento tre volte. Tre registri che dicono no non sono una
prova: sono tre volte lo stesso modo di guardare.
"""
import json, os, sys, time, urllib.request
sys.path.insert(0, "agents")
from keccak import firma
FONTI = ["https://gateway.tenderly.co/public/mainnet",
         "https://ethereum-rpc.publicnode.com", "https://rpc.mevblocker.io"]
CACHE = "data/liquidazioni/vasche_curve.json"
TT = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
S_BAL   = firma("balanceOf(address)")[2:10]
S_COINS = firma("coins(uint256)")[2:10]
# DUE FIRME, E VANNO ABBINATE. Difetto trovato il 4/11: provavo solo
# `int128`, che e' quella delle vasche stableswap. Le vasche CRYPTO (quelle
# con monete volatili, tipo GHO+cbBTC+WETH) usano `uint256`. Risultato: la
# vasca GHO/cbBTC/WETH esisteva, la trovavo, e poi dicevo "nessuna vasca
# utile" perche' le parlavo nella lingua sbagliata.
# E la firma di `get_dy` e quella di `exchange` devono essere DELLO STESSO
# tipo: chiedere il preventivo in una lingua e lo scambio nell'altra
# costruirebbe una calldata che la vasca non capisce.
FIRME = (("get_dy(int128,int128,uint256)",
          "exchange(int128,int128,uint256,uint256)"),
         ("get_dy(uint256,uint256,uint256)",
          "exchange(uint256,uint256,uint256,uint256)"))
S_DY    = firma("get_dy(int128,int128,uint256)")[2:10]
# exchange(int128,int128,uint256,uint256): manda l'incasso A CHI CHIAMA,
# quindi non c'e' nessun indirizzo da scrivere -- l'errore che ho fatto su
# Uniswap (indirizzo di produzione scritto fisso) qui e' impossibile.
# Esiste una variante con un parametro destinatario: NON si usa.
FIRMA_SCAMBIO = "exchange(int128,int128,uint256,uint256)"
def _rpc(m, p, timeout=40):
    c = json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for f in FONTI:
        try:
            r = urllib.request.Request(f, data=c, headers={
                "content-type":"application/json","user-agent":"Mozilla/5.0"})
            v = json.load(urllib.request.urlopen(r, timeout=timeout))
            if "result" in v and v["result"] is not None: return v["result"]
        except Exception: pass
    return None
def _call(to, d): return _rpc("eth_call", [{"to":to,"data":d},"latest"])
def _carica():
    try: return json.load(open(CACHE))
    except Exception: return {}
def _salva(c):
    try: json.dump(c, open(CACHE,"w"), indent=1)
    except OSError: pass
META = "0xf98b45fa17de75fb1ad0e7afd971b0ca00e379fc"
S_FIND = firma("find_pool_for_coins(address,address)")[2:10]
def vasca_dal_registro(a, b):
    """Il registro di Curve, per quello che sa. INCOMPLETO -- non conosce
    la vasca osETH/rETH -- ma quando sa, sa: conosce le vasche sUSDe che il
    metodo dei trasferimenti non trova (sUSDe e' tenuto da tanti contratti
    e la scansione guarda solo i primi venti).
    ERRORE DI REAZIONE, mio, corretto il 4/11: dopo che il registro aveva
    sbagliato su osETH l'ho scartato DEL TUTTO e usavo solo la scansione.
    Ma uno strumento che sbaglia su un caso non diventa inutile su tutti.
    Si usano ENTRAMBI e si unisce: nessuno dei due e' completo da solo."""
    h = _call(META, "0x"+S_FIND+a[2:].zfill(64)+b[2:].zfill(64))
    if not h or len(h) < 42: return None
    p = "0x"+h[-40:]
    return p if int(p,16) else None
def monete_di(vasca):
    m = []
    for i in range(4):
        r = _call(vasca, "0x"+S_COINS+hex(i)[2:].zfill(64))
        if r and len(r) >= 42 and int("0x"+r[-40:],16): m.append("0x"+r[-40:])
        else: break
    return m
def cerca_vasche(gettone, blocchi=40000, cache=None, eta=86400):
    """Le vasche Curve che tengono questo gettone, trovate chiedendo al
    gettone chi lo possiede. Ritorna [(vasca, [coins...])]."""
    g = gettone.lower()
    c = cache if cache is not None else _carica()
    v = c.get(g)
    if v and (time.time()-v.get("quando",0)) < eta:
        return [(p["vasca"], p["coins"]) for p in v.get("vasche",[])]
    testa = _rpc("eth_blockNumber", [])
    if not testa: return []
    t = int(testa,16)
    log = _rpc("eth_getLogs",[{"address":g,"topics":[TT],
          "fromBlock":hex(t-blocchi),"toBlock":hex(t)}]) or []
    conta = {}
    for l in log:
        tp = l.get("topics") or []
        if len(tp) < 3: continue
        for k in ("0x"+tp[1][-40:], "0x"+tp[2][-40:]):
            if int(k,16): conta[k] = conta.get(k,0)+1
    trovate = []
    for a,_ in sorted(conta.items(), key=lambda x:-x[1])[:20]:
        h = _call(g, "0x"+S_BAL+a[2:].zfill(64))
        if not h or int(h,16) == 0: continue
        cod = _rpc("eth_getCode",[a,"latest"]) or "0x"
        if cod == "0x": continue
        monete = []
        for i in range(4):
            r = _call(a, "0x"+S_COINS+hex(i)[2:].zfill(64))
            if r and len(r) >= 42 and int("0x"+r[-40:],16): monete.append("0x"+r[-40:])
            else: break
        if len(monete) >= 2: trovate.append((a, monete))
    c[g] = {"quando": time.time(),
            "vasche": [{"vasca":a,"coins":m} for a,m in trovate]}
    if cache is None: _salva(c)
    return trovate
def preventivo(src, dst, q, cache=None):
    """Un passo di vendita su Curve: (vasca, calldata, offset, daApprovare,
    gettone_in_uscita, quanto_torna) oppure (None, perche', None, None, None, None).

    `gettone_in_uscita` serve a chi compone il piano: se non e' il debito,
    serve un SECONDO passo per arrivarci (il contratto accetta una lista).
    """
    from pescatore import trova_posizione, cast
    src, dst = src.lower(), dst.lower()
    # SI CERCA DA ENTRAMBI I LATI, e il lato giusto e' spesso quello del
    # DEBITO. Difetto trovato il 4/11: cercavo le vasche partendo dalla
    # garanzia, ma WETH sta in migliaia di contratti e la ricerca guarda
    # solo le venti controparti piu' attive -- la vasca GHO/cbBTC/WETH non
    # usciva mai. GHO invece sta in quattro vasche sole: partendo da li' si
    # trova subito. Una vasca e' simmetrica, quindi trovarla da un lato
    # qualsiasi va bene.
    # LEZIONE: quando una ricerca guarda solo i primi N, conviene partire
    # dal gettone RARO, non da quello comune.
    candidate = []
    # IL REGISTRO PRIMA: una sola lettura, e quando sa la risposta e' esatta.
    if dst:
        reg = vasca_dal_registro(src, dst)
        if reg:
            m = monete_di(reg)
            if len(m) >= 2: candidate.append((reg, m))
    # POI LA SCANSIONE, per le vasche che il registro non indicizza.
    for vasca, monete in cerca_vasche(src, cache=cache):
        if (vasca, monete) not in candidate: candidate.append((vasca, monete))
    if dst:
        for vasca, monete in cerca_vasche(dst, cache=cache):
            if (vasca, monete) not in candidate: candidate.append((vasca, monete))
    for vasca, monete in candidate:
        m = [x.lower() for x in monete]
        if src not in m: continue
        i = m.index(src)
        # prima si cerca la vasca che porta DIRETTAMENTE al debito
        for j, moneta in enumerate(m):
            if j == i: continue
            if dst and moneta != dst: continue
            for f_dy, f_ex in FIRME:
                sdy = firma(f_dy)[2:10]
                h = _call(vasca, "0x"+sdy+hex(i)[2:].zfill(64)+hex(j)[2:].zfill(64)+hex(q)[2:].zfill(64))
                if not h or len(h) < 66: continue
                out = int(h[2:66],16)
                if out == 0: continue
                d = cast("calldata", f_ex, str(i), str(j), str(q), "0")
                if not d.startswith("0x"): continue
                pos, n = trova_posizione(d, q)
                if pos is None: continue
                return vasca, d, pos, "0x"+"0"*40, moneta, out
    return None, "nessuna vasca Curve utile per questa coppia", None, None, None, None
def primo_passo(src, q, cache=None):
    """Il passo Curve migliore QUALUNQUE sia il gettone in uscita: serve
    quando il debito non sta nella vasca e ci vuole un secondo salto."""
    from pescatore import trova_posizione, cast
    src = src.lower()
    migliore = None
    for vasca, monete in cerca_vasche(src, cache=cache):
        m = [x.lower() for x in monete]
        if src not in m: continue
        i = m.index(src)
        for j, moneta in enumerate(m):
            if j == i: continue
            for f_dy, f_ex in FIRME:
                sdy = firma(f_dy)[2:10]
                h = _call(vasca, "0x"+sdy+hex(i)[2:].zfill(64)+hex(j)[2:].zfill(64)+hex(q)[2:].zfill(64))
                if not h or len(h) < 66: continue
                out = int(h[2:66],16)
                if out == 0: continue
                if migliore is None or out > migliore[5]:
                    d = cast("calldata", f_ex, str(i), str(j), str(q), "0")
                    if not d.startswith("0x"): continue
                    pos, n = trova_posizione(d, q)
                    if pos is None: continue
                    migliore = (vasca, d, pos, "0x"+"0"*40, moneta, out)
                break
    return migliore or (None, "nessun passo Curve possibile", None, None, None, None)
