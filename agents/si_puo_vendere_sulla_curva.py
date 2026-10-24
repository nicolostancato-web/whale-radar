"""Si riesce davvero a comprare e vendere DENTRO la curva, prima del diploma?

LA DOMANDA DI NICOLO' (11/10): «mi confermi che e' possibile fare trading all'interno della box,
comprando facilmente, vendendo facilmente, monitorando — oppure noi abbiamo ipotizzato ma in
realta' quando si diploma e' impossibile vendere?»

E' la domanda che viene prima di tutte le altre: se non si puo' uscire, un moltiplicatore di
2,8x e' un numero su carta. Qui non si ragiona, si contano le vendite VERE sulla chain:
  - quante vendite ci sono state su ogni curva, e quante persone distinte le hanno fatte;
  - quanto grande e' la vendita tipica e la piu' grande (e' la capienza: se la vendita massima
    mai eseguita e' da 20 euro, con 200 euro si muove il prezzo contro di se');
  - quanto si incassa vendendo rispetto a quanto si e' pagato comprando allo stesso punto
    della curva (e' lo scalino fra prezzo d'acquisto e prezzo di vendita);
  - se le vendite continuano fino al diploma o si fermano prima.

Il senso di «facile» qui e' uno solo: altri lo hanno fatto, molte volte, per importi come i
nostri. Se nessuno vende, non e' che e' difficile: e' che non si puo'.
"""
import json
import os
import statistics
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

import curva_pons as CP                                        # noqa: E402
import archivio as AR                                          # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
ARCH = f"{BASE}/si_puo_vendere.json"
PREZZO_ETH = 2575.78
QUANTE = int(os.environ.get("QUANTE", "10"))
ASSETS = {}


def una_curva(tok, L, bn):
    curva = L["curva"].lower()
    dec = (ASSETS.get((L.get("quote") or "").lower()) or {}).get("decimali", 18)
    fuori = {}
    for topic, verso in ((CP.T_COMPRA, "compra"), (CP.T_VENDE, "vende")):
        log = CP.log_di_finestra(topic, L["blocco"], min(bn, L["blocco"] + 9_999_999),
                                 indirizzo=curva)
        if log is None:
            return None, "la chain non ha risposto"
        righe = []
        for x in log:
            r = CP._riga(x, verso, {curva: (None, dec)})
            if r and r["gettoni"] > 0 and r["valuta"] > 0:
                righe.append(r)
        fuori[verso] = righe
    return fuori, None


def main():
    global ASSETS
    _t, lanci = AR.leggi("curva_lanci")
    ASSETS = _t.get("assets") or {}
    d = json.load(open(f"{BASE}/entrare_prima_del_diploma.json"))["monete"]
    st = json.load(open(f"{BASE}/prova_in_avanti.json"))["posizioni"]
    chiuse = [t for t, p in st.items() if p["stato"] == "chiusa"]
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    # i lanci recenti, come negli altri agenti
    primi = min(st[t]["primo_blocco"] for t in chiuse)
    b = primi - 400_000
    while b < bn:
        fine = min(bn, b + 9_999_999)
        lg = CP.log_di_finestra(CP.T_LANCIO, b, fine, indirizzo=CP.FABBRICA) or []
        for ev in lg:
            ind = [CP._indirizzo(x) for x in ev["topics"][1:]]
            if len(ind) >= 2:
                dd = ev.get("data", "0x")[2:]
                lanci[ind[0]] = {"curva": ind[1], "blocco": int(ev["blockNumber"], 16),
                                 "quote": ("0x" + dd[24:64]) if len(dd) >= 64 else None}
        b = fine + 1

    db = json.load(open(ARCH)) if os.path.exists(ARCH) else {"monete": {}}
    fatte = 0
    for tok in chiuse:
        if tok in db["monete"] or fatte >= QUANTE:
            continue
        L = lanci.get(tok.lower())
        if not L:
            db["monete"][tok] = {"non_misurabile": "lancio sconosciuto"}
        else:
            r, err = una_curva(tok, L, bn)
            if r is None:
                db["monete"][tok] = {"non_misurabile": err}
            else:
                v, c = r["vende"], r["compra"]
                vv = sorted(x["valuta"] * PREZZO_ETH for x in v)
                db["monete"][tok] = {
                    "acquisti": len(c), "vendite": len(v),
                    "venditori_distinti": len({x["chi_compra"] for x in v}),
                    "vendita_mediana_$": round(statistics.median(vv), 2) if vv else None,
                    "vendita_massima_$": round(vv[-1], 2) if vv else None,
                    "vendite_sopra_50$": sum(1 for x in vv if x >= 50),
                    "vendite_sopra_200$": sum(1 for x in vv if x >= 200),
                    "ultima_vendita_prima_del_diploma":
                        bool(v) and v[-1]["blocco"] >= (c[-1]["blocco"] - 1200) if c else None,
                }
        fatte += 1
        json.dump(db, open(ARCH, "w"), indent=1)

    buone = [v for v in db["monete"].values() if v.get("vendite") is not None]
    print(f"SI PUO' VENDERE | {len(buone)} curve lette per intero\n")
    if not buone:
        return 1
    mai = [v for v in buone if v["vendite"] == 0]
    print(f"curve su cui NESSUNO ha mai venduto: {len(mai)} su {len(buone)}")
    for nome, ch in (("vendite per curva", "vendite"),
                     ("venditori distinti", "venditori_distinti"),
                     ("vendita mediana in $", "vendita_mediana_$"),
                     ("vendita MASSIMA in $", "vendita_massima_$"),
                     ("vendite sopra 50 $", "vendite_sopra_50$"),
                     ("vendite sopra 200 $", "vendite_sopra_200$")):
        x = sorted(v[ch] for v in buone if v.get(ch) is not None)
        if x:
            print(f"   {nome:<26} mediana {statistics.median(x):>9.1f}   min {x[0]:>8.1f}   "
                  f"max {x[-1]:>10.1f}")
    fino = [v for v in buone if v.get("ultima_vendita_prima_del_diploma")]
    print(f"\ncurve dove si vendeva ancora POCO PRIMA del diploma: {len(fino)} su {len(buone)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
