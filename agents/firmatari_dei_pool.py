"""CHI HA DAVVERO MANDATO LA TRANSAZIONE, per i pool delle monete graduate.

== PERCHE' ESISTE (6/10/2026) ==

Per sapere se chi entra presto sulla curva guadagna, serve vedere dove esce. Per le monete che
arrivano al mercato l'uscita e' nel pool, e li' l'identita' e' il problema:

 · i nostri file degli scambi hanno un campo `w` con copertura **100%** — ma e' il `sender` di
   Uniswap v4, cioe' **il router che ha chiamato il contratto**, non la persona. Misurato: su
   1.441 scambi ci sono 72 indirizzi distinti, e i primi cinque (tutti CONTRATTI) coprono il 67%.
 · la mappa `iniziatori` ha l'identita' giusta (chi firma la transazione) ma copre solo
   **l'1,6%** degli scambi nei pool graduati.

Con l'uno l'attribuzione e' sbagliata, con l'altra manca il 98%. Il 6/10 usando la seconda mi
usciva che chi entra primo su una moneta graduata rende 0,29x — un numero fatto quasi tutto di
«non ho visto la sua uscita», letto come «non e' mai uscito». E' la terza volta in un giorno che
un'assenza nei miei dati stava per diventare un fatto sul mondo.

== COME ==

Un blocco contiene tutte le sue transazioni con il mittente. Quindi NON si chiede una
transazione per volta: si chiede il BLOCCO, e si risolvono in un colpo tutte le transazioni che
ci stanno dentro. E' la stessa economia che il 6/10 ha fatto scendere l'elenco dei lanci da
34.096 chiamate a 7.

Con contatore: i blocchi gia' risolti non si richiedono, cosi' i giri CONVERGONO invece di
ricominciare.

== COSTO ==

ZERO: RPC pubblico della chain, nessuna chiave.
"""
import glob
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a_fette as AF                       # noqa: E402
from curva_pons import chiama              # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
CARTELLE = tuple(os.environ.get("CARTELLE", "storico,vivo,trades").split(","))
BUDGET = int(os.environ.get("BUDGET_SEC", "900"))


def pool_graduati():
    p = f"{BASE}/curva_lanci.json.gz"
    pc = f"{BASE}/coppie.json"
    for q in (p, pc):
        if not os.path.exists(q):
            raise SystemExit(f"FIRMATARI | manca {q}: non invento quali pool sono graduati")
    nati = set(t.lower() for t in json.load(gzip.open(p, "rt"))["da"])
    fuori = []
    for pool, v in json.load(open(pc))["coppie"].items():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != "0x" + "0" * 40 and a in nati:
                fuori.append(pool.lower())
                break
    return fuori


def main():
    if CHAIN != "robinhood":
        print(f"FIRMATARI | la curva di Pons e' di robinhood: su {CHAIN} niente da fare.")
        return 0
    t0 = time.time()
    pool = AF.mia_parte(sorted(pool_graduati()))
    i_f, n_f = AF.quale_fetta()
    print(f"FIRMATARI | fetta {i_f+1}/{n_f}: {len(pool):,} pool graduati", flush=True)

    # UNA MONETA PER VOLTA, NON UN PO' DI TUTTE.
    #
    # Prima raccoglievo i blocchi di tutti i pool insieme e li risolvevo in ordine di numero.
    # Dopo un giro avevo l'1,7% dei blocchi di OGNI moneta: inutilizzabile, perche' per una
    # moneta sola non avevo mai il quadro completo. E sarebbero serviti ~60 giri.
    #
    # **Una copertura parziale spalmata su tutto non serve a niente; una copertura completa su
    # un sottoinsieme si usa subito.** Quindi: le monete si ordinano per quanto sono scambiate
    # (le piu' vive per prime, perche' sono quelle dove un guadagno e' misurabile), e si
    # risolvono TUTTI i blocchi di una moneta prima di passare alla successiva.
    # Dopo il primo giro avro' poche monete ma COMPLETE, e su quelle la domanda si risponde.
    per_moneta = []
    for p in pool:
        bl, peso = set(), 0
        for c in CARTELLE:
            q = os.path.join(BASE, c, f"{p}.jsonl.gz")
            if not os.path.exists(q):
                continue
            peso += os.path.getsize(q)
            try:
                for l in gzip.open(q, "rt"):
                    if l.strip():
                        b = json.loads(l).get("blocco")
                        if isinstance(b, int):
                            bl.add(b)
            except Exception:
                continue
        if bl:
            per_moneta.append((peso, p, bl))
    per_moneta.sort(reverse=True)          # le piu' scambiate per prime
    blocchi = set()
    for _, _, bl in per_moneta:
        blocchi |= bl
    print(f"FIRMATARI | {len(blocchi):,} blocchi distinti da risolvere", flush=True)
    if not blocchi:
        print("FIRMATARI | nessun blocco: non scrivo un file vuoto che direbbe «nessuno ha "
              "scambiato». Un lavoro che riesce leggendo zero e' un guasto, non un risultato.")
        return 0

    pf = f"{BASE}/firmatari_fatti_pezzo_{i_f}.json"
    fatti = set()
    if os.path.exists(pf):
        try:
            fatti = set(json.load(open(pf))["blocchi"])
        except Exception:
            fatti = set()
    ps = f"{BASE}/firmatari_pezzo_{i_f}.json.gz"
    mappa = {}
    if os.path.exists(ps) and fatti:
        try:
            mappa = json.load(gzip.open(ps, "rt")).get("da", {})
        except Exception:
            mappa = {}
    # l'ordine e' quello delle monete, non quello dei numeri di blocco
    da_fare, complete, parziali = [], 0, 0
    for _, p, bl in per_moneta:
        resta = sorted(bl - fatti)
        if not resta:
            complete += 1
        da_fare.extend(resta)
    print(f"FIRMATARI | {len(fatti):,} blocchi gia' risolti, {len(da_fare):,} da fare, "
          f"{len(mappa):,} transazioni gia' in archivio", flush=True)

    fatti_ora = 0
    for b in da_fare:
        if time.time() - t0 >= BUDGET:
            print(f"   budget speso dopo {fatti_ora:,} blocchi: salvo quello che ho", flush=True)
            break
        blk = chiama("eth_getBlockByNumber", [hex(b), True])
        if not blk or not isinstance(blk.get("transactions"), list):
            continue
        for tx in blk["transactions"]:
            h = str(tx.get("hash", "")).lower()
            f = str(tx.get("from", "")).lower()
            if h and f:
                mappa[h] = f
        fatti.add(b)
        fatti_ora += 1

    json.dump({"acq": int(time.time()), "fetta": i_f, "blocchi": sorted(fatti)},
              open(pf, "w"))
    with gzip.open(ps, "wt") as f:
        json.dump({"acq": int(time.time()), "chain": CHAIN, "fetta": i_f,
                   "blocchi_risolti": len(fatti), "blocchi_da_fare": len(blocchi),
                   "copertura_pct": 100.0 * len(fatti) / max(1, len(blocchi)),
                   "da": mappa}, f)
    finite = sum(1 for _, _, bl in per_moneta if not (bl - fatti))
    print(f"FIRMATARI | risolti {fatti_ora:,} blocchi in questo giro. "
          f"MONETE COMPLETE: {finite:,} su {len(per_moneta):,} "
          f"(e' questo il numero che conta, non la percentuale di blocchi). "
          f"{len(mappa):,} transazioni -> {ps}", flush=True)
    json.dump({"acq": int(time.time()), "fetta": i_f,
               "monete_complete": sorted(p for _, p, bl in per_moneta if not (bl - fatti))},
              open(f"{BASE}/monete_complete_pezzo_{i_f}.json", "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
