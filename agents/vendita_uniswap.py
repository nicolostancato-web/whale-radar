# -*- coding: utf-8 -*-
"""COSTRUIRE LA VENDITA DA SOLI, su Uniswap, senza nessuna API.

Perche' esiste (4/11, notte). L'aggregatore dei preventivi ci ha BLOCCATI:
non un limite di raffica -- anche una singola richiesta nuda torna
rifiutata. Risultato misurato: 36% delle passate rifiutate, rinnovo degli
ordini FERMO, 274 ordini scaduti, e il ripiego dal vivo del pescatore
dipende dalla stessa fonte -- quindi al momento del colpo avremmo perso
anche quello.

LEZIONE: tutta la nostra capacita' di vendere stava su UNA fonte gratuita
che puo' chiudere la porta quando vuole. Qui si costruisce la calldata da
soli, leggendo solo la catena.

Il minimo in uscita si mette a ZERO di proposito: a difendere il guadagno
c'e' la guardia in dollari del contratto (FRAZIONE_PREMIO_PRETESA),
misurata sugli importi VERI al momento del colpo. Una soglia dentro lo
scambio e' una guardia doppia che puo' solo farci perdere occasioni --
e' la stessa lezione del margine inerte.
"""
import json, os, sys, time, urllib.request
sys.path.insert(0, "agents")
from keccak import firma
ROUTER  = "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"   # SwapRouter02
FACTORY = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
WETH    = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
WBTC    = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"
USDC    = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
# I PONTI, in ordine. Il 4/11 all'alba provavo solo WETH, e LBTC->USDC
# restava senza strada: LBTC ha vasca con WBTC, non con WETH. Era l'unica
# posizione scoperta in tutta la fascia 3-9%. Il difetto non era quella
# posizione: era aver supposto che un ponte bastasse per tutte le famiglie.
PONTI = (WETH, WBTC, USDC)
ZERO    = "0x0000000000000000000000000000000000000000"
# CHI RICEVE L'INCASSO. SwapRouter02 riconosce due indirizzi speciali:
#   address(1) = CHI MI HA CHIAMATO    address(2) = il router stesso
# Si usa il primo, e non l'indirizzo del nostro contratto scritto fisso.
# DIFETTO TROVATO il 4/11 notte dalla prova sul blocco vero: avevo messo
# l'indirizzo di produzione, la prova girava su un contratto appena creato
# a un altro indirizzo, e i 184.095 USDT dello scambio sono finiti al
# contratto SBAGLIATO -- "ricevuto 0" e liquidazione annullata.
# Ma il difetto e' piu' grande della prova: con l'indirizzo scritto fisso,
# il giorno che ridistribuiamo il contratto OGNI ordine gia' pronto
# manderebbe l'incasso al contratto VECCHIO. Soldi veri, persi in silenzio.
# Dicendo "manda a chi ti ha chiamato" la cosa e' giusta per costruzione.
CHI_CHIAMA = "0x0000000000000000000000000000000000000001"
LIVELLI = (100, 500, 3000, 10000)
_ULTIMA_RESA = {"uscita": None}
def vasca_a_livello(a, b, fee, cache=None):
    """Esiste la vasca a QUESTO livello di commissione? (con cache)"""
    a, b = a.lower(), b.lower()
    c = cache if cache is not None else _carica()
    k = f"{a}|{b}|{fee}"
    v = c.get(k)
    if v is not None and (time.time()-v.get("quando",0)) < 86400:
        return v.get("pool")
    h = _call(FACTORY, "0x"+S_POOL+a[2:].zfill(64)+b[2:].zfill(64)+hex(fee)[2:].zfill(64))
    pool = ("0x"+h[-40:]) if h else None
    if pool and int(pool,16)==0: pool=None
    c[k] = {"pool": pool, "quando": time.time()}
    if cache is None: _salva(c)
    return pool
FONTI = ["https://gateway.tenderly.co/public/mainnet",
         "https://ethereum-rpc.publicnode.com", "https://rpc.mevblocker.io"]
CACHE_VASCHE = "data/liquidazioni/vasche_uniswap.json"
S_POOL = firma("getPool(address,address,uint24)")[2:10]
S_LIQ  = firma("liquidity()")[2:10]
def _call(to, dati):
    c = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
        "params":[{"to":to,"data":dati},"latest"]}).encode()
    for f in FONTI:
        try:
            r = urllib.request.Request(f, data=c, headers={
                "content-type":"application/json","user-agent":"Mozilla/5.0"})
            v = json.load(urllib.request.urlopen(r, timeout=20)).get("result")
            if v: return v
        except Exception: pass
    return None
def _carica():
    try: return json.load(open(CACHE_VASCHE))
    except Exception: return {}
def _salva(c):
    try: json.dump(c, open(CACHE_VASCHE, "w"), indent=1)
    except OSError: pass
def vasca(a, b, cache=None, eta=86400):
    """Il livello di commissione della vasca diretta piu' liquida, o None.
    Si tiene in cache un giorno: le vasche non nascono e muoiono spesso, e
    cercarle costa quattro letture per coppia."""
    a, b = a.lower(), b.lower()
    k = f"{a}|{b}"
    c = cache if cache is not None else _carica()
    v = c.get(k)
    if v and (time.time() - v.get("quando", 0)) < eta:
        return v.get("fee")
    migliore, liq_max = None, 0
    for fee in LIVELLI:
        h = _call(FACTORY, "0x"+S_POOL+a[2:].zfill(64)+b[2:].zfill(64)+hex(fee)[2:].zfill(64))
        if not h: continue
        pool = "0x"+h[-40:]
        if int(pool, 16) == 0: continue
        l = _call(pool, "0x"+S_LIQ)
        liq = int(l, 16) if l else 0
        if liq > liq_max: migliore, liq_max = fee, liq
    c[k] = {"fee": migliore, "liquidita": liq_max, "quando": time.time()}
    if cache is None: _salva(c)
    return migliore
def _percorso(gettoni_e_fee):
    """Il percorso impacchettato di Uniswap: gettone+fee+gettone+fee+gettone."""
    s = ""
    for i, x in enumerate(gettoni_e_fee):
        if i % 2 == 0: s += x[2:].lower().zfill(40)[-40:]
        else:          s += hex(x)[2:].zfill(6)
    return "0x"+s
QUOTER = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e"   # QuoterV2
S_QUNO  = firma("quoteExactInputSingle((address,address,uint256,uint24,uint160))")[2:10]
S_QPATH = firma("quoteExactInput(bytes,uint256)")[2:10]
# LA SOGLIA DELLA RESA E' PER GETTONE, non una sola per tutti.
# Difetto trovato il 4/11 (settimo blocco): questa era 0,94 fissa,
# giustificata con "sotto il 94% si mangia il premio del 7%". Ma il premio
# vero che Aave paga va dal 4,50% (USDC, USDT) all'8,50% (USDe, LBTC): su
# una garanzia al 4,50% una vendita al 94% va in PERDITA dell'1,8%, e
# questa soglia la autorizzava.
# Ora la soglia la calcola agents/premi.py dal premio vero del gettone:
# va dal 94,21% al 97,74%.
RESA_MINIMA = 0.94      # solo come ripiego se premi.py non risponde
def resa_minima_di(gettone):
    try:
        from premi import resa_minima
        return resa_minima(gettone)
    except Exception:
        return RESA_MINIMA
def _quanto_torna_diretta(src, dst, q, fee):
    d = ("0x"+S_QUNO+src[2:].lower().zfill(64)+dst[2:].lower().zfill(64)
         +hex(q)[2:].zfill(64)+hex(fee)[2:].zfill(64)+"0"*64)
    h = _call(QUOTER, d)
    return int(h[2:66], 16) if h and len(h) >= 66 else None
def _quanto_torna_percorso(percorso_hex, q):
    p = percorso_hex[2:] if percorso_hex.startswith("0x") else percorso_hex
    n = len(p)//2
    corpo = ("0x"+S_QPATH+hex(64)[2:].zfill(64)+hex(q)[2:].zfill(64)
             +hex(n)[2:].zfill(64)+p+"0"*((32-n%32)%32*2))
    h = _call(QUOTER, corpo)
    return int(h[2:66], 16) if h and len(h) >= 66 else None
def preventivo(src, dst, q, contratto, cache=None):
    """(sede, dati, posizione_importo, daApprovare) oppure (None, perche', None, None).

    Un salto solo se esiste la vasca diretta; altrimenti due salti via WETH.
    L'importo si cerca con trova_posizione come per l'aggregatore: non si
    indovina l'offset nemmeno quando lo si conosce, perche' la forma della
    calldata puo' cambiare e un numero scritto nel campo sbagliato e' il
    difetto che ci e' gia' costato una presa.
    """
    from pescatore import cast, trova_posizione
    src, dst = src.lower(), dst.lower()
    if src == dst: return None, "stesso gettone: non c'e' niente da vendere", None, None
    # LA ROTTA SI SCEGLIE PER QUANTO RENDE, non per quanto dichiara.
    # DIFETTO TROVATO il 4/11 mattina misurando le rotte che avevo appena
    # collegato: scegliendo la vasca col numero liquidity() piu' alto,
    # rsETH->WETH rendeva lo 0,01%, LBTC->WBTC il 71,85%. liquidity() e'
    # la liquidita' AL PREZZO CORRENTE, non la profondita': una vasca puo'
    # dichiararla e riempirti pessimo alla nostra taglia.
    # Il contratto ci salva (annulla, gratis), ma l'ordine sarebbe rimasto
    # in cassetto CONTATO COME BUONO e si sarebbe annullato nel momento
    # della verita' -- la stessa famiglia dell'indicatore che mente.
    # Quindi si interroga il Quoter, che e' una lettura e costa zero, e si
    # prende la rotta migliore DAVVERO; se nessuna arriva a RESA_MINIMA si
    # dice no, invece di mettere in cassetto una vendita che fallira'.
    candidate = []
    for fee in LIVELLI:
        if vasca_a_livello(src, dst, fee, cache) is None: continue
        out = _quanto_torna_diretta(src, dst, q, fee)
        if out: candidate.append((out, "diretta", fee, None))
    for ponte in PONTI:
        if ponte in (src, dst): continue
        f1 = vasca(src, ponte, cache); f2 = vasca(ponte, dst, cache)
        if not (f1 and f2): continue
        perc = _percorso([src, f1, ponte, f2, dst])
        out = _quanto_torna_percorso(perc, q)
        if out: candidate.append((out, "percorso", (f1, f2), perc))
    if not candidate:
        return None, "nessuna vasca con una strada percorribile", None, None
    candidate.sort(reverse=True)
    out, tipo, fee, perc = candidate[0]
    if tipo == "diretta":
        d = cast("calldata",
            "exactInputSingle((address,address,uint24,address,uint256,uint256,uint160))",
            f"({src},{dst},{fee},{CHI_CHIAMA},{q},0,0)")
    else:
        d = cast("calldata", "exactInput((bytes,address,uint256,uint256))",
                 f"({perc},{CHI_CHIAMA},{q},0)")
    # E SI RIFIUTA UNA ROTTA CHE SI MANGIA IL PREMIO. Senza questo, la
    # scelta "la migliore fra quelle cattive" metteva comunque in cassetto
    # un ordine destinato ad annullarsi.
    resa = None
    try:
        PR = json.load(open("data/liquidazioni/prezzi_oracolo.json"))
        ps, pd_ = PR.get(src), PR.get(dst)
        if ps and pd_:
            dentro = q/10**ps["decimali"]*ps["prezzo_usd"]
            fuori  = out/10**pd_["decimali"]*pd_["prezzo_usd"]
            resa = fuori/dentro if dentro else None
    except Exception:
        pass
    _ULTIMA_RESA["uscita"] = out
    _ULTIMA_RESA["resa"] = resa
    soglia = resa_minima_di(src)
    if resa is not None and resa < soglia:
        return (None, f"la rotta migliore rende solo il {100*resa:.2f}% "
                      f"(per questa garanzia serve almeno il {100*soglia:.2f}%, "
                      f"perche' Aave paga il {100*(__import__('premi').premio(src)):.2f}%): "
                      f"si mangerebbe il premio", None, None)
    if False:
        pass
    if not d.startswith("0x"):
        return None, f"calldata non costruita: {d[:60]}", None, None
    pos, n = trova_posizione(d, q)
    if pos is None:
        return None, f"importo trovato {n} volte nella calldata", None, None
    # daApprovare = zero: il contratto autorizza la sede stessa, e il
    # router di Uniswap preleva da se'. Con l'aggregatore invece preleva un
    # contratto DIVERSO, ed e' per quello che li' si passa il proxy.
    return ROUTER, d, pos, ZERO
