"""LA PROVA IN AVANTI: la regola applicata a monete che si diplomano DA ADESSO, con soldi finti.

== PERCHE' (8/10/2026) ==

La regola regge sulla storia: «compro a fine primo minuto dopo il diploma, vendo al raddoppio» fa
**+15,2% per moneta a 200 $** con lo scivolamento misurato dentro, su 330 monete mai usate per
scegliere. Ma la storia e' un posto dove si sbaglia in modo elegante: il solo giudice vero e' cio'
che succede DOPO aver scritto la regola.

Quindi questo agente apre posizioni **finte** su monete che si diplomano dopo il blocco di
partenza, scritto nel registro al primo giro e mai piu' toccato.

== LE REGOLE, FISSATE E NON PIU' NEGOZIABILI ==

- **entrata**: 600 blocchi dopo il primo scambio del pool, al prezzo mediano degli ultimi 5 scambi
  della finestra;
- **uscita**: al primo prezzo che tocca 2x l'entrata; se entro **600.000 blocchi** (16,7 ore: NON 7 giorni, errore trovato il 9/10)
  non arriva, si chiude all'ultimo prezzo visto;
- **costi**: 1% in entrata, 1% in uscita, piu' lo scivolamento **misurato** per la dimensione
  scelta (200 $ -> 1,71% a tratta);
- **nessuna selezione**: entra ogni moneta che si diploma.

Cambiare una di queste regole a prova in corso invaliderebbe tutto, e il motivo e' scritto qui
perche' il me stesso di domani lo legga: un criterio modificato dopo aver visto i risultati non e'
piu' una prova, e' una giustificazione.
"""
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402
import prima_la_prova as PP                                  # noqa: E402


# UNA SOLA LIBRERIA DI LETTURA (11/10, prescrizione di Astra). `curva_lanci` e `coppie` erano
# oggetti unici da 52 e 16,6 MB: per aggiungere un dato si riscriveva tutto, e ogni riscrittura
# entrava INTERA nella storia di git. Ora stanno a righe, e queste due funzioni nascondono quale
# forma c'e' sul disco: se cambia di nuovo, cambia in agents/archivio.py e non in dodici file.
def _lanci_interi():
    import archivio as _AR
    _t, _v = _AR.leggi("curva_lanci")
    _d = dict(_t)
    _d["da"] = _v
    return _d


def _coppie():
    import archivio as _AR
    return _AR.leggi("coppie", "coppie")[1]


CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
STATO = f"{BASE}/prova_in_avanti.json"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
ZERO = "0x" + "0" * 40
# l'evento di CREAZIONE del pool in Uniswap v4: topics[1] e' l'id, i dati portano le due valute.
# E' l'unico modo onesto per sapere che un pool e' NUOVO: il nostro registro contiene solo pool
# gia' noti, cioe' vecchi.
INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
FINESTRA = 600
ORIZZONTE = 600000
COSTO = 1.02
SCIV = float(os.environ.get("SCIVOLAMENTO", "0.0171"))      # misurato per 75-300 $
PREZZO_ETH = 2575.78


def _seg(z):
    return z - (1 << 256) if z >= (1 << 255) else z


def leggi_stato():
    if os.path.exists(STATO):
        try:
            return json.load(open(STATO))
        except Exception:
            pass
    return {"versione": 1, "partenza": None, "ultimo_blocco": None, "posizioni": {},
            "regole": {"finestra": FINESTRA, "orizzonte": ORIZZONTE, "uscita": "2x",
                       "costo": COSTO, "scivolamento": SCIV}}


def swap_del_gestore(da, a):
    """Tutti gli scambi v4 nella finestra di blocchi. (None se la chain non risponde.)"""
    return CP.log_di_finestra(PP.SWAP_V4, da, a, indirizzo=GESTORE_V4)


def decimali_di(asset, st):
    """I decimali dell'asset di quotazione, chiesti al contratto una volta e ricordati."""
    cache = st.setdefault("decimali", {})
    a = (asset or "").lower()
    if a in cache:
        return cache[a]
    if a == ZERO:
        cache[a] = 18
        return 18
    r = CP.chiama("eth_call", [{"to": a, "data": "0x313ce567"}, "latest"])
    try:
        cache[a] = int(r, 16) if r and r != "0x" else None
    except Exception:
        cache[a] = None
    return cache[a]


def prezzo_di(l, lato_tok, dec_valuta=18):
    n = CP._numeri(l.get("data", "0x"))
    if len(n) < 2:
        return None
    a0, a1 = _seg(n[0]), _seg(n[1])
    qt = a1 if lato_tok == "t1" else a0
    qq = a0 if lato_tok == "t1" else a1
    if qt == 0 or qq == 0:
        return None
    vq = abs(qq) / (10 ** int(dec_valuta))
    if vq < 1e-9:
        return None
    # IL VERSO ERA INVERTITO (10/10, verificato sulla chain su 4 casi). Nel Swap di
    # Uniswap v4 gli importi sono quelli dello SCAMBIATORE, non del pool: negativo = lo
    # scambiatore PAGA, positivo = RICEVE. Quindi valuta POSITIVA vuol dire che riceve
    # valuta, cioe' ha VENDUTO il gettone. Il codice diceva `qq < 0`, cioe' il contrario,
    # e tutte le attribuzioni compra/vendi erano scambiate (i prezzi no: usano abs()).
    # Trovato guardando i Transfer del gettone nella stessa transazione: in una vendita il
    # gettone ENTRA nel pool. La prova e' questa, non la convenzione letta in un documento.
    return vq / (abs(qt) / 1e18), vq, qq > 0


def main():
    st = leggi_stato()
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("AVANTI | la chain non risponde.")
        return 0
    if st["partenza"] is None:
        st["partenza"] = bn
        st["ultimo_blocco"] = bn
        json.dump(st, open(STATO, "w"), indent=1)
        print(f"AVANTI | prova aperta al blocco {bn:,}. Da qui in poi, ogni moneta che si "
              f"diploma entra. Le regole sono scritte nel registro e non si toccano piu'.")
        return 0

    # I POOL NUOVI, DALL'EVENTO DI CREAZIONE (8/10, dopo aver scoperto che la prova misurava
    # tutt'altro). Prima i pool si riconoscevano da `coppie.json`, che contiene solo pool GIA'
    # NOTI: la prova vedeva monete lanciate 59-915 ore prima e chiamava «primo scambio» il primo
    # che capitava di leggere. Otto posizioni su otto erano vecchie. Tutto cio' che aveva
    # accumulato era senza valore, e non me ne sarei accorto guardando i suoi conti: l'ho visto
    # solo confrontando il blocco di lancio col blocco del «primo scambio».
    # Qui un pool e' nuovo quando la chain dice che e' stato creato: evento Initialize.
    import gzip
    L = _lanci_interi()["da"]
    # I LANCI IN DIRETTA (8/10). L'elenco su disco e' una fotografia vecchia: le monete nate
    # oggi non ci sono, e la prova non riconosceva i loro pool — su 12 pool appena creati, UNO
    # aveva un gettone nel nostro elenco e ZERO la coppia giusta. Il referto diceva «0 nuovi»
    # senza errori, che e' il modo peggiore di sbagliare.
    # Qui i lanci si leggono dalla fabbrica a ogni giro e si accumulano nello stato.
    nati_ora = set(st.get("lanci_visti") or [])
    ev_lanci = CP.log_di_finestra(CP.T_LANCIO, st["ultimo_blocco"] + 1, bn,
                                  indirizzo=CP.FABBRICA.lower())
    if ev_lanci is None:
        print("AVANTI | non riesco a leggere i lanci: non avanzo il segnalibro.")
        return 0
    for l in ev_lanci:
        t = (l.get("topics") or [None, None])[1]
        if t:
            nati_ora.add("0x" + t[-40:])
    st["lanci_visti"] = sorted(nati_ora)
    if ev_lanci:
        print(f"AVANTI | {len(ev_lanci)} lanci nuovi letti dalla fabbrica "
              f"({len(nati_ora)} in tutto)", flush=True)
    lato_di = dict(st.get("pool_noti") or {})
    nuovi_pool = CP.log_di_finestra(INIT, st["ultimo_blocco"] + 1, bn, indirizzo=GESTORE_V4)
    if nuovi_pool is None:
        print("AVANTI | non riesco a leggere le creazioni di pool: non avanzo il segnalibro.")
        return 0
    creati = 0
    for l in nuovi_pool:
        pid = (l.get("topics") or [None, None])[1]
        if not pid:
            continue
        # LE DUE VALUTE STANNO NEI TOPICS, non nei dati (8/10). Le leggevo dai dati e prendevo
        # la commissione (0x2710 = 10000) e lo spacing dei tick (0xc8 = 200) come se fossero
        # indirizzi: nessun pool veniva riconosciuto, e il referto diceva «0 nuovi» senza errore.
        # Un evento c'era, l'ho visto contando i topic emessi dal gestore: 15 Initialize in 2.000
        # blocchi. Zero che non torna va inseguito.
        if len(l.get("topics") or []) < 4:
            continue
        c0 = "0x" + l["topics"][2][-40:]
        c1 = "0x" + l["topics"][3][-40:]
        for lato, a, altro in (("t0", c0, c1), ("t1", c1, c0)):
            # QUALUNQUE VALUTA DI QUOTAZIONE, non solo il nativo (8/10). Pretendere ETH nativo
            # escludeva quasi tutto: i lanci su Pons usano 72 asset di quotazione diversi
            # (USDG, azioni tokenizzate...), e in 36 minuti riconoscevo UN pool su ~140 creati.
            # Misurare una fetta scelta dalla valuta non e' misurare il mercato.
            if (a in L or a in nati_ora) and altro != a:
                dec = decimali_di(altro, st)
                if dec is None:
                    continue              # senza i decimali il prezzo e' un numero senza unita'
                lato_di[pid.lower()] = [lato, a, int(l["blockNumber"], 16), altro, dec]
                creati += 1
    st["pool_noti"] = lato_di
    if creati:
        print(f"AVANTI | {creati} pool NUOVI creati in questa finestra", flush=True)

    da = st["ultimo_blocco"] + 1
    ev = swap_del_gestore(da, bn)
    if ev is None:
        print(f"AVANTI | lettura fallita fra {da:,} e {bn:,}: non avanzo il segnalibro, "
              f"cosi' il giro prossimo riprova gli stessi blocchi.")
        return 0
    print(f"AVANTI | blocchi {da:,}-{bn:,}: {len(ev):,} scambi letti", flush=True)

    per_pool = {}
    for l in ev:
        pid = (l.get("topics") or [None, None])[1]
        if not pid:
            continue
        pid = pid.lower()
        if pid not in lato_di:
            continue
        v = lato_di[pid]
        lato, tok = v[0], v[1]
        p = prezzo_di(l, lato, v[4] if len(v) > 4 else 18)
        if not p:
            continue
        per_pool.setdefault(pid, []).append((int(l["blockNumber"], 16),
                                             int(l.get("logIndex", "0x0"), 16)) + p)

    nuove = chiuse = aggiornate = mescolati = 0
    for pid, scambi in per_pool.items():
        lato, tok = lato_di[pid][0], lato_di[pid][1]
        scambi.sort()
        pos = st["posizioni"].get(tok)
        # UN POOL PER POSIZIONE (8/10, trovato controllando la prova contro la chain).
        # Le posizioni sono indicizzate per MONETA, ma una moneta puo' avere due pool (uno in
        # nativo, uno in un altro asset). Senza questo controllo gli scambi del secondo pool
        # finivano nella stessa posizione: la prova aveva raccolto 5 prezzi in una finestra che
        # contiene 3 scambi, e l'entrata era una media di due scale diverse.
        # E' lo stesso errore che nello storico produceva una salita monotona su TUTTE le monete.
        if pos is not None and pos.get("pool") and pos["pool"] != pid:
            mescolati += 1
            # SEGUIAMO IL POOL GIUSTO? (10/10) Saltare il secondo pool e' corretto, ma se lo
            # scambio vive LI' allora il cammino che registriamo e' quello di un pool morto, e
            # un 2x su un pool vuoto non e' un 2x. Registro quanti scambi ha ciascuno dei due,
            # per poterlo MISURARE invece di supporlo.
            d = pos.setdefault("altri_pool", {})
            r = d.setdefault(pid, {"scambi": 0})
            r["scambi"] += len(scambi)
            r["scambi_nel_mio"] = len(per_pool.get(pos["pool"], []))
            continue
        if pos is None:
            # NUOVA: il primo scambio che vedo e' dentro la finestra che ho letto, quindi il
            # pool e' nato adesso. Se fosse nato prima, lo avrei gia' in registro.
            st["posizioni"][tok] = {"pool": pid, "primo_blocco": lato_di[pid][2],
                                    "aperta_il": int(time.time()), "stato": "in attesa",
                                    "prezzi_finestra": [], "entrata": None, "esito": None}
            pos = st["posizioni"][tok]
            nuove += 1
        if pos["stato"] == "in attesa":
            fine = pos["primo_blocco"] + FINESTRA
            dentro = [s for s in scambi if s[0] <= fine]
            pos["prezzi_finestra"] = (pos["prezzi_finestra"] + [s[2] for s in dentro])[-20:]
            if bn > fine and len(pos["prezzi_finestra"]) >= 5:
                pos["entrata"] = statistics.median(pos["prezzi_finestra"][-5:])
                pos["stato"] = "aperta"
                aggiornate += 1
            # NON si scarta qui (8/10, difetto misurato): questo ciclo vede solo i blocchi letti
            # in QUESTO giro, e se il loop parte quando la finestra e' gia' passata ne legge un
            # pezzo. Contando quel pezzo si scartava il 99,4% delle monete contro il 9,9% che il
            # campione storico dice comprabili. La decisione la prende la rilettura diretta della
            # finestra, che legge tutti i suoi blocchi in una chiamata.
        if pos["stato"] == "aperta" and pos["entrata"]:
            dopo = [s for s in scambi if s[0] > pos["primo_blocco"] + FINESTRA]
            tocca = [s for s in dopo if s[2] >= 2 * pos["entrata"]]
            if tocca:
                r = 2.0 / (COSTO * (1 + SCIV) ** 2) - 1
                pos["stato"] = "chiusa"
                pos["esito"] = {"verso": "raddoppio", "rendimento": round(r, 4),
                                "blocco": tocca[0][0]}
                chiuse += 1
            elif dopo:
                pos["ultimo_prezzo"] = dopo[-1][2]
                pos["ultimo_blocco_visto"] = dopo[-1][0]
            # IL CAMMINO DELLA POSIZIONE (9/10, chiesto da Nicolo'). Si registrano minimo e
            # massimo raggiunti rispetto all'entrata, con il blocco in cui sono avvenuti.
            # NON cambia nessuna regola di decisione: l'entrata, l'uscita al raddoppio e
            # l'orizzonte restano quelli congelati. Questo e' **osservazione**, e serve perche'
            # fra cinque giorni, con cinquanta posizioni, i dati dicano dove mettere uno stop
            # invece di deciderlo noi adesso su tre risultati.
            # Il motivo per cui si registra ORA: il cammino non si puo' ricostruire dopo se non
            # rileggendo la chain, e dopo l'orizzonte le letture diventano lunghe.
            if dopo and pos.get("entrata"):
                for z in dopo:
                    x = z[2] / pos["entrata"]
                    if pos.get("min_x") is None or x < pos["min_x"]:
                        pos["min_x"] = round(x, 5)
                        pos["min_al_blocco"] = z[0]
                    if pos.get("max_x") is None or x > pos["max_x"]:
                        pos["max_x"] = round(x, 5)
                        pos["max_al_blocco"] = z[0]
    # OGNI POOL RICONOSCIUTO DEVE AVERE UNO STATO (9/10). Un pool creato e mai scambiato non
    # diventava una posizione: non era ne' «scartato» ne' tracciato, era **invisibile**. Sembra
    # innocuo e non lo e': fra cinque giorni il denominatore sarebbe sbagliato, e la frase «su N
    # graduazioni X erano comprabili» diventerebbe falsa — proprio il tipo di errore per cui ho
    # ritirato quattro numeri in due giorni.
    # Qui ogni pool la cui finestra e' passata e che non ha una posizione viene chiuso con un
    # motivo esplicito, letto dalla chain. Al massimo 40 per giro, per non sforare il tempo.
    da_chiudere = [(pid, v) for pid, v in lato_di.items()
                   if v[1] not in st["posizioni"] and bn > v[2] + FINESTRA]
    chiusi_esplicitamente = 0
    # il tetto era 40 per giro: con ~64 graduazioni l'ora rincorreva il buco invece di chiuderlo.
    # Ogni chiusura costa UNA chiamata, quindi 120 per giro stanno larghi nel tempo del loop.
    for pid, v in da_chiudere[:120]:
        ev = CP.log_di_finestra(PP.SWAP_V4, v[2], v[2] + FINESTRA,
                                indirizzo=GESTORE_V4, secondo=pid)
        if ev is None:
            continue                     # non si conclude su cio' che non si e' letto
        pr = [q[0] for q in (prezzo_di(l, v[0], v[4] if len(v) > 4 else 18) for l in ev) if q]
        st["posizioni"][v[1]] = {
            "pool": pid, "primo_blocco": v[2], "aperta_il": int(time.time()),
            "stato": "scartata", "prezzi_finestra": [], "entrata": None,
            "esito": {"motivo": ("pool muto: nessuno scambio nel primo minuto" if not pr
                                 else f"solo {len(pr)} scambi nel primo minuto"),
                      "scambi_nella_finestra": len(pr)}}
        chiusi_esplicitamente += 1
    if chiusi_esplicitamente:
        print(f"AVANTI | {chiusi_esplicitamente} pool chiusi con un motivo esplicito "
              f"(erano invisibili); ne restano {max(0, len(da_chiudere)-120)} per il giro prossimo",
              flush=True)

    # LE FINESTRE RIMASTE NEL PASSATO (8/10). Questo agente legge solo i blocchi NUOVI, quindi
    # una posizione la cui finestra e' gia' passata non riceverebbe mai un prezzo d'entrata — e
    # resterebbe «in attesa» per sempre, sparendo dal conto senza che nessuno lo noti.
    # Succede dopo una correzione come quella dei due pool: le posizioni si azzerano e la loro
    # finestra e' indietro. Qui si rileggono una per una, con una chiamata, e si chiude il caso.
    recuperate = 0
    for tok, pos in st["posizioni"].items():
        if pos["stato"] != "in attesa" or not pos.get("pool"):
            continue
        fine = pos["primo_blocco"] + FINESTRA
        if bn <= fine:
            continue
        # si rilegge anche se qualche prezzo era stato raccolto: un pezzo di finestra non e' la
        # finestra, ed e' esattamente l'errore che scartava quasi tutto.
        ev = CP.log_di_finestra(PP.SWAP_V4, pos["primo_blocco"], fine,
                                indirizzo=GESTORE_V4, secondo=pos["pool"])
        if ev is None:
            continue                      # non si conclude su cio' che non si e' letto
        _v = lato_di.get(pos["pool"]) or ["t0"]
        prezzi = []
        for l in ev:
            q = prezzo_di(l, _v[0], _v[4] if len(_v) > 4 else 18)
            if q:
                prezzi.append(q[0])
        if len(prezzi) >= 5:
            pos["prezzi_finestra"] = prezzi[-20:]
            pos["entrata"] = statistics.median(prezzi[-5:])
            pos["stato"] = "aperta"
            recuperate += 1
        else:
            pos["stato"] = "scartata"
            pos["esito"] = {"motivo": "meno di 5 scambi nel primo minuto"}
    if recuperate:
        print(f"AVANTI | {recuperate} finestre rilette dal passato e aperte", flush=True)

    # orizzonte scaduto: si chiude all'ultimo prezzo visto
    for tok, pos in st["posizioni"].items():
        if pos["stato"] == "aperta" and pos.get("entrata") and \
           bn - pos["primo_blocco"] > ORIZZONTE:
            up = pos.get("ultimo_prezzo") or pos["entrata"]
            r = (up / pos["entrata"]) / (COSTO * (1 + SCIV) ** 2) - 1
            pos["stato"] = "chiusa"
            pos["esito"] = {"verso": "orizzonte", "rendimento": round(r, 4)}
            chiuse += 1

    # AUTOVERIFICA A OGNI GIRO (8/10). Un'entrata sbagliata rende la prova inutile, e il difetto
    # dei due pool l'ho trovato SOLO perche' ho ricalcolato tre posizioni contro la chain a mano.
    # Una cosa che dipende dal mio ricordarmene non si fa: qui due posizioni aperte si
    # ricalcolano da zero a ogni giro, e se non combaciano la posizione viene marcata SOSPETTA
    # invece di restare nel conto come se niente fosse.
    import random as _r
    aperte = [(k, v) for k, v in st["posizioni"].items()
              if v["stato"] == "aperta" and v.get("entrata")]
    if aperte:
        _r.seed(bn)
        for tok, pos in _r.sample(aperte, min(2, len(aperte))):
            ev = CP.log_di_finestra(PP.SWAP_V4, pos["primo_blocco"],
                                    pos["primo_blocco"] + FINESTRA,
                                    indirizzo=GESTORE_V4, secondo=pos["pool"])
            if ev is None:
                continue                      # non si giudica su cio' che non si e' letto
            _v = lato_di.get(pos["pool"]) or ["t0"]
            pr = [q[0] for q in (prezzo_di(l, _v[0], _v[4] if len(_v) > 4 else 18)
                                 for l in ev) if q]
            if len(pr) < 5:
                pos["stato"] = "sospetta"
                pos["esito"] = {"motivo": f"rilettura: solo {len(pr)} scambi nella finestra"}
                print(f"AVANTI | SOSPETTA {tok[:14]}…: la rilettura trova {len(pr)} scambi, "
                      f"non abbastanza per un'entrata", flush=True)
                continue
            ric = statistics.median(pr[-5:])
            scarto = abs(ric - pos["entrata"]) / pos["entrata"]
            if scarto > 0.02:
                pos["stato"] = "sospetta"
                pos["esito"] = {"motivo": f"entrata non combacia: {scarto*100:.1f}% di scarto"}
                print(f"AVANTI | SOSPETTA {tok[:14]}…: entrata {pos['entrata']:.4e} contro "
                      f"{ric:.4e} ricalcolata ({scarto*100:.1f}%)", flush=True)
            else:
                pos["verificata_al_blocco"] = bn

    st["ultimo_blocco"] = bn
    json.dump(st, open(STATO, "w"), indent=1)
    ap = [p for p in st["posizioni"].values() if p["stato"] == "aperta"]
    ch = [p for p in st["posizioni"].values() if p["stato"] == "chiusa"]
    sc = [p for p in st["posizioni"].values() if p["stato"] == "scartata"]
    print(f"AVANTI | nuove {nuove}, entrate {aggiornate}, chiuse {chiuse}"
          + (f", scambi di un SECONDO pool ignorati su {mescolati} monete" if mescolati else ""))
    print(f"AVANTI | aperte {len(ap)}, chiuse {len(ch)}, scartate {len(sc)} "
          f"(dalla partenza, blocco {st['partenza']:,})")
    if ch and len(ch) < 50:
        # IL TOTALE NON SI STAMPA PRIMA DI 50 CHIUSURE (9/10). Lo stampava, e diceva «+89,5%,
        # raddoppi 3/3» — il numero piu' ingannevole possibile, perche' chi raddoppia chiude in
        # venti minuti e chi perde solo all'orizzonte dei sette giorni. Un conto intermedio
        # contiene SOLO vincenti. Anche solo vederlo scritto spinge a crederci: quindi non si
        # scrive.
        print(f"AVANTI | {len(ch)} chiusure: il totale NON si legge prima di 50 e prima che le "
              f"perdenti abbiano avuto la stessa occasione (orizzonte reale: 16,7 ore).")
    elif ch:
        r = [p["esito"]["rendimento"] for p in ch]
        vinc = sum(1 for p in ch if p["esito"].get("verso") == "raddoppio")
        print(f"AVANTI | RISULTATO FINORA: medio {100*statistics.mean(r):+.1f}%, "
              f"mediano {100*statistics.median(r):+.1f}%, raddoppi {vinc}/{len(ch)}")
        print(f"AVANTI | (atteso dalla storia a 200$: +15,2% medio) — "
              f"servono almeno 50 posizioni chiuse prima di confrontare")
    return 0


if __name__ == "__main__":
    sys.exit(main())
