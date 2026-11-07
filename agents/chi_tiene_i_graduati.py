"""CHI RICEVE E CHI MANDA i gettoni delle monete arrivate al mercato pubblico.

== PERCHE' ESISTE, E PERCHE' SOSTITUISCE UN ALTRO AGENTE ==

Per sapere se chi compra presto guadagna, serve vedere **chi** vende nel pool. Il campo che
abbiamo nei nostri scambi copre il 100% ma e' il `sender` di Uniswap v4, cioe' il ROUTER: 72
indirizzi distinti per 1.441 scambi, i primi cinque contratti al 67%. Inutile per l'identita'.

Il 6/10 avevo costruito `firmatari_dei_pool.py`, che risolve i firmatari chiedendo i BLOCCHI uno
per uno: 1,2 milioni di blocchi, e dopo diversi giri aveva completato **25 monete su 12.970**.

Poi ho misurato una cosa che cambia tutto: i trasferimenti di un gettone sono eventi
**filtrabili per indirizzo**, e col filtro `address` l'RPC accetta finestre da **10 milioni di
blocchi**. Quindi un gettone intero si legge in UNA chiamata, non in centomila blocchi.
Misurato: 386 trasferimenti e 97 indirizzi distinti in 0,3 secondi.

**Da ~25 monete per giro a tutte e 12.970 in pochi minuti.** E' la stessa lezione del mattino, che
aveva fatto scendere l'elenco dei lanci da 34.096 chiamate a 7: **misurare i limiti invece di
assumerli**.

== UN'INSIDIA, PAGATA SUBITO ==

La prima prova ha dato ZERO trasferimenti, e lo zero era falso: chiedevo dal blocco 1, e la
finestra di 81 milioni veniva accettata svuotando il risultato. Si parte dal blocco di NASCITA
della moneta, che e' noto. **Uno zero che arriva senza errore e' il piu' pericoloso di tutti.**

== PERCHE' AGGREGATO E NON GREZZO ==

La prima prova ha scritto **374.247 righe da sole 6 monete**: le piu' scambiate hanno decine di
migliaia di trasferimenti a testa. Su 12.970 monete sarebbero ~800 milioni di righe, che non e'
un file, e' un problema.

E non servono: la domanda e' «quanti gettoni ha ricevuto e quanti ne ha mandati, questo
indirizzo, su questa moneta», che e' una somma. Si tengono gli hash solo per i primi due
movimenti, come prova verificabile a mano.

== E PERCHE' SOLO I PORTAFOGLI CHE CONOSCIAMO ==

Anche aggregato restano ~3.100 righe per moneta: su 12.970 monete sono 5 GB. Ma la domanda non e'
«chi ha toccato questa moneta», e' **«quelli che abbiamo visto comprare sulla curva, cosa hanno
fatto nel mercato pubblico?»**. Quindi si tengono solo i portafogli che compaiono nei nostri dati
della curva, e si DICHIARA quanti se ne scartano: un filtro taciuto diventa un buco.

== «MOSSO» NON E' «VENDUTO» (aggiunto il 7/10 dopo la prima misura) ==

La prima misura diceva: il 77,5% di chi risultava «mai venduto» sulla curva aveva MOSSO gettoni
nel mercato pubblico. Vero, e risolve un'ambiguita' che bloccava tutto. Ma **mandare gettoni a un
altro portafoglio non e' una vendita**: e' uno spostamento, e attribuirgli un incasso sarebbe lo
stesso errore del «157x».

Quindi ogni flusso porta la sua controparte: se dall'altra parte c'e' il POOL, e' uno scambio; se
c'e' un indirizzo qualunque, e' un trasferimento. Si contano separati, perche' sommarli vorrebbe
dire chiamare guadagno un travaso.

== COSA PRODUCE ==

Per ogni moneta graduata: chi ha ricevuto gettoni e da chi, con le quantita' e la transazione.
Il collegamento col denaro si fa dopo, incrociando per hash di transazione con i nostri scambi.

== IL LATO DENARO (aggiunto il 7/10) ==

I trasferimenti dicono quanti GETTONI si sono mossi e verso chi. Per sapere quanto DENARO e'
entrato o uscito serve l'altro lato dello scambio, che sta nei file degli scambi che gia'
raccogliamo: stesso `tx`, quindi si incrociano per hash.

Si prende la quantita' della VALUTA (il lato che non e' il memecoin) e il suo nome, con le regole
di sempre: mai sommare valute diverse, e se la valuta del pool non e' nota l'importo resta fuori
invece di essere indovinato.

== COSTO ==

ZERO: RPC pubblico, nessuna chiave.
"""
import collections
import glob
import gzip
import json
import os
import sys
import time


# UNA SOLA LIBRERIA DI LETTURA (11/10, prescrizione di Astra). `curva_lanci` e `coppie` erano
# oggetti unici da 52 e 16,6 MB: per aggiungere un dato si riscriveva tutto, e ogni riscrittura
# entrava INTERA nella storia di git. Ora stanno a righe, e queste due funzioni nascondono quale
# forma c'e' sul disco: se cambia di nuovo, cambia in agents/archivio.py e non in dodici file.
def _lanci_interi():
    import archivio as _AR
    _t, _v = _AR.leggi("curva_lanci")
    _d = dict(_t)
    _d["da"] = _v
    return _d


def _coppie():
    import archivio as _AR
    return _AR.leggi("coppie", "coppie")[1]


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a_fette as AF                                   # noqa: E402
import verso as V                                      # noqa: E402
from curva_pons import chiama, log_di_finestra, _indirizzo, _numeri   # noqa: E402
from firma_evento import firma                          # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
BUDGET = int(os.environ.get("BUDGET_SEC", "900"))
# le cartelle degli scambi: i nomi si leggono dall'agente che gia' funziona, non a memoria
# (il 6/10 averli scritti a memoria ha fatto leggere ZERO file dichiarando 11.489 pool)
CARTELLE = tuple(os.environ.get("CARTELLE", "storico,vivo,trades").split(","))
FINESTRA = int(os.environ.get("FINESTRA", "9999999"))   # 10M inclusi = 9.999.999 di ampiezza
TRASF = firma("Transfer(address,address,uint256)")
ZERO = "0x" + "0" * 40


# IL GESTORE DEI POOL UNISWAP v4 su robinhood, trovato sulla chain il 7/10:
# e' l'UNICO contratto che emette gli Swap v4 (8.909 su 8.909 in una finestra campione).
#
# PERCHE' SERVE. Su v4 un pool NON ha indirizzo: ha un identificativo da 32 byte, e i gettoni si
# muovono da e verso questo contratto unico. Confrontare la controparte di un trasferimento con
# gli id dei pool (64 cifre) non puo' mai combaciare con un indirizzo (40 cifre): il 7/10 quel
# confronto dava «zero vendite al pool» su monete che scambiavano eccome.
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
# le firme degli scambi: copiate da agents/storico_evm.py, non riscritte a memoria
SWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
SWAP_V4 = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"


def _con_segno(v):
    """Un intero a 256 bit letto come numero con segno: negli scambi gli importi sono firmati."""
    return v - (1 << 256) if v >= (1 << 255) else v


def pool_delle_monete():
    """moneta -> le controparti che valgono come MERCATO (non come travaso).

    Sono tre cose diverse e vanno tutte dentro:
     · il gestore unico dei pool v4 (dove i pool non hanno indirizzo);
     · i pool con indirizzo vero (l'altra famiglia del registro);
     · la CURVA della moneta, che e' il mercato prima del pool: vendere li' e' una vendita.
    """
    m = collections.defaultdict(set)
    for pool, v in _coppie().items():
        p = pool.lower()
        if len(p) - 2 != 40:          # id v4: non e' un indirizzo, non puo' essere controparte
            continue
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != ZERO:
                m[a].add(p)
    dl = _lanci_interi()
    for t, v in dl["da"].items():
        m[t.lower()].add(v["curva"].lower())
        m[t.lower()].add(GESTORE_V4)
    return m


def graduate():
    pl = f"{BASE}/curva_lanci.json.gz"
    pc = f"{BASE}/coppie.json"
    for q in (pl, pc):
        if not os.path.exists(q):
            raise SystemExit(f"TIENE | manca {q}: non invento quali monete sono graduate")
    dl = json.load(gzip.open(pl, "rt"))
    nati = {t.lower(): v["blocco"] for t, v in dl["da"].items()}
    con_pool = set()
    for pool, v in json.load(open(pc))["coppie"].items():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != ZERO and a in nati:
                con_pool.add(a)
    return [(t, nati[t]) for t in sorted(con_pool)]


def main():
    if CHAIN != "robinhood":
        print(f"TIENE | la curva di Pons e' di robinhood: su {CHAIN} niente da fare.")
        return 0
    t0 = time.time()
    # PER IDENTITA', NON PER POSIZIONE: l'elenco delle graduate cresce ogni giro, e con la
    # posizione la stessa moneta cambia fetta e viene scritta due volte (30.016 duplicati
    # misurati il 7/10). Vedi a_fette.mia_parte_stabile.
    tutte = AF.mia_parte_stabile(graduate(), lambda x: x[0])
    i_f, n_f = AF.quale_fetta()
    print(f"TIENE | fetta {i_f+1}/{n_f}: {len(tutte):,} monete graduate", flush=True)
    if not tutte:
        print("TIENE | nessuna moneta: non scrivo un file vuoto.")
        return 0

    # LA VERSIONE DELLA LOGICA. Il file si scrive in AGGIUNTA, quindi dopo un cambio di regole
    # mescolerebbe righe vecchie e nuove senza che si veda: il 7/10 il conto delle vendite e'
    # passato dal 76,6% misurato in locale al 26,9% letto dalla corsia, e la differenza era
    # tutta qui. Un file che mescola due logiche e' peggio di un file vuoto, perche' sembra
    # pieno. Quando la versione sale, si butta e si rifa'.
    VERSIONE = 10       # 10 = il denaro per asset: le vendite in due salti non mescolano piu' (7/10 notte)
    pf = f"{BASE}/tenute_fatte_pezzo_{i_f}.json"
    fatte = set()
    if os.path.exists(pf):
        try:
            _c = json.load(open(pf))
            if int(_c.get("versione", 1)) < VERSIONE:
                print(f"TIENE | contatore di versione {_c.get('versione', 1)}: lo butto e rifaccio, "
                      f"perche' quelle righe non distinguevano una vendita da un travaso",
                      flush=True)
                for _q in (pf, f"{BASE}/tenute_pezzo_{i_f}.jsonl.gz"):
                    try:
                        os.remove(_q)
                    except OSError:
                        pass
            else:
                fatte = set(_c["monete"])
        except Exception:
            fatte = set()
    ps = f"{BASE}/tenute_pezzo_{i_f}.jsonl.gz"

    # POTATURA DELLE RIGHE VECCHIE, OGNI GIRO (7/10, sera). Buttare il file quando la versione
    # sale non basta: la corsia **riprende il file dal ramo** a ogni giro, quindi le righe della
    # versione rotta tornano e ci si appendono le nuove. Misurato stasera sul ramo:
    # 56.316 righe senza versione + 4.770 a versione 8 nello stesso file.
    # Chi legge le rifiuta (giusto), ma così non si arriverebbe MAI a una misura: il file
    # resterebbe misto per sempre. Qui si pota all'ingresso, non all'uscita.
    # Le righe scartate NON sparisconoo in silenzio: il loro numero finisce in un file accanto,
    # perché un dato buttato senza traccia è un dato che non si può più discutere.
    if os.path.exists(ps):
        tenute, buttate = [], 0
        try:
            with gzip.open(ps, "rt") as _f:
                for _l in _f:
                    if not _l.strip():
                        continue
                    try:
                        _x = json.loads(_l)
                    except Exception:
                        buttate += 1
                        continue
                    if _x.get("v") == VERSIONE:
                        tenute.append(_l.rstrip("\n"))
                    else:
                        buttate += 1
        except Exception as e:
            print(f"TIENE | il file di righe non si legge ({str(e)[:50]}): lo rifaccio da zero")
            tenute, buttate = [], -1
        if buttate:
            with gzip.open(ps, "wt") as _f:
                for _l in tenute:
                    _f.write(_l + "\n")
            json.dump({"versione": VERSIONE, "righe_tenute": len(tenute),
                       "righe_scartate": buttate,
                       "perche": ("righe scritte da una versione precedente del codice: "
                                  "sommarle alle nuove mescola due significati. Si ricalcolano, "
                                  "non si perdono.")},
                      open(f"{BASE}/tenute_potate_pezzo_{i_f}.json", "w"), indent=1)
            print(f"TIENE | potate {buttate:,} righe di versioni precedenti, "
                  f"tenute {len(tenute):,} a versione {VERSIONE}", flush=True)

    print(f"TIENE | {len(fatte):,} monete gia' fatte, {len(tutte)-len(fatte):,} da fare",
          flush=True)

    import collections
    noti = set()
    for q in sorted(glob.glob(f"{BASE}/curva_somme_pezzo_*.json.gz")):
        try:
            for k in json.load(gzip.open(q, "rt")).get("da", {}):
                noti.add(k.split("|")[0])
        except Exception:
            pass
    print(f"TIENE | {len(noti):,} portafogli noti dalla curva: tengo solo loro", flush=True)
    if not noti:
        print("TIENE | nessun portafoglio noto: senza di loro terrei tutto e il file sarebbe "
              "ingestibile. Serve prima la corsia della curva.")
        return 0
    pool_di = pool_delle_monete()
    # moneta -> i suoi pool CON INDIRIZZO e i suoi id v4: i file degli scambi sono nominati cosi'
    _dl = _lanci_interi()
    assets = _dl.get("assets", {})
    quote_di = {t.lower(): (v.get("quote") or "").lower() for t, v in _dl["da"].items()}
    coppia = {p.lower(): v for p, v in _coppie().items()}
    pool_file = collections.defaultdict(set)
    for pool, v in _coppie().items():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != ZERO:
                pool_file[a].add(pool.lower())
    print(f"TIENE | elenco lanci: {len(quote_di):,} monete, {len(assets):,} asset di "
          f"quotazione. SE QUESTO NUMERO E' PICCOLO (1.987 invece di 675.145) la corsia sta "
          f"usando l'elenco corto del ramo e il lato denaro non puo' funzionare.", flush=True)
    print(f"TIENE | {len(pool_di):,} monete con almeno un pool noto: distinguo scambio da travaso",
          flush=True)
    nuove, righe, vuote, scartati, rifatte = 0, 0, 0, 0, 0
    diag = collections.Counter()
    with gzip.open(ps, "at") as f:
        for tok, nato in tutte:
            if tok in fatte:
                continue
            if time.time() - t0 >= BUDGET:
                print(f"   budget speso dopo {nuove:,} monete: salvo quello che ho", flush=True)
                break
            # SI PARTE DALLA NASCITA, non dal blocco 1: una finestra enorme torna uno zero falso
            lg = log_di_finestra(TRASF, nato, nato + FINESTRA, indirizzo=tok)
            if lg is None:
                continue                      # non letta: NON la segno come fatta
            nuove += 1
            if not lg:
                fatte.add(tok)
                vuote += 1
                continue
            # IL DENARO, PRESO DALLA CHAIN E NON DAI NOSTRI FILE.
            #
            # I nostri file degli scambi coprono in mediana **8,9 minuti** di vita di un pool
            # (misurato il 7/10 su 12 file: cinque sotto i 5 minuti, due con una riga sola).
            # Sono una fotografia della nascita, non la storia: per un pool d'esempio il 96%
            # dei movimenti di mercato cadeva DOPO la fine del file, e il collegamento col
            # denaro riusciva solo nel 2,4% dei casi.
            #
            # Gli scambi v4 si chiedono invece per singolo pool con il filtro sull'INDIRIZZO
            # del gestore e l'id del pool come secondo argomento — e col filtro per indirizzo
            # l'RPC accetta 10 milioni di blocchi. Misurato sullo stesso pool: **7.783 scambi
            # in una chiamata da 2,5 secondi, 11,6 giorni coperti**, contro 300 righe e 54
            # secondi del file. Ventisei volte i dati.
            # UNA MONETA NON E' «FATTA» SE IL LATO DENARO E' FALLITO.
            # In corsia girano quattro fette in parallelo e l'RPC rifiuta parecchie richieste:
            # segnando la moneta come fatta comunque, la copertura parziale diventava
            # DEFINITIVA e non si riprovava mai. Misurato il 7/10: in locale 59-90% di
            # copertura del denaro, in corsia nessuna moneta sopra il 50%, mai.
            # E' la stessa regola gia' scritta per le finestre degli scambi: cio' che non si e'
            # letto non si segna come letto.
            # STRUMENTAZIONE (7/10). Dopo tre giri in cui la copertura del denaro restava
            # al 10% in corsia contro il 60-90% in locale, ho smesso di indovinare la causa e
            # ho fatto in modo che l'agente la DICA: quanti pool senza valuta, quante richieste
            # rifiutate, quanti scambi trovati, quanti agganciati per hash.
            # Un numero che non si spiega va strumentato, non interpretato.
            soldi = {}
            denaro_ok = True
            for pool in pool_file.get(tok, ()):
                vp = V.valuta_lato(CHAIN, pool)
                if vp:
                    lato, dec, _ = vp
                    val = V.indirizzo_valuta(CHAIN, pool, lato)
                else:
                    # RIPIEGO, non invenzione: il lato della valuta e' semplicemente quello
                    # che NON e' il memecoin, e i decimali del suo asset stanno gia'
                    # nell'elenco dei lanci (`assets`). Misurato il 7/10: due monete su tre
                    # perdevano del tutto il lato denaro solo perche' il registro non sapeva
                    # dire quale lato fosse la valuta — un'informazione che avevamo altrove.
                    # Se manca anche qui, si salta e NON si indovina.
                    diag["pool_senza_valuta"] += 1
                    cc = coppia.get(pool)
                    if not cc:
                        diag["pool_senza_coppia"] += 1
                        continue
                    lato = "t1" if (cc.get("t0") or "").lower() == tok else "t0"
                    altro = (cc.get(lato) or "").lower()
                    a_info = assets.get(quote_di.get(tok) or "") or {}
                    dec = a_info.get("decimali")
                    if dec is None or altro != (quote_di.get(tok) or altro):
                        diag["ripiego_fallito"] += 1
                        continue
                    diag["ripiego_riuscito"] += 1
                    val = altro
                if len(pool) - 2 == 64:                      # pool v4: id nel secondo argomento
                    ev = log_di_finestra(SWAP_V4, nato, nato + FINESTRA,
                                         indirizzo=GESTORE_V4, secondo=pool)
                    if ev is None:
                        denaro_ok = False
                        diag["richieste_rifiutate"] += 1
                else:                                        # pool con indirizzo proprio
                    e2 = log_di_finestra(SWAP_V2, nato, nato + FINESTRA, indirizzo=pool)
                    e3 = log_di_finestra(SWAP_V3, nato, nato + FINESTRA, indirizzo=pool)
                    if e2 is None or e3 is None:
                        denaro_ok = False
                        diag["richieste_rifiutate"] += 1
                    ev = (e2 or []) + (e3 or [])
                for y in (ev or []):
                    n = _numeri(y.get("data", "0x"))
                    if len(n) < 2:
                        continue
                    # i due importi dello scambio: si prende quello della VALUTA, col segno
                    i0, i1 = _con_segno(n[0]), _con_segno(n[1])
                    qq = i0 if lato == "t0" else i1
                    if qq == 0:
                        continue
                    # IL DENARO SI TIENE PER ASSET, NON UNO SOLO (7/10 notte).
                    # Una vendita puo' avvenire in DUE SALTI: gettone -> asset intermedio ->
                    # nativo. Nella stessa transazione ci sono due scambi, in due pool, in due
                    # asset diversi. Prima scrivevo un valore solo per transazione: vinceva
                    # l'ultimo pool letto, e cosi' 14,873298 di un asset a 6 decimali finivano
                    # registrati come ETH. Risultato: «2.855x» dove il vero era 1,20x, e sette
                    # degli otto moltiplicatori piu' alti erano questo stesso difetto.
                    # Un importo senza il suo asset non e' un dato parziale: e' un dato falso.
                    h0 = str(y["transactionHash"]).lower()
                    d0 = soldi.setdefault(h0, {})
                    pr = d0.get(val)
                    d0[val] = ((pr[0] if pr else 0.0) + abs(qq) / (10 ** dec), qq > 0)
            per_chi = collections.defaultdict(lambda: {"in": 0.0, "out": 0.0, "n": 0,
                                                       "valuta_in": 0.0, "valuta_out": 0.0,
                                                       "valuta": None,
                                                       "scambio_in": 0.0, "scambio_out": 0.0,
                                                       "travaso_in": 0.0, "travaso_out": 0.0,
                                                       "primo": None, "ultimo": None,
                                                       "tx": [], "prove": []})
            for x in lg:
                if len(x.get("topics", [])) < 3:
                    continue
                try:
                    q = (int(x["data"], 16) if x["data"] not in ("0x", "") else 0) / 1e18
                except Exception:
                    q = 0.0
                b = int(x["blockNumber"], 16)
                h = x["transactionHash"]
                mitt, dest = _indirizzo(x["topics"][1]), _indirizzo(x["topics"][2])
                pl = pool_di.get(tok, set())
                for chi, verso, altro in ((mitt, "out", dest), (dest, "in", mitt)):
                    if chi == ZERO:
                        continue
                    d = per_chi[chi]
                    d[verso] += q
                    # la controparte decide se e' uno SCAMBIO o un TRAVASO
                    # IL GESTORE v4 VALE SEMPRE, anche se la moneta non e' nell'elenco
                    # dei lanci che abbiamo sottomano. E' un contratto unico per tutta la chain:
                    # legarlo alla presenza nell'elenco e' stato il difetto del 7/10, per cui
                    # in corsia il tasso di vendita usciva 25,4% invece del 76,6% misurato in
                    # locale — l'elenco in corsia ha 1.987 monete invece di 675.145.
                    mercato = (altro == GESTORE_V4) or (altro in pl)
                    d[("scambio_" if mercato else "travaso_") + verso] += q
                    if mercato:
                        diag["mosse_di_mercato"] += 1
                        _dd = soldi.get(str(h).lower())
                        sd = None
                        if _dd:
                            # L'ASSET DELL'INGRESSO E' QUELLO CHE CONTA: il portafoglio ha
                            # pagato nella valuta della curva, e il guadagno va misurato nella
                            # STESSA. Se in questa transazione quell'asset non c'e', la
                            # posizione resta senza prezzo e si dichiara: meglio un buco che
                            # due asset sommati.
                            _atteso = (quote_di.get(tok) or "").lower()
                            _scelto = _atteso if _atteso in _dd else None
                            if _scelto is None and ZERO in _dd:
                                _scelto = ZERO
                            if _scelto is None:
                                diag["asset_non_combacia"] += 1
                            else:
                                sd = (_dd[_scelto][0], _scelto, _dd[_scelto][1])
                        if not _dd:
                            diag["hash_non_agganciato"] += 1
                        if sd:
                            # chi RICEVE gettoni ha PAGATO; chi li manda ha INCASSATO
                            d["valuta_" + ("in" if verso == "out" else "out")] += sd[0]
                            d["valuta"] = sd[1]
                            # OGNI RIGA PORTA LA PROPRIA PROVA (7/10). Finora una riga diceva
                            # «questo portafoglio ha incassato X» e non c'era modo di risalire
                            # alla transazione: per controllarla dovevo rifare il lavoro a mano,
                            # e cosi' la verifica arrivava DOPO aver comunicato il numero. Il
                            # 7/10 ho detto 7.740 dollari dove la chain diceva 3,36, e il
                            # controllo che lo smentiva costava due minuti.
                            # Con l'hash e l'importo dentro la riga, chi misura puo' pescare un
                            # campione e chiederlo alla chain PRIMA di scrivere un verdetto.
                            if len(d["prove"]) < 6:
                                # I DECIMALI DENTRO LA PROVA (7/10, sera). Senza, chi verifica
                                # deve indovinare la scala: il mio verificatore assumeva 18 e ha
                                # BOCCIATO un dato corretto pagato in un asset a 9 decimali
                                # (121,70698 contro 0,0498: un rapporto di 2.444, cioe' 10^9/2).
                                # Un falso allarme e' grave come un falso via libera: blocca una
                                # misura giusta e manda a cercare un difetto che non c'e'.
                                d["prove"].append([h, round(sd[0], 12), verso, dec])
                    d["n"] += 1
                    d["primo"] = b if d["primo"] is None else min(d["primo"], b)
                    d["ultimo"] = b if d["ultimo"] is None else max(d["ultimo"], b)
                    if len(d["tx"]) < 2:
                        d["tx"].append(h)
            diag["scambi_trovati"] += len(soldi)
            if not denaro_ok:
                # NON si scrive NIENTE per questa moneta, e non la si segna come fatta:
                # scrivere righe incomplete e poi riscriverle al giro dopo creerebbe
                # doppioni, e un doppione in un file aggregato e' un guadagno contato due
                # volte. Si rifa' da capo quando l'RPC e' meno affollato.
                rifatte += 1
                continue
            fatte.add(tok)
            for chi, d in per_chi.items():
                if chi not in noti:
                    scartati += 1
                    continue
                # LA VERSIONE DENTRO OGNI RIGA (7/10). Il marcatore sul contatore non
                # bastava: butta il file della fetta che sta elaborando, ma chi legge
                # l'unione di quattro fette aggiornate in momenti diversi si ritrova il
                # 27,4% di righe in formato vecchio MESCOLATE alle nuove. I miei conti le
                # sommavano, e ne e' uscito un guadagno di 7.740 dollari dove la chain
                # dice 3,36 — sbagliato di 2.300 volte, trovato da Nicolo' aprendo il
                # portafoglio su un sito.
                # Con la versione su OGNI riga, chi legge puo' rifiutare la mescolanza
                # invece di sommarla.
                f.write(json.dumps({"v": VERSIONE, "moneta": tok, "chi": chi, **d}) + "\n")
                righe += 1

    print(f"TIENE | perche' il denaro manca: {dict(diag)}", flush=True)
    json.dump({"acq": int(time.time()), "fetta": i_f, "versione": VERSIONE,
               "diagnostica": dict(diag),
               "monete": sorted(fatte)}, open(pf, "w"))
    print(f"TIENE | {nuove:,} monete nuove in questo giro ({vuote:,} senza trasferimenti), "
          f"{rifatte:,} da rifare perche' il denaro non e' arrivato tutto, "
          f"{righe:,} righe scritte ({scartati:,} indirizzi scartati perche' non visti sulla "
          f"curva), {len(fatte):,}/{len(tutte):,} fatte in tutto "
          f"({100*len(fatte)/max(1,len(tutte)):.1f}%) -> {ps}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
