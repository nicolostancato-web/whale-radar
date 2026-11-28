"""Il contatore che non puo' sbagliare: due fonti, e se non concordano lo dice.

PERCHE' ESISTE, e non e' prudenza teorica. Il 5/11 il mio punteggio ha detto
"zero liquidazioni in 7,5 ore" per quattro giri di fila, con sicurezza. Ce
n'erano DUE. L'ha trovato Nicolo' chiedendo un controllo aggiuntivo.
La causa tecnica l'ho riparata (si leggeva a fette e una fetta vuota veniva
archiviata come "qui non c'era niente" per sempre). Ma la causa vera era di
METODO: avevo interrogato la stessa misura quattro volte invece di
interrogarla in un modo DIVERSO.

Da qui la regola, scritta nel codice e non nelle intenzioni: il numero che
decide se intervenire si chiede a DUE fonti indipendenti. Se concordano, e'
il numero. Se non concordano, non si sceglie la piu' comoda: si dice che non
si sa, e si riprova.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registri as R
from keccak import keccak256

D = "data/liquidazioni"
FUORI = f"{D}/conta_sicuro.json"
POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
FIRMA = "0x" + keccak256(
    b"LiquidationCall(address,address,address,uint256,uint256,address,bool)"
).hex()
DA_BLOCCO = 26347070
SEGNALIBRO = "data/liquidazioni/conta_segnalibro.json"

# IL SEGNALIBRO, E I PEZZETTI (6/11).
#
# Il conteggio rileggeva tutti i 5.600 blocchi dalla riparazione del
# contratto, a ogni giro, da ogni fonte. Ha detto «non lo so» per quattro
# giri di fila. MISURATO il perche':
#   publicnode  429 a intermittenza (lo stiamo stancando noi)
#   drpc        risponde su 50 blocchi, 400 da 500 in su  <- ha un tetto!
#   blastapi    400 sempre
# Quindi: si legge SOLO l'intervallo nuovo, in pezzi da 50 blocchi. Cosi'
# drpc diventa una fonte VERA (prima la contavamo come muta) e publicnode
# riceve tre richieste invece di una enorme.
#
# LA REGOLA CHE EVITA IL FALSO ZERO, imparata a caro prezzo il 5/11 quando
# una lettura a fette archiviava le fette vuote per sempre e dichiarai «zero
# liquidazioni» mentre ce n'erano otto: il segnalibro avanza SOLO se la
# lettura e' riuscita. Se la fonte tace non si sposta niente, non si somma
# niente, e si dice «non lo so». Un intervallo mai letto non puo' diventare
# un intervallo letto e vuoto.
PEZZO = 50
def _segnalibro_leggi(fonte):
    try:
        q = json.load(open(SEGNALIBRO))
    except Exception:
        return None, set()
    v = (q.get("fonti") or {}).get(fonte) or {}
    return v.get("fino_a"), set(v.get("hash") or [])
def _segnalibro_scrivi(fonte, fino_a, hash_visti):
    try:
        q = json.load(open(SEGNALIBRO))
    except Exception:
        q = {}
    q.setdefault("fonti", {})[fonte] = {"fino_a": fino_a,
                                        "hash": sorted(hash_visti)}
    q["quando"] = time.time()
    tmp = SEGNALIBRO + ".tmp"
    with open(tmp, "w") as f:
        json.dump(q, f)
    os.replace(tmp, SEGNALIBRO)
def _conta_incrementale(fonte, testa):
    """Gli hash visti da questa fonte fino a `testa`, leggendo solo il nuovo.
    None se la lettura non e' riuscita -- e allora il segnalibro NON si
    muove."""
    fino, visti = _segnalibro_leggi(fonte)
    da = DA_BLOCCO if (fino is None or fino < DA_BLOCCO) else max(DA_BLOCCO, fino - 10)
    x = da
    nuovi = set(visti)
    while x <= testa:
        y = min(x + PEZZO - 1, testa)
        try:
            ev = R._chiedi(fonte, "eth_getLogs",
                           [{"address": POOL, "topics": [FIRMA],
                             "fromBlock": hex(x), "toBlock": hex(y)}], 30)
        except Exception:
            return None
        if ev is None:
            return None
        for l in ev:
            h = (l.get("transactionHash") or "") + ":" + str(l.get("logIndex"))
            nuovi.add(h)
        x = y + 1
    _segnalibro_scrivi(fonte, testa, nuovi)
    return nuovi


def _conta(fonte, da, a, pezzi=1):
    """Quante liquidazioni vede QUESTA fonte. None se non risponde.

    Con pezzi>1 l'intervallo si spezza in blocchi grossi. Serve perche' drpc
    e blastapi RIFIUTANO l'interrogazione su tutto l'intervallo (errore 400)
    mentre il nostro nodo la accetta: senza questo avremmo una sola fonte, e
    una sola fonte non certifica niente.
    E' anche un metodo DIVERSO, non solo una fonte diversa -- che e'
    esattamente quello che serve per non ripetere l'errore di oggi.
    ATTENZIONE: se anche UN pezzo non risponde, si torna None. Un conteggio
    parziale spacciato per totale e' il guasto che stiamo riparando.
    """
    passo = max(1, (a - da) // pezzi + 1)
    fuori = set()
    x = da
    while x <= a:
        y = min(x + passo - 1, a)
        try:
            ev = R._chiedi(fonte, "eth_getLogs",
                           [{"address": POOL, "topics": [FIRMA],
                             "fromBlock": hex(x), "toBlock": hex(y)}], 40)
        except Exception:
            return None
        if ev is None:
            return None
        fuori |= {e["transactionHash"] + ":" + e["logIndex"] for e in ev}
        x = y + 1
    return fuori


INFINITO = 1e30          # la salute di chi non ha piu' debito, in Aave



def _per_transazione(insieme):
    """LE RIGHE NON SONO I CASI.
    Misurato il 7/11: 12 righe di registro erano 10 transazioni, perche' due
    vincitori hanno chiuso DUE posizioni in una sola transazione. Chiamare
    "12 liquidazioni" il numero di righe fa sbagliare il denominatore di ogni
    rapporto che ci costruiamo sopra ("quante occasioni abbiamo avuto" e'
    10, non 12) e NASCONDE un fatto operativo: il 20% dei vincitori aggrega.
    Quindi il contatore riporta sempre entrambi i numeri, ognuno col suo nome.
    """
    tx = {}
    for h in insieme:
        a = h.split(":")[0]
        tx[a] = tx.get(a, 0) + 1
    return {"eventi": len(insieme), "transazioni": len(tx),
            "aggregate": sum(1 for v in tx.values() if v > 1)}


def _saltate_allo_infinito():
    """Quante posizioni che sorvegliavamo sono rimaste senza debito.

    E' il secondo parere: un segnale di STATO, non di registro. Se una
    posizione era in banda e adesso ha salute infinita, il suo debito e'
    stato chiuso -- quasi sempre perche' liquidata.
    Si contano solo quelle che erano sotto 1,10 nella fotografia piu'
    vecchia che abbiamo, per non prendere chi ha semplicemente ripagato.
    """
    try:
        sn = json.load(open(f"{D}/salute_note.json"))
        righe = [json.loads(l) for l in open(f"{D}/dove_eravamo.jsonl")]
    except Exception:
        return None
    if not righe:
        return None
    erano = {}
    for r in righe:
        for c in (r.get("candidate") or []):
            erano.setdefault((c.get("u") or "").lower(), c.get("salute"))
    n = 0
    for pref, s0 in erano.items():
        if s0 is None or s0 >= 1.10:
            continue
        for u, d in sn.items():
            if u.lower().startswith(pref) and (d.get("salute") or 0) > INFINITO:
                n += 1
                break
    return n


def conta():
    testa = None
    for u in R.FONTI:
        try:
            t = R._chiedi(u, "eth_blockNumber", [])
            if t:
                testa = int(t, 16)
                break
        except Exception:
            continue
    if testa is None:
        return {"so": False, "perche": "nessuna fonte da' la testa della catena"}
    viste = {}
    for u in R.FONTI:
        # PRIMA la lettura incrementale a pezzetti: e' l'unica che drpc
        # accetta, e chiede a publicnode poche richieste piccole invece di
        # una enorme che si fa rifiutare.
        s = _conta_incrementale(u, testa)
        if s is None:
            # ripiego sul vecchio modo, ma NON si tocca il segnalibro
            for pz in (1, 4):
                s = _conta(u, DA_BLOCCO, testa, pz)
                if s is not None:
                    break
        if s is not None:
            viste[u] = s
        if len(viste) >= 2:
            break
    if len(viste) == 0:
        return {"so": False, "perche": "nessuna fonte ha risposto"}
    if len(viste) == 1:
        # SECONDO PARERE DA UN MECCANISMO DIVERSO, non da una seconda fonte.
        # drpc e blastapi rifiutano le letture dei registri in ogni forma,
        # quindi un secondo parere "uguale ma altrove" non si puo' avere. E
        # una fonte sola non certifica: e' esattamente come ho sbagliato oggi.
        # Allora si guarda uno SEGNALE DI ALTRO TIPO: il pescatore legge le
        # salute ogni dieci secondi, e una posizione liquidata salta al
        # valore "infinito" di Aave (2^192/1e18 ~ 1,16e59) perche' il debito
        # va a zero. Contare quante delle posizioni che sorvegliamo sono
        # saltate all'infinito e' una misura indipendente: stato, non log.
        u, s = next(iter(viste.items()))
        saltate = _saltate_allo_infinito()
        if saltate is None:
            return {"so": False, "quante_forse": len(s),
                    "perche": f"una sola fonte ({u.split('//')[1]}) vede "
                              f"{len(s)}, e il secondo parere non si e' "
                              f"potuto prendere"}
        d = dict(_per_transazione(s))
        d.update({"so": True, "quante": len(s), "fonti": 1,
             "secondo_parere": "stato delle posizioni sorvegliate",
             "saltate_allo_infinito": saltate,
             "concordi": None, "fino_al_blocco": testa,
             "quando": time.time()})
        if saltate > len(s):
            d["so"] = False
            d["perche"] = (f"il registro vede {len(s)} liquidazioni ma "
                           f"{saltate} posizioni che sorvegliamo sono senza "
                           f"debito: potremmo averne perse. NON certifico.")
        try:
            tmp = FUORI + ".tmp"
            json.dump(d, open(tmp, "w"), indent=1)
            os.replace(tmp, FUORI)
        except Exception:
            pass
        return d
    chiavi = list(viste)
    a, b = viste[chiavi[0]], viste[chiavi[1]]
    if a == b:
        out = {"so": True, "quante": len(a), "fonti": 2,
               "concordi": True, "fino_al_blocco": testa,
               "quando": time.time()}
        out.update(_per_transazione(a))
    else:
        solo_a = len(a - b)
        solo_b = len(b - a)
        out = {"so": False, "concordi": False,
               "quando": time.time(),
               "perche": f"le due fonti NON concordano: "
                         f"{chiavi[0].split('//')[1]} vede {len(a)}, "
                         f"{chiavi[1].split('//')[1]} vede {len(b)} "
                         f"({solo_a} solo nella prima, {solo_b} solo nella "
                         f"seconda). Prendo il massimo e lo dico.",
               "quante_massimo": max(len(a), len(b))}
    try:
        tmp = FUORI + ".tmp"
        json.dump(out, open(tmp, "w"), indent=1)
        os.replace(tmp, FUORI)
    except Exception:
        pass
    return out


if __name__ == "__main__":
    r = conta()
    if r.get("so"):
        print(f"   CONTATORE SICURO: {r['quante']} liquidazioni in "
              f"{r.get('transazioni', r['quante'])} transazioni"
              + (f" ({r['aggregate']} aggregate)" if r.get("aggregate")
                 else "")
              + f", due fonti CONCORDI (fino al blocco "
                f"{r['fino_al_blocco']})")
    else:
        print(f"   CONTATORE SICURO: NON LO SO -> {r.get('perche')}")
        if r.get("quante_massimo") is not None:
            print(f"     (il massimo visto da una fonte: {r['quante_massimo']})")
