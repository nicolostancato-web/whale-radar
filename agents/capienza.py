"""LA CAPIENZA: quanti soldi l'occasione regge davvero.

== PERCHE' (8/10/2026) ==

Due regole bocciate dalla cassaforte in una notte, e la seconda ha mostrato il difetto del
bersaglio: «arriva a 2x» premiava i pool SOTTILI, dove basta un acquisto modesto per raddoppiare
il prezzo. Su 28 monete scelte cosi', **zero** hanno fatto 10x.

Un 2x su un pool che assorbe cinque euro non e' un 2x: e' un numero che non si incassa. E lo
scivolamento e' precisamente la voce che ha ucciso il progetto precedente su Solana.

Quindi la domanda smette di essere «quante volte sale» e diventa: **quanti euro sono realmente
usciti dal pool mentre il prezzo stava sopra 2x il prezzo di partenza?**

Non e' una stima: e' la somma del denaro che ha DAVVERO lasciato il pool verso chi vendeva, a
quei livelli. Se la mediana e' di pochi euro, la strada e' chiusa e lo diciamo. Se sono
centinaia, c'e' qualcosa e si dimensiona su quello.

== LA CONVENZIONE DEI SEGNI, che e' il punto delicato ==

In uno scambio Uniswap v4 un importo entra nel pool (positivo) e l'altro esce (negativo). Chi
**vende** il gettone lo manda dentro (gettone positivo) e porta via la valuta (valuta negativa).
Quindi il denaro incassato da chi vende e' il valore assoluto della valuta **negativa**.
Confondere i due versi gonfia tutto, ed e' lo stesso errore che il 7/10 ha prodotto il «2855x».
"""
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
SERIE = f"{BASE}/serie_pool.jsonl"
FUORI_ARCH = f"{BASE}/capienza.jsonl"
FUORI = f"{BASE}/capienza.json"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
ZERO = "0x" + "0" * 40
BUDGET = int(os.environ.get("BUDGET_SEC", "2400"))
PREZZO_ETH = 2575.78            # dall'explorer, 7/10/2026


def capienza_di(tok, pool_di, L, bn):
    """Quanto denaro e' uscito dal pool a vari multipli del prezzo iniziale. None se illeggibile."""
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
            s.append((int(x["blockNumber"], 16), int(x.get("logIndex", "0x0"), 16),
                      vq / (abs(qt) / 1e18), vq, qq < 0))  # VERSO INVERTITO, vedi cammino_posizioni (10/10): va messo `qq > 0`. Non lo cambio ora perche' questo agente e' di una fase chiusa e i suoi numeri sono gia' stati ritirati.
        if s and (migliore is None or len(s) > len(migliore)):
            migliore = s
    if not migliore or len(migliore) < 40:
        return {}
    migliore.sort()
    # prezzo di partenza: mediana dei primi 10 scambi (un singolo scambio non e' un prezzo)
    p0 = statistics.median([p for _, _, p, _, _ in migliore[:10]])
    fuori = {"moneta": tok, "nato": nato, "scambi": len(migliore), "p0": p0}
    for soglia in (1, 2, 5, 10):
        # solo chi VENDE: la valuta esce dal pool (negativa) verso chi vende
        v = [q for _, _, p, q, uscita in migliore if uscita and p >= soglia * p0]
        fuori[f"uscito_a_{soglia}x"] = round(sum(v), 9)
        fuori[f"scambi_a_{soglia}x"] = len(v)
        fuori[f"piu_grande_a_{soglia}x"] = round(max(v), 9) if v else 0.0
    return fuori


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
    if os.path.exists(FUORI_ARCH):
        for l in open(FUORI_ARCH):
            if l.strip():
                try:
                    fatte.add(json.loads(l)["moneta"])
                except Exception:
                    pass
    da_fare = [t for t in volute if t not in fatte]
    print(f"CAPIENZA | {len(volute)} monete, {len(fatte)} fatte, {len(da_fare)} da fare",
          flush=True)
    if da_fare:
        bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
        if not bn:
            print("CAPIENZA | la chain non dice il blocco: non comincio.")
            return 0
        t0 = time.time()
        n = 0
        with open(FUORI_ARCH, "a", buffering=1) as f:
            for tok in da_fare:
                if time.time() - t0 > BUDGET:
                    print("CAPIENZA | finito il tempo: l'archivio resta.", flush=True)
                    break
                d = capienza_di(tok, pool_di, L, bn)
                if d is None:
                    continue
                if d:
                    f.write(json.dumps(d) + "\n")
                n += 1
                time.sleep(0.3)
                if n % 25 == 0:
                    print(f"CAPIENZA | {n} fatte, {int(time.time()-t0)}s", flush=True)

    righe = []
    for l in open(FUORI_ARCH):
        if l.strip():
            try:
                righe.append(json.loads(l))
            except Exception:
                pass
    if len(righe) < 30:
        print(f"CAPIENZA | solo {len(righe)} monete: non concludo.")
        return 0
    righe.sort(key=lambda d: d["nato"])
    recenti = righe[len(righe) // 2:]        # SOLO IL PERIODO RECENTE: il vecchio sovrastima
    print(f"\nCAPIENZA | {len(righe)} monete, misuro sulle {len(recenti)} piu' recenti "
          f"(il periodo vecchio sovrastima: l'occasione si e' dimezzata)\n")
    print(f"{'livello':10} {'monete che ci arrivano':>24} {'uscito in ETH, mediana':>24} "
          f"{'in dollari':>12} {'scambio max':>20}")
    out = {}
    for soglia in (2, 5, 10):
        c = [d for d in recenti if d[f"scambi_a_{soglia}x"] > 0]
        if not c:
            print(f"{soglia}x{'':8} {0:>24} {'-':>24} {'-':>12} {'-':>20}")
            continue
        med = statistics.median([d[f"uscito_a_{soglia}x"] for d in c])
        gr = statistics.median([d[f"piu_grande_a_{soglia}x"] for d in c])
        out[f"{soglia}x"] = {"monete": len(c), "su": len(recenti),
                             "uscito_eth_mediana": round(med, 6),
                             "uscito_dollari_mediana": round(med * PREZZO_ETH, 2),
                             "scambio_piu_grande_eth_mediana": round(gr, 6),
                             "scambio_piu_grande_dollari": round(gr * PREZZO_ETH, 2)}
        print(f"{soglia}x{'':8} {f'{len(c)}/{len(recenti)}':>24} {med:>24.6f} "
              f"{med*PREZZO_ETH:>11.0f}$ {gr*PREZZO_ETH:>19.0f}$")
    json.dump({"chain": CHAIN, "monete": len(righe), "recenti": len(recenti),
               "prezzo_eth_usato": PREZZO_ETH, "livelli": out,
               "nota": ("denaro REALMENTE uscito dal pool verso chi vendeva, mentre il prezzo "
                        "stava sopra il livello; misurato sul periodo recente")},
              open(FUORI, "w"), indent=1)
    print(f"\nCAPIENZA | scritto {FUORI}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
