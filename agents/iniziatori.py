"""Chi ha DAVVERO firmato ogni scambio: l'iniziatore della transazione.

PERCHE' (25/09). Il campo che usavamo come «chi ha fatto lo scambio» registra, nell'81% dei casi,
`v4:sender` — cioe' **il router**, non la persona. La prova: un solo indirizzo fa il 42,6% di tutti
gli scambi, e ce ne sono 2.001 distinti su 44.804 operazioni. Nessun trader si comporta cosi'.

Conseguenza: tutto cio' che abbiamo chiamato «compratori distinti», «portafogli nuovi», «scambi per
portafoglio» misurava PORTE, non gente. E l'attribuzione economica — chi crea, chi finanzia chi
crea, se le vendite sono di compratori indipendenti o di indirizzi del creatore — era impossibile.

Il campo `from` della transazione e' l'iniziatore vero. Costa una chiamata per scambio, ma a gruppi
di 50 si arriva a 150 al secondo.

DUE LEZIONI GIA' PAGATE, applicate qui:
 1. **Le risposte di un gruppo si abbinano per CONTENUTO, mai per posizione.** Il 22/09 un nodo
    restituiva risposte riordinate e il 17% dei dati di base e' finito sbagliato. Qui si abbina
    sull'hash che torna dentro il risultato.
 2. **«Il nodo non risponde» non e' «non esiste».** Chi non risponde non si scrive: si riprova.
"""
import gzip
import gzip
import json
import os
import sys
import time
import urllib.request

CHAIN = os.environ.get("CHAIN", "robinhood")
RPC = {"base": "https://mainnet.base.org",
       "robinhood": "https://rpc.mainnet.chain.robinhood.com"}
# base RIFIUTA le richieste a gruppi (25/09: 23.600 tentativi, ZERO risposte). robinhood le accetta
# fino a 50. Dove i gruppi non passano si va a una per volta: lento ma funziona.
GRUPPO = int(os.environ.get("GRUPPO", {"robinhood": 50, "base": 1}.get(
    os.environ.get("CHAIN", "robinhood"), 50)))
BUDGET = int(os.environ.get("BUDGET_SEC", 1500))
FUORI = f"data/multichain/{CHAIN}/iniziatori.json.gz"
# UN FILE PER FETTA (2/10): con un nome solo, quattro lavori paralleli si sovrascriverebbero il
# lavoro a vicenda — esattamente l'incidente del 25/09, quando base scese da 12.581 a 8.052.
_F = os.environ.get("FETTA", "")
# quante transazioni aveva mai fatto chi ha firmato, al momento in cui ha firmato
NONCE = {}
F_NONCE = (f"data/multichain/{CHAIN}/nonce_nuovi"
           + (f"_{os.environ.get('FETTA','')}" if os.environ.get("FETTA", "") not in ("", "0") else "")
           + ".json")

NUOVI = (f"data/multichain/{CHAIN}/iniziatori_nuovi"
         + (f"_{_F}" if _F not in ("", "0") else "") + ".json")
ORE_UTILI = float(os.environ.get("ORE_UTILI", 3))   # servono gli scambi PRIMA della decisione


def chiedi(hash_list, tentativi=4):
    """Torna {hash: from}. None se il nodo non ha risposto per niente."""
    corpo = [{"jsonrpc": "2.0", "method": "eth_getTransactionByHash",
              "params": [h], "id": i} for i, h in enumerate(hash_list)]
    b = json.dumps(corpo).encode()
    attesa = 3
    for k in range(tentativi):
        try:
            r = urllib.request.Request(RPC[CHAIN], data=b,
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=60) as x:
                d = json.load(x)
            if not isinstance(d, list):
                return None
            fuori = {}
            for e in d:
                res = e.get("result")
                if res and res.get("hash") and res.get("from"):
                    # ABBINAMENTO PER CONTENUTO: l'hash sta dentro il risultato, non ci si fida
                    # dell'ordine ne' dell'id. Lezione del 22/09, 17% dei dati sbagliati.
                    fuori[res["hash"].lower()] = res["from"].lower()
                    # IL NONCE ERA GIA' NELLA RISPOSTA E LO BUTTAVAMO (2/10). Ogni transazione
                    # porta il numero di transazioni che il suo firmatario aveva MAI fatto prima.
                    # Costa zero chiamate in piu': e' dentro la stessa risposta che chiediamo
                    # dal 25/09, e per sei giorni l'abbiamo scartata.
                    # Vale molto: nonce 0-5 e' un portafoglio nato per quella moneta — l'insider
                    # col wallet nuovo di cui parla Nicolo'. Nonce 385.878 (misurato oggi su un
                    # primo compratore vero) e' una macchina industriale: e' anche il filtro
                    # anti-trash chiesto mesi fa, misurato invece che intuito.
                    # Va in un file SEPARATO: aggiungere un campo a `iniziatori.json.gz`
                    # romperebbe tutti i pezzi che lo leggono, e una migrazione non si fa per
                    # un dato che si puo' affiancare.
                    try:
                        NONCE[res["hash"].lower()] = int(res["nonce"], 16)
                    except Exception:
                        pass
            return fuori
        except Exception:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
    return None


def main():
    t0 = time.time()
    noti = {}
    if os.path.exists(FUORI):
        try:
            noti = json.load(gzip.open(FUORI,"rt")).get("da", {})
        except Exception:
            noti = {}
    # SOLO CIO' CHE SERVE (25/09). Prendere tutta la storia sono 2,4 milioni di transazioni:
    # quaranta ore. Ma per l'attribuzione servono solo gli scambi PRIMA della decisione dei pool
    # che analizziamo davvero — chi ha comprato per primo e chi ha venduto prima che entrassimo.
    # Restringendo si passa da 2,4 milioni a poche centinaia di migliaia.
    # IL FILE DELLE DECISIONI DEVE STARE SUL REPO (25/09). La prima versione leggeva
    # `insieme_<chain>.jsonl`, che esiste solo sul Mac: sul cloud mancava, la restrizione non si
    # applicava e la corsia partiva su 2,4 milioni di transazioni invece di 603 mila.
    # Ottavo caso in cinque giorni di «funziona da me»: ora si pubblica un file leggero apposta.
    voluti = {}
    dec = f"data/loop1/decisioni_{CHAIN}.json"
    if os.path.exists(dec):
        try:
            voluti = json.load(open(dec))
        except Exception:
            voluti = {}
    if not voluti:
        print(f"INIZIATORI | {CHAIN}: manca {dec}, lavoro su TUTTA la storia "
              f"(molto piu' lento)", flush=True)
    # IL FRENO ERA SULLA PARTE CHE CREDEVO LENTA (2/10). Il budget sotto guarda solo la fase
    # delle CHIAMATE. Ma prima delle chiamate c'e' questa scansione, che apre ogni file di
    # scambi di ogni pool, e non aveva nessun limite: con decine di migliaia di file si
    # consumavano tutti i 35 minuti concessi QUI, il giro veniva annullato e la corsia non ha
    # consegnato nulla per giorni — zero giri riusciti su dieci.
    # E' la stessa lezione di ieri sera in un punto nuovo: un budget che non copre la parte
    # piu' lenta non e' un budget. Qui la scansione si ferma al 40% del tempo, perche' il 60%
    # serve a chiamare e a salvare. Meglio un elenco parziale consegnato che uno completo
    # buttato.
    QUOTA_SCANSIONE = float(os.environ.get("QUOTA_SCANSIONE", 0.40))
    da_fare = []
    fermata = False
    # ANCHE «trades» (2/10). Questa scansione guardava solo `storico` e `vivo`, mentre
    # `agents/insider.py` — che usa il risultato — legge anche `trades`. I pool che stanno solo
    # in `trades` avevano gli scambi e NESSUNA persona risolta: e' una parte del motivo per cui
    # il passato dei compratori e' noto solo per il 40% dei pool.
    # Due pezzi che leggono liste di cartelle diverse sono due pezzi che non parlano.
    for sub in ("storico", "vivo", "trades"):
        if fermata:
            break
        d = f"data/multichain/{CHAIN}/{sub}"
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if time.time() - t0 > BUDGET * QUOTA_SCANSIONE:
                print(f"INIZIATORI | scansione fermata a {(time.time()-t0)/60:.0f} min "
                      f"({len(da_fare):,} transazioni da fare trovate finora): il resto del "
                      f"budget serve per chiamare e salvare", flush=True)
                fermata = True
                break
            pool = fn.split(".")[0]
            if voluti and pool not in voluti:
                continue                       # pool che non analizziamo: non serve
            try:
                rr = [json.loads(l) for l in gzip.open(os.path.join(d, fn), "rt") if l.strip()]
            except Exception:
                continue
            rr = [y for y in rr if y.get("ts") and y.get("tx")]
            if not rr:
                continue
            rr.sort(key=lambda y: y["ts"])
            lim = voluti.get(pool, rr[0]["ts"] + ORE_UTILI * 3600)
            for y in rr:
                if y["ts"] > lim:
                    break                      # oltre il momento della decisione non serve
                h = y["tx"].lower()
                if h not in noti:
                    da_fare.append(h)
    da_fare = list(dict.fromkeys(da_fare))
    # IL LAVORO SI DIVIDE FRA LAVORI PARALLELI (2/10). Dopo che l'elenco e' passato da 9.009 a
    # 46.628 pool, al ritmo misurato (circa 16.000 transazioni per giro) servirebbero decine di
    # giri, cioe' giorni, e il filone insider resterebbe fermo su un quinto dei dati.
    # Ogni lavoro prende una FETTA diversa dello stesso elenco: `da_fare[FETTA::FETTE]`. Niente
    # si sovrappone, niente va perso, e nessuno ha bisogno di sapere cosa fanno gli altri —
    # l'unico punto in cui si incontrano e' la fusione, che unisce invece di sovrascrivere.
    # Gli endpoint sono pubblici e gratuiti: il rischio non e' il costo, e' la strozzatura del
    # nodo. Per questo si parte da quattro fette e si guarda il contatore «non risposti», che
    # dice quando il nodo smette di rispondere.
    FETTE = max(1, int(os.environ.get("FETTE", 1)))
    FETTA = int(os.environ.get("FETTA", 0)) % FETTE
    if FETTE > 1:
        tutte = len(da_fare)
        da_fare = da_fare[FETTA::FETTE]
        print(f"INIZIATORI | {CHAIN}: fetta {FETTA+1} di {FETTE} — {len(da_fare):,} "
              f"transazioni su {tutte:,}", flush=True)
    print(f"INIZIATORI | {CHAIN}: {len(noti):,} gia' noti, {len(da_fare):,} da fare", flush=True)
    presi = falliti = 0
    solo_nuovi = {}
    for i in range(0, len(da_fare), GRUPPO):
        if time.time() - t0 > BUDGET:
            break
        gruppo = da_fare[i:i + GRUPPO]
        d = chiedi(gruppo)
        if d is None:
            falliti += len(gruppo)
            time.sleep(3)
            continue
        noti.update(d)
        solo_nuovi.update(d)
        presi += len(d)
        if presi and presi % 2000 < GRUPPO:
            os.makedirs(os.path.dirname(FUORI), exist_ok=True)
            json.dump(solo_nuovi, open(NUOVI, "w"))
            print(f"INIZIATORI | {presi:,} presi", flush=True)
        time.sleep(0.05)
    # NON si riscrive il file intero (25/09). Le due chain girano insieme e, salvando l'intero
    # file, chi arriva secondo cancellava il lavoro del primo: base e' SCESA da 12.581 a 8.052.
    # Adesso si scrivono solo i NUOVI in un file a parte, e la fusione avviene DOPO il pull,
    # quando si ha davanti anche il lavoro dell'altro.
    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    json.dump(solo_nuovi, open(NUOVI, "w"))
    if NONCE:
        json.dump(NONCE, open(F_NONCE, "w"))
        bassi = sum(1 for n in NONCE.values() if n <= 5)
        alti = sum(1 for n in NONCE.values() if n >= 10000)
        print(f"INIZIATORI | {CHAIN}: nonce raccolti per {len(NONCE):,} transazioni "
              f"({bassi:,} da portafogli nuovissimi con nonce<=5, {alti:,} da macchine con "
              f"nonce>=10.000) — costo aggiuntivo: ZERO chiamate", flush=True)
    v = time.time() - t0
    print(f"INIZIATORI | {CHAIN}: {presi:,} nuovi in {v:.0f}s ({presi/max(v,1):.0f}/s) | "
          f"totale {len(noti):,} | non risposti {falliti:,} | "
          f"indirizzi distinti {len(set(noti.values())):,}", flush=True)


if __name__ == "__main__":
    main()
