"""Il punteggio che conta: da quando la macchina puo' davvero vincere.

PERCHE' ESISTE (5/11). Tutti i nostri numeri di esito -- 12.000 pacchetti,
zero prese -- vengono da sei settimane in cui il contratto in catena era una
versione vecchia e NESSUN pacchetto poteva eseguire. Tenerli nello stesso
conto con quelli di adesso rende inutili entrambi: un contatore che somma due
regimi mente su tutti e due.
Misurato quel giorno: nelle 24 ore precedenti il mondo ha prodotto 4
liquidazioni, di cui UNA da 509.058 $ di premio. Quella posizione la
conoscevamo, la sorvegliavamo e avevamo l'ordine pronto -- ed e' avvenuta
16,4 ore PRIMA della riparazione, quindi non era vincibile in nessun caso.
Quindi: l'occasione grossa esiste e passa circa una volta al giorno. Il
punteggio onesto parte dal blocco in cui il contratto giusto e' andato in
catena.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pescatore as P
import registri as R
from keccak import keccak256

D = "data/liquidazioni"
FUORI = f"{D}/da_quando_siamo_veri.json"
POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
DA_BLOCCO = 26347070          # dove il contratto giusto e' entrato in catena
NOSTRO = "0x2acffbca10c0214c1ee7c1bd679c7b19e7ee3ed5"
FIRMA = "0x" + keccak256(
    b"LiquidationCall(address,address,address,uint256,uint256,address,bool)"
).hex()


def misura():
    testa = P.rpc("eth_blockNumber", [])
    if not testa:
        return None
    testa = int(testa, 16)
    PR = json.load(open(f"{D}/prezzi_oracolo.json"))
    sn = json.load(open(f"{D}/salute_note.json"))
    corta = {r["indirizzo"].lower()
             for r in json.load(open(f"{D}/lista_corta.json"))}
    VP = {k.lower(): v for k, v in
          json.load(open(f"{D}/vendite_pronte.json")).items()}
    # UNA SOLA INTERROGAZIONE, SENZA FETTE E SENZA ARCHIVIO.
    #
    # DIFETTO TROVATO DA NICOLO' il 5/11, e il piu' grave di tutta la
    # giornata: il mio punteggio diceva "zero liquidazioni in 7,5 ore" e una
    # sola interrogazione su tutto l'intervallo ne trovava DUE. Esattamente
    # il guasto che mi ero scritto: un punteggio che perde eventi direbbe
    # "nessuna occasione" proprio quando ne passa una.
    #
    # LA CAUSA: leggevo a fette di 400 blocchi e archiviavo ogni fetta come
    # "letta". Se una fonte risponde con un elenco VUOTO invece di un
    # errore -- e succede -- quella fetta resta archiviata come "qui non
    # c'era niente", PER SEMPRE. L'archivio, nato per non perdere eventi,
    # li cementava.
    #
    # LA RADICE VERA: le fette erano un'ottimizzazione messa prima di
    # servire. La finestra da quando il contratto e' giusto e' di poche
    # migliaia di blocchi, e il nodo accetta UNA domanda su tutto
    # l'intervallo -- ed e' proprio quella domanda che ha trovato le due.
    # Quindi: niente fette, niente archivio, niente copertura parziale. Si
    # chiede tutto, e se la rete non risponde si DICE che non si sa, invece
    # di dire zero.
    eventi = None
    for u in R.FONTI:
        try:
            eventi = R._chiedi(u, "eth_getLogs",
                               [{"address": POOL, "topics": [FIRMA],
                                 "fromBlock": hex(DA_BLOCCO),
                                 "toBlock": hex(testa)}], 40)
            if eventi is not None:
                break
        except Exception:
            eventi = None
    if eventi is None:
        print("   DA QUANDO SIAMO VERI: la rete non ha risposto. NON dico "
              "zero: dico che non lo so.")
        return {"quando": time.time(), "so": False,
                "perche": "nessuna fonte ha risposto all'interrogazione"}
    buchi = 0
    _copertura = 1.0

    righe = []
    for e in eventi:
        gar = ("0x" + e["topics"][1][-40:]).lower()
        deb = ("0x" + e["topics"][2][-40:]).lower()
        ut = ("0x" + e["topics"][3][-40:]).lower()
        d = e["data"][2:]
        coperto = int(d[0:64], 16); preso = int(d[64:128], 16)
        liq = ("0x" + d[128:192][-40:]).lower()
        # IL PREMIO PASSATO SI VALUTA COL PREZZO DI QUEL BLOCCO.
        # Regola che avevo gia' scritta e che ho violato nel codice nuovo:
        # la stessa liquidazione mi ha letto 509.058 $, poi 787.320, poi
        # 947.639 -- perche' la valutavo coi prezzi del momento in cui
        # guardavo. Solo l'ultimo e' vero: e' il prezzo di quel blocco.
        pg, pd = PR.get(gar), PR.get(deb)
        prem = None
        if pg and pd:
            try:
                import tabellone as _TB
                _p1 = _TB.prezzo_al_blocco(gar, int(e["blockNumber"], 16))
                _p2 = _TB.prezzo_al_blocco(deb, int(e["blockNumber"], 16))
            except Exception:
                _p1 = _p2 = None
            _u1 = _p1 or pg["prezzo_usd"]
            _u2 = _p2 or pd["prezzo_usd"]
            prem = (preso / 10**pg["decimali"] * _u1
                    - coperto / 10**pd["decimali"] * _u2)
        righe.append({
            "blocco": int(e["blockNumber"], 16), "utente": ut,
            "premio": round(prem, 2) if prem is not None else None,
            "conosciuta": ut in sn, "sorvegliata": ut in corta,
            "ordine_pronto": bool((VP.get(ut) or {}).get("chiamata")),
            "vinta_da_noi": liq == NOSTRO, "vincitore": liq})
    ore = (testa - DA_BLOCCO) * 12 / 3600
    pronti = [r for r in righe if r["ordine_pronto"]]
    out = {"quando": time.time(), "da_blocco": DA_BLOCCO, "ore": round(ore, 1),
           "fette_non_lette": buchi,
           "copertura_finestra": round(_copertura, 3),
           "liquidazioni_nel_mondo": len(righe),
           "eravamo_pronti_su": len(pronti),
           "vinte_da_noi": len([r for r in righe if r["vinta_da_noi"]]),
           "premio_passato": round(sum(r["premio"] or 0 for r in righe), 2),
           "premio_su_cui_eravamo_pronti": round(
               sum(r["premio"] or 0 for r in pronti), 2),
           "liquidazioni": righe[-12:]}
    tmp = FUORI + ".tmp"
    json.dump(out, open(tmp, "w"), indent=1)
    os.replace(tmp, FUORI)
    print(f"   copertura della finestra: {100*_copertura:.0f}%"
          + (f" ({buchi} fette non lette a questo giro)" if buchi else ""))
    print(f"   DA QUANDO SIAMO VERI ({ore:.1f} ore): "
          f"{len(righe)} liquidazioni nel mondo, "
          f"eravamo pronti su {len(pronti)}, vinte {out['vinte_da_noi']}")
    if righe:
        print(f"   premio passato ${out['premio_passato']:,.0f}, "
              f"di cui ${out['premio_su_cui_eravamo_pronti']:,.0f} alla nostra portata")
    return out


if __name__ == "__main__":
    misura()
