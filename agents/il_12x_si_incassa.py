"""IL 12x SI INCASSA O NO? La domanda decisiva sulla curva.

== PERCHE' (7/10/2026, notte) ==

La documentazione di Pons dice che dal primo acquisto alla graduazione il prezzo fa **12,25x**, e
l'ho verificato sui nostri dati: su 39 monete graduate, mediana 11,79x, massimo 12,21x, nessuna
sopra il tetto. Quindi il premio ESISTE e non e' un'opinione di mercato: e' una formula.

Ma nei primi ~5 secondi c'e' una tassa anti-sniper del **99%**, e chi la paga non puo' prendere
niente. Esistono indirizzi **esentati** (uno esente su 22 lanci su 30) e quelli chiudono a 0,987x.

Restano due spiegazioni, e **vanno distinte con una misura, non scelte per gusto**:

  (1) il 12x NON e' incassabile — e' l'intervallo di prezzo fra primo e ultimo acquisto, ma
      vendere ripercorre la curva al contrario e 5/7 della fornitura esce lungo la salita;
  (2) il 12x e' incassabile, ma chi ha la chiave non lo prende (fa altro).

La misura che le distingue: **fra chi e' entrato nei primissimi acquisti SENZA pagare il 99%,
quanto ha incassato davvero?** Se nemmeno loro arrivano vicino al 12x, vale (1) e la curva e'
chiusa come strada. Se qualcuno lo prende, abbiamo trovato chi cerchiamo.

== LE REGOLE, LE SOLITE ==

Posizione intera (letta dal blocco di nascita), gettoni venduti uguali a quelli comprati
(90-110%), una sola valuta e dichiarata, lanciatori esclusi, gas incluso, chi non esce vale
ZERO e non «non misurabile».
"""
import collections
import gzip
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
QUANTE = int(os.environ.get("QUANTE", "40"))
GAS = 0.000008135
ZERO = "0x" + "0" * 40
FUORI = os.environ.get("FUORI", f"{BASE}/il_12x_si_incassa.json")


def graduate(L):
    p = f"{BASE}/coppie.json"
    if not os.path.exists(p):
        print("12X | manca il registro delle coppie: non so quali monete hanno graduato.")
        return []
    fuori = set()
    for _pool, v in json.load(open(p))["coppie"].items():
        for lato in ("t0", "t1"):
            a = (v.get(lato) or "").lower()
            if a and a != ZERO and a in L:
                fuori.add(a)
    return sorted(fuori)


def main():
    pl = f"{BASE}/curva_lanci.json.gz"
    if not os.path.exists(pl):
        print("12X | manca l'elenco dei lanci.")
        return 0
    dl = json.load(gzip.open(pl, "rt"))
    L, assets = dl["da"], dl["assets"]
    creatori = {v["creatore"].lower() for v in L.values()}
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("12X | la chain non risponde.")
        return 0

    per_fascia = collections.defaultdict(list)     # (esente?, posizione) -> moltiplicatori
    casi_belli = []
    lette = 0
    for tok in graduate(L):
        if lette >= QUANTE:
            break
        v = L[tok]
        curva = v["curva"].lower()
        a = assets.get((v.get("quote") or "").lower(), {})
        if a.get("decimali") is None:
            continue                                # unita' sconosciuta: fuori, non si indovina
        valute = {curva: (a.get("simbolo"), a.get("decimali"))}
        comp = CP.log_di_finestra(CP.T_COMPRA, v["blocco"], min(bn, v["blocco"] + 9999999),
                                  indirizzo=curva)
        vend = CP.log_di_finestra(CP.T_VENDE, v["blocco"], min(bn, v["blocco"] + 9999999),
                                  indirizzo=curva)
        if comp is None or vend is None:
            continue                                # mezza lettura non si usa
        righe = []
        for x in comp:
            r = CP._riga(x, "compra", valute)
            if r:
                righe.append(r)
        for x in vend:
            r = CP._riga(x, "vende", valute)
            if r:
                righe.append(r)
        if len(righe) < 5:
            continue
        lette += 1
        righe.sort(key=lambda r: (r["blocco"], r["ordine"]))

        # la posizione nella coda degli ACQUISTI, e se ha pagato la tassa
        pos = {}
        tassa = {}
        n = 0
        per_chi = collections.defaultdict(lambda: {"ci": 0.0, "co": 0.0, "gi": 0.0, "go": 0.0})
        for r in righe:
            chi = r["chi_riceve"]
            d = per_chi[chi]
            if r["verso"] == "compra":
                if chi not in pos:
                    n += 1
                    pos[chi] = n
                    q = (100 * r["commissione"] / r["valuta"]) if r["valuta"] > 0 else 0.0
                    tassa[chi] = q >= 50          # ha pagato il 99%?
                d["ci"] += r["valuta"]
                d["gi"] += r["gettoni"]
            else:
                d["co"] += r["valuta"]
                d["go"] += r["gettoni"]
        for chi, d in per_chi.items():
            if chi in creatori or d["ci"] <= 0 or d["gi"] <= 0:
                continue
            if d["go"] > 0 and not (0.9 <= d["go"] / d["gi"] <= 1.1):
                continue                            # i gettoni venduti non sono quelli comprati
            x = (d["co"] - GAS) / d["ci"]           # chi non esce vale ZERO, non «ignoto»
            p = pos.get(chi, 999)
            fascia = ("1-3" if p <= 3 else "4-10" if p <= 10 else "11-50" if p <= 50 else ">50")
            per_fascia[("tassato" if tassa.get(chi) else "esente", fascia)].append(x)
            if x >= 5 and not tassa.get(chi):
                casi_belli.append({"chi": chi, "moneta": tok, "x": round(x, 3),
                                   "posizione": p, "speso": round(d["ci"], 9),
                                   "incassato": round(d["co"], 9), "valuta": a.get("simbolo")})

    print(f"12X | monete graduate lette per intero: {lette}\n")
    print(f"{'chi':10} {'posizione':10} {'quanti':>7} {'mediana':>9} {'migliore':>9} {'>=5x':>6}")
    fuori = {}
    for (chi, fascia) in sorted(per_fascia, key=lambda k: (k[0], k[1])):
        xs = per_fascia[(chi, fascia)]
        if not xs:
            continue
        fuori[f"{chi}|{fascia}"] = {"quanti": len(xs),
                                    "mediana": round(statistics.median(xs), 4),
                                    "migliore": round(max(xs), 3),
                                    "sopra_5x": sum(1 for x in xs if x >= 5)}
        print(f"{chi:10} {fascia:10} {len(xs):7,} {statistics.median(xs):8.3f}x "
              f"{max(xs):8.2f}x {sum(1 for x in xs if x >= 5):6}")

    e13 = per_fascia.get(("esente", "1-3"), [])
    print()
    if e13:
        m = statistics.median(e13)
        print(f"12X | LA RISPOSTA: chi entra nei primi 3 acquisti SENZA pagare la tassa "
              f"incassa in mediana {m:.3f}x (su {len(e13)} casi), migliore {max(e13):.2f}x.")
        print("12X | " + ("il 12x NON si incassa: nemmeno chi ha la chiave e arriva primo lo "
                          "prende. La curva e' chiusa come strada." if max(e13) < 5 else
                          "qualcuno lo prende: ci sono casi da aprire uno per uno."))
    else:
        print("12X | nessun caso di entrata nei primi 3 senza tassa: non concludo niente.")
    json.dump({"chain": CHAIN, "monete": lette, "fasce": fuori,
               "casi_sopra_5x_senza_tassa": sorted(casi_belli, key=lambda c: -c["x"])[:30],
               "regole": ("posizione intera, gettoni 90-110%, una valuta, lanciatori esclusi, "
                          "gas incluso, chi non esce vale zero")},
              open(FUORI, "w"), indent=1)
    print(f"12X | scritto {FUORI}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
