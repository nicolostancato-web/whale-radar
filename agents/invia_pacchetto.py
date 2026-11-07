# -*- coding: utf-8 -*-
"""Consegna la liquidazione come PACCHETTO PRIVATO al costruttore del blocco.

Perche' (1/11). Il percorso armato spediva con un invio PUBBLICO: la
transazione finisce nella piazza dove tutte le transazioni in attesa sono
visibili. Due conseguenze, e la seconda e' peggiore della lentezza:
  1. l'ordine dentro il blocco si decide a colpi di commissione, in un'asta
     aperta dove non offrivamo niente di particolare;
  2. una liquidazione redditizia e' VISIBILE prima di essere eseguita, quindi
     copiabile da chiunque guardi la piazza. Giocavamo a carte scoperte.

Il pacchetto privato risolve tutte e tre le cose insieme:
  - nessuno lo vede prima che sia nel blocco;
  - si offre direttamente al costruttore una commissione di priorita';
  - UN PACCHETTO RESPINTO NON SI PAGA. Tentare costa zero, non gas bruciato.
    (gia' misurato e scritto in memoria: feedback_pacchetti_annullati_gratis)

CANCELLO OBBLIGATORIO: prima di spedire si SIMULA con eth_callBundle, che e'
gratis. Se la simulazione dice che si annulla, non si spedisce. Cosi' non si
offre al costruttore un pacchetto che non vale niente, e si sa in anticipo
quanto sarebbe il guadagno.
"""
import json, os, subprocess, sys, threading, urllib.request, urllib.error
import time   # serviva a tieni_calde: mancava, e il filo moriva all'avvio
import concurrent.futures as cf   # era importato DENTRO una funzione: la
# seconda che ne aveva bisogno moriva di NameError. Quarto nome mancante
# della notte, e tutti e quattro trovati ESEGUENDO, non leggendo.
FOUNDRY=os.path.expanduser("~/.foundry/bin")
RELAY="https://relay.flashbots.net"
# l'indirizzo dell'identita' verso il relay: non cambia, si tiene
_IDENT = {}
TEMPI = {}      # quanto costa ogni porta, in ms, misurato
RIFIUTI_LENTI = []   # gli esiti della porta che non aspettiamo
# LE CONNESSIONI SI TENGONO APERTE (6/11).
#
# urllib apre una connessione nuova a ogni richiesta, e una stretta di mano
# TLS verso quattro porte costava ~650 ms per invio. La finestra fra
# l'apparire dell'aggiornamento dell'oracolo e la chiusura del blocco e'
# 80-250 ms: la sola apertura delle connessioni la sforava.
# Una connessione per FILO e per porta, riusata: la stretta si paga una
# volta e poi non piu'. Non e' una ottimizzazione prematura -- e' il termine
# dominante misurato, e Astra e Grok hanno indicato la stessa cosa.
# Per filo e non globale perche' HTTPSConnection non si puo' usare da due
# fili insieme: i tre blocchi (+1/+2/+3) partono in parallelo.
import http.client as _hc, threading as _th, ssl as _ssl, queue as _q
# LE CONNESSIONI SONO CONDIVISE E RESTANO CALDE (6/11, seconda correzione).
#
# La prima versione le teneva per FILO (threading.local). Sembrava giusto --
# HTTPSConnection non e' usabile da due fili insieme -- ma la sentinella crea
# fili NUOVI a ogni evento, quindi ogni campanella ripagava la stretta di
# mano: le connessioni «persistenti» erano fredde ogni volta.
# MISURATO, ed e' la differenza fra essere in gara e non esserlo:
#   a freddo: flashbots 369 ms, beaverbuild 117, BuilderNet 95, titan 67
#   a caldo:  flashbots 125 ms, beaverbuild  47, BuilderNet 29, titan 27
# Con la firma a 16 ms, a caldo siamo a ~141 ms in tutto (e 63 verso
# beaverbuild, che costruisce il 75% dei blocchi che contano): DENTRO la
# finestra di 80-250 ms. A freddo eravamo fuori.
# Quindi: una CODA di connessioni per porta, condivisa fra tutti i fili e
# riusata fra un evento e l'altro, piu' un filo che le tiene vive.
_POZZE = {}
_POZZE_LOCK = _th.Lock()
_QUANTE_PER_PORTA = 4      # i tre blocchi partono in parallelo, piu' margine
def _pozza(url):
    with _POZZE_LOCK:
        if url not in _POZZE:
            _POZZE[url] = _q.LifoQueue()
            for _ in range(_QUANTE_PER_PORTA):
                _POZZE[url].put(None)      # None = da aprire alla prima usata
        return _POZZE[url]
def _apri(url):
    host = url.split("://", 1)[1].partition("/")[0]
    return _hc.HTTPSConnection(host, timeout=20,
                               context=_ssl.create_default_context())
def tieni_calde():
    """Una richiesta banale su ogni connessione ogni 20 secondi: i
    costruttori chiudono le connessioni inattive, e una connessione chiusa
    si riscopre solo nel momento in cui serve -- cioe' il momento peggiore."""
    while True:
        for _, u in PORTE:
            try:
                _posta(u, json.dumps({"jsonrpc":"2.0","id":1,
                        "method":"eth_blockNumber","params":[]}).encode(),
                       {"content-type":"application/json"})
            except Exception:
                pass
        # OGNI 3 SECONDI, e il numero e' MISURATO non scelto (6/11).
        # Prova diretta sullo stesso invio, a parita' di tutto il resto:
        #   appena usate          124 ms
        #   dopo  4 s di fermo    155 ms
        #   dopo  8 s di fermo    259 ms
        #   dopo 15 s di fermo    210 ms
        # Tenerle calde ogni 8 secondi le lasciava esattamente nel punto
        # peggiore, ed era il motivo per cui la consegna nel sistema vivo
        # costava ~250 ms mentre in isolamento ne costava 130: in isolamento
        # le avevo appena usate.
        # Tre secondi costano 4 richieste banali ogni 3 s: poco piu' di una
        # al secondo in tutto, niente per un costruttore che riceve migliaia
        # di pacchetti -- e non e' la stessa cosa dei nodi pubblici, che sono
        # quelli da non bruciare.
        time.sleep(3)
def _posta(url, corpo, intest, riprova=True):
    """POST riusando una connessione calda della pozza. Se e' morta si
    riapre UNA volta: un ripiego silenzioso su una cosa indispensabile e'
    una bugia, ma qui il ripiego e' dichiarato e misurato."""
    pz = _pozza(url)
    percorso = url.split("://", 1)[1].partition("/")[2]
    try:
        c = pz.get(timeout=5)
    except Exception:
        c = None
    if c is None:
        c = _apri(url)
    try:
        c.request("POST", "/" + percorso, body=corpo,
                  headers=dict(intest, **{"Connection": "keep-alive"}))
        r = c.getresponse()
        d = r.read()
        pz.put(c)                 # torna nella pozza, ancora calda
        if r.status >= 400:
            return {"http": r.status, "corpo": d.decode("utf-8", "replace")[:200]}
        return json.loads(d)
    except Exception as e:
        try: c.close()
        except Exception: pass
        pz.put(None)              # il posto resta, la connessione no
        if riprova:
            return _posta(url, corpo, intest, riprova=False)
        return {"errore": "connessione: " + str(e)[:100]}
from keccak import keccak256 as _keccak_locale
# LE PORTE DOVE SI CONSEGNA. Trovato il 4/11 sera, ed e' quasi certamente
# il motivo per cui 12.000 pacchetti accettati hanno prodotto ZERO
# inclusioni: mandavamo tutto a UNA porta sola.
# MISURATO sulle 42 liquidazioni sopra i $500 degli ultimi 30 giorni, chi
# ha costruito quei blocchi:
#    beaverbuild  29 blocchi  $654.891 di premio  75,5%
#    BuilderNet   12 blocchi  $153.360            17,7%
#    un terzo      1 blocco    $58.682             6,8%
# Tre costruttori, e beaverbuild da solo tre quarti del mercato. Un
# pacchetto accettato dal relay di Flashbots non arriva necessariamente a
# beaverbuild: "accettato" non e' "arrivato a chi costruisce quel blocco".
# Provato: accettano tutti, e sono PIU' VELOCI del relay di Flashbots
# (beaverbuild 171 ms, BuilderNet 129, Titan 114, Flashbots 373).
# Si consegna a tutte in parallelo: costa come consegnarne una.
PORTE = [("flashbots",  "https://relay.flashbots.net"),
         ("beaverbuild","https://rpc.beaverbuild.org"),
         ("buildernet", "https://rpc.buildernet.org"),
         ("titan",      "https://rpc.titanbuilder.xyz")]
_BLX = {}


def _chiave_blx():
    """La credenziale bloXroute, letta UNA volta e tenuta in cache.
    Non si rilegge il file delle credenziali a ogni colpo: siamo nel percorso
    caldo, e una lettura di disco qui e' un regalo che facciamo ai
    concorrenti. Se manca, si torna None e la terza porta semplicemente non
    esiste -- nessun ripiego, nessun errore: le altre due bastano."""
    if "k" not in _BLX:
        try:
            import chiavi
            _BLX["k"] = chiavi.bloxroute()
        except Exception:
            _BLX["k"] = None
    return _BLX["k"]


def cast(*a):
    return subprocess.run([f"{FOUNDRY}/cast",*a],capture_output=True,
                          text=True).stdout.strip()
def _chiave_identita():
    """La chiave che FIRMA la richiesta al relay. Non muove soldi: serve solo
    a farsi riconoscere e accumulare reputazione presso il relay (questa si',
    esiste -- ma e' del relay, non del protocollo Aave)."""
    # DOVE VIVE: fuori dalla cartella di lavoro, perche' quella si svuota.
    # Il 3/11 il file era stato cancellato e tutto il resto sembrava sano.
    # Non e' un segreto che muove soldi (serve solo a farsi riconoscere dal
    # relay e accumulare reputazione), ma va comunque solo in locale a 0600
    # e MAI nel repo pubblico.
    fuori=os.path.expanduser("~/.chiavi_whale/identita")
    for p in (fuori, ".chiavi/identita"):
        if os.path.exists(p):
            k=open(p).read().strip()
            if k.startswith("0x") and len(k)==66: return k
    # SI CREA, e se non si riesce si GRIDA. Il 3/11 qui c'era
    # `except: return None`, e quel ripiego ha nascosto un guasto totale:
    # `cast wallet new --json` ha cambiato formato (ora avvolge tutto in
    # {"data":[...]}), il `[0]` su un dizionario alzava KeyError, la
    # funzione tornava None e OGNI pacchetto spedito falliva in silenzio.
    # Senza identita' non si consegna niente: non e' un caso da ripiego.
    k=cast("wallet","new","--json")
    nuova=None
    try:
        g=json.loads(k)
        # due formati visti: lista nuda, e oggetto con "data"
        voci = g if isinstance(g, list) else (g.get("data") or [])
        nuova = voci[0]["private_key"]
    except Exception as e:
        print(f"   !!! NESSUNA IDENTITA' VERSO IL RELAY: {type(e).__name__}: {e}")
        print(f"   !!! finche' manca, NESSUN pacchetto viene consegnato")
        return None
    os.makedirs(os.path.dirname(fuori), exist_ok=True)
    open(fuori,"w").write(nuova); os.chmod(fuori,0o600)
    print("   creata una nuova identita' verso il relay (reputazione da zero)")
    return nuova
def a_tutte_le_porte(metodo, par, kid=None):
    """Consegna lo stesso pacchetto a OGNI porta, in parallelo.
    Ritorna {nome: accettato?} -- e basta che UNA accetti perche' il
    pacchetto sia in gara su quel costruttore."""
    import concurrent.futures as cf
    kid = kid or _chiave_identita()
    # SI FIRMA UNA VOLTA SOLA. La firma e' sul corpo della richiesta, che e'
    # IDENTICO per tutte le porte: rifirmarla per ognuna voleva dire quattro
    # sottoprocessi `cast` invece di uno.
    # DIFETTO CAUSATO DA ME il 4/11 sera, mezz'ora dopo aver aggiunto le
    # quattro porte: 30 pacchetti x 4 porte = 120 firme per ogni
    # aggiornamento dell'oracolo, e il pescatore e' diventato CIECO AL 25%
    # perche' i sottoprocessi gli rubavano la macchina.
    # E' la terza volta in un giorno che un miglioramento, applicato senza
    # guardare cosa costa agli altri, rompe qualcosa di gia' funzionante:
    # dopo ogni propagazione va guardato l'effetto su chi non ho toccato.
    corpo = json.dumps({"jsonrpc":"2.0","id":1,"method":metodo,"params":par})
    # DUE SOTTOPROCESSI SU TRE ELIMINATI DAL PERCORSO CALDO (6/11).
    #
    # Qui girava `cast` tre volte per OGNI corpo -- indirizzo, keccak, firma
    # -- e i corpi sono tre (un blocco ciascuno): nove sottoprocessi per
    # campanella, a ~100 ms l'uno. Astra e Grok, consultati separatamente,
    # concordano che la finestra utile e' 80-250 ms e che chi vince ci sta
    # in 20-80: nove avvii di processo sono da soli piu' della finestra
    # intera. «Fuori gara per costruzione», parole loro.
    # L'indirizzo dell'identita' non cambia MAI -> si calcola una volta e si
    # tiene. Il keccak lo sappiamo fare in casa (agents/keccak.py) -> niente
    # processo. Resta solo la firma, che vuole la chiave privata.
    ident = _IDENT.get(kid)
    if not ident:
        ident = cast("wallet","address","--private-key",kid)
        _IDENT[kid] = ident
    # IL PREFISSO "0x" FA PARTE DEL MESSAGGIO FIRMATO (difetto mio, 6/11,
    # trovato dieci minuti dopo averlo introdotto).
    # `cast keccak` stampa "0x25e7...", e la firma si fa sui CARATTERI di
    # quella stringa, prefisso compreso. Il keccak in casa restituiva
    # "25e7..." senza prefisso: hash giusto, MESSAGGIO DIVERSO.
    # Flashbots e BuilderNet rispondevano «invalid flashbots signature»
    # mentre beaverbuild e Titan accettavano -- cioe' avrei perso DUE porte
    # su quattro in silenzio, e il contatore «accettati» avrebbe continuato
    # a salire grazie alle altre due. La lezione era GIA' scritta nella
    # funzione qui sotto e non l'ho riletta prima di toccare questa.
    h = "0x" + _keccak_locale(corpo.encode()).hex()
    firma_una = cast("wallet","sign","--private-key",kid,"0x"+h.encode().hex())
    intest = {"content-type":"application/json","user-agent":"Mozilla/5.0",
              "X-Flashbots-Signature": f"{ident}:{firma_una}"}
    def una(t):
        nome, url = t
        _t0 = time.time()
        try:
            r = _posta(url, corpo.encode(), intest)
        except Exception as e:
            r = {"errore": str(e)[:120]}
        # IL CRONOMETRO PER PORTA. Stanotte ho sbagliato sei volte a indovinare
        # dove andava il tempo: ora lo si misura dove accade. Il totale di un
        # invio e' il MASSIMO fra le porte, non la somma, quindi serve sapere
        # QUALE porta e' lenta.
        TEMPI.setdefault(nome, []).append(round((time.time() - _t0) * 1000))
        if len(TEMPI[nome]) > 200: TEMPI[nome] = TEMPI[nome][-100:]
        res = (r or {}).get("result")
        ok = bool(isinstance(res, dict) and res.get("bundleHash"))
        return nome, ok, r
    # NON SI ASPETTA LA PORTA LENTA (6/11, misurato col cronometro appena
    # messo): flashbots costa 276 ms di media, beaverbuild 78, BuilderNet 57,
    # titan 55. Il totale di un invio e' il MASSIMO, quindi flashbots da sola
    # dettava i tre quarti del tempo di consegna.
    # Il pacchetto le viene mandato comunque -- la richiesta parte e arriva --
    # ma non si resta ad aspettare la sua risposta per dichiarare fatto il
    # lavoro: il 97,4% del premio passa da beaverbuild, BuilderNet e Titan,
    # misurato sui blocchi dove avvengono le liquidazioni che valgono.
    # NOTA SUL RISCHIO: se flashbots rifiutasse sistematicamente (per esempio
    # per una firma rotta, come e' successo stanotte) non lo vedremmo piu' da
    # qui. Per questo il suo esito si registra comunque in TEMPI e in
    # RIFIUTI_LENTI, e il C-check lo guarda.
    ex = cf.ThreadPoolExecutor(max_workers=len(PORTE))
    futuri = {n: ex.submit(una, (n, u)) for n, u in PORTE}
    fuori = {}
    for n, f in futuri.items():
        if n == "flashbots":
            continue
        _n, ok, r = f.result()
        fuori[_n] = (ok, r)
    def _dopo():
        try:
            _n, ok, r = futuri["flashbots"].result(timeout=20)
            if not ok: RIFIUTI_LENTI.append(str(r)[:120])
            if len(RIFIUTI_LENTI) > 50: del RIFIUTI_LENTI[:25]
        except Exception as e:
            RIFIUTI_LENTI.append(str(e)[:120])
        finally:
            ex.shutdown(wait=False)
    threading.Thread(target=_dopo, daemon=True).start()
    return fuori
def a_tutte_le_porte_molti(metodo, corpi, kid=None):
    """Lo stesso pacchetto per PIU' blocchi, tutte le richieste in UN SOLO
    gruppo di fili.

    PERCHE' (6/11). La sentinella spediva i tre blocchi (+1/+2/+3) con un
    gruppo di fili per blocco, e dentro ciascuno un altro gruppo per le
    porte: gruppi annidati, un avvio di fili per ogni invio, e in Python il
    lucchetto globale fa pagare quella struttura. Misurato: consegna ~250 ms
    quando le singole porte costano 61-99 ms, cioe' tre quarti del tempo
    erano struttura e non rete.
    Qui si costruisce UNA lista di (corpo, porta) e si manda tutto insieme.
    """
    # DUE ONDATE: prima chi accetta il pacchetto NUDO, poi chi vuole la firma.
    #
    # MISURATO il 6/11: beaverbuild e Titan accettano un pacchetto senza
    # X-Flashbots-Signature; BuilderNet e Flashbots la pretendono. E
    # beaverbuild costruisce il 75,5% dei blocchi dove avvengono le
    # liquidazioni che valgono.
    # Quindi il percorso critico puo' non avere NESSUN avvio di processo:
    # si spedisce subito a beaverbuild e Titan senza firmare, e le altre due
    # partono dietro, in sottofondo, con la firma.
    # (Le tre firme costano 27 ms in tutto, non i 240 che avevo supposto: la
    # quarta volta che sbaglio a indovinare dove va il tempo. Ma 27 ms
    # gratis sono 27 ms gratis, e soprattutto spariscono gli avvii di
    # processo, che su una macchina carica non costano sempre uguale.)
    kid = kid or _chiave_identita()
    NUDE = {"beaverbuild", "titan"}          # misurato: accettano senza firma
    intest_nudo = {"content-type": "application/json", "user-agent": "Mozilla/5.0"}
    lavoro = []                              # l'ondata che si aspetta
    corpi_pronti = []
    for c in corpi:
        corpo = json.dumps({"jsonrpc": "2.0", "id": 1, "method": metodo,
                            "params": [c]}).encode()
        corpi_pronti.append(corpo)
        for nome, url in PORTE:
            if nome in NUDE:
                lavoro.append((nome, url, corpo, intest_nudo))
        # TERZA PORTA: bloXroute (7/11). Metodo e forma DIVERSI dagli altri,
        # quindi non basta aggiungerla alla lista: `blxr_submit_bundle` vuole
        # `transaction` + `block_number` e l'intestazione Authorization,
        # niente firma.
        # Perche' vale la pena: la consegna e' metà del nostro collo di
        # bottiglia, la loro rete e' costruita per questo, e l'invio e'
        # AUTORIZZATO sul piano gratuito -- provato con un payload vuoto, che
        # viene rifiutato per il contenuto e non per il diritto. Zero euro.
        # Non si aspetta e non si fa dipendere niente da lei: se e' lenta o
        # cade, le altre due hanno gia' spedito.
        _blx = _chiave_blx()
        if _blx:
            _txs = c.get("txs") or c.get("transaction") or []
            _blocco = c.get("blockNumber") or c.get("block_number")
            if _txs and _blocco:
                _corpo_blx = json.dumps({
                    "id": "1", "method": "blxr_submit_bundle",
                    "params": {"transaction": [t[2:] if t.startswith("0x")
                                               else t for t in _txs],
                               "block_number": _blocco}}).encode()
                lavoro.append(("bloxroute", "https://api.blxrbdn.com",
                               _corpo_blx,
                               dict(intest_nudo, Authorization=_blx)))
    def _firmate_dietro():
        """Le porte che vogliono la firma, fuori dal percorso critico."""
        ident = _IDENT.get(kid)
        if not ident:
            ident = cast("wallet", "address", "--private-key", kid)
            _IDENT[kid] = ident
        for corpo in corpi_pronti:
            h = "0x" + _keccak_locale(corpo).hex()
            f = cast("wallet", "sign", "--private-key", kid,
                     "0x" + h.encode().hex())
            intest = dict(intest_nudo, **{"X-Flashbots-Signature": f"{ident}:{f}"})
            for nome, url in PORTE:
                if nome in NUDE: continue
                try:
                    r = _posta(url, corpo, intest)
                    res = (r or {}).get("result")
                    if not (isinstance(res, dict) and res.get("bundleHash")):
                        RIFIUTI_LENTI.append(f"{nome}: {str(r)[:100]}")
                except Exception as e:
                    RIFIUTI_LENTI.append(f"{nome}: {str(e)[:100]}")
        if len(RIFIUTI_LENTI) > 50: del RIFIUTI_LENTI[:25]
    threading.Thread(target=_firmate_dietro, daemon=True).start()
    def una(t):
        nome, url, corpo, intest = t
        t0 = time.time()
        try:
            r = _posta(url, corpo, intest)
        except Exception as e:
            r = {"errore": str(e)[:120]}
        TEMPI.setdefault(nome, []).append(round((time.time() - t0) * 1000))
        if len(TEMPI[nome]) > 200: TEMPI[nome] = TEMPI[nome][-100:]
        res = (r or {}).get("result")
        return nome, bool(isinstance(res, dict) and res.get("bundleHash")), r
    with cf.ThreadPoolExecutor(max_workers=max(1, len(lavoro))) as ex:
        fuori = {}
        for nome, ok, r in ex.map(una, lavoro):
            pre = fuori.get(nome)
            fuori[nome] = (ok or (pre[0] if pre else False), r)
    return fuori
def flashbots(metodo, par, kid=None, url=None):
    kid=kid or _chiave_identita()
    if not kid: return {"errore":"nessuna chiave di identita'"}
    ident=cast("wallet","address","--private-key",kid)
    corpo=json.dumps({"jsonrpc":"2.0","id":1,"method":metodo,"params":par})
    h=cast("keccak",corpo)
    # LEZIONE: la firma e' sui CARATTERI del hash, non sui byte. `cast`
    # decodifica da solo qualunque cosa inizi per 0x, quindi si passa
    # l'esadecimale DEI CARATTERI del hash. Senza questo il relay rifiuta.
    s=cast("wallet","sign","--private-key",kid,"0x"+h.encode().hex())
    req=urllib.request.Request(url or RELAY, data=corpo.encode(),
        headers={"content-type":"application/json","user-agent":"Mozilla/5.0",
                 "X-Flashbots-Signature": f"{ident}:{s}"})
    try: return json.load(urllib.request.urlopen(req, timeout=20))
    except urllib.error.HTTPError as e:
        return {"http":e.code,"corpo":e.read().decode()[:300]}
    except Exception as e: return {"errore":str(e)[:150]}
# QUANTO OFFRIRE AL COSTRUTTORE. Misurato l'1/11 dalle ricevute dei VINCITORI
# delle 14 liquidazioni piu' grosse degli 88 giorni:
#   su $1.044.685 di premio hanno pagato in tutto $64,16 = lo 0,006%.
#   Il piu' caro: $42,88 per incassare $214.993. Nove su quattordici: $0.
# Quindi queste liquidazioni NON si vincono pagando: si vincono arrivandoci.
# Avevo dedotto il contrario da un «10% del premio» inventato da me, che
# avrebbe richiesto 5 ETH di gas: il muro del capitale non esiste.
# Qui si offre un paio di gwei -- piu' di quasi tutti i vincitori, e dentro
# quello che il portafoglio operativo puo' pagare.
PRIORITA_GWEI=2.0
TETTO_DOLLARI=12.0        # mai piu' di cosi' di gas per un tentativo
def manda(contratto, chiamata, chiave, gas_limite, testa, priorita_gwei=None,
          blocchi=3, rpc="https://ethereum-rpc.publicnode.com",
          prezzo_eth=None, nonce=None):
    """Firma e CONSEGNA, poi simula per sapere com'e' andata.

    ORDINE, misurato l'1/11 pezzo per pezzo:
      comporre la chiamata    90 ms
      leggere la testa       394 ms  -> si passa da fuori, il pescatore la sa
      firmare               290 ms  -> con --nonce diventa locale
      CONSEGNARE            381 ms  <- il pavimento, non si tocca
      simulare              387 ms  -> DOPO, non prima
    Simulare prima costava 1.479 ms in tutto e si mangiava gli 885 ms
    guadagnati col preventivo pronto. E la simulazione NON serve da cancello:
    un pacchetto che si annulla non viene incluso e non si paga, quindi
    spedirlo non costa niente. Serve a sapere PERCHE' non e' andata.
    """
    out={"via":"pacchetto"}
    if priorita_gwei is None: priorita_gwei=PRIORITA_GWEI
    if prezzo_eth:
        costo=gas_limite*priorita_gwei*1e-9*prezzo_eth
        if costo>TETTO_DOLLARI:
            priorita_gwei=TETTO_DOLLARI/(gas_limite*1e-9*prezzo_eth)
            out["priorita_tagliata_al_tetto"]=round(priorita_gwei,4)
    out["priorita_gwei"]=round(priorita_gwei,4)
    # `cast mktx` rifiuta se la priorita' supera il massimo che calcola da
    # solo: la commissione base e' 0,04 gwei, quindi il tetto va dichiarato.
    massimo=priorita_gwei+2.0
    arg=["mktx",contratto,chiamata,"--private-key",chiave,
         "--gas-limit",str(gas_limite),"--gas-price",f"{massimo}gwei",
         "--priority-gas-price",f"{priorita_gwei}gwei"]
    if nonce is not None:
        # col nonce dato, la firma non chiede niente alla rete
        arg += ["--nonce",str(nonce),"--chain","1"]
    else:
        arg += ["--rpc-url",rpc]
    grezza=cast(*arg)
    if not grezza.startswith("0x"):
        out["esito"]="firma fallita"; out["perche"]=grezza[:160]; return out
    out["lunghezza"]=len(grezza)
    # SI CONSEGNA IL PRIMO BLOCCO E SI TORNA SUBITO.
    # L'unico tempo che conta e' fino alla PRIMA consegna: i blocchi
    # successivi e la simulazione avvengono mentre siamo gia' in gara.
    # Mandarli in fila costava 1.790 ms contro i ~570 della prima consegna:
    # tre quarti del tempo era lavoro che non serviva a vincere.
    # A TUTTE LE PORTE. Prima andava solo al relay di Flashbots, e
    # beaverbuild -- che costruisce il 75,5% dei blocchi dove avvengono le
    # liquidazioni che valgono -- non lo riceveva mai.
    _es=a_tutte_le_porte("eth_sendBundle", [{"txs":[grezza],"blockNumber":hex(testa+1)}])
    _acc=[n for n,(ok,_) in _es.items() if ok]
    out["porte_accettate"]=_acc
    r={"result":{"bundleHash":"ok"}} if _acc else None
    primo=bool((r or {}).get("result",{}).get("bundleHash"))
    out["accettati"]=1 if primo else 0
    out["primo_blocco"]=testa+1
    out["esito"]="pacchetto consegnato" if primo else "il relay ha rifiutato"
    out["coda"]={}           # lo riempie il filo di fondo
    def dopo():
        for b in range(2, blocchi+1):
            rr=flashbots("eth_sendBundle", [{"txs":[grezza],
                "blockNumber":hex(testa+b)}])
            out["coda"][f"blocco_{testa+b}"]=bool(
                (rr or {}).get("result",{}).get("bundleHash"))
        sim=flashbots("eth_callBundle", [{"txs":[grezza],
            "blockNumber":hex(testa+1),"stateBlockNumber":"latest"}])
        ris=((sim or {}).get("result") or {}).get("results") or []
        if ris:
            r0=ris[0]
            out["gas_simulato"]=r0.get("gasUsed")
            if ("error" in r0) or ("revert" in r0) or (r0.get("value") is None):
                out["simulazione"]="si annulla"
                out["perche"]=str(r0.get("revert") or r0.get("error") or "-")[:160]
            else:
                out["simulazione"]="riuscirebbe"
    if primo:
        threading.Thread(target=dopo, daemon=True).start()
    return out
if __name__=="__main__":
    print("   chiave di identita':", "c'e'" if os.path.exists(".chiavi/identita")
          else "da creare al primo uso")
    kid=_chiave_identita()
    print("   indirizzo di identita':", cast("wallet","address","--private-key",kid))
    print("   il relay risponde:", json.dumps(flashbots("eth_blockNumber",[]))[:140])
