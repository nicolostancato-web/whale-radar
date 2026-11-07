"""LA QUOTA IN GRAPPOLO: quanta fornitura e' finita in mano a un solo operatore.

== PERCHE' (8/10/2026) ==

Il bundling non e' un'ipotesi: e' un prodotto a pagamento, e **ne esiste uno dedicato alla chain
di Robinhood** — `Flap Bundle Sell`, fino a 25 portafogli, commissione fissa 0,004 ETH
(tools.smithii.io/flap-bundle-sell/robinhood). Lo strumento mette le uscite di tutti i
portafogli **nello stesso blocco**, cosi' nessuno si infila in mezzo.

Quindi una moneta con molta fornitura comprata in transazioni a piu' portafogli ha, per
costruzione, un'uscita coordinata pronta a scattare. E' la caratteristica della **seconda
previsione registrata** (prevista NEGATIVA: piu' grappolo, meno occasione).

Non confondere con il numero di compratori: quello misura la liquidita' sottile e ci ha ingannati
tre volte. Questo misura **concentrazione del controllo**, che e' un'altra cosa.
"""
import gzip
import json
import os
import sys
import time
import collections

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
SERIE = f"{BASE}/serie_pool.jsonl"
ARCH = f"{BASE}/quota_grappolo.jsonl"
BUDGET = int(os.environ.get("BUDGET_SEC", "2400"))


def quota_di(tok, L, assets, bn):
    v = L[tok]
    curva = v["curva"].lower()
    a = assets.get((v.get("quote") or "").lower(), {})
    if a.get("decimali") is None:
        return {}
    valute = {curva: (a.get("simbolo"), a.get("decimali"))}
    comp = CP.log_di_finestra(CP.T_COMPRA, v["blocco"], min(bn, v["blocco"] + 9999999),
                              indirizzo=curva)
    if comp is None:
        return None
    righe = [CP._riga(x, "compra", valute) for x in comp]
    righe = [r for r in righe if r and r["gettoni"] > 0]
    if len(righe) < 3:
        return {}
    # per transazione: quanti portafogli DISTINTI hanno ricevuto gettoni
    per_tx = collections.defaultdict(set)
    gettoni_tx = collections.defaultdict(float)
    for r in righe:
        per_tx[r["tx"]].add(r["chi_riceve"])
        gettoni_tx[r["tx"]] += r["gettoni"]
    tot = sum(gettoni_tx.values())
    in_grappolo = sum(g for h, g in gettoni_tx.items() if len(per_tx[h]) >= 2)
    tx_grappolo = sum(1 for h in per_tx if len(per_tx[h]) >= 2)
    return {"moneta": tok, "nato": v["blocco"],
            "quota_in_grappolo": round(in_grappolo / tot, 6) if tot > 0 else 0.0,
            "tx_in_grappolo": tx_grappolo, "tx_totali": len(per_tx),
            "portafogli_max_in_una_tx": max((len(w) for w in per_tx.values()), default=0)}


def main():
    dl = _lanci_interi()
    L, assets = dl["da"], dl["assets"]
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
    print(f"GRAPPOLO | {len(volute)} monete, {len(fatte)} fatte, {len(da_fare)} da fare",
          flush=True)
    if not da_fare:
        return 0
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("GRAPPOLO | la chain non dice il blocco: non comincio.")
        return 0
    t0 = time.time()
    n = 0
    with open(ARCH, "a", buffering=1) as f:
        for tok in da_fare:
            if time.time() - t0 > BUDGET:
                print("GRAPPOLO | finito il tempo: l'archivio resta.", flush=True)
                break
            d = quota_di(tok, L, assets, bn)
            if d is None:
                continue
            if d:
                f.write(json.dumps(d) + "\n")
            n += 1
            time.sleep(0.3)
            if n % 50 == 0:
                print(f"GRAPPOLO | {n} fatte, {int(time.time()-t0)}s", flush=True)
    print(f"GRAPPOLO | aggiunte {n}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
