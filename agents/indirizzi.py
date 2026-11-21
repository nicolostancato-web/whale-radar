"""L'indirizzo del contratto, in UN SOLO POSTO, col suo cancello.

PERCHE' ESISTE, e costa sei settimane di pacchetti morti (scoperto il
4/11/2026 sera). L'indirizzo del liquidatore era scritto a mano in DIECI
file. Il sorgente e' cresciuto -- la struct Passo ha preso i campi
`daApprovare` e `posizioneImporto` per le catene di vendita su Curve -- e
il contratto in catena non e' mai stato ridistribuito. Risultato: la
calldata che costruivamo chiamava il selettore 0x038188d0, che nel
bytecode distribuito NON ESISTE. Ogni pacchetto moriva al primo byte:
~12.000 pacchetti, 660 il 3/11, 183 in una sera, tutti con revert vuoto e
67.910 gas, cioe' il costo dei soli byte.

Perche' nessuna verifica lo vedeva: la prova sul fork DISTRIBUISCE un
contratto nuovo dal sorgente, quindi non ha mai toccato l'indirizzo vero.
Una prova che non attraversa il pezzo vero rassicura invece di provare.

Il cancello qui sotto e' la lezione resa eseguibile: prima di armare
qualunque cosa, si chiede alla CATENA se la funzione che stiamo per
chiamare esiste nel bytecode. Non al sorgente: alla catena.
"""
import json, os, sys, time

_QUI = os.path.dirname(os.path.abspath(__file__))
_DOVE = os.path.join(_QUI, "..", "data", "liquidazioni", "contratto.json")

# L'ingresso del contratto: la firma e il suo selettore, calcolato con
# `cast sig`, non indovinato (errore mio, due volte in un giorno).
# LA FIRMA STA QUI E SOLO QUI. Era copiata a mano in QUATTRO file, e due di
# quelli (catena.py, prenota.py) portavano ancora la versione con quattro
# campi nel Passo: erano gia' vecchi anche loro, nello stesso modo in cui era
# vecchio il contratto. Un campo in piu' nella struct CAMBIA IL SELETTORE, e
# una firma copiata e' una seconda verita' che invecchia da sola.
FIRMA_ESEGUI = ("esegui(address,uint256,(address,address,"
                "(address,address,address,bytes,uint256)[],uint256,uint256))")
# calcolato con `cast sig`, verificato presente nel bytecode compilato
SELETTORE_ESEGUI = "ce5997a4"

# LA SECONDA PORTA: come esegui, ma sa pagare il costruttore anche quando il
# guadagno NON e' in WETH, convertendo il residuo con una catena preparata
# fuori.
#
# PERCHE' ESISTE, col numero che lo rende non opinabile (5/11): delle 10
# liquidazioni avvenute da quando il contratto e' giusto, il debito era
# USDC/USDT/LINK in TUTTE E DIECI. Zero in WETH. Quindi il canale della
# mancia -- quello che abbiamo costruito come la chiave per vincere -- non si
# e' mai applicato a una sola occasione vera: su quelle 10 offrivamo solo la
# priority fee dal portafoglio, tappata a 45 dollari dal saldo.
# E la riga «la nostra offerta sta sopra chi vince (9,6% contro il 2,0%)» era
# vera solo per i debiti in WETH, cioe' per NESSUN caso reale: un indicatore
# che rassicura misurando il ramo che non si percorre.
#
# E' una funzione IN PIU', non al posto di `esegui`: cambiare la firma di
# quella avrebbe invalidato in un colpo tutti i 985 ordini pronti, che si
# rigenerano a 29 per passata -- ore di cecita'. Il vecchio selettore resta
# ce5997a4, verificato dopo la modifica.
FIRMA_ESEGUI_MANCIA = ("eseguiConMancia(address,uint256,(address,address,"
                       "(address,address,address,bytes,uint256)[],uint256,"
                       "uint256),(address,address,address,bytes,uint256)[])")
# calcolato con `cast sig`, verificato presente nel bytecode compilato
SELETTORE_ESEGUI_MANCIA = "bfa77cf8"

_SA_LA_MANCIA = {}
def sa_pagare_in_qualsiasi_moneta(rpc, indirizzo=None):
    """Il contratto IN CATENA espone eseguiConMancia? Si chiede alla catena.

    E' lo stesso cancello che ha chiuso lo zero di sei settimane: il
    contratto distribuito era vecchio e noi costruivamo calldata per una
    firma che non esisteva. Una costante in un file non sa cosa c'e' in
    catena; il bytecode si', e costa una lettura.
    Cosi' il codice si puo' scrivere PRIMA della distribuzione senza
    rompere niente: finche' la funzione non c'e', si continua con la
    vecchia via e la mancia resta sui soli debiti in WETH.
    """
    ind = (indirizzo or contratto() or "").lower()
    if not ind: return False
    if ind in _SA_LA_MANCIA: return _SA_LA_MANCIA[ind]
    try:
        c = rpc("eth_getCode", [ind, "latest"]) or ""
        if isinstance(c, dict): c = c.get("result") or ""
    except Exception:
        return False                      # non si sa: si resta prudenti
    if not isinstance(c, str) or len(c) < 10: return False
    ok = SELETTORE_ESEGUI_MANCIA in c
    _SA_LA_MANCIA[ind] = ok
    return ok
def mancia_qualunque_moneta(premio_usd, prezzo_eth):
    """La mancia su QUALSIASI debito: la moneta non c'entra piu', perche' il
    contratto nuovo sa convertire il residuo. Stessa frazione di sempre."""
    if not premio_usd or not prezzo_eth or premio_usd <= 0: return 0
    vero = premio_usd / QUANTO_IL_PREMIO_GONFIA
    return int(vero * FRAZIONE_MANCIA / prezzo_eth * 10**18)

# QUANTO SI PAGA AL COSTRUTTORE, in wei, preso DAL RICAVATO dell'operazione.
# Zero finche' il contratto nuovo non e' in catena. Poi si calcolera' come
# frazione del premio ATTESO, non come numero fisso: un'offerta legata al
# PORTAFOGLIO (massimo 23,68 $ con 39 $ di saldo) non puo' competere con una
# legata al PREMIO, e con 52 euro di capitale quello non e' un parametro da
# tarare meglio ma un canale su cui non si vince per costruzione.
# ACCESA il 5/11 mattina, dopo che il contratto nuovo e' in catena e la
# misura dice che il meccanismo esegue correttamente 66 volte su 67.
# E' la FRAZIONE del premio atteso che si offre a chi costruisce il blocco,
# presa dal ricavato dell'operazione stessa.
#
# Perche' il 10%: il vincitore studiato pagava priority fee ZERO e stava in
# posizione 2 dopo l'oracolo, quindi pagava per vie interne; non sappiamo
# quanto (il metodo del delta-saldo misura tutto il MEV del blocco, non il
# suo pagamento). Quindi il 10% non e' tarato sui dati: e' un PUNTO DI
# PARTENZA dichiarato tale, e si tara sui primi esiti veri.
# Perche' e' sicuro provarlo: il contratto paga solo a operazione riuscita e
# si annulla se la mancia supera il guadagno; un pacchetto annullato non
# entra nel blocco e non si paga. Lo sbaglio peggiore e' un'occasione
# mancata, non una perdita.
# MISURATA, non piu' indovinata (5/11 mezzogiorno).
#
# Come l'ho misurata: due nodi pubblici gratuiti (eth.drpc.org e
# eth-mainnet.public.blastapi.io) servono i SALDI STORICI, che il nostro non
# serviva -- ed e' quello che bloccava la misura da giorni. Con quelli:
#   pagamento interno = (saldo del costruttore a N meno a N-1)
#                       - somma delle priority fee di tutte le tx
#                       - prelievi dei validatori - trasferimenti espliciti
#
# Sul blocco della liquidazione da 509.058 $: il costruttore (beaverbuild)
# ha incassato 25,84 ETH, di cui solo 0,048 da priority fee di 321
# transazioni. Residuo 25,79 ETH = 62.656 $, cioe' il 12,3% del premio.
# Su 8 blocchi con liquidazioni sopra 500 $: mediana 12,3%.
#
# I LIMITI DEL METODO, dichiarati: il residuo e' di BLOCCO, non di singolo
# searcher. Dove un blocco ha due liquidazioni lo stesso residuo viene
# attribuito a entrambe (nei dati si vede: 12,3% e 75,6% sono lo stesso
# blocco), e un valore negativo (-7,5%) e' un costruttore che ha pagato al
# proponente piu' di quanto ha incassato. Quindi la mediana e' il numero
# utile, gli estremi sono rumore del metodo.
#
# PERCHE' 15 E NON 12,3: l'errore non e' simmetrico. Offrire poco significa
# perdere TUTTO il premio; offrire troppo significa tenerne un po' meno. Con
# 52 euro di capitale, vincere qualcosa conta piu' che ottimizzare la
# divisione. Su un premio da 509.058 $ si pagherebbero 76.359 $ e se ne
# terrebbero 432.699.
# ALZATA da 0,15 a 0,25 il 5/11 sera, sulla DISTANZA SOTTILE misurata.
#
# Su 4 liquidazioni in cui eravamo nel pacchetto e abbiamo perso, ho
# misurato quanto ha incassato il costruttore oltre le commissioni normali
# (metodo del residuo sui saldi storici): mediana 7,3% del premio. Noi
# offrivamo il 5,8% del premio -- cioe' 0,15 del guadagno vero stimato,
# che e' il premio diviso 2,6. Perdevamo per UN PUNTO E MEZZO.
# A 0,25 offriamo il 9,6% del premio: sopra la mediana di chi vince.
#
# Il conto che lo giustifica: su un premio da 1.000 $ passiamo da 58 a 96 $
# di offerta. Trentotto dollari in piu' per avere la possibilita' di tenere
# gli altri 900, invece di perdere tutto. L'errore non e' simmetrico.
#
# I due estremi della misura (-39,9% e +46,5%) sono rumore del metodo: il
# residuo e' di BLOCCO, non del singolo searcher, quindi dove c'e' altro MEV
# il numero e' gonfiato e dove il costruttore ha margine negativo e' sotto
# zero. La mediana e' il numero utile.
FRAZIONE_MANCIA = 0.25

# LIMITE DURO: la mancia si paga in ETH scartando il WETH del ricavato,
# quindi funziona SOLO quando il debito e' WETH. Su un altro debito il
# contratto si annulla (ManciaOltreIlGuadagno), percio' li' resta zero --
# meglio nessuna mancia che un ordine che non puo' eseguire.
WETH_PER_MANCIA = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
MANCIA_WEI = 0          # il valore fisso resta zero: si calcola per ordine


# IL PREMIO DICHIARATO NON E' IL GUADAGNO VERO (misurato il 5/11 ora di
# pranzo, e ci avrebbe fatto pagare il triplo).
#
# Il campo "premio" di un ordine e' calcolato sul DEBITO INTERO, ma Aave
# limita una singola liquidazione a meta' del debito e la nostra taglia e'
# limitata anche dal tetto di vendita misurato. Provato in catena sullo
# stesso ordine: premio dichiarato 42.348 $, guadagno lordo VERO 16.322 $
# -> il dichiarato e' 2,59 volte il vero.
# Conseguenza: una mancia del 15% del dichiarato e' il 39% del guadagno
# vero, contro un livello di mercato misurato al 12,3%. Pagheremmo tre volte
# tanto, e dove il guadagno e' piu' basso il contratto si annulla e si perde
# l'occasione INTERA.
#
# QUESTO DIVISORE E' MISURATO SU UN CASO SOLO, e lo dichiaro: una costante
# presa da un caso va cercata a ogni giro e rifiutata se non ricompare.
# Finche' non ne abbiamo altri si tiene prudente.
#
# LA RIPARAZIONE GIUSTA, per la prossima distribuzione: la mancia va
# calcolata DENTRO il contratto come frazione di cio' che resta davvero,
# non passata come numero fisso da fuori. Il contratto conosce il guadagno
# vero, noi no.
QUANTO_IL_PREMIO_GONFIA = 2.6


def mancia_per(debito, premio_usd, prezzo_eth):
    """Quanto offrire a chi costruisce, in wei, per QUESTO ordine."""
    if (debito or "").lower() != WETH_PER_MANCIA:
        return 0
    if not premio_usd or not prezzo_eth or premio_usd <= 0:
        return 0
    vero = premio_usd / QUANTO_IL_PREMIO_GONFIA
    return int(vero * FRAZIONE_MANCIA / prezzo_eth * 10**18)


def contratto():
    """L'indirizzo in uso. Sta in un file perche' cambia a ogni distribuzione
    e un indirizzo copiato a mano in dieci file e' esattamente il guasto
    che questo modulo esiste per rendere impossibile."""
    with open(_DOVE) as f:
        return json.load(f)["indirizzo"]


def scrivi(indirizzo, nota=""):
    tmp = _DOVE + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"indirizzo": indirizzo, "nota": nota,
                   "selettore_atteso": SELETTORE_ESEGUI}, f, indent=1)
    os.replace(tmp, _DOVE)


def bytecode_ha_l_ingresso(rpc, indirizzo=None):
    """La CATENA ha la funzione che stiamo per chiamare? (vero/falso, perche')"""
    a = indirizzo or contratto()
    # ASSENTE E NON-HO-POTUTO-CHIEDERE SONO DUE COSE DIVERSE. Un buco di
    # rete che torna None si leggeva come "il contratto non c'e'": e' la
    # stessa famiglia di errore che ha fatto registrare "nessuna strada"
    # su una rotta che rendeva il 99,62%. Si riprova, e se la rete non
    # risponde lo si DICE invece di accusare il contratto.
    code = None
    for _ in range(4):
        code = rpc("eth_getCode", [a, "latest"])
        if isinstance(code, str) and len(code) >= 10:
            break
        time.sleep(0.6)
    if code is None:
        return False, f"la rete non ha risposto: non so dire se {a} ha codice"
    if not isinstance(code, str) or len(code) < 10:
        return False, f"nessun codice a {a}: non c'e' nessun contratto"
    c = code.lower()
    if SELETTORE_ESEGUI not in c:
        return False, (f"il bytecode a {a} ({len(c)//2} byte) NON contiene "
                       f"{SELETTORE_ESEGUI}: e' una versione diversa dal "
                       f"sorgente, e ogni calldata muore al primo byte")
    return True, f"{len(c)//2} byte, selettore {SELETTORE_ESEGUI} presente"


def pretendi(rpc, indirizzo=None):
    """Come sopra, ma GRIDA e si ferma. Un ripiego silenzioso su una cosa
    indispensabile e' una bugia: senza l'ingresso non si consegna niente."""
    ok, perche = bytecode_ha_l_ingresso(rpc, indirizzo)
    if not ok:
        sys.exit(f"FERMO: {perche}")
    return True
