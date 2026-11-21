# -*- coding: utf-8 -*-
"""Le VENDITE PRONTE: il preventivo preparato PRIMA che la posizione cada.

Perche' esiste (1/11). Il pescatore, quando vedeva una caduta, andava a
chiedere in rete il preventivo di vendita della garanzia: misurato **1,1
secondi**. Ma le liquidazioni grosse vengono prese NELLO STESSO BLOCCO
dell'aggiornamento di prezzo, cioe' in meno di dodici secondi e spesso in
meno di uno. Quel secondo di preventivo e' quasi certamente tutto il nostro
ritardo contro i professionisti.

Qui il preventivo si prepara mentre la posizione e' ancora SANA: al momento
della caduta non c'e' niente da chiedere a nessuno, si firma e si spara.

Prova che la reputazione non c'entra niente (misurata l'1/11): il premio piu'
grosso degli 88 giorni, EUR 214.993, l'ha preso un contratto che un anno fa
non esisteva; quello da EUR 184.525 un contratto nato DENTRO gli 88 giorni.
Il protocollo non guarda chi chiama. La barriera e' la velocita', e la
velocita' si costruisce -- e' questo file.

Si preparano prima le piu' vicine alla caduta: una vendita pronta per una
posizione a salute 1,30 non serve a nessuno.
"""
from indirizzi import (FIRMA_ESEGUI, SELETTORE_ESEGUI, mancia_per,
                       SELETTORE_ESEGUI_MANCIA,
                       FIRMA_ESEGUI_MANCIA, mancia_qualunque_moneta,
                       sa_pagare_in_qualsiasi_moneta)
from premi import resa_minima as _resa_minima_di

WETH_BASSO = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
USDC_BASSO = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
import json, os, sys, time, urllib.request
sys.path.insert(0,"agents")
# IL PREMIO VERO (agents/premi.py) serve a DUE cicli diversi: l'import va
# qui in cima, prima di qualunque uso. Il 4/11 l'ho messo prima dentro un
# ciclo e poi dopo il primo uso: due NameError di fila, e ogni volta la
# preparazione degli ordini si fermava DEL TUTTO.
# Terza volta che ci casco in un giorno. La regola e' semplice e la scrivo
# qui: un import sta in cima al file, sempre. Non "vicino a dove serve".
from premi import premio as _premio_vero
# IN CIMA, come dice la lezione tre righe sopra: _VC era importato DENTRO
# una funzione e _VU non c'era affatto. La catena della mancia li usa a
# livello di modulo, e un NameError qui fermerebbe la preparazione di TUTTI
# gli ordini -- com'e' gia' successo tre volte in un giorno il 4/11.
import vendita_curve as _VC
import vendita_uniswap as _VU
from keccak import firma as _firma
_S_DATI = _firma("getUserReserveData(address,address)")[2:10]
_PDP = "0x41393e5e337606dc3821075af65aee84d7688cbd"
def _debito_vero(utente, gettone):
    """Quell'utente ha davvero in prestito quella moneta? Una lettura."""
    try:
        import vendita_curve as _VC
        h = _VC._call(_PDP, "0x"+_S_DATI+gettone[2:].lower().zfill(64)
                      +utente[2:].lower().zfill(64))
        if not h or len(h) < 200: return True      # se non si legge, non si blocca
        x = h[2:]
        stabile = int(x[64*1:64*2], 16)
        variabile = int(x[64*2:64*3], 16)
        return (stabile + variabile) > 0
    except Exception:
        return True
from pescatore import (AMMESSI, GUADAGNO_MINIMO_USD, preventivo, tetto_per,
                       SCIVOLAMENTO_BP, FRAZIONE_PREMIO_PRETESA,
                       CONTRATTO, PROXY, cast)
D="data/liquidazioni"
FUORI=f"{D}/vendite_pronte.json"
PER_GIRO=int(sys.argv[1]) if len(sys.argv)>1 else 100
from banda import BANDA as FINO_A   # un numero, un posto: vedi agents/banda.py
                     # La salute scala col prezzo della garanzia, quindi un
                     # crollo del X% rende liquidabile chi sta sotto
                     # 1/(1-X). Misurato il 3/11 sulle 88.183 posizioni:
                     #   crollo  5% -> salute < 1,053 ->   487 posizioni
                     #   crollo  9% -> salute < 1,099 ->   672
                     #   crollo 20% -> salute < 1,250 ->  1.503
                     # A 1,12 si copriva fino a un crollo del 10,7%: per le
                     # elezioni americane serve di piu'. 1,25 copre il 20%.
def L(f,d=None):
    try: return json.load(open(f"{D}/{f}.json"))
    except Exception: return d if d is not None else []
PR=L("prezzi_oracolo",{}); T=L("tetti",{})
corta=L("lista_corta"); co=L("composizione",{})
sal={x["indirizzo"].lower():x for x in corta}
pronte=L("vendite_pronte",{}) if os.path.exists(FUORI) else {}
# LE LAPIDI NON SONO UN ARRETRATO (7/11).
# Il contatore «record senza sede» segnava 19, e 17 dicevano «il debito
# registrato non esiste piu'»: sembrava lavoro da fare. Andando a vedere,
# quelle posizioni hanno salute 1,157e59 e debito ZERO -- il valore che Aave
# restituisce quando il debito e' stato RIMBORSATO per intero. Hanno chiuso.
# Non erano un arretrato: erano lapidi, e facevano sembarare un lavoro da
# fare una cosa che non esiste. Un contatore che mescola «da riparare» con
# «non esiste piu'» non misura niente, e intanto nasconde quelli veri.
# Si cancellano solo quando la CATENA conferma che il debito e' zero: una
# nostra convenzione non basta per buttare un record.
INFINITO = 1e30
try:
    _note = json.load(open(f"{D}/salute_note.json"))
except Exception:
    _note = {}
_lapidi = []
for _a in list(pronte):
    _x = _note.get(_a) or _note.get(_a.lower()) or {}
    if not _x:
        continue
    if (_x.get("salute") or 0) > INFINITO and (_x.get("debito") or 0) <= 0:
        _lapidi.append(_a)
for _a in _lapidi:
    del pronte[_a]
if _lapidi:
    print(f"   {len(_lapidi)} lapidi rimosse dal cassetto (debito rimborsato "
          f"per intero, salute infinita)")
def salva(mie):
    """SI FONDE, NON SI SOVRASCRIVE.

    DISASTRO del 4/11 a mezzogiorno, e l'ho causato io. Giravano due
    preparazioni insieme -- la mia a mano e quella del giro -- entrambe
    avevano letto il cassetto all'inizio e alla fine entrambe l'hanno
    riscritto per intero: l'ultima ha cancellato il lavoro dell'altra, e
    il cassetto e' passato da 1.019 ordini a 250.
    Un sovrascrittura totale di un file condiviso e' una bomba a orologeria:
    funziona finche' c'e' un solo scrittore, e nessuno garantisce che ci
    sia. (Me l'ero gia' scritta altrove: scrivi solo i nuovi e fondi dopo
    aver riletto.)
    Qui si rilegge dal disco, si tiene la voce PIU' RECENTE per ogni
    posizione, e si scrive in modo atomico."""
    disco = {}
    try: disco = json.load(open(FUORI))
    except Exception: pass
    for k, v in mie.items():
        vecchia = disco.get(k) or {}
        if v.get("quando", 0) >= vecchia.get("quando", 0):
            disco[k] = v
    tmp = FUORI + ".tmp"
    with open(tmp, "w") as f: json.dump(disco, f)
    os.replace(tmp, FUORI)      # mai un cassetto mezzo scritto
    return len(disco)
cand=[]
for u,v in co.items():
    g=v["garanzia_principale"].lower(); d=v["debito_principale"].lower()
    if g not in AMMESSI: continue
    s=sal.get(u.lower())
    if not s or s["salute"]>FINO_A: continue
    # Lo STESSO tetto che usa il pescatore al momento del colpo: se qui si
    # preparasse una vendita da 2 milioni e li' se ne chiudesse 1, l'ordine
    # pronto sarebbe tarato sulla taglia sbagliata. Una costante, un nome.
    dus=s["debito"]*0.5; tet=tetto_per(g,d)
    if dus*1.07>tet: dus=tet/1.07
    if dus*_premio_vero(g) < GUADAGNO_MINIMO_USD: continue
    cand.append((s["salute"], u, g, d, dus))
# PRIMA LE COPPIE DIVERSE, poi per salute. Preparare la vendita di una
# coppia uguale a 1,0005 e' lavoro quasi sprecato: quelle cadono lo 0,7% in
# 9 giorni contro l'11,2% delle diverse. La sentinella pesca da qui, e se
# qui ci sono solo coppie uguali i suoi pacchetti si annullano sempre.
# la tabella delle famiglie sta in agents/famiglie.py: un posto solo
from famiglie import famiglia as _fam_di, coppia_uguale
_f=_fam_di
# L'ORDINE DELLA CODA, cambiato il 3/11 su direttiva di Nicolo': la prima
# bolla la vogliamo PICCOLA e PRESTO, da 50-300 euro, non dentro un dump.
# "partire con un dump, siamo impreparati, magari dobbiamo fissare delle
#  robe e non riusciamo a prenderle".
#
# E una presa FUORI dal dump non arriva da un movimento di prezzo: arriva
# da una posizione che scivola sotto 1,0 da sola, perche' gli interessi
# maturano. A quel tipo di caduta la famiglia della coppia non interessa
# niente -- una coppia uguale scivola esattamente come una diversa.
# Il vecchio ordine (coppie diverse prima, sempre) era giusto per le cadute
# da dump e sbagliato per questa: il 3/11 lasciava con l'ordine FRAGILE la
# posizione a salute 1,000087, premio $274, cioe' precisamente la prima
# bolla che cerchiamo.
# Quindi: chi e' a un soffio da 1,0 passa davanti a tutti, poi valgono le
# coppie diverse (che sono quelle che cadono nei dump), poi il resto.
UN_SOFFIO = 1.002
cand.sort(key=lambda c: (0 if c[0] < UN_SOFFIO else 1,
                         1 if _f(c[2])==_f(c[3]) else 0,
                         c[0]))
ora=time.time()
# QUANTO REGGE una vendita preparata, misurato l'1/11: la tolleranza che si
# chiede all'aggregatore E' il margine di invecchiamento. Con il 5% la
# calldata sopravvive a un movimento del 5% del prezzo; sotto quel movimento
# si annulla. Il nostro premio e' il 7%, quindi anche nel caso peggiore
# resta profitto (7 - 5 - 0,05 = 1,95%), e il contratto si annulla da solo
# se il guadagno non c'e'. Quindi conviene chiedere il 5% e tenere le
# vendite piu' a lungo, invece dell'1% e rifarle ogni quarto d'ora.
#
# E la freschezza si SCAGLIA per urgenza: tenere 823 posizioni fresche ogni
# quarto d'ora vorrebbe dire una richiesta al secondo per sempre, che e'
# torturare una fonte gratuita. Chi e' a un soffio dalla soglia si rifa'
# spesso, chi e' lontano raramente.
def _da_rifare(v):
    """Un ordine non e' pronto solo perche' e' RECENTE: deve anche essere
    GIUSTO.

    DIFETTO TROVATO il 5/11, ed e' la stessa malattia del contratto vecchio
    un livello sopra. Aggiungere un campo alla struct cambia il selettore di
    esegui: 273 ordini IN BANDA portavano la calldata col selettore vecchio e
    questa funzione li contava fra le "806 pronte", quindi non sarebbero mai
    stati ricostruiti -- e al primo colpo utile avremmo rispedito byte morti
    il giorno dopo aver riparato i byte morti.
    La freschezza dice QUANDO, non SE va bene.
    """
    ch = v.get("chiamata")
    # UN FALLIMENTO NON E' UN ORDINE (7/11). Questa riga diceva «se c'e' un
    # errore, non c'e' niente da rifare» -- e la freschezza guardava la data
    # del fallimento come se fosse la data di un successo. Risultato: un
    # tentativo andato male restava in pace per SEI ORE.
    # Trovato cercando i nomi delle «3 scoperte» al dump del 9%: tutte e tre
    # avevano un record con `errore` e `quando` e nessuna sede, da 4,4 ore.
    # E sette di quei fallimenti erano «la rotta rende troppo poco», cioe'
    # esattamente quelli che 1inch avrebbe salvato -- collegata DOPO che
    # quei record erano stati scritti.
    # Ora un fallimento scade presto (10 minuti) e si ritenta. Non diventa
    # un ciclo infinito perche' le coppie davvero impossibili le ferma la
    # lista «senza strada», che e' il posto giusto per un no definitivo.
    if v.get("errore") and not (v.get("sede") or v.get("stesso")):
        return (time.time() - (v.get("quando") or 0)) > 600
    if v.get("errore") or v.get("stesso"):
        return False
    if not ch:
        return True
    # DUE PORTE VALIDE, NON UNA (5/11). Questa riga accettava solo
    # SELETTORE_ESEGUI: appena il contratto ha imparato la seconda porta,
    # ogni ordine costruito con quella sarebbe stato dichiarato DA RIFARE e
    # ricostruito all'infinito, consumando tutte le passate e non
    # convertendo mai nessuno. Trovato prima di accenderlo, leggendo.
    if not (ch.lower().startswith("0x" + SELETTORE_ESEGUI)
            or ch.lower().startswith("0x" + SELETTORE_ESEGUI_MANCIA)):
        return True
    # UN ORDINE SUPERATO VA RIFATTO, anche se e' recente e corretto.
    #
    # «Vecchio» e «superato» sono due cose diverse: questi ordini non sono
    # invecchiati, e' il sistema che ha imparato a fare una cosa che loro
    # non portano. Delle 10 liquidazioni osservate il debito era
    # USDC/USDT/LINK in tutte e dieci: 576 ordini su 839 andavano all'asta
    # senza offerta, e aspettare la loro scadenza naturale (fino a sei ore
    # per le piu' sane) vorrebbe dire restare muti tutta la notte.
    # La regola si spegne da sola: quando tutti portano l'offerta, nessuno
    # risulta piu' superato.
    if not v.get("mancia_wei"):
        try:
            if sa_pagare_in_qualsiasi_moneta(lambda m, pr: _VC._rpc(m, pr)):
                return True
        except Exception:
            pass
    return False


def quanto_regge(salute):
    if salute < 1.02: return 1800      # mezz'ora
    if salute < 1.05: return 7200      # due ore
    return 21600                       # sei ore
VECCHIA=1800
# SI SALTANO LE COPPIE CHE SAPPIAMO DI NON SAPER VENDERE. Il 4/11 il giro
# bruciava 74 tentativi su 120 a ogni passata su coppie che la taratura
# aveva gia' dichiarato senza strada (sUSDe, osETH, rsETH: vivono su Curve,
# non su Uniswap). Ritentare un impossibile a ogni giro non lo rende
# possibile, e intanto ruba il posto a chi una strada ce l'ha.
# Non e' un abbandono: la taratura rigira ogni due ore e appena una strada
# compare la coppia torna in coda da sola.
try:
    _SENZA = set(json.load(open(f"{D}/tetti_coppia.json")).get("senza_strada") or {})
except Exception:
    _SENZA = set()
# UNA COPPIA «SENZA STRADA» LO E' SOLO FINCHE' NON SI CERCA ALTROVE (7/11).
# La lista teneva fuori rsETH (1,36 milioni di premio in gioco), sUSDe (1,14
# milioni) e altre due coppie: oltre 2,8 MILIONI dichiarati irraggiungibili.
# Era una conclusione tirata da Uniswap piu' una pool Curve, e oggi 1inch
# vende rsETH al 99,67% e sUSDe al 99,9% -- verificato contro il pari valore
# dell'oracolo. Era la nostra ricerca a essere stretta, non il mercato.
# 1inch era collegata solo al preventivo DAL VIVO (il ripiego di `pescatore`),
# non alla PREPARAZIONE degli ordini: quindi le coppie restavano scoperte
# comunque, perche' un ordine pronto non esisteva. Mezza riparazione.
# Qui si chiede a 1inch, UNA volta per coppia e non per posizione, se quella
# coppia si vende: se rende sopra la soglia la coppia torna in gioco.
_RISCATTATE = {}


def _riscattata(gar, deb, dus):
    """1inch sa vendere questa coppia? Si chiede una volta sola per coppia."""
    k = f"{gar.lower()}|{deb.lower()}"
    if k in _RISCATTATE:
        return _RISCATTATE[k]
    _RISCATTATE[k] = False
    try:
        import rotta_migliore as _RM
        pg = PR.get(gar.lower()) or PR.get(gar)
        if not pg or not pg.get("prezzo_usd"):
            return False
        q = int(min(dus, 100_000) * 1.07 / pg["prezzo_usd"]
                * 10 ** pg["decimali"])
        if q <= 0:
            return False
        sede, dati, uscita = _RM.da_1inch(gar, deb, q, CONTRATTO)
        if not sede:
            return False
        r = _RM.recupero(gar, deb, q, uscita)
        if r is not None and r >= _RM.SOGLIA_RECUPERO:
            print(f"   COPPIA RISCATTATA: {gar[:10]}->{deb[:10]} 1inch rende "
                  f"{r*100:.2f}%, torna in gioco")
            _RISCATTATE[k] = True
    except Exception as e:
        print(f"   riscatto non riuscito per {gar[:10]}: {str(e)[:50]}")
    return _RISCATTATE[k]


def _ha_strada(c):
    k = f"{c[2].lower()}|{c[3].lower()}"
    if k not in _SENZA:
        return True
    return _riscattata(c[2], c[3], c[4])
_saltate = [c for c in cand if not _ha_strada(c)]
if _saltate:
    print(f"   salto {len(_saltate)} posizioni su coppie senza strada "
          f"(premio ${sum(x[4]*0.07 for x in _saltate):,.0f}): "
          f"la taratura riprova ogni due ore")
_da_lavorare=[c for c in cand
              if _ha_strada(c)
              and ((ora - pronte.get(c[1],{}).get("quando",0)) > quanto_regge(c[0])
                   or _da_rifare(pronte.get(c[1],{})))]
# UNA CORSIA PER I PEZZI GROSSI (7/11). Ordinare per vicinanza sola
# seleziona la cosa sbagliata: con 2.186 posizioni e 100 per giro, una a
# salute 1,13 con 4,5 MILIONI di debito perde sempre contro una a 1,01 con
# venti dollari, e il suo ordine resta vecchio per ore.
# Trovato cercando chi fossero le «3 scoperte» al dump del 9%: tutte e tre
# avevano l'ordine vecchio di 4,3 ore, non mancante, e una valeva 4,5
# milioni di debito = 135.000 \$ di premio. Non erano un confine: erano in
# fondo a una coda.
# Un quarto del giro va alle piu' RICCHE fra quelle da rifare, tre quarti
# restano alla vicinanza. Cosi' nessuna delle due fame affama l'altra.
_QUOTA_RICCHE = max(1, PER_GIRO // 4)
_ricche = sorted(_da_lavorare, key=lambda c: -(c[4] or 0))[:_QUOTA_RICCHE]
_visti_r = {c[1] for c in _ricche}
_vicine = [c for c in _da_lavorare if c[1] not in _visti_r][:PER_GIRO - len(_ricche)]
da_fare = _vicine + _ricche
if _ricche:
    print(f"   corsia dei pezzi grossi: {len(_ricche)} posizioni, "
          f"la piu' ricca ${(_ricche[0][4] or 0)*0.03:,.0f} di premio")
print(f"   {len(cand)} posizioni sotto salute {FINO_A} | pronte {len(pronte)} | "
      f"ne preparo {len(da_fare)}")
fatte=0; falliti=0
for salute,u,g,d,dus in da_fare:
    pg=PR.get(g); pd=PR.get(d)
    if not pg or not pd: falliti+=1; continue
    # SI VERIFICA CHE QUEL DEBITO ESISTA DAVVERO, prima di costruire.
    #
    # DIFETTO TROVATO il 4/11 sera dalla prova sulla copia della catena:
    # era fallita con l'errore di Aave "SpecifiedCurrencyNotBorrowedByUser",
    # cioe' la moneta che credevamo in prestito NON lo era. La composizione
    # registrata diceva un debito che quell'utente non ha.
    # E il punto non e' la prova: se SPARIAMO su una posizione di cui
    # sbagliamo il debito, la liquidazione si annulla e la presa e' persa.
    #
    # Il posto giusto per il controllo e' QUI, non al momento del colpo: un
    # ordine si prepara in anticipo, quindi una lettura in piu' non costa
    # niente; al colpo costerebbe millisecondi che non abbiamo.
    # Costa una lettura per ordine preparato, e la composizione sbagliata
    # viene scoperta mentre c'e' tempo di correggerla.
    if not _debito_vero(u, d):
        # CHI SCOPRE DEVE AVVISARE (7/11). Questo controllo scopriva che la
        # composizione e' sbagliata, scriveva l'errore e l'informazione
        # MORIVA LI': la composizione resta sbagliata per sempre e ogni
        # ritentativo sbatte sullo stesso muro.
        # Peggio: `composizione_posizioni` compone solo le posizioni che non
        # ha MAI composto, quindi una composizione vecchia non si rinnova
        # nemmeno da sola. I 29 record «il debito registrato non esiste
        # piu'» sarebbero rimasti sbagliati per sempre -- e uno di quelli
        # vale 4,5 MILIONI di debito.
        # Ora si scrive in una coda che la composizione legge con priorita'.
        pronte[u]={"quando":ora,"errore":"il debito registrato non esiste piu'",
                   "salute":salute}
        try:
            _cq = f"{D}/da_ricomporre.json"
            try:
                _coda = json.load(open(_cq))
            except Exception:
                _coda = {}
            _coda[u.lower()] = {"quando": ora,
                                "perche": "debito registrato inesistente",
                                "debito_creduto": d}
            _t = _cq + ".tmp"
            json.dump(_coda, open(_t, "w"), indent=1)
            os.replace(_t, _cq)
        except Exception as _e:
            print(f"   non ho potuto mettere {u[:12]} in coda di "
                  f"ricomposizione: {str(_e)[:50]}")
        falliti+=1; continue
    # IL PREMIO VERO, calcolato UNA VOLTA SOLA e prima dei rami.
    # Difetto trovato il 4/11 sera: lo calcolavo dentro il ramo della
    # vendita, ma il ramo "stesso gettone" (che viene PRIMA) lo usava --
    # NameError, e la preparazione degli ordini si e' fermata del tutto.
    # Un nome usato prima di esistere: il quarto errore della stessa
    # famiglia oggi. La lezione resta quella: una cosa che serve a piu'
    # rami si calcola prima dei rami, non dentro uno.
    _pv = _premio_vero(g)
    if g == d:
        # stesso gettone: non c'e' niente da vendere, il piano va a zero passi
        pronte[u]={"quando":ora,"stesso":True,"salute":salute,
                   "premio":round(dus*_pv,2)}
        fatte+=1; continue
    qg=int(dus*1.07*0.995/pg["prezzo_usd"]*10**pg["decimali"])
    sede,dati,pos,app=preventivo(g,d,qg,pg["decimali"],pd["decimali"])
    passi_extra=None
    if not sede:
        # UNISWAP V4 COME ULTIMA SPIAGGIA, e non e' un ripiego debole:
        # misurato il 5/11, li' vive la maggior parte della liquidita' dei
        # nostri gettoni (cbBTC 99%, LBTC 100%, wstETH 81%, WBTC 76%,
        # USDT 65%) con rese fra il 99,67% e il 100,21%. Finora rispondevamo
        # "nessuna pozza" su una piazza che non sapevamo leggere.
        # Serve un passaggio in PIU': il router preleva tramite Permit2,
        # quindi prima si autorizza Permit2 verso il router e poi si scambia.
        try:
            import vendita_univ4 as V4
            meglio=V4.quota(g, d, qg, dst_e_weth=(d.lower()==WETH_BASSO))
            if meglio and meglio[0] > 0:
                reso = meglio[0]/10**pd["decimali"]*pd["prezzo_usd"]
                dato = qg/10**pg["decimali"]*pg["prezzo_usd"]
                resa = reso/dato if dato else 0
                if resa >= _resa_minima_di(g):
                    _fee, _dst = meglio[1], meglio[2]
                    _ts = {100:1, 500:10, 3000:60, 10000:200}[_fee]
                    r4=V4.scambio(g, _dst, _fee, _ts, qg, con_posizione=True)
                    if r4:
                        _cd4, _pos4 = r4
                        _perm=cast("calldata",
                          "approve(address,address,uint160,uint48)",
                          g, V4.UNIVERSAL_ROUTER, str((1<<160)-1), "4000000000")
                        if _perm.startswith("0x"):
                            passi_extra=[(g, V4.PERMIT2, V4.PERMIT2, _perm, 0),
                                         (g, V4.UNIVERSAL_ROUTER, V4.PERMIT2,
                                          _cd4, _pos4)]
                            sede, dati, pos, app = (V4.UNIVERSAL_ROUTER, _cd4,
                                                    _pos4, V4.PERMIT2)
                            print(f"   v4 apre {g[:8]}->{d[:8]}: resa "
                                  f"{100*resa:.2f}%")
            # E SE LA DIRETTA NON C'E', IL PONTE MISTO: garanzia -> USDC
            # su v3, poi USDC -> debito su v4. Misurato il 5/11: su GHO la
            # diretta non esiste da nessuna parte, ma USDC->GHO su v4 rende
            # il 100,08% fino a 100.000 $, e con il ponte TUTTE e sette le
            # coppie con debito GHO diventano vendibili ($44.637 di premio).
            # Il contratto accetta una catena di passaggi proprio per
            # questo: tre passaggi, due piazze.
            if not passi_extra and d.lower() != USDC_BASSO:
                s1, d1, p1, a1 = preventivo(g, USDC_BASSO, qg,
                                            pg["decimali"], 6)
                if s1:
                    _u = V4.quota(USDC_BASSO, d, int(dus*1e6),
                                  dst_e_weth=(d.lower()==WETH_BASSO))
                    if _u and _u[0] > 0:
                        _fee, _dst = _u[1], _u[2]
                        _ts = {100:1, 500:10, 3000:60, 10000:200}[_fee]
                        _r4=V4.scambio(USDC_BASSO, _dst, _fee, _ts,
                                       int(dus*1e6), con_posizione=True)
                        _pm=cast("calldata",
                                 "approve(address,address,uint160,uint48)",
                                 USDC_BASSO, V4.UNIVERSAL_ROUTER,
                                 str((1<<160)-1), "4000000000")
                        if _r4 and _pm.startswith("0x"):
                            passi_extra=[(g, s1, a1 or s1, d1, p1),
                                         (USDC_BASSO, V4.PERMIT2, V4.PERMIT2,
                                          _pm, 0),
                                         (USDC_BASSO, V4.UNIVERSAL_ROUTER,
                                          V4.PERMIT2, _r4[0], _r4[1])]
                            sede, dati, pos, app = (V4.UNIVERSAL_ROUTER,
                                                    _r4[0], _r4[1], V4.PERMIT2)
                            print(f"   ponte v3+v4 apre {g[:8]}->{d[:8]}")
        except Exception as _e4:
            print(f"   v4 non ha risposto su {g[:8]}->{d[:8]}: "
                  f"{type(_e4).__name__}: {str(_e4)[:50]}")
    if not sede:
        falliti+=1
        # NON SI BRUCIA LA FONTE. L'1/11 ho lanciato sette passate di fila e
        # Paraswap ha risposto 429 a 201 posizioni su 212: la copertura si
        # e' fermata al 68% e sembrava un limite, era impazienza mia.
        # Al primo rifiuto per troppe richieste si SMETTE e si riprova al
        # giro dopo. E non si segna il tentativo come fatto, altrimenti la
        # posizione resterebbe fuori fino alla scadenza della freschezza.
        # NON SI FERMA PIU' LA PASSATA. Fino al 4/11 un rifiuto
        # dell'aggregatore la interrompeva: era giusto quando era l'unica
        # fonte, ed e' diventato dannoso quando abbiamo imparato a
        # costruirci le vendite da soli. Adesso l'aggregatore va in
        # castigo per un quarto d'ora (dentro pescatore.py) e le vendite
        # continuano su Uniswap. Un rifiuto costava TUTTA la passata, e il
        # rinnovo degli ordini era fermo da ore.
        if "429" in str(dati) or "Too Many" in str(dati):
            print(f"   l'aggregatore ci caccia: va in castigo, continuo "
                  f"con Uniswap ({fatte} preparate finora)")
        pronte[u]={"quando":ora,"errore":str(dati)[:60],"salute":salute}
        continue
    # LA CHIAMATA COMPLETA, pronta da firmare. Misurato: comporla costa 90 ms
    # (e' un sottoprocesso), e 90 ms su 507 sono il 18% del tempo totale.
    # Si prepara con un debito PRUDENTE (il 95% della meta' che si puo'
    # chiudere): se nel frattempo il debito scende un po', la chiamata resta
    # valida. Se scende piu' del 5%, il pescatore la ricompone dal vivo.
    dus_p=dus*0.95
    qd=int(dus_p/pd["prezzo_usd"]*10**pd["decimali"])
    # LA GUARDIA VERA. Il margine chiesto all'aggregatore e' larghissimo
    # (15%) perche' un movimento di prezzo non ci deve bloccare; a difendere
    # il guadagno ci pensa QUI il contratto, in dollari, al momento vero.
    # Si pretende un quarto del premio atteso: sotto quello il riempimento
    # e' stato cattivo e il pacchetto si annulla senza costare niente.
    # Un quarto e non la meta' perche' il debito nel frattempo puo' essere
    # stato ripagato in parte, e allora il premio vero e' piu' piccolo del
    # previsto: la guardia deve fermare i disastri, non le buone occasioni.
    # IL PREMIO VERO, non il 7% inventato. Letto dal protocollo: va dal
    # 4,50% all'8,50% secondo la garanzia. Pretendere un quarto di un 7%
    # che non esiste voleva dire, sui gettoni a basso bonus, chiedere al
    # contratto piu' di quello che la presa puo' dare -- e rifiutare prese
    # buone.
    gm_usd=max(GUADAGNO_MINIMO_USD, dus*_pv*FRAZIONE_PREMIO_PRETESA)
    gm=int(gm_usd/pd["prezzo_usd"]*10**pd["decimali"])
    # CHI AUTORIZZARE lo dice il preventivo, non e' piu' scritto a mano:
    # con l'aggregatore preleva il suo proxy, con il ripiego su Uniswap
    # preleva il router stesso (e allora si passa zero).
    # LA MANCIA A CHI COSTRUISCE IL BLOCCO, per QUESTO ordine.
    # Fino al 5/11 offrivamo solo la priority fee, pagata in anticipo dal
    # portafoglio operativo: con 39 $ di saldo il massimo era 23,61 $, cioe'
    # lo 0,06% di un premio da 42.000 $. Un'offerta legata al PORTAFOGLIO
    # non batte una legata al PREMIO. Questa si prende dal RICAVATO.
    _mancia = mancia_per(d, dus*_pv, PR.get(WETH_BASSO, {}).get("prezzo_usd"))
    if passi_extra:
        passi="["+",".join(f"({a},{b},{c},{dd},{e})" for a,b,c,dd,e in passi_extra)+"]"
    else:
        passi=f"[({g},{sede},{app},{dati},{pos})]"
    # L'OFFERTA AL COSTRUTTORE ANCHE SUI DEBITI CHE NON SONO WETH (5/11).
    #
    # Il numero che obbliga: delle 10 liquidazioni avvenute da quando il
    # contratto e' giusto, il debito era USDC/USDT/LINK in TUTTE E DIECI,
    # zero in WETH. Il canale della mancia non si e' mai applicato a UNA
    # occasione vera, e la riga «offriamo il 9,6% contro il loro 2,0%»
    # descriveva un ramo che non percorrevamo mai.
    # Qui si costruisce la catena che porta il residuo in WETH -- con lo
    # stesso preventivo di tutte le altre vendite, nessuna sede scelta dal
    # contratto -- e si usa la seconda porta del contratto.
    # IL CANCELLO LO APRE LA CATENA, non questo file: se il contratto
    # distribuito non espone quella funzione si resta sulla vecchia via.
    _passi_mancia = None
    if (_mancia == 0 and dus*_pv > 0
            and sa_pagare_in_qualsiasi_moneta(lambda m, pr: _VC._rpc(m, pr))):
        _pe = PR.get(WETH_BASSO, {}).get("prezzo_usd")
        _m2 = mancia_qualunque_moneta(dus*_pv, _pe)
        _pdeb = PR.get(d) or {}
        if _m2 and _pdeb.get("prezzo_usd"):
            # quanto residuo convertire: la stima serve solo a SCEGLIERE la
            # rotta (il contratto converte poi tutto il residuo vero)
            _q = int(dus*_pv / _pdeb["prezzo_usd"] * 10**_pdeb.get("decimali", 18))
            try:
                _s2, _d2, _p2, _a2 = _VU.preventivo(d, WETH_BASSO, _q, CONTRATTO)
            except Exception as _e:
                _s2, _d2 = None, str(_e)[:60]
            if _s2:
                _mancia = _m2
                _passi_mancia = (f"[({d},{_s2},"
                                 f"{_a2 or '0x0000000000000000000000000000000000000000'},"
                                 f"{_d2},{_p2})]")
    if _passi_mancia:
        ch=cast("calldata", FIRMA_ESEGUI_MANCIA,
          d,str(qd),f"({g},{u},{passi},{gm},{_mancia})",_passi_mancia)
    else:
        ch=cast("calldata",
          FIRMA_ESEGUI,
          d,str(qd),f"({g},{u},{passi},{gm},{_mancia})")
    pronte[u]={"quando":ora,"stesso":False,"sede":sede,"dati":dati,
               # si REGISTRA la mancia messa nella calldata: cercarla dentro
               # i byte non si puo' (e il mio primo controllo cercava un
               # numero decimale in una calldata esadecimale, quindi non
               # trovava niente e dichiarava zero ordini su 195 -- un falso
               # allarme costruito da me).
               "mancia_wei":_mancia,
               # QUALE PORTA DEL CONTRATTO usa questo ordine: senza questo
               # campo, un ordine con la firma nuova e uno con la vecchia
               # sarebbero indistinguibili, e la prima differenza si
               # vedrebbe solo quando si annulla.
               "porta":("eseguiConMancia" if _passi_mancia else "esegui"),
               "passi_mancia":_passi_mancia,
               "approvare":app,
               "posizione":pos,"garanzia":g,"debito":d,
               "quantita":qg,"premio":round(dus*_pv,2),"salute":salute,
               "chiamata":ch if ch.startswith("0x") else None,
               "debito_previsto":round(dus_p,2),
               "guadagno_preteso_usd":round(gm_usd,2),"margine_bp":SCIVOLAMENTO_BP}
    fatte+=1
    if fatte%15==0: salva(pronte)
    # LA PAUSA SERVE SOLO SE HO CHIESTO ALL'AGGREGATORE. Trovata il 4/11
    # a mezzogiorno dal blocco 5 che e' TORNATO INDIETRO da solo (95% ->
    # 91%, 223 ordini in ritardo sul rinnovo): la pausa di 1,5 secondi
    # esiste per non torturare una fonte gratuita, ma quando la vendita
    # l'abbiamo costruita NOI leggendo la catena non c'e' nessuna fonte da
    # proteggere -- e quella pausa si mangiava due minuti per passata
    # senza nessun motivo.
    # Un accorgimento giusto applicato dove non serve diventa un freno.
    from pescatore import aggregatore_in_castigo
    if not aggregatore_in_castigo():
        time.sleep(1.5)
in_tutto=salva(pronte)
tutte=json.load(open(FUORI))
buone=sum(1 for v in tutte.values() if v.get("sede") or v.get("stesso"))
print(f"   preparate {fatte}, fallite {falliti} | in cassetto: {buone} vendite "
      f"pronte su {len(tutte)} in archivio")
if cand:
    pr=[c for c in cand if pronte.get(c[1],{}).get("sede") or pronte.get(c[1],{}).get("stesso")]
    print(f"   copertura delle vicine: {len(pr)}/{len(cand)} "
          f"({100*len(pr)/len(cand):.0f}%)")
