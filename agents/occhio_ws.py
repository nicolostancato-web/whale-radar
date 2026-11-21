# -*- coding: utf-8 -*-
"""L'OCCHIO LARGO: il mempool via websocket, con la sola libreria standard.

PERCHE' ESISTE (5/11, dopo l'ottava liquidazione). Misurato: la sentinella
guardava il mempool con eth_newPendingTransactionFilter + eth_getFilterChanges
su HTTP, e vedeva l'8% degli aggiornamenti dell'oracolo (8 su 96 in 41
blocchi). Per questo l'aggiornamento che ha fatto cadere la posizione ci e'
sfuggito 8 volte su 8: non sfortuna, copertura.
Il co-pacchetto [oracolo, nostra] era GIA' giusto e completo. Non serviva a
niente, perche' si innescava sull'8% sbagliato.

NON si installa niente: PEP 668 blocca pip qui e .venv_bot2 non e' un venv
vero (sono collegamenti al python di sistema), quindi un `pip install` andrebbe
a toccare il python di sistema. Un websocket minimo e' 60 righe di stdlib.
"""
import base64, json, os, socket, ssl, struct, time
FONTI_WS = [
    "wss://ethereum-rpc.publicnode.com",
    "wss://eth.drpc.org",
]
class Ws:
    def __init__(self, url, timeout=20):
        p = url.split("://", 1)[1]
        host, _, resto = p.partition("/")
        host, _, porta = host.partition(":")
        self.host = host
        s = socket.create_connection((host, int(porta or 443)), timeout=timeout)
        self.s = ssl.create_default_context().wrap_socket(s, server_hostname=host)
        chiave = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((
            f"GET /{resto} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\n"
            f"Connection: Upgrade\r\nSec-WebSocket-Key: {chiave}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n").encode())
        testa = b""
        while b"\r\n\r\n" not in testa:
            p = self.s.recv(4096)
            if not p: raise OSError("la porta si e' chiusa durante il saluto")
            testa += p
        if b"101" not in testa.split(b"\r\n", 1)[0]:
            raise OSError("saluto rifiutato: " + testa.split(b"\r\n",1)[0].decode("latin1"))
        self.resto = testa.split(b"\r\n\r\n", 1)[1]
    def _leggi(self, n):
        while len(self.resto) < n:
            p = self.s.recv(65536)
            if not p: raise OSError("la porta si e' chiusa")
            self.resto += p
        fuori, self.resto = self.resto[:n], self.resto[n:]
        return fuori
    def manda(self, testo):
        d = testo.encode(); m = os.urandom(4)
        n = len(d)
        if n < 126: testa = struct.pack("!BB", 0x81, 0x80 | n)
        elif n < 65536: testa = struct.pack("!BBH", 0x81, 0xFE, n)
        else: testa = struct.pack("!BBQ", 0x81, 0xFF, n)
        self.s.sendall(testa + m + bytes(b ^ m[i % 4] for i, b in enumerate(d)))
    def ricevi(self):
        """Un messaggio di testo, o None per i frame di servizio."""
        b0, b1 = struct.unpack("!BB", self._leggi(2))
        op = b0 & 0x0F; n = b1 & 0x7F
        if n == 126: n = struct.unpack("!H", self._leggi(2))[0]
        elif n == 127: n = struct.unpack("!Q", self._leggi(8))[0]
        if b1 & 0x80: self._leggi(4)          # mascherato dal server: raro
        d = self._leggi(n)
        if op == 0x9:                          # ping -> pong, o ci chiude
            self.s.sendall(struct.pack("!BB", 0x8A, 0x80) + os.urandom(4)); return None
        if op == 0x8: raise OSError("chiusura richiesta dalla porta")
        if op != 0x1: return None
        return d.decode("utf-8", "replace")
    def chiudi(self):
        try: self.s.close()
        except OSError: pass
def apri_sottoscrizione(url, metodo="newPendingTransactions", pieno=False):
    """Apre e sottoscrive. `pieno=True` chiede le transazioni intere invece
    dei soli hash: cosi' si legge il selettore SENZA una seconda richiesta,
    che e' il tempo che non abbiamo nel momento che conta."""
    w = Ws(url)
    par = [metodo] + ([True] if pieno else [])
    w.manda(json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_subscribe","params":par}))
    scad = time.time() + 10
    while time.time() < scad:
        m = w.ricevi()
        if not m: continue
        r = json.loads(m)
        if r.get("id") == 1:
            if r.get("error"):
                w.chiudi(); raise OSError(str(r["error"])[:120])
            if not pieno:
                return w
            # LA FORMA SI VERIFICA, NON SI ASSUME (7/11).
            # drpc accetta la richiesta di transazioni intere, NON da' errore,
            # e poi manda solo gli hash. Per giorni l'abbiamo contata come una
            # porta buona: su 177 campanelle publicnode e' stata prima 177
            # volte e drpc zero, e credevamo di avere due occhi sulla gara.
            # Un ripiego silenzioso su una cosa indispensabile e' una bugia:
            # qui la bugia era della porta, ma l'errore di non accorgersene
            # era mio, perche' misuravo «si sottoscrive» invece di «consegna
            # qualcosa che si puo' leggere».
            # Quindi si guarda il PRIMO risultato: se e' una stringa, questa
            # porta non serve alla gara e si dice subito, ad alta voce.
            scad2 = time.time() + 12
            while time.time() < scad2:
                m2 = w.ricevi()
                if not m2:
                    continue
                try:
                    r2 = json.loads(m2)
                except ValueError:
                    continue
                res = (r2.get("params") or {}).get("result")
                if res is None:
                    continue
                if isinstance(res, dict) and "input" in res:
                    return w
                w.chiudi()
                raise OSError(
                    "manda SOLO HASH invece delle transazioni intere: "
                    "inutile per la gara (serve una seconda richiesta di "
                    "rete per leggere il selettore)"
                    if not isinstance(res, dict) else
                    "manda un dizionario SENZA il campo input: "
                    "non si puo' leggere il selettore")
            w.chiudi()
            raise OSError("sottoscritta ma non ha mandato niente in 12s")
    w.chiudi(); raise OSError("nessuna risposta alla sottoscrizione")

# ---------------------------------------------------------------------------
# L'OCCHIO IN PRODUZIONE: tutte le porte insieme, e si tiene il primo che
# sente. PERCHE' PIU' DI UNA: ogni nodo e' collegato a vicini diversi e sente
# una fetta diversa del mempool. La copertura e' l'UNIONE, non il massimo.
# Misurato il 5/11: delle 13 porte pubbliche gratuite provate, 3 accettavano
# le transazioni intere (publicnode, drpc, tenderly); le altre 10 rifiutano
# il saluto o chiedono una chiave.
#
# TENDERLY TOLTA IL 7/11, MISURANDO IL VOLUME E NON IL SALUTO.
# Provata da sola per 35 secondi: ZERO messaggi consegnati e una caduta. Nel
# log della sentinella era caduta 40 volte in 68 minuti, e quel rumore
# COPRIVA le 5 cadute di drpc -- che invece e' una porta vera. Una porta
# muta non e' gratis: occupa un filo che si riapre in continuazione e
# nasconde i guasti di quelle che contano.
# E' la seconda volta che questa porta ci inganna: la prima perche' l'avevo
# provata sulla stretta di mano ("si apre") invece che sul volume ("manda
# qualcosa"), e per giorni abbiamo creduto di avere tre finestre quando ne
# avevamo due. La copertura e' l'unione delle porte che PARLANO.
# Quindi adesso sono DUE, e il C-check lo dice invece di farci credere tre.
# DRPC TOLTA IL 7/11: accetta la richiesta di transazioni intere, non da'
# errore, e manda solo gli hash. Venticinquemila messaggi in 34 minuti, zero
# utili. Un flusso di soli hash NON si recupera come ripiego: per sapere se
# un hash e' un aggiornamento d'oracolo bisogna risolverlo con una richiesta
# di rete, e ne arrivano dodici al secondo -- ci farebbero bandire in un
# minuto. Quindi non e' una porta lenta: e' una porta che non serve.
#
# CENSIMENTO RIFATTO col criterio giusto (agents/censimento_porte.py), 30
# indirizzi provati: ne consegna transazioni intere UNO SOLO. Il secondo
# nome di publicnode (ethereum.publicnode.com) funziona ma risolve agli
# STESSI due indirizzi IP, quindi non e' un secondo occhio -- protegge solo
# dall'essere strozzati su un nome, non dalla caduta del fornitore.
# E' tenuto come riserva proprio per quel caso, dichiarato per quello che e'.
#
# QUINDI: abbiamo UN SOLO occhio indipendente sulla gara, ed e' caduto 2
# volte in 5 ore. Se cade, siamo ciechi sull'unica cosa che decide se
# vinciamo. Non e' riparabile gratis: le 29 porte gratuite rimanenti o
# rifiutano il saluto, o chiedono una chiave, o mandano hash. La guardia
# qui sotto almeno lo rende RUMOROSO invece che invisibile.
PORTE_BUONE = ["wss://ethereum-rpc.publicnode.com",
               "wss://ethereum.publicnode.com"]
# CHI CI NUTRE DAVVERO? (7/11)
# Non lo sapevamo: le porte erano tre e nessuno contava quante transazioni
# arrivavano da ognuna. E' lo stesso errore che ci e' gia' costato caro --
# tenderly era stata provata sulla STRETTA DI MANO (si apre) invece che sul
# VOLUME (manda qualcosa), e per giorni abbiamo creduto di avere tre finestre
# quando ne avevamo due. Stanotte quella porta e' caduta 40 volte in 68
# minuti e il rumore copriva le cadute di drpc, che invece e' una porta vera.
# Un contatore per stadio, sempre: "aperta" non e' "sente", e "sente" non e'
# "sente per prima". Costa un incremento in un dizionario.
# «PRIMA» E' BINARIO E NON BASTA (7/11).
# Primo frutto del contatore: drpc ha consegnato 21.118 messaggi ed e' stata
# prima su ZERO delle 21 campanelle; publicnode prima su tutte e 21. Ma
# «zero volte prima» non distingue una porta che arriva 5 ms dopo -- utile,
# perche' coprirebbe l'altra se cadesse -- da una che arriva mezzo secondo
# dopo, che sulla gara dell'oracolo non serve a niente.
# Quindi si misura il RITARDO: quando lo stesso hash riarriva da un'altra
# porta, si segna di quanto e' tardi. Serve a sapere se publicnode e' un
# punto singolo di rottura sulla cosa che decide se vinciamo.
# 177 CAMPANELLE, DRPC PRIMA SU ZERO E NESSUN RITARDO REGISTRATO (7/11).
# Se drpc portasse gli aggiornamenti d'oracolo in ritardo, il ritardo si
# vedrebbe: arriverebbe al confronto e troverebbe l'hash gia' visto. Zero
# ritardi su 177 campanelle vuol dire che drpc non li porta AFFATTO --
# centosessantottomila messaggi consegnati e nessuno era una campanella.
# Ma «non li porta» ha due cause diverse e non so ancora quale sia: o il suo
# nodo non vede quelle transazioni, o le manda in una forma che il filtro
# scarta prima (per esempio senza il campo input). La differenza conta: la
# prima e' una porta da sostituire, la seconda e' un nostro difetto di
# lettura che ci sta buttando via una finestra intera.
# Quindi si conta anche quanti messaggi SUPERANO il filtro, per porta: e'
# lo stadio in mezzo, quello che distingue le due cause.
PASSATI = {}        # url -> messaggi che hanno superato il filtro selettore
RITARDI = {}        # url -> [ritardi in ms rispetto alla prima]
SENTITE = {}        # url -> quante transazioni e' stata la PRIMA a portare
MESSAGGI = {}       # url -> quanti messaggi ha consegnato in tutto
CADUTE = {}         # url -> quante volte e' caduta


def resoconto_porte():
    """(url, messaggi, prime, cadute, ritardo_mediano_ms, quanti_ritardi,
    passati_dal_filtro)."""
    tutte = set(MESSAGGI) | set(SENTITE) | set(CADUTE)
    tutte = tutte | set(PASSATI)
    fuori = []
    for u in tutte:
        r = sorted(RITARDI.get(u) or [])
        med = r[len(r) // 2] if r else None
        fuori.append((u, MESSAGGI.get(u, 0), SENTITE.get(u, 0),
                      CADUTE.get(u, 0), med, len(r), PASSATI.get(u, 0)))
    return sorted(fuori, key=lambda x: -x[2])


def ascolta_tutte(quando_senti, selettore=None, ferma=None, porte=None,
                  su_errore=None):
    """Apre tutte le porte in thread separati e chiama `quando_senti(tx, porta)`
    per ogni transazione nuova (filtrata per selettore, se dato).

    Si consegna il PRIMO che sente: lo stesso hash arriva da porte diverse e
    va passato una volta sola, altrimenti componiamo lo stesso pacchetto tre
    volte e bruciamo il tempo che stiamo cercando di guadagnare.

    Se una porta cade si riapre da sola: una finestra chiusa in silenzio e'
    esattamente il guasto che ci e' costato 8 liquidazioni su 8.
    """
    import threading
    visti = {}            # hash -> porta che l'ha sentito per prima
    quando_visto = {}     # hash -> quando l'ha sentito la prima porta
    lock = threading.Lock()
    attesa = {}
    def una(url):
        while not (ferma and ferma()):
            w = None
            try:
                w = apri_sottoscrizione(url, pieno=True)
                vissuto = time.time()
                while not (ferma and ferma()):
                    m = w.ricevi()
                    if not m: continue
                    MESSAGGI[url] = MESSAGGI.get(url, 0) + 1
                    # IL SELETTORE SI CERCA NEL TESTO GREZZO, PRIMA di
                    # interpretare il messaggio (6/11).
                    #
                    # PERCHE'. Qui passano ~12 messaggi al secondo per porta,
                    # ognuno una transazione intera da qualche kilobyte, e
                    # facevamo json.loads su TUTTI per poi buttarne il 99,9%.
                    # In Python quel lavoro tiene il lucchetto globale e
                    # rallenta ogni altro filo dello stesso processo: nel
                    # sistema vivo comporre un pacchetto costava 84-304 ms
                    # mentre in isolamento costa ZERO, e la differenza erano
                    # i nostri stessi ascoltatori.
                    # Cercare una sottostringa di dieci caratteri costa
                    # qualche microsecondo; interpretare il JSON costa mille
                    # volte tanto. Il filtro che si puo' fare prima, si fa
                    # prima -- e non cambia cosa passa, perche' il selettore
                    # compare comunque nel campo input.
                    if selettore and selettore not in m: continue
                    try: r = json.loads(m)
                    except ValueError: continue
                    tx = (r.get("params") or {}).get("result")
                    if not isinstance(tx, dict):
                        # forma diversa dal previsto: si segna, perche' una
                        # porta che manda qualcosa che non sappiamo leggere
                        # e' un nostro difetto, non una porta muta
                        continue
                    if selettore and not (tx.get("input") or "0x").startswith(selettore):
                        continue
                    h = (tx.get("hash") or "").lower()
                    if not h: continue
                    PASSATI[url] = PASSATI.get(url, 0) + 1
                    ora = time.time()
                    with lock:
                        if h in visti:
                            _q = quando_visto.get(h)
                            if _q is not None:
                                _l = RITARDI.setdefault(url, [])
                                if len(_l) < 500:
                                    _l.append((ora - _q) * 1000)
                            continue
                        visti[h] = url
                        quando_visto[h] = ora
                        SENTITE[url] = SENTITE.get(url, 0) + 1
                        if len(visti) > 60000:        # il registro non cresce all'infinito
                            for k in list(visti)[:20000]:
                                del visti[k]
                                quando_visto.pop(k, None)
                    quando_senti(tx, url)
                    if attesa.get(url) and time.time() - vissuto > 120:
                        attesa[url] = 0      # ha retto 2 minuti: si riparte sereni
            except Exception as e:
                CADUTE[url] = CADUTE.get(url, 0) + 1
                if su_errore: su_errore(url, e)
                # NON SI BRUCIA LA FONTE. publicnode ci ha messo in castigo
                # il 5/11 per troppe richieste (due processi in ascolto sulle
                # stesse porte insieme, colpa mia). Riprovare ogni 2 secondi
                # su un rifiuto per limite tiene la porta chiusa per ore:
                # l'attesa raddoppia fino a 5 minuti, e si riparte da 2
                # secondi solo dopo un collegamento che ha retto.
                m = str(e).lower()
                if "rate" in m or "limit" in m or "429" in m or "too many" in m:
                    attesa[url] = min(300, max(15, attesa.get(url, 15) * 2))
                else:
                    attesa[url] = min(60, max(2, attesa.get(url, 2) * 2))
                time.sleep(attesa[url])
            finally:
                if w: w.chiudi()
    th = [threading.Thread(target=una, args=(u,), daemon=True)
          for u in (porte or PORTE_BUONE)]
    for t in th: th and t.start()
    return th, visti
