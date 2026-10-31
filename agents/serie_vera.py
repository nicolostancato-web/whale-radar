"""La storia vera del prezzo di ogni moneta, letta dalla chain.

PERCHE' (15/10). I cammini registrati dalle posizioni NON sono la storia del prezzo: sono
quello che una singola posizione ha visto. Segnano un punto solo quando il prezzo si muove
del 2% rispetto al loro riferimento, e smettono quando quella posizione chiude. Misurato: la
stessa moneta, la stessa regola, applicata ai cammini di strategie diverse, da' da -20% a
+34%. Qualunque ricerca fatta li' sopra cerca dentro un riflesso deformato.

Qui si legge dalla chain OGNI scambio della curva di una moneta — acquisti e vendite, in
ordine — e si costruisce una serie sola, indipendente da qualunque strategia. Col filtro
sull'indirizzo della curva la chain accetta finestre da 10 milioni di blocchi, quindi due
chiamate per moneta bastano a coprirne tutta la vita.

COSTO ZERO: RPC pubblico, nessuna chiave.
"""
import json
import os
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import curva_pons as CP                                        # noqa: E402

USCITA = "data/multichain/robinhood/serie_vera.jsonl"
FATTE = "data/multichain/robinhood/serie_vera_fatte.json"
BUDGET = int(os.environ.get("BUDGET_SEC", "600"))


def serie_di(curva, da, a):
    """Tutti gli scambi di una curva, in ordine di blocco, come (blocco, prezzo, verso)."""
    fuori = []
    for topic, verso in ((CP.T_COMPRA, "compra"), (CP.T_VENDE, "vende")):
        ev = CP.log_di_finestra(topic, da, a, indirizzo=curva)
        if ev is None:
            return None
        for l in ev:
            d = l["data"][2:]
            if len(d) < 128:
                continue
            x, y = int(d[:64], 16), int(d[64:128], 16)
            if x == 0 or y == 0:
                continue
            # CurveBuy: entra valuta (x), escono gettoni (y). CurveSell: entrano gettoni (x),
            # esce valuta (y). Il prezzo e' sempre valuta per gettone.
            prezzo = (x / y) if verso == "compra" else (y / x)
            fuori.append([int(l["blockNumber"], 16),
                          int(l.get("logIndex", "0x0"), 16), prezzo, verso])
    fuori.sort(key=lambda r: (r[0], r[1]))
    return [[r[0], r[2], r[3]] for r in fuori]


def main():
    st = json.load(open("data/multichain/robinhood/prova_nella_curva.json"))
    coppie = {}
    for p in st["posizioni"].values():
        if p.get("gettone") and p.get("curva"):
            coppie.setdefault(p["gettone"], (p["curva"], p.get("blocco_entrata", 0)))
    fatte = json.load(open(FATTE)) if os.path.exists(FATTE) else {}
    resta = [(g, c, b) for g, (c, b) in coppie.items() if g not in fatte]
    print(f"SERIE VERA | {len(coppie)} monete in tutto, {len(resta)} ancora da leggere")
    t0 = time.time()
    nuove = 0
    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    with open(USCITA, "a") as f:
        for g, c, b in resta:
            if time.time() - t0 > BUDGET:
                print("SERIE VERA | budget finito: riprendo al prossimo giro")
                break
            s = serie_di(c, max(b - 50_000, 0), b + 2_000_000)
            if s is None:
                print(f"   {g[:12]}… lettura fallita, riprovo al prossimo giro")
                continue
            f.write(json.dumps({"gettone": g, "curva": c, "serie": s}) + "\n")
            fatte[g] = len(s)
            nuove += 1
    tmp = FATTE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(fatte, f)
    os.replace(tmp, FATTE)
    print(f"SERIE VERA | lette {nuove} monete in questo giro, {len(fatte)} in archivio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
