"""I PRIMI MINUTI NEL POOL, misurati in DENARO — e l'esito solo DOPO quella finestra.

== PERCHE' (8/10/2026) ==

Cinque tentativi di selezione falliti, tutti basati su cio' che succede **sulla curva**: due
regole bocciate dalla cassaforte, una caratteristica bocciata, due previsioni registrate non
dimostrate (+5,2 e +0,0 punti su 174 monete mai lette). Il fatto misurato: **niente della curva
predice l'esito nel pool**.

Quindi si guarda il pool stesso, nei suoi primi minuti. Due vincoli imparati a caro prezzo:

1. **In DENARO, non in conteggi.** «Quanti compratori» ci ha ingannati tre volte: su un pool
   vuoto pochi compratori bastano a raddoppiare il prezzo, quindi i conteggi misurano la
   sottigliezza e non la domanda. Il denaro no.
2. **Nessuno sguardo al futuro.** Le caratteristiche si leggono nei primi `FINESTRA` blocchi;
   l'esito si conta **solo dopo**. Se la finestra e l'esito si sovrappongono, si misura una cosa
   con se stessa — ed e' il modo piu' elegante di inventarsi un segnale.
"""
import collections
import gzip
import json
import os
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
SERIE = f"{BASE}/serie_pool.jsonl"
ARCH = f"{BASE}/primi_minuti_v2.jsonl"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
ZERO = "0x" + "0" * 40
FINESTRA = int(os.environ.get("FINESTRA", "600"))     # ~60 secondi a 10 blocchi al secondo
BUDGET = int(os.environ.get("BUDGET_SEC", "2400"))
PREZZO_ETH = 2575.78


def scambi_del_pool(tok, pool_di, L, bn):
    nato = L[tok]["blocco"]
    migliore = None
    for pid, lato_tok, v in pool_di.get(tok, ()):
        altro = (v.get("t1" if lato_tok == "t0" else "t0") or "").lower()
        if altro != ZERO:
            continue
        if len(pid) - 2 == 64:
            ev = CP.log_di_finestra(PP.SWAP_V4, nato, min(bn, nato + 9999999),
                                    indirizzo=GESTORE_V4, secondo=pid)
        else:
            ev = CP.log_di_finestra(PP.SWAP_V3, nato, min(bn, nato + 9999999), indirizzo=pid)
        if ev is None:
            return None
        s = []
        for x in ev:
            n = CP._numeri(x.get("data", "0x"))
            if len(n) < 2:
                continue
            a0 = n[0] - (1 << 256) if n[0] >= (1 << 255) else n[0]
            a1 = n[1] - (1 << 256) if n[1] >= (1 << 255) else n[1]
            qt = a1 if lato_tok == "t1" else a0
            qq = a0 if lato_tok == "t1" else a1
            if qt == 0 or qq == 0:
                continue
            vq = abs(qq) / 1e18
            if vq < 1e-6:
                continue
            s.append({"b": int(x["blockNumber"], 16),
                      "i": int(x.get("logIndex", "0x0"), 16),
                      "prezzo": vq / (abs(qt) / 1e18), "denaro": vq,
                      "vende": qq < 0,  # VERSO INVERTITO, vedi cammino_posizioni (10/10): va messo `qq > 0`. Non lo cambio ora perche' questo agente e' di una fase chiusa e i suoi numeri sono gia' stati ritirati.     # la valuta ESCE dal pool: qualcuno ha venduto
                      "chi": (x.get("topics") or [None, None])[1]})
        if s and (migliore is None or len(s) > len(migliore)):
            migliore = s
    return migliore or []


def riga(tok, pool_di, L, bn):
    s = scambi_del_pool(tok, pool_di, L, bn)
    if s is None:
        return None
    if len(s) < 40:
        return {}
    s.sort(key=lambda d: (d["b"], d["i"]))
    b0 = s[0]["b"]
    fine = b0 + FINESTRA
    dentro = [d for d in s if d["b"] <= fine]
    dopo = [d for d in s if d["b"] > fine]
    if len(dentro) < 5 or not dopo:
        return {}
    import statistics
    p0 = statistics.median([d["prezzo"] for d in dentro[:10]])
    compra = sum(d["denaro"] for d in dentro if not d["vende"])
    vende = sum(d["denaro"] for d in dentro if d["vende"])
    # L'ESITO SI CONTA SOLO DOPO LA FINESTRA: altrimenti si misura una cosa con se stessa.
    uscito_5x = sum(d["denaro"] for d in dopo if d["vende"] and d["prezzo"] >= 5 * p0)
    uscito_2x = sum(d["denaro"] for d in dopo if d["vende"] and d["prezzo"] >= 2 * p0)
    # L'ESITO DAL PREZZO DI ENTRATA (8/10, dopo una previsione ritirata da me stesso).
    # Misurare l'esito come multiplo del prezzo INIZIALE fa sembrare predittiva qualunque
    # caratteristica di «quanto e' gia' salito»: il terzo alto stava a 1,456x e per arrivare a
    # 5x del prezzo iniziale gli bastava salire 3,4 volte, al terzo basso ne servivano 7.
    # +11,1 punti sono diventati -6,2 rimisurando da dove comprerei davvero.
    # Quindi l'esito vero e' questo: multipli del prezzo a FINE FINESTRA.
    p_ent = statistics.median([d["prezzo"] for d in dentro[-5:]])
    u2e = sum(d["denaro"] for d in dopo if d["vende"] and d["prezzo"] >= 2 * p_ent)
    u5e = sum(d["denaro"] for d in dopo if d["vende"] and d["prezzo"] >= 5 * p_ent)
    return {
        "moneta": tok, "nato": L[tok]["blocco"], "scambi": len(s),
        "finestra_blocchi": FINESTRA,
        "denaro_comprato": round(compra, 9),
        "denaro_venduto": round(vende, 9),
        "denaro_netto": round(compra - vende, 9),
        "acquisto_piu_grande": round(max((d["denaro"] for d in dentro if not d["vende"]),
                                         default=0.0), 9),
        "scambi_nella_finestra": len(dentro),
        "prezzo_fine_finestra_su_inizio": round(
            statistics.median([d["prezzo"] for d in dentro[-5:]]) / p0, 6) if p0 > 0 else 0,
        "uscito_dopo_a_2x": round(uscito_2x, 9),
        "uscito_dopo_a_5x": round(uscito_5x, 9),
        "buona": 1 if uscito_5x * PREZZO_ETH >= 1000 else 0,
        "prezzo_entrata": p_ent,
        "uscito_da_entrata_2x": round(u2e, 9),
        "uscito_da_entrata_5x": round(u5e, 9),
        "buona_2x_da_entrata": 1 if u2e * PREZZO_ETH >= 1000 else 0,
        "buona_5x_da_entrata": 1 if u5e * PREZZO_ETH >= 1000 else 0,
    }


def main():
    dl = _lanci_interi()
    L = dl["da"]
    pool_di = {}
    for pid, v in _coppie().items():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != ZERO and a in L:
                pool_di.setdefault(a, []).append((pid.lower(), lato, v))
    volute = []
    for l in open(SERIE):
        if l.strip():
            x = json.loads(l)
            if len(x.get("serie") or []) >= 3:
                volute.append(x["moneta"])
    fatte = set()
    if os.path.exists(ARCH):
        for l in open(ARCH):
            if l.strip():
                try:
                    fatte.add(json.loads(l)["moneta"])
                except Exception:
                    pass
    da_fare = [t for t in volute if t not in fatte]
    # PRIMA LE MONETE CHE SERVONO (8/10). Leggere in ordine d'archivio significava spendere
    # mezz'ora sulle monete gia' usate per scegliere — lavoro corretto e inutile — prima di
    # arrivare a quelle su cui il giudizio e' ancora possibile. Con PRIORITA si legge un elenco
    # di indirizzi da fare per primi. Non e' ottimizzazione: e' la differenza fra avere il
    # risultato stasera o domani.
    _pr = os.environ.get("PRIORITA")
    if _pr and os.path.exists(_pr):
        _p = set(x.strip().lower() for x in open(_pr) if x.strip())
        da_fare.sort(key=lambda t: 0 if t in _p else 1)
        print(f"MINUTI | priorita': {sum(1 for t in da_fare if t in _p)} monete da fare per prime",
              flush=True)
    print(f"MINUTI | {len(volute)} monete, {len(fatte)} fatte, {len(da_fare)} da fare", flush=True)
    if not da_fare:
        return 0
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("MINUTI | la chain non dice il blocco: non comincio.")
        return 0
    t0 = time.time()
    n = 0
    with open(ARCH, "a", buffering=1) as f:
        for tok in da_fare:
            if time.time() - t0 > BUDGET:
                print("MINUTI | finito il tempo: l'archivio resta.", flush=True)
                break
            d = riga(tok, pool_di, L, bn)
            if d is None:
                continue
            if d:
                f.write(json.dumps(d) + "\n")
            n += 1
            time.sleep(0.3)
            if n % 50 == 0:
                print(f"MINUTI | {n} fatte, {int(time.time()-t0)}s", flush=True)
    print(f"MINUTI | aggiunte {n}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
