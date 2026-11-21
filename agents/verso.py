"""Da che parte sta il memecoin: token0 o token1. Senza questo, ogni prezzo e ogni vendita e' un
tiro di moneta.

IL DIFETTO CHE HA FATTO NASCERE QUESTO FILE (25/09, segnalato da Grok e verificato sui dati).
Negli eventi di scambio `a0` e `a1` sono le quantita' dei due token, col segno visto dal pool
(positivo = entra nel pool). Quale dei due sia il memecoin dipende dall'ORDINE DEGLI INDIRIZZI:
token0 e' semplicemente quello con l'indirizzo piu' piccolo. E' una proprieta' alfabetica, non
economica, e cambia da pool a pool.

`insieme.py` la ignorava. Usava `a0 > 0` per dire «vendita» e `a0/a1` per dire «prezzo».
Misurato sui 61.610 pool delle due chain:

    valuta = token0 (memecoin e' token1):  73,3% robinhood · 64,5% base
    valuta = token1 (memecoin e' token0):  12,5% robinhood · 24,9% base

Cosa vuol dire, esattamente:
  · dove la valuta e' token0 (la MAGGIORANZA), `a0 > 0` vuol dire «e' entrata VALUTA nel pool»,
    cioe' qualcuno ha COMPRATO. Contavamo i compratori come venditori.
  · dove la valuta e' token1, `a0/a1` e' memecoin-per-valuta, cioe' l'INVERSO del prezzo.
Nessuna delle due formule era giusta ovunque, e sbagliavano su sottoinsiemi diversi.

E' particolarmente amaro perche' il 24/09 avevamo corretto proprio questo: «il prezzo mediano di
tutti gli scambi e' quanto gli ALTRI pagano per entrare, non quanto io incasso per uscire».
Avevamo cambiato la regola e lasciato il segno sbagliato: nel 73% dei pool finivamo a misurare
esattamente la cosa che volevamo evitare.

IN POSITIVO: **prima di dare un segno a una quantita', stabilisci a quale token appartiene.**
Qui si stabilisce una volta per chain, e i due lettori (`insieme.py`, `cercatore.py`) lo chiedono.

COME SI RICONOSCE LA VALUTA senza una lista da mantenere: un token che compare in decine di pool
diversi e' una valuta (WETH, USDC, il nativo, gli hub della chain); un memecoin compare nel suo
pool e basta. Soglia a 50 pool. Dove non si capisce — due valute, o nessuna — si restituisce None e
il pool si dichiara non usabile invece di tirare a indovinare.
"""
import json
import os
from collections import Counter

SOGLIA_HUB = int(os.environ.get("SOGLIA_HUB", 50))


def carica(chain):
    """pool -> True se il MEMECOIN e' token0, False se e' token1, None se non si capisce."""
    p = f"data/multichain/{chain}/coppie.json"
    if not os.path.exists(p):
        return {}
    coppie = json.load(open(p)).get("coppie", {})
    freq = Counter()
    for v in coppie.values():
        for k in ("t0", "t1"):
            a = (v.get(k) or "").lower()
            if a:
                freq[a] += 1
    hub = {a for a, n in freq.items() if n >= SOGLIA_HUB}
    fuori = {}
    for pool, v in coppie.items():
        t0, t1 = (v.get("t0") or "").lower(), (v.get("t1") or "").lower()
        h0, h1 = t0 in hub, t1 in hub
        if h0 and not h1:
            fuori[pool.lower()] = False      # valuta t0 -> memecoin e' token1
        elif h1 and not h0:
            fuori[pool.lower()] = True       # valuta t1 -> memecoin e' token0
        else:
            fuori[pool.lower()] = None       # due valute o nessuna: non si tira a indovinare
    return fuori


# QUANTO VALE UN'UNITA' DI VALUTA, per poter parlare in dollari invece che in unita' grezze.
# Verificato sulla catena il 26/09 con `decimals()` e `symbol()`, non assunto: su robinhood USDG ha
# SEI decimali e WETH diciotto — numeri che differiscono di mille miliardi di volte. Senza questa
# tabella ogni confronto di taglia fra pool di valute diverse e' privo di senso.
# I prezzi in dollari sono approssimati e dichiarati: servono a distinguere «trenta dollari» da
# «tremila», non a fare contabilita'.
VALUTE = {
    "0x5fc5360d0400a0fd4f2af552add042d716f1d168": (6, 1.0),      # USDG
    "0x0bd7d308f8e1639fab988df18a8011f41eacad73": (18, 3000.0),  # WETH (robinhood)
    "0x4200000000000000000000000000000000000006": (18, 3000.0),  # WETH (base)
    "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913": (6, 1.0),      # USDC (base)
    "0x0000000000000000000000000000000000000000": (18, 3000.0),  # nativo
}


_LATO_DAI_DATI = {}
_COPPIE = {}


def lato_valuta_dai_dati(chain, pool, soglia=50):
    """Quale lato e' la valuta, ricavato dalla FREQUENZA invece che da una lista fissa.

    PERCHE' (6/10). `valuta_lato` richiede che la valuta sia in una lista scritta a mano di
    cinque indirizzi. Misurato: il 17,1% delle coppie su base e il 14,2% su robinhood non ha
    nessuno dei due lati in quella lista, quindi viene SALTATO — e le valute mancanti sono una
    coda lunga (la piu' grossa al 3,9%), quindi nessuna aggiunta singola risolve.

    LA DISTINZIONE CHE NON AVEVO FATTO: per sapere se uno scambio e' un ACQUISTO o una VENDITA
    serve solo sapere **quale lato e' la valuta**. Il PREZZO serve soltanto per convertire in
    dollari. Sono due domande diverse, e io le avevo legate alla stessa lista.
    Il lato si ricava dai dati senza rischio: una valuta compare in migliaia di coppie, un
    memecoin in una o due. Il prezzo NO — inventarlo riprodurrebbe l'errore dei sedici milioni
    di dollari del 2/10, e per quello la lista fissa resta l'unica fonte.

    Quindi: questa funzione serve a chi deve solo distinguere compra da vende (per esempio
    l'elenco degli arbitraggi). Chi ha bisogno di dollari continua a usare `valuta_lato`.
    """
    if chain not in _LATO_DAI_DATI:
        p = f"data/multichain/{chain}/coppie.json"
        if not os.path.exists(p):
            _LATO_DAI_DATI[chain] = {}
        else:
            try:
                cop = json.load(open(p))["coppie"]
            except Exception:
                cop = {}
            import collections
            q = collections.Counter()
            for v in cop.values():
                for k in ("t0", "t1"):
                    a = (v.get(k) or "").lower()
                    if len(a) == 42:
                        q[a] += 1
            valute = {a for a, n in q.items() if n > soglia}
            mappa = {}
            for pid, v in cop.items():
                a0 = (v.get("t0") or "").lower()
                a1 = (v.get("t1") or "").lower()
                v0, v1 = a0 in valute, a1 in valute
                if v0 and not v1:
                    mappa[pid.lower()] = "t0"
                elif v1 and not v0:
                    mappa[pid.lower()] = "t1"
                # se entrambi o nessuno sono valute, NON si indovina: il pool resta fuori
            _LATO_DAI_DATI[chain] = mappa
    return _LATO_DAI_DATI[chain].get(pool.lower())


def valuta_lato(chain, pool):
    """(quale lato e' la valuta: 't0' o 't1', decimali, prezzo in dollari) — o None.

    PERCHE' SERVE IL LATO (3/10). `valuta(x, meme_t0)` prende la quantita' del lato che NON e'
    il memecoin, deducendolo dalla mappa del verso. Se quella mappa sbaglia per un pool, prende
    la quantita' del MEMECOIN — e su un token con mille miliardi di unita' e 18 decimali diventa
    un importo in dollari astronomico.
    Misurato il 3/10: due indirizzi risultavano aver perso 12,09 e 4,2 MILIONI di dollari, il
    93% di tutte le perdite misurate. Quei due indirizzi hanno ZERO transazioni e saldo ZERO
    sull'esploratore: non avevano scambiato niente. Il totale di «sedici milioni persi dal
    mercato» era interamente un errore di unita' mio.
    Qui il lato della valuta si legge DALLA FONTE (`coppie.json`), non si deduce: se il token in
    `t0` e' una valuta nota, la valuta e' t0. Un fatto invece di un'inferenza.
    """
    # IL FILE SI LEGGE UNA VOLTA, NON A OGNI CHIAMATA (6/10).
    # Qui si apriva e si ANALIZZAVA `coppie.json` — fra 7 e 16 MB — a ogni singola chiamata.
    # Con 35.000 pool su base e 68.000 su robinhood sono decine di migliaia di letture dello
    # stesso file: e' il motivo per cui le corsie che scorrono i pool andavano in timeout
    # leggendo l'80% dei loro file, e perche' l'elenco degli arbitraggi ha richiesto tre
    # tentativi e venti macchine.
    # Trovato per caso, misurando un'altra cosa: un confronto fra due funzioni non finiva piu'.
    # La lezione e' che un difetto di lentezza si presenta come un problema di capacita' —
    # «serve piu' budget», «serve piu' parallelismo» — e si rincorre dalla parte sbagliata.
    if chain not in _COPPIE:
        p = f"data/multichain/{chain}/coppie.json"
        if not os.path.exists(p):
            _COPPIE[chain] = {}
        else:
            try:
                _COPPIE[chain] = json.load(open(p))["coppie"]
            except Exception:
                _COPPIE[chain] = {}
    v = _COPPIE[chain].get(pool.lower()) or {}
    if not v:
        return None
    for k in ("t0", "t1"):
        a = (v.get(k) or "").lower()
        if a in VALUTE:
            d, pr = VALUTE[a]
            return k, d, pr
    return None


# IL V4 HA LA CONVENZIONE DEI SEGNI ROVESCIATA (5/10, verificato sulla chain).
# Nei V2/V3 gli importi dell'evento di scambio sono dalla prospettiva della POOL: positivo
# vuol dire che la pool RICEVE quel gettone. Nel V4 sono dalla prospettiva di CHI SCAMBIA,
# quindi il segno e' rovesciato — e il nostro decodificatore li leggeva allo stesso modo.
#
# COME L'ABBIAMO DECISO, e non per plausibilita': per una pool V2/V3 (che E' un contratto) si
# prende uno scambio emesso da lei e si guarda quale gettone le e' arrivato davvero. DIECI casi
# su dieci coerenti, CINQUE PER CIASCUN VERSO — perche' una convenzione si verifica in entrambe
# le direzioni, altrimenti si misura un caso particolare. Quindi V2/V3 e' letto bene e per
# differenza l'invertita e' la V4.
#
# QUANTO PESAVA: le pool V4 sono il 56,1% su base e l'81,6% su robinhood. Su quattro pool su
# cinque di robinhood, acquisti e vendite erano SCAMBIATI — e con loro ogni attributo di
# pressione e tutta la contabilita' per portafoglio.
#
# PERCHE' SI CORREGGE QUI E NON NEL DECODIFICATORE: correggere alla fonte sistemerebbe solo i
# dati NUOVI, e gli archivi raccolti finora resterebbero sbagliati. Correggendo in lettura,
# tutto cio' che abbiamo torna leggibile senza riscaricare niente.
def _rovesciato(x):
    """Vero se questo scambio ha la convenzione V4 (segni dalla parte di chi scambia)."""
    try:
        return int(x.get("dex", 0)) == 4
    except Exception:
        return False


def quantita_lato(x, lato):
    """La quantita' grezza del lato chiesto, in valore assoluto.

    Il valore assoluto non cambia col verso, quindi qui non serve correggere niente: la
    quantita' e' la stessa, e' il SEGNO che diceva la cosa sbagliata.
    """
    try:
        return abs(float(x["a0" if lato == "t0" else "a1"]))
    except Exception:
        return 0.0


def entra_valuta(x, lato):
    """Vero se la VALUTA entra nel pool, cioe' se qualcuno sta COMPRANDO il memecoin."""
    try:
        v = float(x["a0" if lato == "t0" else "a1"])
    except Exception:
        return False
    return (v < 0) if _rovesciato(x) else (v > 0)


def valuta_del_pool(chain, pool):
    """(decimali, prezzo in dollari) della valuta di quel pool, o None se non la conosciamo.

    STESSA CACHE di valuta_lato (6/10): questa funzione aveva lo stesso difetto — riapriva
    `coppie.json` a ogni chiamata. Correggerne una sola lo lasciava intatto nell'altra, ed e'
    la lezione «un controllo doppio si corregge due volte» applicata alla lentezza.
    """
    if chain not in _COPPIE:
        pf = f"data/multichain/{chain}/coppie.json"
        if not os.path.exists(pf):
            _COPPIE[chain] = {}
        else:
            try:
                _COPPIE[chain] = json.load(open(pf))["coppie"]
            except Exception:
                _COPPIE[chain] = {}
    v = _COPPIE[chain].get(pool.lower()) or {}
    if not v:
        return None
    for k in ("t0", "t1"):
        a = (v.get(k) or "").lower()
        if a in VALUTE:
            return VALUTE[a]
    return None


def indirizzo_valuta(chain, pool, lato):
    """L'INDIRIZZO della valuta di quel pool. Serve per non sommare mai valute diverse.

    Il 6/10 abbiamo misurato che sulla chain robinhood ci sono 72 asset di quotazione distinti
    (valuta nativa, USDG a 6 decimali, perfino gettoni di azioni). Un rapporto «quanto ho messo
    / quanto ho portato a casa» ha senso solo fra quantita' della STESSA valuta: senza questo
    indirizzo non si puo' sapere se due numeri sono confrontabili.
    """
    valuta_del_pool(chain, pool)          # riempie la cache, se non lo e' gia'
    v = (_COPPIE.get(chain) or {}).get(pool) or {}
    a = v.get(lato)
    return a.lower() if isinstance(a, str) else None


def prezzo(x, meme_t0):
    """VALUTA PER MEMECOIN: quanto incasso per ogni gettone. Non l'inverso."""
    try:
        a0 = abs(float(x["a0"]))
        a1 = abs(float(x["a1"]))
    except Exception:
        return None
    if a0 <= 0 or a1 <= 0:
        return None
    return a1 / a0 if meme_t0 else a0 / a1


def e_vendita(x, meme_t0):
    """Vendita = il MEMECOIN entra nel pool (positivo dal punto di vista del pool).

    LA STESSA CORREZIONE V4 (5/10): sui V4 i segni sono dalla parte di chi scambia, quindi
    rovesciati. Questa funzione aveva lo stesso difetto di `entra_valuta`, e correggerne una
    sola avrebbe lasciato il difetto intatto per tutti i suoi chiamanti — e' la lezione «un
    controllo doppio si corregge due volte», scritta in caratteristiche.py per le soglie e
    valida identica qui per i segni.
    """
    try:
        v = float(x["a0" if meme_t0 else "a1"])
    except Exception:
        return False
    return (v < 0) if _rovesciato(x) else (v > 0)


def valuta(x, meme_t0):
    """Quanta VALUTA e' passata in questo scambio, in unita' grezze.

    Serve a mettere una taglia accanto a un prezzo. Un prezzo a 10x che ha scambiato polvere non e'
    un'uscita: e' una stampa. Le unita' sono grezze (non divise per i decimali) e quindi confrontabili
    solo fra pool che usano la stessa valuta — dentro una chain e' quasi sempre lo stesso hub, e per
    la domanda «ci stava dentro una posizione?» basta."""
    try:
        return abs(float(x["a1" if meme_t0 else "a0"]))
    except Exception:
        return 0.0
