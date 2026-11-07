"""Imparare dai giorni scorsi, senza il campione storto e senza fare casino.

LA REGOLA, decisa con Nicolo' il 5/11: il LIVE e' il giudice, perche' nel
live eravamo gia' posizionati. Lo storico serve per UNA domanda che il live
non puo' ancora rispondere, con un budget dichiarato e una FINE. Non si
apre un cantiere sullo storico.

LA DOMANDA: delle liquidazioni avvenute nei giorni scorsi, quante erano
dentro la nostra fascia di sorveglianza poco prima di cadere? Cioe': la
fascia basta?

PERCHE' NON BASTAVA IL CONTO DI PRIMA. L'avevo misurato sui nostri appunti
(da_che_salute.json, 40 casi) e veniva 40 su 40 -- ma quegli appunti
esistono PERCHE' stavamo osservando quelle posizioni: il campione era
selezionato sulla cosa che volevo misurare. Dire 100% la' significa solo
che fra quelle che tenevamo d'occhio le tenevamo d'occhio.
Qui la popolazione viene dalla CATENA, non dai nostri appunti, e la salute
si legge al blocco PRECEDENTE sui nodi d'archivio (drpc e blastapi: il
nostro nodo non serve lo stato storico).

COME NON FA CASINO: lavora a pezzi. Ogni chiamata fa un pezzo e si ferma,
cosi' nessun giro di sorveglianza si allunga. Quando ha finito, lo dice e
non rifa' niente.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pescatore as P
import registri as R
from keccak import keccak256

D = "data/liquidazioni"
STATO = f"{D}/impara_dai_giorni_scorsi.json"
POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
FIRMA = "0x" + keccak256(
    b"LiquidationCall(address,address,address,uint256,uint256,address,bool)"
).hex()
GIORNI = 3
A_PEZZO = 25            # quante posizioni per chiamata: il giro resta corto
SEL_SALUTE = "bf92857c"  # getUserAccountData
UN_ORA = 300             # blocchi: ~un'ora prima della caduta


def _carica():
    try:
        return json.load(open(STATO))
    except Exception:
        return {"fase": "raccolta", "eventi": {}, "saluti": {},
                "fette_lette": [], "quando": 0}


def _salva(s):
    s["quando"] = time.time()
    t = STATO + ".tmp"
    json.dump(s, open(t, "w"), indent=1)
    os.replace(t, STATO)


def _il_live_ha_la_precedenza():
    """Se c'e' una liquidazione LIVE da spiegare, lo studio si ferma.

    Regola di Nicolo' (5/11): il live e' il giudice, perche' nel live
    eravamo gia' posizionati. Lo storico riempie i giri vuoti, non li
    occupa. La precedenza sta QUI e non nel ciclo, perche' una regola
    scritta nella shell la si dimentica al primo riordino.
    """
    try:
        q = json.load(open(f"{D}/perche_lui_e_non_io.json"))
    except Exception:
        return False
    casi = q.get("casi") or []
    return any(c.get("autorizza_modifica") for c in casi)


def un_pezzo():
    if _il_live_ha_la_precedenza():
        print("   imparare dai giorni scorsi: SOSPESO, c'e' un caso LIVE da "
              "spiegare e quello ha la precedenza")
        return _carica()
    s = _carica()
    testa = P.rpc("eth_blockNumber", [])
    if not testa:
        print("   imparare dai giorni scorsi: la rete non ha risposto")
        return s
    testa = int(testa, 16)
    da = testa - GIORNI * 7200

    # FASE 1 — si raccolgono le liquidazioni dalla CATENA, un pezzo per volta
    if s["fase"] == "raccolta":
        lette = set(s["fette_lette"])
        fatte = 0
        for a in range(da, testa, 400):
            if str(a) in lette:
                continue
            ev, ok, persi = R.eventi(POOL, FIRMA, a, min(a + 399, testa), 400)
            if persi:
                continue                  # si riprova al pezzo dopo
            lette.add(str(a))
            for e in ev:
                s["eventi"][e["transactionHash"] + ":" + e["logIndex"]] = {
                    "blocco": int(e["blockNumber"], 16),
                    "utente": "0x" + e["topics"][3][-40:],
                    "garanzia": "0x" + e["topics"][1][-40:],
                    "debito": "0x" + e["topics"][2][-40:],
                    "dati": e["data"]}
            fatte += 1
            if fatte >= 6:                # sei fette per volta: giro corto
                break
        s["fette_lett" + "e"] = sorted(lette)
        attese = len(range(da, testa, 400))
        if len(lette) >= attese:
            s["fase"] = "salute"
        _salva(s)
        print(f"   imparare dai giorni scorsi: raccolta {len(lette)}/{attese} "
              f"fette, {len(s['eventi'])} liquidazioni trovate")
        return s

    # FASE 2 — per ognuna, la salute un'ora PRIMA, dai nodi d'archivio
    if s["fase"] == "salute":
        da_fare = [k for k in s["eventi"] if k not in s["saluti"]]
        for k in da_fare[:A_PEZZO]:
            e = s["eventi"][k]
            n = e["blocco"] - UN_ORA
            u = e["utente"]
            v = None
            for fonte in R.FONTI[1:]:     # il nostro nodo non serve lo storico
                try:
                    v = R._chiedi(fonte, "eth_call",
                                  [{"to": POOL,
                                    "data": "0x" + SEL_SALUTE + u[2:].zfill(64)},
                                   hex(n)])
                    if v:
                        break
                except Exception:
                    v = None
            if isinstance(v, str) and len(v) >= 2 + 64 * 6:
                x = v[2:]
                s["saluti"][k] = {"salute": int(x[320:384], 16) / 1e18,
                                  "debito": int(x[64:128], 16) / 1e8}
            else:
                s["saluti"][k] = {"salute": None, "debito": None}
        _salva(s)
        manca = len([k for k in s["eventi"] if k not in s["saluti"]])
        print(f"   imparare dai giorni scorsi: salute letta per "
              f"{len(s['saluti'])}/{len(s['eventi'])}, mancano {manca}")
        if manca == 0:
            s["fase"] = "fatto"
            _salva(s)
            verdetto(s)
        return s

    verdetto(s)
    return s


def premio_al_blocco(e):
    """Il premio valutato col prezzo DI QUEL BLOCCO, non di oggi.

    La stessa liquidazione, valutata in tre momenti diversi, mi ha dato
    509.058 $, 787.320 e 947.639. Solo il terzo e' vero.
    """
    import tabellone as TB
    PR = json.load(open(f"{D}/prezzi_oracolo.json"))
    g = e["garanzia"].lower(); d = e["debito"].lower()
    pg, pd = PR.get(g), PR.get(d)
    if not (pg and pd):
        return None
    x = e["dati"][2:]
    coperto = int(x[0:64], 16); preso = int(x[64:128], 16)
    p1 = TB.prezzo_al_blocco(g, e["blocco"]) or pg["prezzo_usd"]
    p2 = TB.prezzo_al_blocco(d, e["blocco"]) or pd["prezzo_usd"]
    return (preso / 10**pg["decimali"] * p1
            - coperto / 10**pd["decimali"] * p2)


def verdetto(s=None):
    s = s or _carica()
    import banda
    dentro = fuori = ignote = 0
    for k, v in (s.get("saluti") or {}).items():
        h = v.get("salute")
        if h is None:
            ignote += 1
        elif h < banda.BANDA:
            dentro += 1
        else:
            fuori += 1
    tot = dentro + fuori
    print(f"   VERDETTO sui giorni scorsi: {len(s.get('eventi') or {})} "
          f"liquidazioni dalla CATENA (non dai nostri appunti)")
    if tot:
        print(f"     dentro la fascia ({banda.BANDA}) un'ora prima: {dentro} "
              f"su {tot} = {100*dentro/tot:.0f}%")
        print(f"     fuori dalla fascia: {fuori}" +
              ("  <<< la fascia non basta" if fuori > tot*0.2 else ""))
    if ignote:
        print(f"     salute non leggibile: {ignote} (si dice, non si tace)")
    # il premio, valutato al blocco dell'evento
    tot = 0.0
    for k, e in (s.get("eventi") or {}).items():
        try:
            v = premio_al_blocco(e)
        except Exception:
            v = None
        if v:
            tot += v
    print(f"     premio passato nel mondo, al prezzo di quei blocchi: "
          f"${tot:,.0f}")
    return {"dentro": dentro, "fuori": fuori, "ignote": ignote}


if __name__ == "__main__":
    un_pezzo()
