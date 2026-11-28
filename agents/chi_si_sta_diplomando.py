"""BECCARE CHI SI STA DIPLOMANDO, mentre la curva si riempie.

== IL MANDATO (Nicolo', 8/10/2026) ==

«Il secondo goal e' vedere se riusciamo a beccare quell'1%, cosi' poi quando viene promosso noi
siamo gia' dentro. Se non riusciamo a beccarlo andiamo nel mercato normale.»

== PERCHE' QUESTA VOLTA PUO' FUNZIONARE (ed e' diverso dai sette tentativi falliti) ==

I sette fallimenti cercavano di prevedere **come andra' la moneta dopo** il diploma: un giudizio
di mercato. Qui si prevede **se** si diploma, e il diploma non e' un giudizio: e' una **soglia
meccanica**. La moneta gradua quando la curva ha incassato **4,2 ETH reali**
(docs.ponsfamily.com/v2, verificato sui nostri dati: mediana 11,79x dal primo all'ultimo acquisto,
massimo 12,21x, tetto 12,25x mai superato).

Quindi la domanda non e' «sara' una buona moneta» ma **«a che velocita' si sta riempiendo il
secchio?»** — ed e' un numero che si legge in diretta.

== LA PROCEDURA, DICHIARATA PRIMA DI GUARDARE ==

1. **Campione bilanciato**: le monete graduate sono lo 0,77%, quindi un campione casuale ne
   conterrebbe 5 su 600 e non si misurerebbe niente. Si prendono N graduate e M non graduate, e
   le probabilita' si riportano **riconvertite al tasso vero** (0,77%): altrimenti sembrerebbe
   che una curva su due si diplomi.
2. **Solo informazione precoce**: si guarda quanto ha incassato la curva nei primi
   `FINESTRE` blocchi dalla nascita. Niente che arrivi dopo.
3. **Meta' per scegliere, meta' in cassaforte**, divise per data di lancio.
4. La soglia utile si dichiara come **quanta parte dei diplomi si cattura** e **quante false
   sveglie costa**: un segnale che becca il 90% dei diplomi ma suona su un terzo delle monete non
   serve a niente.
"""
import gzip
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402


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
ARCH = f"{BASE}/riempimento_curva.jsonl"
ZERO = "0x" + "0" * 40
FINESTRE = [300, 1200, 6000, 36000]        # ~30s, 2min, 10min, 1h a 10 blocchi/s
QUANTE_GRAD = int(os.environ.get("QUANTE_GRAD", "150"))
QUANTE_NO = int(os.environ.get("QUANTE_NO", "350"))
BUDGET = int(os.environ.get("BUDGET_SEC", "2500"))


def main():
    dl = _lanci_interi()
    L, assets = dl["da"], dl["assets"]
    grad = set()
    for _pid, v in _coppie().items():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != ZERO and a in L:
                grad.add(a)
    print(f"CURVA | {len(L):,} lanci, {len(grad):,} diplomate ({100*len(grad)/len(L):.2f}%)",
          flush=True)
    random.seed(17)
    g = random.sample(sorted(grad), min(QUANTE_GRAD, len(grad)))
    no = [t for t in random.sample(sorted(L), QUANTE_NO * 3) if t not in grad][:QUANTE_NO]
    voluti = [(t, 1) for t in g] + [(t, 0) for t in no]
    random.shuffle(voluti)
    fatte = set()
    if os.path.exists(ARCH):
        for l in open(ARCH):
            if l.strip():
                try:
                    fatte.add(json.loads(l)["moneta"])
                except Exception:
                    pass
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("CURVA | la chain non risponde.")
        return 0
    t0 = time.time()
    n = 0
    with open(ARCH, "a", buffering=1) as f:
        for tok, diplomata in voluti:
            if tok in fatte:
                continue
            if time.time() - t0 > BUDGET:
                print("CURVA | finito il tempo: l'archivio resta.", flush=True)
                break
            v = L[tok]
            curva = v["curva"].lower()
            a = assets.get((v.get("quote") or "").lower(), {})
            if a.get("decimali") is None:
                continue
            valute = {curva: (a.get("simbolo"), a.get("decimali"))}
            log = CP.log_di_finestra(CP.T_COMPRA, v["blocco"],
                                     min(bn, v["blocco"] + 9999999), indirizzo=curva)
            if log is None:
                continue
            righe = [CP._riga(x, "compra", valute) for x in log]
            righe = [r for r in righe if r and r["valuta"] > 0]
            n += 1
            rec = {"moneta": tok, "diplomata": diplomata, "nato": v["blocco"],
                   "simbolo": a.get("simbolo"), "acquisti_totali": len(righe)}
            for w in FINESTRE:
                dentro = [r for r in righe if r["blocco"] <= v["blocco"] + w]
                rec[f"incassato_{w}"] = round(sum(r["valuta"] for r in dentro), 9)
                rec[f"compratori_{w}"] = len({r["chi_riceve"] for r in dentro})
            f.write(json.dumps(rec) + "\n")
            time.sleep(0.25)
            if n % 40 == 0:
                print(f"CURVA | {n} fatte, {int(time.time()-t0)}s", flush=True)
    print(f"CURVA | aggiunte {n}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
