"""DOPO IL DIPLOMA: le serie di prezzo nel pool, e la prova con la cassaforte.

== PERCHE' (7/10/2026, notte) ==

La curva e' chiusa come strada: tutte le regole giocabili perdono. Dopo il diploma, invece, il
quadro e' quello classico — su 20 monete il prezzo finisce a **0,054x** (meno 95%) in mediana, 19
su 20 sotto il prezzo di partenza, ma **2 su 20 superano 10x** (23x e 27x). Le X stanno qui.

Una prima occhiata dava regole promettenti (+104% medio per moneta vendendo a 10x e tagliando a
0,5x). **Non vale niente**, e il motivo e' scritto qui perche' non lo dimentichi nessuno:
30 monete, la media poggiava su 5 vincenti, e avevo provato SETTE regole sugli stessi dati.
Cercando fra molte configurazioni si trova sempre qualcosa.

Quindi questo agente fa tre cose che la prima occhiata non faceva:

1. **SALVA le serie su disco.** Rileggerle dalla chain a ogni analisi costa minuti e invita a
   provare una regola in piu' «tanto che ci siamo»: e' esattamente come si scambia rumore per
   segnale. Le serie si accumulano una volta e si riusano.
2. **Divide per DATA, non a caso.** La prima metà nel tempo serve a scegliere; la seconda si
   guarda UNA volta sola. Dividere a caso lascerebbe che il futuro informi il passato.
3. **Confronta col caso.** Una regola che rende meno di «compro e tengo» o di un'entrata casuale
   non e' una strategia: e' rumore con una storia addosso.

E rifiuta di concludere se la cassaforte ha meno di 40 monete: su meno non si distingue niente.

== I DUE DIFETTI GIA' PAGATI, scritti dove possono tornare ==

- **un pool per volta**: la stessa moneta ha pool in valute diverse; unendo le serie il prezzo
  salta fra due scale e si ottiene una salita monotona su TUTTE le monete (mediana 17x). Un
  risultato troppo uniforme e' un difetto, non una scoperta.
- **i lati non si indovinano**: se il gettone sta su `t1`, il suo importo e' `a1`. Prendendo `a0`
  si calcola il rapporto fra due merci diverse, che deriva piano e somiglia a un prezzo.
"""
import glob
import gzip
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
# TESTO SEMPLICE, NON COMPRESSO (7/10 notte). L'archivio era un .jsonl.gz aperto in aggiunta:
# ho interrotto il processo a metà scrittura e il file e' diventato ILLEGGIBILE per intero
# («Compressed file ended before the end-of-stream marker»), perdendo anche cio' che c'era.
# Un archivio che si accumula deve sopravvivere a un'interruzione: il testo semplice perde al
# massimo l'ultima riga, il gzip perde tutto. Lo spazio risparmiato non vale il rischio.
SERIE = os.environ.get("SERIE", f"{BASE}/serie_pool.jsonl")
FUORI = os.environ.get("FUORI", f"{BASE}/dopo_il_diploma.json")
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
ZERO = "0x" + "0" * 40
QUANTE = int(os.environ.get("QUANTE", "300"))
BUDGET = int(os.environ.get("BUDGET_SEC", "2400"))
MIN_SCAMBI = 40
MIN_CASSAFORTE = 40
COSTO = 1.02                 # 1% entrata + 1% uscita, misurati
VERSIONE = 1


def finestre(prezzi, k=10, passo=5):
    """Mediane su finestre di 10 scambi: un singolo scambio non e' un prezzo."""
    return [statistics.median(prezzi[i:i + k]) for i in range(0, len(prezzi) - k + 1, passo)]


def serie_di(tok, pool_di, L, bn):
    """La serie di prezzo nel pool in NATIVO. None se non leggibile.

    `bn` arriva da fuori: chiederlo per OGNI moneta (300 volte) mi faceva respingere dall'RPC
    con 429 — mi limitavo da solo con una chiamata che non serviva. Una richiesta inutile
    ripetuta non e' inefficienza: e' la causa del fallimento.
    """
    nato = L[tok]["blocco"]
    migliore = None
    for pid, lato_tok, v in pool_di.get(tok, ()):
        altro = (v.get("t1" if lato_tok == "t0" else "t0") or "").lower()
        if altro != ZERO:
            continue                 # un pool per volta, e in una valuta sola
        if len(pid) - 2 == 64:
            ev = CP.log_di_finestra(PP.SWAP_V4, nato, min(bn, nato + 9999999),
                                    indirizzo=GESTORE_V4, secondo=pid)
        else:
            ev = CP.log_di_finestra(PP.SWAP_V3, nato, min(bn, nato + 9999999), indirizzo=pid)
        if ev is None:
            return None              # mezza lettura non si usa
        s = []
        for x in ev:
            n = CP._numeri(x.get("data", "0x"))
            if len(n) < 2:
                continue
            a0 = n[0] - (1 << 256) if n[0] >= (1 << 255) else n[0]
            a1 = n[1] - (1 << 256) if n[1] >= (1 << 255) else n[1]
            qt = a1 if lato_tok == "t1" else a0      # il gettone sta dove dice il registro
            qq = a0 if lato_tok == "t1" else a1
            if qt == 0 or qq == 0:
                continue
            vq = abs(qq) / 1e18
            if vq < 1e-6:
                continue                              # scambi infinitesimi: rumore
            s.append((int(x["blockNumber"], 16), int(x.get("logIndex", "0x0"), 16),
                      vq / (abs(qt) / 1e18)))
        if s and (migliore is None or len(s) > len(migliore)):
            migliore = s
    if not migliore or len(migliore) < MIN_SCAMBI:
        return []
    migliore.sort()
    return finestre([p for _, _, p in migliore])


def accumula():
    # UNA SOLA LIBRERIA DI LETTURA (10/10, prescrizione di Astra). Questo file era un
    # oggetto unico da 52 MB con 675.145 voci: per aggiungere un lancio si riscriveva
    # tutto. Ora sta a righe, e `archivio.leggi` nasconde quale forma c'e': se un giorno
    # cambia di nuovo, cambia li' e non in dieci script con dieci interpretazioni.
    import archivio as AR
    _test, _voci = AR.leggi("curva_lanci")
    dl = dict(_test)
    dl["da"] = _voci
    L = dl["da"]
    pool_di = {}
    for pid, v in _coppie().items():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != ZERO and a in L:
                pool_di.setdefault(a, []).append((pid.lower(), lato, v))
    fatte = set()
    if os.path.exists(SERIE):
        for l in open(SERIE):
            if not l.strip():
                continue
            try:
                fatte.add(json.loads(l)["moneta"])
            except Exception:
                pass          # l'ultima riga di un'interruzione: si salta, non si cade
    print(f"DIPLOMA | {len(pool_di):,} monete diplomate, {len(fatte):,} serie gia' in archivio",
          flush=True)
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("DIPLOMA | la chain non dice il blocco attuale: non comincio.")
        return
    t0 = time.time()
    nuove = vuote = 0
    with open(SERIE, "a", buffering=1) as f:
        for tok in sorted(pool_di):
            if tok in fatte or len(fatte) + nuove >= QUANTE:
                continue
            if time.time() - t0 > BUDGET:
                print("DIPLOMA | finito il tempo: mi fermo, l'archivio resta.", flush=True)
                break
            s = serie_di(tok, pool_di, L, bn)
            if s is None:
                continue                 # la chain non ha risposto: si riprova al giro dopo
            if not s:
                vuote += 1
                f.write(json.dumps({"v": VERSIONE, "moneta": tok, "nato": L[tok]["blocco"],
                                    "serie": []}) + "\n")
                nuove += 1
                continue
            f.write(json.dumps({"v": VERSIONE, "moneta": tok, "nato": L[tok]["blocco"],
                                "serie": [round(p, 18) for p in s]}) + "\n")
            nuove += 1
            time.sleep(0.4)      # respiro fra le monete: senza, l'RPC risponde 429
            if nuove % 20 == 0:
                print(f"DIPLOMA | {nuove} serie nuove ({vuote} troppo corte), "
                      f"{int(time.time()-t0)}s", flush=True)
    print(f"DIPLOMA | aggiunte {nuove} serie ({vuote} troppo corte)", flush=True)


REGOLE = [("vendo a 2x", 2, None), ("vendo a 3x", 3, None), ("vendo a 5x", 5, None),
          ("vendo a 10x", 10, None), ("vendo a 5x, taglio a 0,5x", 5, 0.5),
          ("vendo a 10x, taglio a 0,5x", 10, 0.5), ("vendo a 10x, taglio a 0,3x", 10, 0.3),
          ("tengo fino alla fine", 10 ** 9, None)]


def applica(serie, obiettivo, stop):
    e = serie[0]
    for p in serie[1:]:
        if p / e >= obiettivo:
            return obiettivo * e / (e * COSTO) - 1
        if stop and p / e <= stop:
            return stop * e / (e * COSTO) - 1
    return serie[-1] / (e * COSTO) - 1


def misura():
    righe = []
    if not os.path.exists(SERIE):
        print("DIPLOMA | nessun archivio di serie: niente da misurare.")
        return 0
    for l in open(SERIE):
        if not l.strip():
            continue
        try:
            x = json.loads(l)
        except Exception:
            continue
        if x.get("v") == VERSIONE and len(x.get("serie") or []) >= 3:
            righe.append(x)
    righe.sort(key=lambda x: x["nato"])          # PER DATA: il futuro non informa il passato
    meta = len(righe) // 2
    scelta, cassaforte = righe[:meta], righe[meta:]
    print(f"\nDIPLOMA | {len(righe)} serie usabili: {len(scelta)} per scegliere, "
          f"{len(cassaforte)} in cassaforte", flush=True)
    if len(cassaforte) < MIN_CASSAFORTE:
        print(f"DIPLOMA | la cassaforte ha {len(cassaforte)} monete (minimo {MIN_CASSAFORTE}): "
              f"NON scelgo e NON concludo. Servono piu' serie.")
        return 0

    print(f"\n{'regola':30} {'medio':>9} {'mediana':>9} {'vinte':>8}")
    tabella = {}
    for nome, ob, st in REGOLE:
        es = [applica(x["serie"], ob, st) for x in scelta]
        tabella[nome] = {"medio": round(statistics.mean(es), 4),
                         "mediana": round(statistics.median(es), 4),
                         "vinte": sum(1 for v in es if v > 0), "su": len(es)}
        print(f"{nome:30} {100*statistics.mean(es):+8.1f}% {100*statistics.median(es):+8.1f}% "
              f"{tabella[nome]['vinte']:4}/{len(es)}")
    # SI SCEGLIE SULLA MEDIANA, non sulla media: la media di 30 serie e' decisa da due vincenti,
    # e scegliere su di essa significa scegliere il caso piu' fortunato del campione.
    migliore = max(REGOLE, key=lambda r: statistics.median(
        [applica(x["serie"], r[1], r[2]) for x in scelta]))
    nome, ob, st = migliore
    print(f"\nDIPLOMA | scelta sulla prima metà: «{nome}»", flush=True)

    es = [applica(x["serie"], ob, st) for x in cassaforte]
    med, mdn = statistics.mean(es), statistics.median(es)
    # IL CONFRONTO: tenere e basta. Una regola che non batte questo non e' una strategia.
    tieni = [applica(x["serie"], 10 ** 9, None) for x in cassaforte]
    print(f"DIPLOMA | SULLA CASSAFORTE (guardata una volta sola): medio {100*med:+.1f}%, "
          f"mediana {100*mdn:+.1f}%, vinte {sum(1 for v in es if v>0)}/{len(es)}")
    print(f"DIPLOMA | per confronto, tenere e basta: medio {100*statistics.mean(tieni):+.1f}%, "
          f"mediana {100*statistics.median(tieni):+.1f}%")
    verdetto = ("REGGE" if mdn > 0 and mdn > statistics.median(tieni) else "NON REGGE")
    print(f"DIPLOMA | {verdetto}")
    json.dump({"chain": CHAIN, "serie_usabili": len(righe), "scelta": len(scelta),
               "cassaforte": len(cassaforte), "sulla_prima_meta": tabella,
               "regola_scelta": nome,
               "cassaforte_esito": {"medio": round(med, 4), "mediana": round(mdn, 4),
                                    "vinte": sum(1 for v in es if v > 0)},
               "tenere_e_basta": {"medio": round(statistics.mean(tieni), 4),
                                  "mediana": round(statistics.median(tieni), 4)},
               "verdetto": verdetto,
               "nota": ("scelta sulla MEDIANA della prima metà nel tempo; cassaforte guardata "
                        "una volta sola; prezzo = mediana di 10 scambi; 1% in entrata e 1% in "
                        "uscita; manca ancora lo scivolamento misurato")},
              open(FUORI, "w"), indent=1)
    print(f"DIPLOMA | scritto {FUORI}")
    return 0


if __name__ == "__main__":
    if os.environ.get("SOLO_MISURA") != "1":
        accumula()
    sys.exit(misura())
