"""Chi muove quale asset: la mappa feed -> asset, chiesta all'oracolo.

PERCHE' ESISTE (misurato il 4/11 sera). La sentinella beccava gli
aggiornamenti dell'oracolo e spediva TUTTE le candidate su OGNI
aggiornamento, senza guardare quale asset stesse cambiando prezzo. Su 41
feed distinti beccati, la quasi totalita' dei pacchetti era morta per
costruzione: se si aggiorna il prezzo di LINK, una posizione con garanzia
WETH e debito USDC non cambia salute di un millimetro.
Era lo stesso errore della salute a 1,25, un livello piu' sotto: spendere
i posti del blocco su cavalli che non possono correre.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Si riusa la rete del pescatore invece di riscrivere l'indirizzo del nodo:
# un indirizzo copiato e' una seconda verita' che invecchia da sola, e la
# prima versione di questo file ha preso un 403 proprio per quello.
from pescatore import rpc

ORACOLO = "0x54586bE62E3c3580375aE3723C145253060Ca0C2"
DOVE = "data/liquidazioni/mappa_feed.json"


def chiama(a, dati):
    return rpc("eth_call", [{"to": a, "data": dati}, "latest"])


# I SELETTORI SI CALCOLANO, NON SI INDOVINANO (4/11 sera). La prima
# versione di questo file usava 0xb3596f07 credendolo getSourceOfAsset:
# e' getAssetPrice, e tornava PREZZI. La mappa risultante diceva "zero dei
# 41 feed beccati e' nostro" -- un numero falso che stavo per consegnare.
# Ogni selettore qui sotto viene da `cast sig`.
SORGENTE = "0x92bf2be0"          # getSourceOfAsset(address)
# Un adattatore con tetto non risponde ad aggregator(): dichiara il feed
# che avvolge con uno di questi nomi. Si provano tutti.
SONDE = ("0x245a7bfc",           # aggregator()
         "0x4ebdc284",           # ASSET_TO_USD_AGGREGATOR()
         "0xd221087c",           # BASE_TO_USD_AGGREGATOR()
         "0xdc4a4be8")           # RATIO_PROVIDER()


def _ind(res):
    if not res or len(res) < 66:
        return None
    v = "0x" + res[-40:]
    return None if int(v, 16) == 0 else v.lower()


def costruisci(assets):
    """Per ogni asset: oracolo -> sorgente (proxy) -> aggregatore vero.

    La transazione di aggiornamento va all'AGGREGATORE, non al proxy che
    l'oracolo di Aave dichiara: senza il secondo salto la mappa non
    combacia con niente di quello che becchiamo in mempool.
    """
    m = {}
    for a in assets:
        a = a.lower()
        src = _ind(chiama(ORACOLO, SORGENTE + a[2:].rjust(64, "0")))
        if not src:
            print(f"   ATTENZIONE: nessuna sorgente per {a}")
            continue
        m.setdefault(src, set()).add(a)
        # si scende finche' si scende: l'adattatore puo' avvolgere un
        # adattatore che avvolge il feed vero.
        da_aprire, visti = [src], {src}
        while da_aprire:
            q = da_aprire.pop()
            for sel in SONDE:
                giu = _ind(chiama(q, sel))
                if giu and giu not in visti:
                    visti.add(giu); da_aprire.append(giu)
                    m.setdefault(giu, set()).add(a)
    return {k: sorted(v) for k, v in m.items()}


if __name__ == "__main__":
    from pescatore import AMMESSI
    assets = {k.lower() for k in AMMESSI}
    try:
        for x in json.load(open("data/liquidazioni/vendite_pronte.json")):
            for k in ("garanzia", "debito"):
                if x.get(k):
                    assets.add(x[k].lower())
    except Exception:
        pass
    m = costruisci(assets)
    json.dump({"feed": m}, open(DOVE, "w"), indent=1)
    print(f"{len(assets)} asset -> {len(m)} indirizzi che li muovono")
    becc = set()
    try:
        for l in open("data/liquidazioni/sentinella.jsonl"):
            try:
                v = json.loads(l).get("verso")
            except Exception:
                continue
            if v:
                becc.add(v.lower())
    except Exception:
        pass
    noti = becc & set(m)
    print(f"feed beccati in mempool: {len(becc)} | di cui NOSTRI: {len(noti)}")
    for f in sorted(noti):
        print("  ", f, "->", ",".join(m[f]))


# ---------------------------------------------------------------------------
# CHI STA CAMBIANDO PREZZO, DAVVERO (4/11 sera, la scoperta piu' importante
# della serata). La sentinella filtrava le transazioni per il selettore
# 0x6fadcf72 e registrava `tx.to`: 41 indirizzi distinti, tutti con lo stesso
# codice. Non erano feed: sono gli `AuthorizedForwarder 1.1.0` di Chainlink,
# cioe' gli inoltratori dei singoli operatori, e 0x6fadcf72 e'
# `forward(address,bytes)`. Registravamo il MITTENTE (quale operatore ha
# parlato) invece del PREZZO (quale feed sta cambiando). L'informazione che
# ci serve era dentro la chiamata, nel primo argomento, e per 2.749 eventi
# non l'abbiamo mai letta.
# Conseguenza misurata: dietro 60 eventi c'erano 44 feed veri, e solo tre
# toccavano i nostri asset. Spedire su tutti gli altri non costa (un
# pacchetto non incluso non si paga) ma spedire le 27 posizioni piu' vicine
# IN GENERALE quando cambia UN asset preciso significa mancare l'unica
# posizione che potrebbe davvero cadere.
SIMBOLI = {}      # asset -> simbolo, riempito da simboli()
_NOMI = {}        # feed -> descrizione, memoria per non richiedere due volte
_DOVE_NOMI = "data/liquidazioni/nomi_feed.json"


def bersaglio_di(calldata):
    """Il feed vero dietro un forward(address,bytes). None se non e' uno."""
    if not calldata or calldata[:10] != "0x6fadcf72":
        return None
    try:
        return ("0x" + calldata[10:74][-40:]).lower()
    except Exception:
        return None


def nome_feed(feed):
    """description() del feed, chiesta una volta sola e ricordata."""
    if not _NOMI:
        try:
            _NOMI.update(json.load(open(_DOVE_NOMI)))
        except Exception:
            pass
    if feed in _NOMI:
        return _NOMI[feed]
    r = chiama(feed, "0x7284e416")
    n = None
    if r and len(r) >= 130:
        try:
            q = int(r[66:130], 16)
            n = bytes.fromhex(r[130:130 + q * 2]).decode().strip()
        except Exception:
            n = None
    _NOMI[feed] = n
    try:
        tmp = _DOVE_NOMI + ".tmp"
        json.dump(_NOMI, open(tmp, "w"))
        os.replace(tmp, _DOVE_NOMI)
    except Exception:
        pass
    return n


def simboli(assets):
    """asset -> simbolo, chiesto al gettone stesso."""
    for a in assets:
        a = a.lower()
        if a in SIMBOLI:
            continue
        r = chiama(a, "0x95d89b41")              # symbol()
        s = None
        if r and len(r) >= 130:
            try:
                q = int(r[66:130], 16)
                s = bytes.fromhex(r[130:130 + q * 2]).decode().strip()
            except Exception:
                s = None
        if s:
            SIMBOLI[a] = s.upper()
    return SIMBOLI


def asset_toccati(feed, assets):
    """Quali dei nostri asset muove questo feed.

    Si abbina per SIMBOLO letto dalla descrizione del feed, non per la
    catena degli adattatori: Aave avvolge i feed in adattatori con tetto e
    scendere la catena dava zero sovrapposizioni con cio' che becchiamo.
    Il nome e' la via che combacia -- "STETH / USD" dice STETH.
    """
    n = nome_feed(feed)
    if not n:
        return []
    testa = n.upper().replace("-", " / ").split("/")[0].strip()
    testa = testa.split("(")[0].strip()
    sim = simboli(assets)
    fuori = []
    for a, s in sim.items():
        if s == testa or (s.startswith("W") and s[1:] == testa):
            fuori.append(a)
    return fuori
