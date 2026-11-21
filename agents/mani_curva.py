"""Le mani, chiamate dal cervello nell'istante della decisione.

PERCHE' NON BASTAVA IL BOT CHE LEGGE IL FILE (14/10). Nella notte del 13 il bot ha visto zero
posizioni `50-5` su dieci occasioni: quella regola ha lo stop a -5% e il bersaglio a +50%, si
risolve in pochi secondi, e quando qualcuno rilegge il file di stato e' gia' chiusa. L'unica
regola che abbiamo dimostrato funzionare era l'unica che l'architettura non poteva eseguire.
Qui non c'e' nessun file in mezzo: il cervello chiama `apre()` nel momento esatto in cui
decide, e `chiude()` nel momento esatto del tocco.

SICUREZZA. Stesso impianto del bot: chiavi solo dal file delle credenziali, tetti scritti nel
codice, intenzione registrata prima dell'invio, un portafoglio per posizione. In piu', qui si
agisce dentro il cervello: se qualcosa esplode, la prova deve continuare a misurare. Ogni
chiamata e' quindi protetta — un guasto delle mani non ferma mai il cervello.

A VUOTO salvo MANI_VERE=1. Senza quella variabile non parte nessuna transazione.
"""
import json
import os
import time

import bot_curva as B

VERE = os.environ.get("MANI_VERE") == "1"
REGOLA = os.environ.get("MANI_REGOLA", "50-5")
# quanti blocchi di ritardo si accettano fra l'attraversamento e l'acquisto:
# 300 blocchi = circa 28 secondi di chain.
BLOCCHI_MAX = int(os.environ.get("BLOCCHI_MAX", "300"))
REGISTRO = "data/multichain/robinhood/mani_curva.json"
STATO = "data/multichain/robinhood/prova_nella_curva.json"

_conti = None
_reg = None


def _carica():
    global _conti, _reg
    if _conti is None:
        from eth_account import Account
        _conti = [Account.from_key(k) for k in B.chiavi()]
        print(f"MANI | {len(_conti)} portafogli, modo {'VERO' if VERE else 'a vuoto'}")
    if _reg is None:
        _reg = json.load(open(REGISTRO)) if os.path.exists(REGISTRO) else {
            "fatte": {}, "spesi_nativi": 0.0}
    return _conti, _reg


def _salva():
    os.makedirs(os.path.dirname(REGISTRO), exist_ok=True)
    tmp = REGISTRO + ".tmp"
    with open(tmp, "w") as f:
        json.dump(_reg, f)
    os.replace(tmp, REGISTRO)


def apre(chiave, pos):
    """Il cervello ha appena aperto una posizione. Compriamo, se e' la nostra regola."""
    try:
        if pos.get("strategia") != REGOLA:
            return
        conti, reg = _carica()
        if not conti or chiave in reg["fatte"]:
            return
        # NON SI COMPRA UN ATTRAVERSAMENTO VECCHIO (15/10, costato 7,71 EUR in tre minuti).
        # Il cervello, dopo ogni riavvio, ripercorre i blocchi arretrati e apre posizioni su
        # attraversamenti gia' avvenuti: venti in tre minuti, tutte comprate al prezzo di
        # ADESSO e chiuse subito, ognuna persa per il solo costo di andata e ritorno. Il
        # controllo sulla freschezza non le fermava perche' guarda l'orologio, e l'orologio
        # dice «adesso» anche quando il cervello sta rileggendo il passato. Il tempo vero di
        # una decisione e' il suo BLOCCO, non l'ora in cui l'abbiamo scoperta.
        testa = B.chiama("eth_blockNumber", [])
        be = pos.get("blocco_entrata")
        if testa and be and int(testa, 16) - be > BLOCCHI_MAX:
            print(f"MANI | SALTO {pos.get('gettone')}: attraversamento di "
                  f"{(int(testa, 16) - be) * 0.093:.0f}s fa, il cervello sta recuperando")
            return
        # IL PAVIMENTO: si compra finche' la cassa complessiva resta sopra la soglia.
        cassa = 0.0
        for c in conti:
            b = B.chiama("eth_getBalance", [c.address, "latest"])
            if b is None:
                print("MANI | non leggo la cassa: per prudenza non compro")
                return
            cassa += int(b, 16) / 1e18
        quanto = B.taglia(cassa)
        if cassa - quanto < B.PAVIMENTO:
            print(f"MANI | PAVIMENTO raggiunto: cassa {cassa:.6f} contro soglia "
                  f"{B.PAVIMENTO}. Non compro piu' finche' un umano non guarda.")
            return
        conto = conti[len(reg["fatte"]) % len(conti)]
        wei = int(quanto * 1e18)
        print(f"MANI | COMPRO {quanto:.6f} nativi di {pos['gettone']} "
              f"(riserva {pos.get('riserva_all_entrata')}) da {conto.address}")
        if VERE:
            reg["fatte"][chiave] = {"ordine": "in corso", "quando": int(time.time()),
                                    "gettone": pos["gettone"], "curva": pos["curva"],
                                    "portafoglio": conto.address, "nativi": quanto}
            reg["spesi_nativi"] += quanto
            _salva()
        esito = None
        try:
            esito = B.manda(conto, pos["curva"],
                            B.dati_acquisto(wei, 1, conto.address), wei, VERE)
        finally:
            if VERE:
                if esito:
                    reg["fatte"][chiave]["ordine"] = esito
                    # IL PERMESSO SUBITO, NON AL MOMENTO DI SCAPPARE (14/10). Senza, la
                    # vendita torna indietro con «permesso insufficiente» e la posizione
                    # resta in mano mentre il prezzo crolla: e' costato il 75% invece del
                    # 10% dello stop. Si manda ora, che la posizione e' appena nata e non
                    # c'e' fretta; cosi' all'uscita c'e' una transazione sola.
                    try:
                        B.manda(conto, pos["gettone"], B.dati_permesso(pos["curva"]), 0, True)
                        reg["fatte"][chiave]["permesso"] = True
                    except Exception as e:                      # noqa: BLE001
                        print(f"MANI | permesso non dato: {e}")
                else:
                    # IL CONTATORE SI RIAVVOLGE SE NON E' PARTITO NIENTE (14/10). Prima
                    # l'intenzione restava scritta e la spesa contata anche quando la firma
                    # falliva: il registro dichiarava 4 euro usciti mentre i portafogli erano
                    # intatti. Un registro che sbaglia in eccesso ferma il bot per un tetto
                    # mai raggiunto; uno che sbaglia in difetto lo fa spendere oltre. Qui si
                    # cancella la riga e si restituisce la cifra.
                    reg["fatte"].pop(chiave, None)
                    reg["spesi_nativi"] = round(reg["spesi_nativi"] - B.TETTO_POSIZIONE, 8)
                    print("MANI | l'ordine non e' partito: spesa riavvolta")
                _salva()
    except Exception as e:                                      # noqa: BLE001
        # UN GUASTO DELLE MANI NON FERMA IL CERVELLO. La misura vale piu' dell'esecuzione:
        # se smettiamo di misurare perdiamo anche la ragione per cui stiamo eseguendo.
        print(f"MANI | l'acquisto e' fallito ma la prova continua: {e}")


def recupera():
    """La rete di sicurezza: nessun gettone deve restare in mano per sbaglio.

    PERCHE' SERVE (14/10). `chiude()` viene chiamata una volta sola, nell'istante in cui il
    cervello chiude la posizione. Se la vendita fallisce in quell'istante — permesso mancante,
    numero d'ordine sfasato, nodo che tossisce — nessuno la richiama piu': la posizione
    risulta «chiusa» nel registro e i gettoni restano li' per sempre. E' successo a due
    posizioni, una delle quali aveva gia' fatto +50%. Un'uscita che si tenta una volta sola
    non e' un'uscita: e' una speranza.

    Questa gira a ogni passata e guarda i FATTI, non il registro: se un portafoglio ha
    gettoni di una posizione che doveva essere chiusa, prova a venderli. Finche' ci riesce.
    """
    try:
        conti, reg = _carica()
        # LA RETE DI SICUREZZA NON DEVE PESCARE LE POSIZIONI ANCORA APERTE (14/10). Cosi'
        # com'era, `recupera()` vendeva qualunque gettone avessimo in mano — comprese le
        # posizioni che il cervello teneva APERTE. Risultato misurato: una posizione venduta
        # 73 secondi PRIMA che la regola dicesse di uscire, a prezzo quasi invariato. La rete
        # di sicurezza faceva concorrenza alla strategia invece di proteggerla: un ritardo
        # NEGATIVO fra decisione e vendita non e' lentezza, e' una vendita non autorizzata.
        st_ = json.load(open(STATO)) if os.path.exists(STATO) else {"posizioni": {}}
        for chiave, f in list(reg["fatte"].items()):
            # SI GUARDANO I GETTONI, NON IL REGISTRO (14/10, mia regola violata da me stesso).
            # Saltavo le posizioni il cui `uscita` era un codice di transazione, dando per
            # scontato che una transazione mandata fosse una transazione riuscita. Una di esse
            # era FALLITA: il registro la dava per venduta e i gettoni erano ancora li', fuori
            # dalla portata della rete di sicurezza che esiste apposta per quello. Il fatto e'
            # il saldo del portafoglio; il registro e' solo un'opinione su quel fatto.
            if f.get("finita"):
                continue
            if (st_["posizioni"].get(chiave) or {}).get("stato") == "aperta":
                continue   # ci pensera' chiude() quando la regola lo dira'
            conto = next((c for c in conti if c.address == f["portafoglio"]), None)
            if not conto:
                continue
            q = B.chiama("eth_call", [{"to": f["gettone"],
                                       "data": "0x70a08231" + "0" * 24 + conto.address[2:]},
                                      "latest"])
            saldo = int(q, 16) if q and q != "0x" else 0
            if not saldo:
                reg["fatte"][chiave]["finita"] = True
                _salva()
                continue
            dati = B.dati_vendita(saldo, 1, conto.address)
            if B.chiama("eth_estimateGas", [{"from": conto.address, "to": f["curva"],
                                             "data": dati, "value": "0x0"}]) is None:
                print(f"MANI | recupero {f['gettone'][:12]}…: do il permesso alla sua curva")
                if not B.manda(conto, f["gettone"], B.dati_permesso(f["curva"]), 0, VERE):
                    continue
                reg["fatte"][chiave]["permesso"] = True
                _salva()
                continue      # al prossimo giro il permesso sara' confermato in un blocco
            print(f"MANI | recupero: vendo {saldo} gettoni di {f['gettone'][:12]}…")
            esito = B.manda(conto, f["curva"], dati, 0, VERE)
            if esito:
                reg["fatte"][chiave]["uscita"] = esito
                _salva()
    except Exception as e:                                      # noqa: BLE001
        print(f"MANI | il recupero e' fallito ma la prova continua: {e}")


def chiude(chiave, pos):
    """Il cervello ha appena chiuso una posizione. Usciamo, se era nostra."""
    try:
        conti, reg = _carica()
        f = reg["fatte"].get(chiave)
        if not f or f.get("uscita"):
            return
        conto = next((c for c in conti if c.address == f["portafoglio"]), None)
        if not conto:
            return
        q = B.chiama("eth_call", [{"to": f["gettone"],
                                   "data": "0x70a08231" + "0" * 24 + conto.address[2:]},
                                  "latest"])
        saldo = int(q, 16) if q and q != "0x" else 0
        if not saldo:
            reg["fatte"][chiave]["uscita"] = "nessun gettone"
            _salva()
            return
        print(f"MANI | VENDO {saldo} gettoni di {f['gettone']} "
              f"({(pos.get('esito') or {}).get('verso')})")
        # SI RIPARA DA SOLO SE IL PERMESSO MANCA (14/10). Il permesso si da' all'acquisto, ma
        # due posizioni sono nate quando quella parte era rotta e sarebbero rimaste in mano
        # per sempre. Qui, se la vendita non si lascia nemmeno stimare, si prova a dare il
        # permesso e si riprova subito: una posizione che non si puo' chiudere e' il guasto
        # peggiore che questo programma possa avere.
        if VERE and not f.get("permesso"):
            if B.chiama("eth_estimateGas", [{"from": conto.address, "to": f["curva"],
                                             "data": B.dati_vendita(saldo, 1, conto.address),
                                             "value": "0x0"}]) is None:
                print("MANI | manca il permesso: lo do adesso e riprovo")
                if B.manda(conto, f["gettone"], B.dati_permesso(f["curva"]), 0, True):
                    reg["fatte"][chiave]["permesso"] = True
                    _salva()
        esito = B.manda(conto, f["curva"], B.dati_vendita(saldo, 1, conto.address), 0, VERE)
        if VERE:
            reg["fatte"][chiave]["uscita"] = esito or "MANDATA SENZA RISPOSTA: controllare"
            _salva()
    except Exception as e:                                      # noqa: BLE001
        print(f"MANI | la vendita e' fallita ma la prova continua: {e}")
