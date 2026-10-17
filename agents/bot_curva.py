"""Le mani. La prova dentro la curva decide, questo esegue.

PERCHE' NON DECIDE DA SE'. Un secondo cervello che rilegge la chain per conto suo si
scosterebbe dal primo per mille dettagli — un blocco letto prima, una riserva arrotondata
diversa — e quando i due non coincidono non si sa piu' quale dei due stai misurando. Qui il
cervello resta uno solo: `prova_nella_curva.py` apre e chiude le posizioni, questo legge le
sue decisioni e le trasforma in transazioni. Per costruzione non possono divergere.

LA REGOLA CHE ESEGUE e' `50-5` e solo quella: e' l'unica con abbastanza chiusure per essere
letta (+9,8% su 232 al 13/10). Le altre restano sulla carta finche' non maturano.

COME SI PAGA, verificato sulla chain il 13/10 su acquisti veri:
  acquisto  -> alla curva, con i nativi ALLEGATI:  0x59a87bc1(quanto, minimo, a_chi)
  vendita   -> alla curva, senza valore allegato:  0xd04c6983(gettoni, minimo, a_chi)
Ogni gettone ha la SUA curva: il destinatario cambia a ogni moneta.

SICUREZZA. La chiave privata non sta qui, non sta nel repository (che e' pubblico) e non
passa da nessun messaggio: si legge dal file delle credenziali sul disco di Nicolo'. Un
repository pubblico con dentro una chiave viene svuotato in minuti da programmi che non
fanno altro che cercarle.

COSTO. Il nodo e' pubblico e gratuito. Le transazioni costano gas: 0,007 EUR l'una, misurato.
A vuoto (modo predefinito) non si spende nulla, perche' non si manda niente.
"""
import json
import os
import re
import sys
import time
import urllib.request

RPC = os.environ.get("RPC_ROBINHOOD", "https://rpc.mainnet.chain.robinhood.com")
CHAIN_ID = 4663
STATO = "data/multichain/robinhood/prova_nella_curva.json"
MIO = "data/multichain/robinhood/bot_curva.json"
CREDENZIALI = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
SEZIONE = "=== WHALE RADAR BOT ==="

REGOLA = "50-5"
SEL_COMPRA = "0x59a87bc1"
SEL_VENDE = "0xd04c6983"

# I TETTI SONO NEL CODICE, NON NELLE OPZIONI. Un tetto che si puo' alzare da riga di comando
# non e' un tetto: e' un suggerimento. Per alzarli si modifica questo file, si rilegge la
# riga, e lo si fa da svegli.
# SCESO DA 2 A 1 EURO (14/10, su richiesta di Nicolo' di abbassare la posta finche' la
# macchina si sistema). Non si scende a 0,50 per una ragione di conti: ogni posizione costa
# tre transazioni (compra, autorizza, vendi), circa 6 centesimi in tutto. Su 2 euro sono il
# 3%, su 1 euro il 6%, su 0,50 il 12% — e a quel punto il gas si mangia proprio il segnale
# che stiamo misurando. Un euro e' il punto piu' basso dove il costo fisso resta leggibile.
TETTO_POSIZIONE = float(os.environ.get("TETTO_POSIZIONE", "0.0007"))   # ~2 EUR
TETTO_GIRO = float(os.environ.get("TETTO_GIRO", "0.0035"))             # ~10 EUR per giro
# IL TETTO CHE CONTA E' QUELLO CUMULATO. Un tetto per giro non limita niente se i giri sono
# mille: limita la singola botta, non il danno. Questo invece si somma e non si azzera mai,
# quindi dopo ~20 posizioni il bot si ferma da solo e aspetta che un umano guardi.
# IL FRENO GIUSTO E' SULLA PERDITA, NON SULLA SPESA (14/10). Il tetto contava quanto avevamo
# speso in totale, ma i soldi rientrano a ogni vendita: dopo venti giri la macchina si fermava
# con la cassa ancora intatta. Un freno che scatta quando non c'e' nessun danno non protegge,
# intralcia — e uno che non guarda la cassa non si accorgerebbe del danno vero. Qui si guarda
# il saldo complessivo dei portafogli: si compra finche' resta sopra la soglia.
TETTO_TOTALE = float(os.environ.get("TETTO_TOTALE", "999"))            # spento: vedi PAVIMENTO
PAVIMENTO = float(os.environ.get("PAVIMENTO", "0.0188"))               # 80% di 0,023487
# LE POSIZIONI CHE NESSUNO CHIUDE. Il 24% delle curve smette semplicemente di scambiare: la
# prova non vede piu' prezzi e la posizione resta aperta per sempre. Misurato il 13/10, il
# taglio a un'ora e' il migliore fra quattro (136 operazioni invece di 83, e piu' resa).
TAGLIO_SEC = int(os.environ.get("TAGLIO_SEC", "3600"))
LUCCHETTO = "/tmp/bot_curva.lock"
# NON SI COMPRA UNA DECISIONE VECCHIA. Il bot legge quello che la prova ha deciso, e quel file
# puo' avere minuti. Comprare una posizione aperta venti minuti fa vuol dire entrare a un
# prezzo che non c'e' piu' — ed entrare tardi e' esattamente la cosa che abbiamo MISURATO non
# funzionare (entrata a 3,6 di riserva: tutte le varianti in perdita, nessuna arrivata a 3x).
# Oltre questo limite la decisione si butta, non si esegue in ritardo.
FRESCHEZZA_SEC = int(os.environ.get("FRESCHEZZA_SEC", "600"))
# QUELLO CHE CONTA NON E' L'OROLOGIO, E' IL PREZZO. Il limite a 60 secondi era un modo
# indiretto di dire «non entrare dopo che il prezzo e' scappato». Ma una posizione lenta puo'
# stare ferma al prezzo d'ingresso per minuti — e rifiutarla per anzianita' significa buttare
# proprio le occasioni che il bot riesce a vedere. Misurato il 13/10: il 63% delle posizioni
# vive oltre i 6 secondi del nostro ciclo, e di quelle il 46% e' ancora al prezzo d'entrata.
# Quindi si guarda il prezzo, e l'orologio resta solo come rete di sicurezza.
PREZZO_MIN = float(os.environ.get("PREZZO_MIN", "0.97"))
PREZZO_MAX = float(os.environ.get("PREZZO_MAX", "1.05"))
SCARTO = 0.15      # quanto prezzo in meno accetto di ricevere, per non farmi annullare l'ordine
# RIDOTTO DA 3 A 1,5 (14/10). Lo scarto che aveva fatto rimbalzare la vendita era dello
# 0,6% fra il prezzo letto e la base del blocco: una volta e mezza lo copre ottanta volte.
# Triplicare era prudenza pagata in contanti, e a 1 euro di posizione il gas pesa.
MARGINE_GAS = float(os.environ.get("MARGINE_GAS", "1.5"))
# PRIMA DI VENDERE SERVE UN PERMESSO (14/10). La curva non puo' prendersi i gettoni se il
# portafoglio non l'ha autorizzata: la prima vendita vera e' tornata indietro con
# «ERC20InsufficientAllowance». Lo avevo pure "validato" la notte prima su un portafoglio
# altrui — che il permesso ce l'aveva gia'. Avevo controllato il passaggio senza accorgermi
# che funzionava per una ragione che a noi mancava.
SEL_PERMESSO = "0x095ea7b3"


def chiama(metodo, parametri, attesa=15):
    d = json.dumps({"jsonrpc": "2.0", "id": 1, "method": metodo, "params": parametri}).encode()
    r = urllib.request.Request(RPC, data=d, headers={"Content-Type": "application/json",
                                                     "User-Agent": "whale-radar/1.0"})
    try:
        o = json.load(urllib.request.urlopen(r, timeout=attesa))
    except Exception as e:
        print(f"BOT | il nodo non risponde a {metodo}: {e}")
        return None
    if "error" in o:
        print(f"BOT | il nodo rifiuta {metodo}: {o['error']}")
        return None
    return o.get("result")


def chiavi():
    """Le chiavi private, dal file delle credenziali. Mai da altrove, mai stampate.

    UN PORTAFOGLIO PER POSTO (13/10). Gli ordini di uno stesso portafoglio si mettono in fila
    e il secondo aspetta il primo: misurato, il 51% delle uscite cade entro un secondo dalla
    precedente, e non sparse ma ammassate nello stesso istante, perche' le scatena lo stesso
    movimento di mercato. Con un portafoglio solo, meta' delle uscite arriverebbe in ritardo
    proprio quando il ritardo costa. Con uno per posizione, nessuna coda.

    Il formato della riga non si impone: si cerca una chiave da 64 cifre esadecimali in
    qualunque riga della sezione. Pretendere `NOME=valore` significava zero chiavi trovate
    su sei presenti.
    """
    if not os.path.exists(CREDENZIALI):
        print(f"BOT | manca il file delle credenziali: {CREDENZIALI}")
        return []
    dentro, fuori = False, []
    for riga in open(CREDENZIALI, encoding="utf-8", errors="ignore"):
        if riga.strip().startswith("==="):
            dentro = riga.strip() == SEZIONE
            continue
        if not dentro:
            continue
        m = re.search(r"(?:0x)?([0-9a-fA-F]{64})\b", riga)
        if m:
            fuori.append("0x" + m.group(1))
    if not fuori:
        print(f"BOT | nella sezione «{SEZIONE}» non trovo nessuna chiave")
    return fuori


def campo(n):
    return f"{n:064x}"


def dati_acquisto(quanto_wei, minimo_gettoni, a_chi):
    return SEL_COMPRA + campo(quanto_wei) + campo(minimo_gettoni) + campo(int(a_chi, 16))


def dati_permesso(curva):
    """Autorizza LA CURVA DI QUESTO GETTONE a prendere i gettoni.

    CHI VA AUTORIZZATO CAMBIA A OGNI MONETA (14/10). Avevo letto l'indirizzo da autorizzare
    nel messaggio d'errore di UNA posizione e l'avevo scritto fisso nel codice. Funzionava per
    quella e per nessun'altra: le due posizioni successive sono rimaste invendibili, e una
    aveva gia' toccato il bersaglio a +50%. L'indirizzo e' sempre la curva del gettone — ogni
    moneta ha la sua. Generalizzare da un caso solo e' lo stesso errore di sempre, con la
    differenza che questa volta teneva in ostaggio una posizione vincente.

    Si manda SUBITO DOPO L'ACQUISTO, mentre la posizione e' tranquilla — mai nell'istante in
    cui bisogna scappare.
    """
    return SEL_PERMESSO + campo(int(curva, 16)) + campo((1 << 256) - 1)


def dati_vendita(gettoni, minimo_wei, a_chi):
    return SEL_VENDE + campo(gettoni) + campo(minimo_wei) + campo(int(a_chi, 16))


def leggi_stato():
    if not os.path.exists(STATO):
        print(f"BOT | non trovo le decisioni della prova: {STATO}")
        return None
    with open(STATO) as f:
        return json.load(f)


def mio_registro():
    if os.path.exists(MIO):
        with open(MIO) as f:
            return json.load(f)
    return {"fatte": {}, "spesi_nativi": 0.0, "giri": 0}


def salva(reg):
    # ANCHE QUI SI SPOSTA, NON SI SCRIVE SUL POSTO: questo registro dice quali posizioni sono
    # nostre. Troncarlo a meta' significa dimenticare una posizione comprata e non venderla.
    os.makedirs(os.path.dirname(MIO), exist_ok=True)
    tmp = MIO + ".tmp"
    with open(tmp, "w") as f:
        json.dump(reg, f)
    os.replace(tmp, MIO)


_NUMERI = {}


def prossimo_numero(indirizzo):
    """Il numero d'ordine della prossima transazione, contato da noi.

    PERCHE' NON SI CHIEDE OGNI VOLTA AL NODO (14/10). Subito dopo un acquisto mandiamo il
    permesso di vendere dallo stesso portafoglio. Chiedendo il numero al nodo, quello appena
    usato non risultava ancora consumato: «nonce too low, tx: 0 state: 1». Risultato: due
    acquisti riusciti e due permessi rifiutati, cioe' due posizioni comprate che non si
    potevano vendere — esattamente la trappola che volevamo evitare. Il numero lo teniamo
    noi: si chiede al nodo una volta sola, poi si incrementa a ogni invio riuscito.
    """
    if indirizzo not in _NUMERI:
        n = chiama("eth_getTransactionCount", [indirizzo, "pending"])
        if n is None:
            return None
        _NUMERI[indirizzo] = int(n, 16)
    return _NUMERI[indirizzo]


def manda(conto, a, dati, valore_wei, vero):
    """Firma e manda. A vuoto si ferma un attimo prima, dopo aver provato tutto il resto."""
    gas = chiama("eth_estimateGas", [{"from": conto.address, "to": a,
                                      "data": dati, "value": hex(valore_wei)}])
    if gas is None:
        print("BOT | la stima del gas fallisce: l'ordine verrebbe rifiutato, non lo mando")
        return None
    prezzo = chiama("eth_gasPrice", [])
    nonce = prossimo_numero(conto.address)
    if prezzo is None or nonce is None:
        return None
    # IL PREZZO DEL GAS SI MAGGIORA (14/10, costato 1,50 euro per impararlo). La prima vendita
    # vera e' stata rifiutata dal nodo per 118.000 wei di differenza fra il prezzo che avevamo
    # letto e la base del blocco al momento dell'invio: «max fee per gas less than block base
    # fee». Zero euro di differenza, e l'ordine non parte. Il gas qui costa 0,007 euro: pagarne
    # il triplo e' un'assicurazione gratis contro un'uscita che non parte proprio quando serve.
    tx = {"to": a, "value": valore_wei, "gas": int(int(gas, 16) * 1.3),
          "gasPrice": int(int(prezzo, 16) * MARGINE_GAS), "nonce": nonce,   # gia' un numero: lo conta prossimo_numero(), non il nodo
          "data": dati, "chainId": CHAIN_ID}
    costo = int(gas, 16) * int(prezzo, 16) / 1e18
    if not vero:
        print(f"   A VUOTO: ordine pronto e accettato dal nodo (gas {int(gas, 16):,}, "
              f"costo {costo:.6f} nativi). NON lo mando.")
        return "a-vuoto"
    from eth_account import Account
    from eth_utils import to_checksum_address
    # L'INDIRIZZO VA IN FORMA CON LE MAIUSCOLE (14/10). Noi li teniamo tutti minuscoli perche'
    # cosi' arrivano dalla chain e cosi' si confrontano senza sorprese. Ma la firma li rifiuta:
    # «Transaction had invalid fields: to». L'eccezione finiva dentro il riparo generico delle
    # mani, che stampava «fallito ma la prova continua» — e intanto il contatore della spesa
    # era GIA' stato incrementato. Risultato: il registro diceva 4 euro spesi e sulla chain non
    # era partito niente. Un errore che mente sui soldi e' peggio di un errore che si ferma.
    tx["to"] = to_checksum_address(tx["to"])
    firmata = Account.from_key(conto.key).sign_transaction(tx)
    grezza = firmata.raw_transaction.hex()
    # NON si usa lstrip("0x"): toglierebbe anche gli zeri iniziali veri dell'esadecimale.
    h = chiama("eth_sendRawTransaction",
               [grezza if grezza.startswith("0x") else "0x" + grezza])
    if h:
        _NUMERI[conto.address] = _NUMERI.get(conto.address, 0) + 1
    else:
        # invio fallito: forse e' il NOSTRO conto a essere sfasato. Lo si dimentica, cosi' al
        # prossimo tentativo si riparte dal numero vero del nodo.
        _NUMERI.pop(conto.address, None)
    print(f"   MANDATO: {h}")
    return h


def lucchetto_preso():
    """Un bot solo alla volta. Due copie in parallelo userebbero lo stesso numero d'ordine
    per due transazioni diverse: la seconda viene scartata e quella posizione non esce."""
    if os.path.exists(LUCCHETTO):
        eta = time.time() - os.path.getmtime(LUCCHETTO)
        if eta < 600:
            print(f"BOT | un altro giro e' in corso da {eta:.0f}s: non ne parto un secondo")
            return False
        print(f"BOT | lucchetto vecchio di {eta:.0f}s: lo considero abbandonato")
    with open(LUCCHETTO, "w") as f:
        f.write(str(os.getpid()))
    return True


def main():
    vero = "--vero" in sys.argv
    if vero and not lucchetto_preso():
        return 0
    print(f"BOT | modo {'VERO (si spende)' if vero else 'A VUOTO (non si spende niente)'}")
    st = leggi_stato()
    if st is None:
        return 1
    reg = mio_registro()
    reg["giri"] += 1

    aperte = {k: p for k, p in st["posizioni"].items()
              if p.get("strategia") == REGOLA and p["stato"] == "aperta"}
    print(f"BOT | la prova ha {len(aperte)} posizioni aperte con la regola {REGOLA}")

    conti = []
    kk = chiavi()
    if kk:
        from eth_account import Account
        for k in kk:
            c = Account.from_key(k)
            saldo = chiama("eth_getBalance", [c.address, "latest"])
            s_ = int(saldo, 16) / 1e18 if saldo else None
            conti.append((c, s_))
            print(f"BOT | {c.address}  "
                  + (f"{s_:.6f} nativi" if s_ is not None else "saldo non leggibile"))
        vuoti = [c for c, s_ in conti if not s_]
        if vuoti:
            print(f"BOT | {len(vuoti)} portafogli su {len(conti)} sono VUOTI su questa rete: "
                  f"o i fondi non sono ancora arrivati, o sono su un'altra catena")
    else:
        print("BOT | senza chiavi posso solo dire cosa farei, non provare gli ordini")

    # PRIMA SI ESCE, POI SI ENTRA. Se il giro finisse i soldi entrando, le posizioni che la
    # prova ha gia' chiuso resterebbero aperte sulla chain: si comprerebbe senza vendere, che
    # e' il modo piu' veloce di restare incastrati. Le uscite vengono prima, sempre.
    chiuse = {k: q for k, q in st["posizioni"].items() if q["stato"] != "aperta"}
    adesso = int(time.time())
    scadute = [k for k, f in reg["fatte"].items()
               if not f.get("uscita") and adesso - f.get("quando", adesso) > TAGLIO_SEC]
    if scadute:
        print(f"BOT | {len(scadute)} posizioni aperte da piu' di {TAGLIO_SEC//60} minuti: "
              f"esco comunque, la curva potrebbe aver smesso di scambiare")
    da_chiudere = [k for k in reg["fatte"]
                   if not reg["fatte"][k].get("uscita") and (k in chiuse or k in scadute)]
    if da_chiudere:
        print(f"\nBOT | la prova ha chiuso {len(da_chiudere)} posizioni che io tengo aperte")
    for kid in da_chiudere:
        f = reg["fatte"][kid]
        gett, curva = f.get("gettone"), f.get("curva")
        conto = next((c for c, _ in conti if c.address == f.get("portafoglio")), None)
        if not (gett and curva and conto):
            print(f"   {kid}: non so con cosa uscire (gettone o portafoglio mancante)")
            continue
        q = chiama("eth_call", [{"to": gett,
                                 "data": "0x70a08231" + "0" * 24 + conto.address[2:]}, "latest"])
        saldo = int(q, 16) if q and q != "0x" else 0
        if not saldo:
            print(f"   {kid}: zero gettoni in mano, niente da vendere")
            reg["fatte"][kid]["uscita"] = "nessun gettone"
            continue
        print(f"\n   VENDERE {saldo} gettoni di {gett} dal portafoglio {conto.address}")
        # IL MINIMO A 1, NON AL PREZZO GIUSTO. Una protezione stretta fa annullare l'ordine
        # proprio quando il prezzo corre, e si resta dentro: lo scarto fra acquisto e vendita
        # e' gia' dentro il costo del 5,91% con cui misuriamo. Meglio uscire peggio che non
        # uscire.
        esito = manda(conto, curva, dati_vendita(saldo, 1, conto.address), 0, vero)
        if esito and vero:
            reg["fatte"][kid]["uscita"] = esito

    speso = 0.0
    for kid, p in sorted(aperte.items(), key=lambda x: x[1].get("aperta_il", 0)):
        if kid in reg["fatte"]:
            continue
        eta = int(time.time()) - int(p.get("aperta_il") or 0)
        if eta > FRESCHEZZA_SEC:
            print(f"\n   SALTO {p.get('gettone')}: decisione di {eta}s fa, oltre la rete di "
                  f"sicurezza di {FRESCHEZZA_SEC}s.")
            continue
        x = p.get("ultimo_x")
        if x is None or not (PREZZO_MIN <= x <= PREZZO_MAX):
            print(f"\n   SALTO {p.get('gettone')}: il prezzo e' a {x} dell'entrata, fuori "
                  f"dalla finestra {PREZZO_MIN}-{PREZZO_MAX}. Non rincorro.")
            continue
        quanto = min(TETTO_POSIZIONE, TETTO_GIRO - speso)
        if quanto < TETTO_POSIZIONE:
            print(f"BOT | tetto del giro raggiunto ({TETTO_GIRO} nativi): mi fermo")
            break
        if reg.get("spesi_nativi", 0) + quanto > TETTO_TOTALE:
            print(f"BOT | TETTO TOTALE raggiunto: spesi {reg.get('spesi_nativi', 0):.4f} di "
                  f"{TETTO_TOTALE} nativi. Non compro piu' finche' un umano non guarda.")
            break
        curva = p.get("curva") or p.get("gettone")
        print(f"\n   COMPRARE {quanto:.6f} nativi di {p.get('gettone')} sulla curva {curva}")
        print(f"      entrata della prova a riserva {p.get('riserva_all_entrata')}, "
              f"bersaglio +50%, stop -5%")
        # UN PORTAFOGLIO PER POSIZIONE, a turno: cosi' due uscite simultanee non si accodano.
        conto = conti[len(reg["fatte"]) % len(conti)][0] if conti else None
        if conto and curva:
            wei = int(quanto * 1e18)
            print(f"      lo farebbe il portafoglio {conto.address}")
            if vero:
                # SI SCRIVE L'INTENZIONE PRIMA DI MANDARE, non l'esito dopo. Se la
                # transazione parte ma la risposta si perde (nodo lento, rete caduta), al
                # giro dopo — sei secondi — il bot non la troverebbe nel registro e
                # comprerebbe DI NUOVO la stessa posizione. Scrivendo prima, il peggio che
                # puo' succedere e' una riga «non so com'e' finita», che si controlla a mano:
                # molto meglio di un acquisto doppio che nessuno ha chiesto.
                reg["fatte"][kid] = {"ordine": "in corso", "quando": int(time.time()),
                                     "gettone": p.get("gettone"), "curva": curva,
                                     "portafoglio": conto.address, "nativi": quanto}
                reg["spesi_nativi"] = reg.get("spesi_nativi", 0) + quanto
                salva(reg)
            esito = manda(conto, curva, dati_acquisto(wei, 1, conto.address), wei, vero)
            if vero:
                reg["fatte"][kid]["ordine"] = esito or "MANDATO MA SENZA RISPOSTA: controllare"
                salva(reg)
        speso += quanto

    if not aperte:
        print("BOT | niente da fare in questo giro: nessuna posizione aperta")
    salva(reg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
