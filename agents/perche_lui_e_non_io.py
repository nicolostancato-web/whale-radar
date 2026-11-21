"""Perche' l'ha preso lui e non io? La domanda del regime di sorveglianza.

L'IMPOSTAZIONE E' DI NICOLO' (5/11 pomeriggio), ed e' migliore di quella
che avevo fatto io. Io avevo costruito una sorveglianza che chiede
"eravamo pronti?", binaria. Lui chiede QUANTO ERAVAMO LONTANI dal
vincitore, e in quale dimensione -- che e' la domanda che dice QUALE BLOCCO
aggiustare, invece di dire solo si' o no.

Per tre giorni il loop camminava dentro la macchina: blocco per blocco, "e'
giusto? si puo' migliorare?". Serviva, perche' la macchina era rotta. Ora e'
provata, e il loop deve guardare FUORI: per ogni liquidazione avvenuta nel
mondo, quanto distavamo dal vincitore.

LE CINQUE DISTANZE, dalla piu' innocente alla piu' grave:

  1. C'ERAVAMO NEL PACCHETTO e ha vinto lui          -> l'asta. La macchina
     e' giusta: si guarda quanto ha pagato in piu'.      (blocco 6)
  2. AVEVAMO L'ORDINE ma non era nel pacchetto       -> la scelta dei posti.
     Trenta posti e lei fuori: perche'?                  (blocco 6/2)
  3. LA SORVEGLIAVAMO ma non avevamo l'ordine        -> non sapevamo
     venderla.                                           (blocco 5)
  4. LA CONOSCEVAMO ma non la sorvegliavamo          -> la banda, la
     freschezza.                                         (blocco 4)
  5. NON LA CONOSCEVAMO                              -> la raccolta.
                                                          (blocco 4)

Solo le distanze 2-5 autorizzano una modifica. La 1 e' un'asta persa, e si
perde senza che niente sia rotto.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pescatore as P

D = "data/liquidazioni"
FUORI = f"{D}/perche_lui_e_non_io.json"
DISTANZE = {
    1: ("c'eravamo nel pacchetto, ha vinto lui", 6, False),
    2: ("avevamo l'ordine ma non era nel pacchetto", 6, True),
    3: ("la sorvegliavamo ma non avevamo l'ordine", 5, True),
    4: ("la conoscevamo ma non la sorvegliavamo", 4, True),
    5: ("non la conoscevamo", 4, True),
}


def _nostri_pacchetti_vicino(ts, utente, finestra=120):
    """Era fra le candidate che abbiamo spedito intorno a quel momento?

    Si abbina per TEMPO perche' il registro della sentinella non salva il
    numero di blocco: l'ora e' in UTC, e si guarda +/- due minuti.
    """
    ora = time.strftime("%H:%M:%S", time.gmtime(ts))
    hh, mm, ss = (int(x) for x in ora.split(":"))
    secondi = hh*3600 + mm*60 + ss
    trovata = False
    vicini = 0
    try:
        righe = open(f"{D}/sentinella.jsonl").readlines()[-4000:]
    except Exception:
        return None, 0
    for l in righe:
        try:
            r = json.loads(l)
            q = r.get("quando")
            if not q:
                continue
            a, b, c = (int(x) for x in q.split(":"))
            if abs((a*3600 + b*60 + c) - secondi) > finestra:
                continue
            vicini += 1
            for cd in r.get("candidate") or []:
                if (cd.get("u") or "").lower()[:12] == utente[:12]:
                    trovata = True
        except Exception:
            continue
    return trovata, vicini


def misura(da_blocco=None):
    sv, _ = (json.load(open(f"{D}/da_quando_siamo_veri.json")), None) \
        if os.path.exists(f"{D}/da_quando_siamo_veri.json") else (None, None)
    if not sv:
        return {"so": False, "perche": "il punteggio non e' misurato"}
    sn = json.load(open(f"{D}/salute_note.json"))
    corta = {r["indirizzo"].lower()
             for r in json.load(open(f"{D}/lista_corta.json"))}
    VP = {k.lower(): v for k, v in
          json.load(open(f"{D}/vendite_pronte.json")).items()}
    righe = []
    for r in (sv.get("liquidazioni") or []):
        u = r["utente"]
        b = P.rpc("eth_getBlockByNumber", [hex(r["blocco"]), False], giri=2)
        ts = int(b["timestamp"], 16) if b else None
        # LA PROVA MIGLIORE E' LA NOSTRA FOTOGRAFIA DI QUEL BLOCCO.
        # Nel LIVE eravamo gia' posizionati, quindi la domanda "c'ero?" si
        # risponde col nostro registro di allora, cercato per NUMERO DI
        # BLOCCO. Il vecchio abbinamento per ORA funzionava solo se in quel
        # momento avevamo beccato un aggiornamento di prezzo: senza
        # aggiornamento non c'era traccia, e l'autopsia non poteva
        # rispondere. Il registro di dove_eravamo scatta a intervalli
        # regolari, quindi ogni liquidazione trova una fotografia.
        import dove_eravamo as DE
        foto, dist_blocchi = DE.piu_vicina_al_blocco(r["blocco"], tolleranza=120)
        if foto:
            nel_pacchetto = any(
                (c.get("u") or "").lower()[:12] == u[:12]
                for c in (foto.get("candidate") or []))
            vicini = foto.get("candidate_quante") or 0
            prova = f"fotografia a {dist_blocchi} blocchi di distanza"
        else:
            nel_pacchetto, vicini = (_nostri_pacchetti_vicino(ts, u)
                                     if ts else (None, 0))
            prova = ("nessuna fotografia vicina: ripiego sull'abbinamento "
                     "per ora, meno affidabile")
        if u not in sn:
            d = 5
        elif u not in corta:
            d = 4
        elif not (VP.get(u) or {}).get("chiamata"):
            d = 3
        elif nel_pacchetto is False:
            d = 2
        else:
            d = 1
        eti, blocco, autorizza = DISTANZE[d]
        righe.append({"blocco_catena": r["blocco"], "utente": u,
                      "premio": r.get("premio"), "distanza": d,
                      "cosa": eti, "colpa_del_blocco": blocco,
                      "autorizza_modifica": autorizza,
                      "nostri_pacchetti_in_quel_momento": vicini,
                      "prova": prova,
                      "vinta_da_noi": r.get("vinta_da_noi")})
    out = {"quando": time.time(), "ore": sv.get("ore"), "casi": righe}
    tmp = FUORI + ".tmp"
    json.dump(out, open(tmp, "w"), indent=1)
    os.replace(tmp, FUORI)
    if not righe:
        print(f"   PERCHE' LUI E NON IO: nessuna liquidazione nel mondo da "
              f"{sv.get('ore')} ore. Niente da spiegare.")
        return out
    print(f"   PERCHE' LUI E NON IO ({len(righe)} casi in {sv.get('ore')} ore):")
    for x in righe:
        print(f"     ${(x['premio'] or 0):>10,.0f}  distanza {x['distanza']}: "
              f"{x['cosa']}  -> blocco {x['colpa_del_blocco']}"
              + ("  [MODIFICA AUTORIZZATA]" if x["autorizza_modifica"] else ""))
    return out


if __name__ == "__main__":
    misura()
