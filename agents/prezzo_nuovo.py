# -*- coding: utf-8 -*-
"""IL PREZZO NUOVO, LETTO PRIMA CHE ENTRI NEL BLOCCO.

PERCHE' ESISTE (5/11). Sapevamo QUALE prezzo stava cambiando (il primo
argomento di forward), non DI QUANTO. Senza il quanto bisogna spedire un
pacchetto per ogni posizione esposta "nel caso": 106 pacchetti per 4 porte,
e misurato male -- 31 secondi per consegnarli, quando un blocco dura 12. Il
mazzo JSON-RPC non e' accettato da nessuno dei quattro costruttori (710 KB:
flashbots -32014, beaverbuild e BuilderNet 400, titan -32005).
Col prezzo nuovo in mano si spedisce SOLO per chi cade davvero: da 106 a
pochissimi, e in millisecondi.

PROVATO su un caso vero: la mediana letta dalla transazione in attesa del
blocco 26350931 e' 224484382842, identica a latestAnswer dell'aggregatore a
quel blocco. Non "simile": identica.

Il rapporto nuovo/vecchio e' tutto quello che serve, perche' la salute e'
lineare nel prezzo: se cambia il prezzo della GARANZIA la salute si muove
come il rapporto, se cambia quello del DEBITO si muove come il suo inverso.
"""
import sys
sys.path.insert(0, "agents")
_cache = {}
# I FEED DA SCALDARE: i prezzi vecchi si vanno a prendere in sottofondo, mai
# nel momento che conta.
_da_scaldare = set()
_scaldatore = [None]
_LUCCHETTO = None
# QUANTE VOLTE HA SCALDATO E QUANTE E' CADUTO: senza questi due numeri il
# filo puo' morire e nessuno se ne accorge -- ed e' esattamente cio' che e'
# successo.
_SCALDATE = [0, 0]      # [riuscite, errori]
def _avvia_scaldatore(leggi_catena):
    """Il filo che va a prendere i prezzi vecchi, fuori dal percorso caldo.

    IL GUASTO CHE QUESTO CODICE HA AVUTO (6/11, trovato dopo tre giri di
    diagnosi). Il percorso caldo fa `_da_scaldare.add(feed)` mentre questo
    filo fa `list(_da_scaldare)`: su un insieme che cambia durante
    l'iterazione Python solleva RuntimeError. Il filo moriva, e siccome
    partiva UNA VOLTA SOLA (`if _scaldatore[0] is not None: return`) non si
    riaccendeva mai piu'. Risultato: la cache dei prezzi vecchi non si
    riempiva, `rapporto` restituiva sempre None, e il filtro delle cadute era
    SPENTO IN SILENZIO -- 58 campanelle e 12 pacchetti spediti senza che una
    sola riga del registro lo dicesse.
    Tre regole applicate qui, tutte imparate a caro prezzo:
      - un filo che deve vivere per sempre si avvolge in un try che NON lo
        lascia morire, qualunque cosa capiti;
      - un insieme condiviso fra fili si copia sotto lucchetto, non con
        list() a mani nude;
      - un meccanismo che lavora in silenzio porta un CONTATORE, altrimenti
        la sua morte e' indistinguibile dal suo funzionamento.
    """
    import threading, time
    global _LUCCHETTO
    if _LUCCHETTO is None: _LUCCHETTO = threading.Lock()
    if _scaldatore[0] is not None and _scaldatore[0].is_alive(): return
    def gira():
        while True:
            try:
                with _LUCCHETTO:
                    da_fare = list(_da_scaldare)
                for f in da_fare:
                    if f in _cache:
                        with _LUCCHETTO: _da_scaldare.discard(f)
                        continue
                    try:
                        v = leggi_catena(f)
                        if v:
                            _cache[f] = v; _SCALDATE[0] += 1
                        else:
                            _SCALDATE[1] += 1
                    except Exception:
                        _SCALDATE[1] += 1
                    with _LUCCHETTO: _da_scaldare.discard(f)
                    # UNA PAUSA MINIMA FRA LE LETTURE. All'avvio si scaldano
                    # 258 feed conosciuti in un colpo: senza pausa sono 258
                    # richieste in dieci secondi alla stessa fonte, e
                    # publicnode ci ha gia' messo in castigo due volte
                    # stanotte. Cosi' il giro completo dura ~25 secondi, che
                    # e' niente perche' e' tutto in sottofondo.
                    time.sleep(0.05)
            except Exception:
                _SCALDATE[1] += 1      # e NON si muore
            time.sleep(2)
    t = threading.Thread(target=gira, daemon=True)
    _scaldatore[0] = t
    t.start()
def scalda_tutti(leggi_catena, feed=None):
    """Mette in coda TUTTI i feed conosciuti, non uno alla volta.

    PERCHE' (6/11, misurato sul registro vivo). Il prezzo vecchio si andava a
    prendere solo DOPO aver visto un feed per la prima volta. Ma gli
    aggregatori Chainlink sono decine, e in 13 campanelle di fila ne sono
    arrivati 13 DIVERSI: la cache cresceva di uno per volta e il filtro delle
    cadute non si accendeva MAI, perche' nessun feed si ripeteva.
    Il registro lo diceva riga per riga («ancora SENZA storico», cache 8, 9,
    10, 11, 12...) solo da quando ho dato voce al caso muto -- prima erano
    tre giri di diagnosi al buio.
    Adesso all'avvio si mettono in coda tutti i feed che conosciamo
    (data/liquidazioni/nomi_feed.json, riempito dalle campanelle passate):
    il filo li scalda in sottofondo in pochi secondi e il filtro e' attivo
    dalla prima campanella su un feed noto.
    """
    import json as _j
    if feed is None:
        try:
            feed = list(_j.load(open("data/liquidazioni/nomi_feed.json")).keys())
        except Exception:
            feed = []
    import threading
    global _LUCCHETTO
    if _LUCCHETTO is None: _LUCCHETTO = threading.Lock()
    with _LUCCHETTO:
        for f in feed:
            if f and f not in _cache: _da_scaldare.add(f.lower())
    _avvia_scaldatore(leggi_catena)
    return len(_da_scaldare)
def quanto_ha_scaldato():
    """(prezzi in cache, riusciti, errori, il filo e' vivo?)"""
    return (len(_cache), _SCALDATE[0], _SCALDATE[1],
            bool(_scaldatore[0] and _scaldatore[0].is_alive()))
def feed_e_mediana(calldata):
    """Da forward(address,bytes) -> (indirizzo del feed, mediana osservata).
    None se non e' la forma attesa: NON si tira a indovinare."""
    try:
        cd = calldata[2:] if calldata.startswith("0x") else calldata
        if cd[:8] != "6fadcf72": return None, None
        feed = "0x" + cd[8:72][-40:]
        off = int(cd[72:136], 16)
        pos = 8 + off * 2
        lung = int(cd[pos:pos+64], 16)
        dentro = cd[pos+64:pos+64+lung*2]
        p = dentro[8:]                      # dopo il selettore di transmit
        # transmit(bytes32[3] contesto, bytes report, ...): il report e' il
        # 4' slot, ed e' un offset. I selettori di transmit sono piu' di uno
        # (visti b1dc65a4 e ba0cb29e), ma la forma dei primi slot e' la stessa.
        rp = int(p[3*64:4*64], 16) * 2
        rl = int(p[rp:rp+64], 16)
        report = p[rp+64:rp+64+rl*2]
        off_oss = int(report[2*64:3*64], 16) * 2
        n = int(report[off_oss:off_oss+64], 16)
        if not (0 < n < 64): return feed, None
        val = []
        for i in range(n):
            x = int(report[off_oss+64+i*64:off_oss+128+i*64], 16)
            if x >= 2**191: x -= 2**192     # int192 col segno
            val.append(x)
        val.sort()
        return feed, val[n // 2]
    except Exception:
        return None, None
def rapporto(feed, mediana, leggi_catena):
    """Quanto cambia il prezzo: nuovo/vecchio. None se il vecchio non si sa --
    e allora si NON si filtra, si tengono tutte le candidate. Un filtro che
    non sa e' peggio di nessun filtro: escluderebbe la caduta vera."""
    if not feed or not mediana: return None
    vecchio = _cache.get(feed)
    if vecchio is None:
        # NEL PERCORSO CALDO NON SI CHIAMA LA RETE (6/11).
        #
        # Qui si leggeva latestAnswer dalla catena la prima volta che si
        # vedeva un feed: una chiamata da 80-260 ms DENTRO la finestra di
        # 80-250 ms. E i feed distinti sono una ventina, quindi lo pagavamo
        # spesso -- e' questo che spiegava i 94-258 ms del «comporre» dopo
        # che firma e testa della catena erano gia' a zero.
        # Prima avevo incolpato la contesa dei fili e la rilettura degli
        # ordini: misurate entrambe, erano 12-18 ms. Due ipotesi sbagliate,
        # e la terza l'ho trovata leggendo il percorso riga per riga invece
        # di indovinare una quarta volta.
        # Adesso: se il prezzo vecchio non lo sappiamo, NON si filtra (si
        # tengono tutte le candidate, come prima del filtro) e lo si va a
        # prendere in SOTTOFONDO, cosi' dalla campanella dopo c'e'.
        if _LUCCHETTO is not None:
            with _LUCCHETTO: _da_scaldare.add(feed)
        else:
            _da_scaldare.add(feed)
        _avvia_scaldatore(leggi_catena)
        return None
    _cache[feed] = mediana
    if vecchio <= 0: return None
    return mediana / vecchio
def salute_dopo(salute, rap, garanzia_si_muove, debito_si_muove):
    """La salute stimata dopo l'aggiornamento. Se si muovono entrambi non si
    sa di quanto resta (sono due prezzi diversi): si restituisce la salute
    attuale, cioe' non si esclude niente."""
    if rap is None: return salute
    if garanzia_si_muove and not debito_si_muove: return salute * rap
    if debito_si_muove and not garanzia_si_muove: return salute / rap
    return salute
