"""Chi vende quando la moneta crolla — e se aveva comprato nel primo minuto.

L'IDEA E' DI NICOLO' (10/10): «hai detto che certe volte scende di brutto, quindi viene dampata
di brutto: chi e' che sta vendendo li'? Magari possiamo prendere spunto da chi vende a quel
punto, perche' se dampa forte vuol dire che qualcuno vende forte, o qualcuno ha comprato anche
forte all'inizio.»

E' una domanda ben posta, perche' e' falsificabile: se i crolli li causano POCHI indirizzi che
avevano comprato per primi, allora si vedono in anticipo (comprano al minuto zero, in grande) e
diventano un segnale. Se invece a vendere sono tanti indirizzi diversi che non c'erano
all'inizio, i crolli sono folla, non regia: nessun segnale, e lo sapremo.

PERCHE' SOLO NEL DUMP. L'evento Swap di Uniswap v4 porta nel terzo argomento il *mittente*, che
e' il router, non la persona. La persona sta nel campo `from` della TRANSAZIONE, e costa una
chiamata per transazione. Chiederlo per tutti gli scambi di tutte le monete sarebbe decine di
migliaia di chiamate; chiederlo solo nella finestra del crollo e nel primo minuto costa poche
centinaia, e sono le due finestre che rispondono alla domanda.

OGNI RIGA PORTA LE SUE PROVE: per ogni venditore restano gli hash delle sue transazioni, cosi'
ogni numero si puo' aprire su un explorer e controllare. Senza le prove sarebbe un'altra
classifica di cui fidarsi, e di quelle ne abbiamo gia' smontate troppe.
"""
import collections
import json
import os
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

import curva_pons as CP                                        # noqa: E402
import prima_la_prova as PP                                    # noqa: E402
import iniziatori as IN                                        # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
STATO = f"{BASE}/prova_in_avanti.json"
ARCH = f"{BASE}/chi_vende_nel_dump.json"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()

FINESTRA = 600            # il primo minuto, come nella prova in avanti
ORIZZONTE = 600_000       # 16,7 ore, come nella prova in avanti
MAX_TX = 150              # tetto di chiamate per finestra e per moneta: oltre si dichiara
VERSIONE = 1


def chi_sono(hash_list, pezzo=25):
    """{hash: from}, chiesto a PACCHETTI PICCOLI.

    PERCHE' (10/10, trovato un'ora dopo averlo scritto). Chiedevo 150 transazioni in una sola
    chiamata: il nodo rifiutava in silenzio e tornava vuoto, e il record finiva con «0 venditori»
    su un crollo con 2.331 scambi. **«Zero» e «non l'ho potuto sapere» sono due cose diverse, e
    scrivere la prima al posto della seconda mette una bugia nel database** — peggio di un buco,
    perche' un buco si vede e una bugia no.
    Qui si chiede a pezzi da 25, e si torna anche QUANTI pezzi sono falliti, per scriverlo.
    """
    fuori, falliti = {}, 0
    for i in range(0, len(hash_list), pezzo):
        r = IN.chiedi(hash_list[i:i + pezzo])
        if not r:
            falliti += 1
            continue
        fuori.update(r)
    return fuori, falliti


def _numeri(l, lato, dec):
    """(prezzo, quantita' di valuta, vende) di uno scambio. None se illeggibile."""
    n = CP._numeri(l.get("data", "0x"))
    if len(n) < 2:
        return None
    a0 = n[0] - (1 << 256) if n[0] >= (1 << 255) else n[0]
    a1 = n[1] - (1 << 256) if n[1] >= (1 << 255) else n[1]
    qt = a1 if lato == "t1" else a0
    qq = a0 if lato == "t1" else a1
    if qt == 0 or qq == 0:
        return None
    vq = abs(qq) / (10 ** int(dec))
    if vq < 1e-12:
        return None
    # IL VERSO ERA INVERTITO (10/10, verificato sulla chain su 4 casi). Nel Swap di
    # Uniswap v4 gli importi sono quelli dello SCAMBIATORE, non del pool: negativo = lo
    # scambiatore PAGA, positivo = RICEVE. Quindi valuta POSITIVA vuol dire che riceve
    # valuta, cioe' ha VENDUTO il gettone. Il codice diceva `qq < 0`, cioe' il contrario,
    # e tutte le attribuzioni compra/vendi erano scambiate (i prezzi no: usano abs()).
    # Trovato guardando i Transfer del gettone nella stessa transazione: in una vendita il
    # gettone ENTRA nel pool. La prova e' questa, non la convenzione letta in un documento.
    return vq / (abs(qt) / 1e18), vq, qq > 0


TRASFERIMENTO = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def trasferimenti_del_gettone(token, blocco_pool, fino_a):
    """Tutti i Transfer del gettone, letti UNA volta per moneta.

    PERCHE' COSI'. Mi servirebbe filtrare sul destinatario, che nei Transfer e' il TERZO
    argomento indicizzato, ma `log_di_finestra` sa filtrare solo il secondo. Potevo aggiungere
    il parametro a quella funzione — e' usata da tutto il progetto, e un errore la' rompe
    undici agenti. Invece leggo tutto una volta e attribuisco in casa: una query per moneta
    invece di una per venditore, e nessuna modifica a codice condiviso (10/10).
    """
    return CP.log_di_finestra(TRASFERIMENTO, max(0, blocco_pool - 2_000_000), fino_a,
                              indirizzo=token)


CODICE = f"{BASE}/e_un_contratto.json"


def e_un_contratto(indirizzo):
    """True se all'indirizzo c'e' del codice. La risposta si tiene, perche' non cambia.

    PERCHE' SERVE (11/10). «Da un altro indirizzo» era la provenienza piu' frequente (43%), e i
    fornitori che comparivano su piu monete sembravano un'entita' dietro piu' lanci: uno su 20
    monete, uno su 18, uno su 11. Controllati: sono TUTTI CONTRATTI, cioe' router e portafogli
    intelligenti. Infrastruttura, non persone.
    E' la lezione «ordinare seleziona gli artefatti» in forma nuova: una classifica per ricorrenza
    mette in cima l'infrastruttura per COSTRUZIONE, perche' l'infrastruttura e' esattamente la
    cosa che ricorre. Quindi l'etichetta non e' un dettaglio: senza, il 43% sembra una scoperta e
    invece e' in buona parte il modo in cui questa chain fa passare i gettoni.
    """
    cache = {}
    if os.path.exists(CODICE):
        try:
            cache = json.load(open(CODICE))
        except json.JSONDecodeError:
            cache = {}
    a = indirizzo.lower()
    if a in cache:
        return cache[a]
    c = CP.chiama("eth_getCode", [a, "latest"]) or "0x"
    cache[a] = len(c) > 2
    json.dump(cache, open(CODICE, "w"))
    return cache[a]


def chi_ha_venduto_davvero(trasf):
    """{transazione: [(indirizzo, quantita')]} — chi ha davvero mandato il gettone nel pool.

    PERCHE' SOSTITUISCE IL MITTENTE DELLA TRANSAZIONE (11/10). Prendevo il campo `from` della
    transazione, e in 30 casi su 84 quell'indirizzo non appariva in NESSUN trasferimento del
    gettone: non poteva essere lui il venditore. Grok, interrogato in parallelo sulla
    documentazione di Uniswap v4, dice la stessa cosa con la fonte: «il `sender` e' chi ha
    chiamato PoolManager.swap e ha ricevuto la callback, di solito il ROUTER, non il portafoglio
    finale. Il Transfer ERC-20 esce dal PoolManager nella stessa transazione.»

    Il venditore vero e' il MITTENTE del trasferimento che porta il gettone DENTRO il pool. E
    non costa niente: i trasferimenti li leggiamo gia' per la provenienza, quindi questa versione
    e' insieme piu' giusta e piu' economica — spariscono tutte le chiamate al nodo che prima
    servivano a chiedere il mittente.
    """
    fuori = {}
    for x in trasf or []:
        tp = x.get("topics") or []
        if len(tp) < 3:
            continue
        if ("0x" + tp[2][-40:].lower()) != GESTORE_V4:
            continue                 # il gettone entra nel pool = qualcuno vende
        da = "0x" + tp[1][-40:].lower()
        if da in (GESTORE_V4, ZERO):
            continue
        n = CP._numeri(x.get("data", "0x"))
        fuori.setdefault(str(x["transactionHash"]).lower(), []).append(
            (da, (n[0] / 1e18) if n else 0.0))
    return fuori


def chi_ha_comprato_davvero(trasf):
    """Lo stesso, dal verso opposto: chi RICEVE il gettone dal pool sta comprando."""
    fuori = {}
    for x in trasf or []:
        tp = x.get("topics") or []
        if len(tp) < 3:
            continue
        if ("0x" + tp[1][-40:].lower()) != GESTORE_V4:
            continue
        a = "0x" + tp[2][-40:].lower()
        if a in (GESTORE_V4, ZERO):
            continue
        n = CP._numeri(x.get("data", "0x"))
        fuori.setdefault(str(x["transactionHash"]).lower(), []).append(
            (a, (n[0] / 1e18) if n else 0.0))
    return fuori


def provenienza(trasf, indirizzo, blocco_pool):
    """Da dove arrivano i gettoni di questo indirizzo: curva, pool, o un altro indirizzo.

    E' LA DOMANDA DI NICOLO' (10/10): «quando andiamo a vedere chi vende forte, andiamo a vedere
    DOVE hanno comprato: sono entrate prima che venisse promossa, o subito in promozione? Questo
    e' importantissimo.»

    Si guardano i trasferimenti RICEVUTI da questo indirizzo, da chi arrivano e quando rispetto
    alla creazione del pool:
      dal gestore dei pool        -> comprato nel pool, cioe' DOPO il diploma
      dall'indirizzo zero         -> coniato
      prima del blocco del pool   -> veniva dalla curva, cioe' PRIMA della promozione
      da un altro indirizzo       -> ricevuto, e la domanda si sposta su quello
    Il conto e' in quantita' di gettone: qui interessa dove sono NATI i gettoni venduti.
    """
    if trasf is None:
        return {"non_misurabile": "non ho potuto leggere i trasferimenti del gettone"}
    a = indirizzo.lower()
    quote = {"dal_pool": 0.0, "coniato": 0.0, "dalla_curva": 0.0, "da_un_altro_indirizzo": 0.0}
    chi, quanti = {}, 0
    for x in trasf:
        tp = x.get("topics") or []
        if len(tp) < 3 or ("0x" + tp[2][-40:].lower()) != a:
            continue
        quanti += 1
        da = "0x" + tp[1][-40:].lower()
        b = int(x["blockNumber"], 16)
        n = CP._numeri(x.get("data", "0x"))
        q = (n[0] / 1e18) if n else 0.0
        if da == GESTORE_V4:
            quote["dal_pool"] += q
        elif da == ZERO:
            quote["coniato"] += q
        elif b < blocco_pool:
            quote["dalla_curva"] += q
            chi[da] = chi.get(da, 0.0) + q
        else:
            quote["da_un_altro_indirizzo"] += q
            chi[da] = chi.get(da, 0.0) + q
    tot = sum(quote.values())
    if quanti == 0:
        return {"non_misurabile": "nessun trasferimento ricevuto da questo indirizzo"}
    if tot <= 0:
        return {"non_misurabile": f"{quanti} trasferimenti ricevuti ma quantita' illeggibili"}
    fuori = {k: round(v / tot, 4) for k, v in quote.items()}
    fuori["gettoni_ricevuti"] = round(tot, 4)
    fuori["trasferimenti_ricevuti"] = quanti
    if chi:
        # ogni fornitore con la sua etichetta: contratto (infrastruttura) o persona
        fuori["da_chi"] = [[k, round(v, 4), "contratto" if e_un_contratto(k) else "persona"]
                           for k, v in sorted(chi.items(), key=lambda y: -y[1])[:3]]
        da_persone = sum(v for k, v in chi.items() if not e_un_contratto(k))
        fuori["da_una_persona"] = round(da_persone / tot, 4)
        fuori["da_un_contratto"] = round((sum(chi.values()) - da_persone) / tot, 4)
    return fuori


ZERO = "0x" + "0" * 40


def trova_il_crollo(serie):
    """La caduta peggiore: dal massimo corrente al minimo successivo.

    Si cerca il MASSIMO ribasso relativo, non il minimo assoluto: un crollo e' una discesa da un
    picco, e una moneta che parte bassa e resta bassa non e' crollata, e' nata morta.
    """
    if len(serie) < 4:
        return None
    picco = serie[0][1]
    i_picco = 0
    peggio = (0.0, 0, 0)
    for i, (b, p, _, _, _) in enumerate(serie):
        if p > picco:
            picco, i_picco = p, i
        caduta = 1 - p / picco
        if caduta > peggio[0]:
            peggio = (caduta, i_picco, i)
    if peggio[0] < 0.30:          # sotto il 30% non lo chiamiamo crollo
        return None
    return peggio


def main():
    st = json.load(open(STATO))
    noti = st.get("pool_noti") or {}
    db = json.load(open(ARCH)) if os.path.exists(ARCH) else {"versione": VERSIONE, "monete": {}}
    db["versione"] = VERSIONE
    quali = [(t, p) for t, p in st["posizioni"].items()
             if p["stato"] in ("aperta", "chiusa") and p.get("entrata")]
    print(f"DUMP | {len(quali)} posizioni da guardare", flush=True)

    # UN TETTO DI TEMPO, E SI DICE COSA RESTA (10/10). Questo agente legge 600.000 blocchi per
    # moneta e poi chiede l'identita' di centinaia di transazioni: al primo giro completo la
    # maglia e' passata da due minuti a oltre dieci. Una maglia lenta e' una maglia che si salta,
    # e allora i controlli non girano affatto — il rimedio diventa il guasto.
    # Quindi: poche monete per giro, le piu' vecchie prima, e si DICHIARA quante restano. Il
    # ritardo non si nasconde facendo durare il giro di piu' (e' la regola che Astra ha dato
    # sulle sovrapposizioni: se non ci stai, riduci il carico, non allungare il turno).
    PER_GIRO = int(os.environ.get("DUMP_PER_GIRO", "6"))
    MINUTI = float(os.environ.get("DUMP_MINUTI", "6"))
    partenza = time.time()
    da_fare = [x for x in quali if x[0] not in db["monete"]]
    gia_fatte = [x for x in quali if x[0] in db["monete"]]
    quali = da_fare + gia_fatte          # le nuove prima: sono quelle che mancano al conto
    fatte = 0
    saltate = 0
    for tok, pos in quali:
        if fatte >= PER_GIRO or (time.time() - partenza) / 60 > MINUTI:
            saltate += 1
            continue
        pid = pos["pool"]
        info = noti.get(pid) or ["t0", tok, pos["primo_blocco"], None, 18]
        lato, dec = info[0], (info[4] if len(info) > 4 else 18)
        inizio = pos["primo_blocco"]
        gia = db["monete"].get(tok)
        if gia and gia.get("aggiornato_al_blocco", 0) >= min(st.get("ultimo_blocco", 0),
                                                            inizio + ORIZZONTE):
            continue                       # gia' completa: non si rilegge la chain per niente

        ev = CP.log_di_finestra(PP.SWAP_V4, inizio, inizio + ORIZZONTE,
                                indirizzo=GESTORE_V4, secondo=pid)
        if ev is None:
            continue
        serie = []
        for x in ev:
            q = _numeri(x, lato, dec)
            if q:
                serie.append((int(x["blockNumber"], 16), q[0], q[1], q[2],
                              str(x["transactionHash"]).lower()))
        serie.sort()
        if len(serie) < 4:
            continue

        d = {"v": VERSIONE, "pool": pid, "scambi": len(serie),
             "aggiornato_al_blocco": serie[-1][0]}
        cr = trova_il_crollo(serie)
        if cr is None:
            d["crollo"] = None
            d["perche"] = "nessuna caduta oltre il 30% da un picco"
            db["monete"][tok] = d
            fatte += 1
            continue

        caduta, ia, ib = cr
        d["crollo"] = {"profondita": round(caduta, 4),
                       "da_x": round(serie[ia][1] / pos["entrata"], 4),
                       "a_x": round(serie[ib][1] / pos["entrata"], 4),
                       "minuti_dal_mio_ingresso": round((serie[ia][0] - inizio - FINESTRA)
                                                        / 10 / 60, 1),
                       "minuti_di_durata": round((serie[ib][0] - serie[ia][0]) / 10 / 60, 1),
                       "scambi_nel_crollo": ib - ia + 1}

        # I TRASFERIMENTI DEL GETTONE, una lettura sola per moneta: serve a sapere da dove
        # arrivano i gettoni di chi vende (la domanda di Nicolo' del 10/10).
        trasf = trasferimenti_del_gettone(tok, inizio, min(st.get("ultimo_blocco", 0),
                                                           inizio + ORIZZONTE))
        if trasf is not None:
            d["trasferimenti_letti"] = len(trasf)

        # CHI VENDE NEL CROLLO
        vendite = [s for s in serie[ia:ib + 1] if s[3]]
        tagliato = False
        venditore_di = chi_ha_venduto_davvero(trasf)
        falliti_v = 0 if trasf is not None else 1
        quanto = collections.Counter()
        prove = collections.defaultdict(list)
        for b, p, vq, vende, h in vendite:
            righe = venditore_di.get(h) or []
            tg = sum(q for _, q in righe) or 1.0
            for a, q in righe:
                # se la transazione ha piu' mittenti, la valuta si divide in proporzione
                quanto[a] += vq * (q / tg)
                if len(prove[a]) < 3:
                    prove[a].append(h)
        tot = sum(quanto.values()) or 1e-18

        # CHI AVEVA COMPRATO NEL PRIMO MINUTO
        primi = [s for s in serie if s[0] <= inizio + FINESTRA and not s[3]]
        compratore_di = chi_ha_comprato_davvero(trasf)
        comprato = collections.Counter()
        for b, p, vq, vende, h in primi:
            righe = compratore_di.get(h) or []
            tg = sum(q for _, q in righe) or 1.0
            for a, q in righe:
                comprato[a] += vq * (q / tg)

        incrocio = [a for a in quanto if a in comprato]
        d["chi_vende"] = {
            "venditori": len(quanto),
            "quota_del_primo": round(max(quanto.values()) / tot, 4) if quanto else None,
            "quota_dei_primi_tre": round(sum(sorted(quanto.values(), reverse=True)[:3]) / tot, 4)
                                   if quanto else None,
            "valuta_venduta": round(tot, 6),
            "tetto_raggiunto": tagliato,       # dichiarato: oltre MAX_TX non ho chiesto tutto
            "vendite_nella_finestra": len(vendite),
            "transazioni_di_vendita": len(venditore_di),
            "pezzi_senza_risposta": falliti_v,
            "attendibile": falliti_v == 0 and len(quanto) > 0,
            "primi_cinque": [{"indirizzo": a, "venduto": round(v, 6),
                              "aveva_comprato_nel_primo_minuto": round(comprato.get(a, 0.0), 6),
                              "prove": prove[a],
                              # DOVE HA PRESO I GETTONI: la domanda di Nicolo' del 10/10
                              "provenienza": provenienza(trasf, a, inizio)}
                             for a, v in quanto.most_common(3)],
        }
        d["compratori_del_primo_minuto"] = {
            "quanti": len(comprato),
            "quanti_poi_vendono_nel_crollo": len(incrocio),
            "quota_del_venduto_che_e_loro": round(
                sum(quanto[a] for a in incrocio) / tot, 4) if quanto else None,
        }
        db["monete"][tok] = d
        fatte += 1

    json.dump(db, open(ARCH, "w"), indent=1)
    print(f"DUMP | aggiornate {fatte} monete ({len(db['monete'])} in archivio)"
          + (f", {saltate} rimandate al giro prossimo (tetto: {PER_GIRO} monete o "
             f"{MINUTI:.0f} minuti)" if saltate else ""), flush=True)

    # IL REFERTO: la domanda di Nicolo', con i numeri che ha oggi
    # IL DENOMINATORE VERO (10/10). La prima versione stampava «su 27 crolli» un numero che
    # era calcolato su 4: gli altri 23 avevano la ricerca dei venditori fallita. Un numero col
    # denominatore sbagliato e' la cosa che Nicolo' mi ha chiesto di non fare piu'.
    tutti = [v for v in db["monete"].values() if v.get("crollo")]
    con = [v for v in tutti if v.get("chi_vende", {}).get("attendibile")]
    print(f"DUMP | crolli trovati: {len(tutti)} | con i venditori identificati davvero: "
          f"{len(con)}", flush=True)
    if con:
        q1 = [v["chi_vende"]["quota_del_primo"] for v in con
              if v.get("chi_vende", {}).get("quota_del_primo") is not None]
        inc = [v["compratori_del_primo_minuto"]["quota_del_venduto_che_e_loro"]
               for v in con if v.get("compratori_del_primo_minuto", {}).get(
                   "quota_del_venduto_che_e_loro") is not None]
        import statistics
        if q1:
            print(f"DUMP | su {len(con)} crolli ATTENDIBILI: il venditore piu' grosso fa in mediana "
                  f"il {statistics.median(q1)*100:.0f}% del venduto", flush=True)
        if inc:
            print(f"DUMP | e in mediana il {statistics.median(inc)*100:.0f}% del venduto viene "
                  f"da chi aveva comprato nel primo minuto", flush=True)
        print("   (con pochi crolli sono indizi, non conclusioni: servono 30 casi)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
