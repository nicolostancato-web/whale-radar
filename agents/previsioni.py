"""PREVISIONI — scrive oggi cio' che andra' giudicato domani.

E' il pezzo che fa partire l'orologio del loop 1, e parte PRIMA che la macchina sia rifinita.

PERCHE' ADESSO E NON QUANDO SARA' TUTTO PRONTO. Le previsioni non si accumulano da sole: si
accumulano da quando si comincia a scriverle. Ogni giorno passato ad aspettare la macchina
perfetta e' un giorno di previsioni che non avremo mai — e siccome ne servono centinaia per dire
qualcosa, quel giorno non si recupera.
Il rigore non cambia: le ipotesi sono scritte prima (in `IPOTESI.md`, con la loro condizione di
morte) e il voto arriva dopo, da solo. Cambia solo quando parte l'orologio.

COSA NON FA. Non compra niente, non decide niente, non tocca nessuna strategia. Scrive righe in un
registro. Il costo di sbagliarsi e' una riga sbagliata in un file.

LE CONDIZIONI SI GUARDANO AL MOMENTO DELLA DECISIONE, e solo quelle osservabili allora: liquidita',
numero di indirizzi distinti che hanno comprato, se qualcuno e' gia' riuscito a uscire. Niente che
si sappia solo dopo — e' il difetto che ha contaminato fra il 12% e il 31% della popolazione
vecchia.

IL PREZZO DI ENTRATA NON E' QUELLO DEL SEGNALE. La nostra latenza di raccolta, misurata, e' di 1-3
secondi mediani e fino a 15 minuti. Si entra a cio' che c'e' DOPO il ritardo, e il ritardo si
scrive nel record cosi' chi giudica non deve fidarsi.
"""
import gzip
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registro_segnali as R           # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
FINESTRA_ORE = float(os.environ.get("FINESTRA_ORE", 6))
LATENZA = int(os.environ.get("LATENZA_S", 3))
MAX_PER_GIRO = int(os.environ.get("MAX_PER_GIRO", 60))
# si guardano i pool toccati nell'ultima ora: quelli vivi adesso, non l'archivio
FRESCHEZZA = int(os.environ.get("FRESCHEZZA_S", 3600))
ORE_ATTESA = float(os.environ.get("ORE_ATTESA", 2))        # come nello storico: 2 ore dal primo scambio
# oltre questo ritardo il pool ha passato la sua finestra e non si annota: annotarlo sarebbe
# rispondere a una domanda diversa da quella della regola
MASSIMO_RITARDO = int(os.environ.get("MASSIMO_RITARDO_S", 3 * 3600))


RPC = {"base": "https://mainnet.base.org",
       "robinhood": "https://rpc.mainnet.chain.robinhood.com"}
SYNC = "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"


def _chiedi(metodo, params, tentativi=3):
    url = RPC.get(CHAIN)
    if not url:
        return None
    b = json.dumps({"jsonrpc": "2.0", "method": metodo,
                    "params": params, "id": 1}).encode()
    attesa = 2
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=b,
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=30) as x:
                return json.load(x).get("result")
        except Exception:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
    return None


def riserve_dalla_catena(pool, entro_blocchi=3000):
    """La liquidita' CHIESTA ALLA CATENA adesso, per i pool che l'archivio non copre.

    PERCHE' (23/09). Il raccoglitore di riserve va all'indietro nel tempo, ma i pool su cui si
    fanno le previsioni sono NUOVI: per loro la liquidita' non l'ha ancora presa nessuno. Misurato:
    presente in 106 previsioni su 676 di base e 36 su 1.147 di robinhood — troppo poco per provare
    se la liquidita' conti qualcosa, ed e' l'unico campo che non abbiamo mai usato.
    Una chiamata per pool, solo quando l'archivio non ce l'ha.
    """
    # I POOL V4 NON HANNO UN INDIRIZZO (23/09). Il loro identificativo e' 32 byte, non 20: non sono
    # contratti, vivono dentro un unico contratto condiviso e non emettono l'evento che porta le
    # riserve. Il nodo risponde «invalid address: hex has invalid length 32». Sono l'83% di
    # robinhood e il 48% di base — ed e' la vera ragione per cui la liquidita' era al 6% e al 33%,
    # non una raccolta lenta.
    # NON e' un «non si puo' avere»: si legge interrogando il contratto che li contiene. E' un
    # lavoro a se', e finche' non c'e' si dichiara il motivo invece di restituire un silenzio.
    if len(pool) != 42:
        return None
    punta = _chiedi("eth_blockNumber", [])
    if not punta:
        return None
    alto = int(punta, 16)
    log = _chiedi("eth_getLogs", [{"fromBlock": hex(max(1, alto - entro_blocchi)),
                                   "toBlock": hex(alto),
                                   "address": pool,
                                   "topics": [[SYNC]]}])
    if not log:
        return None
    d = (log[-1].get("data") or "0x")[2:]
    if len(d) < 128:
        return None
    try:
        return int(d[:64], 16)
    except Exception:
        return None


def riserve(pool):
    """La liquidita' piu' recente che conosciamo per questo pool, se la conosciamo."""
    p = f"data/multichain/{CHAIN}/riserve/{pool}.jsonl.gz"
    if os.path.exists(p):
        try:
            rr = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
            rr = [x for x in rr if x.get("r0")]
            if rr:
                return rr[-1]["r0"]
        except Exception:
            pass
    return riserve_dalla_catena(pool)


def gia_annotati(entro_ore=12):
    """I pool gia' annotati di recente: non si riannotano.

    UN POOL GUARDATO OTTO VOLTE NON E' OTTO PROVE (23/09). Il primo giro notturno ha prodotto
    5.733 previsioni su soli 693 pool distinti — otto per pool, perche' i pool attivi restano
    attivi e venivano ripresi a ogni passaggio.
    Le condizioni di morte delle ipotesi contano i POOL DISTINTI, quindi accumulare ripetizioni
    non avvicina di un passo il momento in cui potremo dire qualcosa: riempie il registro e basta.
    Meglio poche righe su tanti pool che tante righe su pochi."""
    fuori = {}
    if not os.path.exists(R.REG):
        return fuori
    limite = time.time() - entro_ore * 3600
    try:
        for l in open(R.REG):
            if not l.strip():
                continue
            r = json.loads(l)
            if (r.get("annotato") or 0) >= limite:
                fuori[(r["chain"], r["pool"])] = True
    except Exception:
        pass
    return fuori


def main():
    ora = time.time()
    visti = gia_annotati()
    scritti = 0
    senza_riserve = 0
    for sub in ("vivo", "storico"):
        d = f"data/multichain/{CHAIN}/{sub}"
        if not os.path.isdir(d) or scritti >= MAX_PER_GIRO:
            continue
        for fn in os.listdir(d):
            if scritti >= MAX_PER_GIRO:
                break
            pool = fn.split(".")[0]
            if (CHAIN, pool.lower()) in visti:
                continue                    # gia' annotato di recente: si cercano pool nuovi
            try:
                rr = [json.loads(l) for l in gzip.open(os.path.join(d, fn), "rt") if l.strip()]
            except Exception:
                continue
            rr = [x for x in rr if x.get("ts") and x.get("w") and x.get("a0") and x.get("a1")]
            if len(rr) < 10:
                continue
            rr.sort(key=lambda x: x["ts"])
            # NON si chiede piu' che sia vivo ADESSO: si chiede che abbia circa due ore di vita.
            # Chiedere entrambe le cose selezionerebbe i pool sopravvissuti, che e' una scelta
            # basata sul futuro.

            # IL MOMENTO DELLA DECISIONE DEVE ESSERE LO STESSO DELLA REGOLA (23/09 sera).
            # Errore mio, grave: la prova in avanti decideva all'ULTIMO scambio — cioe' «adesso» —
            # e contava compratori e scambi di TUTTA la vita del token. Ma la regola dice
            # «a due ore dal primo scambio, con cio' che si e' visto in quelle due ore».
            # Misurato: solo l'1% delle decisioni cadeva attorno alle 2 ore, la mediana era a 69
            # ore, il 75% oltre un giorno. La prova non stava esaminando la regola: stava
            # esaminando «token vecchi con molti compratori», che e' un'altra cosa e per giunta
            # ovviamente peggiore, perche' a quel punto il movimento e' finito.
            # Quindi il verdetto del 23/09 sera NON vale, in nessuno dei due versi: la regola non
            # e' bocciata e non e' promossa. E' da provare.
            t_primo = rr[0]["ts"]
            t_dec = t_primo + ORE_ATTESA * 3600
            if ora < t_dec:
                continue                    # non ha ancora due ore: si aspetta
            if ora - t_dec > MASSIMO_RITARDO:
                continue                    # troppo tardi per questo pool: la finestra e' passata
            prima = [x for x in rr if x["ts"] <= t_dec]
            if len(prima) < 5:
                continue                    # come nello storico: servono almeno 5 scambi
            compratori = len({x["w"].lower() for x in prima})
            scambi = len(prima)
            # qualcuno e' gia' riuscito a uscire? (i due versi del segno di a0)
            versi = set()
            for x in prima:
                try:
                    versi.add(1 if float(x["a0"]) > 0 else -1)
                except Exception:
                    pass
            vendibile = len(versi) > 1
            liq = riserve(pool)
            if liq is None:
                senza_riserve += 1
                # si distingue «non l'abbiamo presa» da «con questo metodo non si prende»
                motivo_liq = "v4_senza_indirizzo" if len(pool) != 42 else "non_raccolta"
            else:
                motivo_liq = None
            p = R._prezzo(prima[-1])      # il prezzo a DUE ORE, non quello di adesso
            if not p:
                continue

            # H4 — LA SUCCESSIONE DI PATTERN, misurata sullo storico il 23/09 e scritta qui
            # PRIMA di vedere un solo esito in avanti. Le soglie sono quelle trovate, non ritoccate.
            # Si annota OGNI pool, scelto o no: i non scelti sono il gruppo di controllo, e senza di
            # loro la prova non dimostra niente (il mercato intero si muove del 20-60% in un'ora,
            # quindi un numero assoluto non dice nulla — conta solo la differenza fra i due gruppi).
            SOGLIE = {"robinhood": (11, 73), "base": (8, 71)}
            sc, ss = SOGLIE.get(CHAIN, (11, 73))
            scelto = compratori >= sc and scambi >= ss

            nota = json.dumps({"compratori": compratori, "scambi": scambi,
                               "scelto_H4": scelto, "soglie_H4": [sc, ss],
                               "perche_manca_liquidita": motivo_liq,
                               "vendibile": vendibile, "liquidita": liq,
                               "rapporto_ind_scambi": round(compratori / max(1, scambi), 3)})
            # una previsione per ipotesi: cosi' ognuna ha il suo conto e la sua morte
            # H5, non piu' H4: la prova precedente misurava un'altra cosa (decideva a 69 ore di
            # mediana invece che a 2). Le previsioni vecchie restano nel registro come sono — non
            # si riscrive il passato — ma non vanno mescolate con queste.
            for ip in ("H1:liquidita", "H2:compratori_distinti", "H3:vendibilita",
                       "H5:successione_a_2h" + ("/scelto" if scelto else "/controllo")):
                R.annota(CHAIN, pool, ip, t_dec, FINESTRA_ORE, p, LATENZA, nota)
            scritti += 1

    print(f"PREVISIONI | {CHAIN}: {len(visti)} gia' annotati di recente, saltati | "
          f"{scritti} pool NUOVI osservati, {scritti*3} previsioni scritte "
          f"(3 ipotesi ciascuno)", flush=True)
    if senza_riserve:
        print(f"   {senza_riserve} senza liquidita' nota: la condizione H1 su quelli non si potra'"
              f" giudicare, ed e' scritto nel record invece che indovinato", flush=True)
    # e intanto si chiudono quelle scadute: il voto arriva da solo
    R.chiudi()
    R.rapporto()


if __name__ == "__main__":
    main()
