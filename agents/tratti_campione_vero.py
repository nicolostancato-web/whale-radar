"""LE CARATTERISTICHE DEL CAMPIONE NON STORTO, per la prova di selezione.

== PERCHE' UN AGENTE NUOVO ==

Gli archivi di caratteristiche che ho (`tratti_al_diploma`, `quota_grappolo`, `primi_minuti_v2`)
sono costruiti sulle monete di `serie_pool`, cioe' sul campione **estratto dal nostro registro** —
quello che ha falsificato tre numeri in un giorno. Riusarli qui rimetterebbe dentro lo stesso
difetto per comodita'.

Qui le caratteristiche si calcolano per le monete del campione **casuale vero** (lanci a caso ->
diploma verificato sulla chain -> id del pool dall'evento Initialize), e solo per quelle
**comprabili**: le altre non sono decisioni che potremmo prendere.

== L'ELENCO E' CHIUSO ==

Esattamente quello dichiarato in `PROCEDURA_SELEZIONE_FINALE.md`, pubblicato prima di guardare una
sola relazione. Non si aggiunge niente dopo aver visto i risultati — e questo file esiste anche
per rendere visibile un eventuale tentativo di aggiungerlo.
"""
import collections
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
ARCH = f"{BASE}/tratti_campione_vero.jsonl"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
FIN = 600
P = 2575.78
BUDGET = int(os.environ.get("BUDGET_SEC", "2500"))


def main():
    dl = _lanci_interi()
    L, assets = dl["da"], dl["assets"]
    esito = {}
    for l in open(f"{BASE}/mercato_campione_vero.jsonl"):
        if l.strip():
            d = json.loads(l)
            if d["esito"] == "misurata":
                esito[d["moneta"]] = d
    dip = {}
    for l in open(f"{BASE}/diplomate_vere.jsonl"):
        if l.strip():
            d = json.loads(l)
            if d.get("diplomata") and d.get("pool") not in (None, "senza id"):
                dip[d["moneta"]] = d
    voluti = [t for t in esito if t in dip]
    fatte = set()
    if os.path.exists(ARCH):
        for l in open(ARCH):
            if l.strip():
                try:
                    fatte.add(json.loads(l)["moneta"])
                except Exception:
                    pass
    print(f"TRATTI VERI | {len(voluti)} monete comprabili del campione vero, "
          f"{len(fatte)} gia' fatte", flush=True)
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("TRATTI VERI | la chain non risponde.")
        return 0
    t0 = time.time()
    n = 0
    with open(ARCH, "a", buffering=1) as f:
        for tok in voluti:
            if tok in fatte:
                continue
            if time.time() - t0 > BUDGET:
                print("TRATTI VERI | finito il tempo: l'archivio resta.", flush=True)
                break
            v = L[tok]
            curva = v["curva"].lower()
            a = assets.get((v.get("quote") or "").lower(), {})
            dec = a.get("decimali")
            if dec is None:
                continue                  # unita' sconosciuta: fuori, non si indovina
            valute = {curva: (a.get("simbolo"), dec)}
            comp = CP.log_di_finestra(CP.T_COMPRA, v["blocco"],
                                      min(bn, v["blocco"] + 9999999), indirizzo=curva)
            vend = CP.log_di_finestra(CP.T_VENDE, v["blocco"],
                                      min(bn, v["blocco"] + 9999999), indirizzo=curva)
            if comp is None or vend is None:
                continue                  # mezza lettura non si scrive
            B = [CP._riga(x, "compra", valute) for x in comp]
            B = [r for r in B if r and r["valuta"] > 0 and r["gettoni"] > 0]
            S = [CP._riga(x, "vende", valute) for x in vend]
            S = [r for r in S if r and r["valuta"] > 0]
            if len(B) < 3:
                continue
            B.sort(key=lambda r: (r["blocco"], r["ordine"]))
            esenti = {r["chi_riceve"] for r in B
                      if r["blocco"] <= v["blocco"] + 50
                      and 100 * r["commissione"] / r["valuta"] < 50}
            tassati = {r["chi_riceve"] for r in B
                       if r["blocco"] <= v["blocco"] + 50
                       and 100 * r["commissione"] / r["valuta"] >= 50}
            per_tx = collections.defaultdict(set)
            gettoni_tx = collections.defaultdict(float)
            for r in B:
                per_tx[r["tx"]].add(r["chi_riceve"])
                gettoni_tx[r["tx"]] += r["gettoni"]
            tot_g = sum(gettoni_tx.values())
            in_gr = sum(g for h, g in gettoni_tx.items() if len(per_tx[h]) >= 2)
            # il primo minuto NEL POOL, in denaro
            ev = CP.log_di_finestra(PP.SWAP_V4, dip[tok]["blocco_diploma"],
                                    min(bn, dip[tok]["blocco_diploma"] + 9999999),
                                    indirizzo=GESTORE_V4, secondo=dip[tok]["pool"])
            if ev is None:
                continue
            s = []
            for x in ev:
                nn = CP._numeri(x.get("data", "0x"))
                if len(nn) < 2:
                    continue
                a0 = nn[0] - (1 << 256) if nn[0] >= (1 << 255) else nn[0]
                a1 = nn[1] - (1 << 256) if nn[1] >= (1 << 255) else nn[1]
                v0, v1 = abs(a0) / 1e18, abs(a1) / 1e18
                if v0 == 0 or v1 == 0 or min(v0, v1) * 1000 > max(v0, v1):
                    continue
                vq = min(v0, v1)
                s.append({"b": int(x["blockNumber"], 16), "denaro": vq * P,
                          "vende": (a0 < 0) if v0 < v1 else (a1 < 0)})
            if not s:
                continue
            b0 = min(z["b"] for z in s)
            dentro = [z for z in s if z["b"] <= b0 + FIN]
            n += 1
            f.write(json.dumps({
                "moneta": tok,
                "nato": v["blocco"],
                # --- sulla curva ---
                "incassato_curva": round(sum(r["valuta"] for r in B), 9),
                "blocchi_per_riempirsi": B[-1]["blocco"] - v["blocco"],
                "velocita_riempimento": round(sum(r["valuta"] for r in B) /
                                              max(B[-1]["blocco"] - v["blocco"], 1), 12),
                "compratori_curva": len({r["chi_riceve"] for r in B}),
                "acquisto_mediano_dollari": round(
                    statistics.median([r["valuta"] for r in B]) * P, 2),
                "esenti": len(esenti), "tassati_99": len(tassati),
                "quota_in_grappolo": round(in_gr / tot_g, 6) if tot_g > 0 else 0.0,
                "vendite_sulla_curva": len(S),
                # --- primo minuto nel pool, in denaro ---
                "denaro_comprato_1min": round(sum(z["denaro"] for z in dentro
                                                  if not z["vende"]), 2),
                "denaro_venduto_1min": round(sum(z["denaro"] for z in dentro
                                                 if z["vende"]), 2),
                "acquisto_piu_grande_1min": round(max((z["denaro"] for z in dentro
                                                       if not z["vende"]), default=0.0), 2),
                "scambi_1min": len(dentro),
                # --- esito, gia' misurato ---
                "rendimento": esito[tok]["rendimento"],
                "tocca_2x": esito[tok]["tocca_2x"],
                "max_x": esito[tok]["max_x"],
            }) + "\n")
            time.sleep(0.2)
            if n % 40 == 0:
                print(f"TRATTI VERI | {n} fatte, {int(time.time()-t0)}s", flush=True)
    tot = sum(1 for l in open(ARCH) if l.strip())
    print(f"TRATTI VERI | aggiunte {n}, totale in archivio {tot}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
