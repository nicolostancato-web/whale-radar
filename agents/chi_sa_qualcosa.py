"""Chi compra curve che poi crescono? Misurato IN AVANTI, non sul passato.

L'IDEA DI NICOLO' (13/10): «guardiamo i wallet che casualmente partecipano sempre nel comprare
quelli che fanno tante X».

PERCHE' SI MISURA IN AVANTI E NON ALL'INDIETRO. Guardando il passato ho gia' trovato un indirizzo
presente in 4 monete forti su 10 e in zero deboli — ma era uno su ventiquattro esaminati, e
trovare un 4-0 fra ventiquattro succede per caso con facilita'. E' lo stesso errore che in questo
progetto e' costato cinque numeri ritirati: scegliere il candidato guardando dove ha gia' vinto.
Qui invece si registra cosa compra OGNUNO adesso, e si guarda dopo come e' andata. Nessuna
selezione, nessun senno di poi.

COME: a ogni giro si leggono gli acquisti recenti e si segna, per ogni compratore, su quale curva
e' entrato e quanta riserva aveva quella curva in quel momento. Ai giri successivi si rilegge la
riserva delle stesse curve: la differenza e' quanto la scelta e' "cresciuta". Si confronta con la
crescita media di tutte le curve comprate nello stesso periodo — altrimenti si premierebbe chi
compra quando il mercato intero sale.
"""
import json
import os
import statistics
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import curva_pons as CP                                        # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
ARCH = f"data/multichain/{CHAIN}/chi_sa_qualcosa.json"
FINESTRA = 30_000
GIRI = int(os.environ.get("GIRI", "2"))
ORE_PER_GIUDICARE = 1.0


def main():
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("SMART | la chain non risponde")
        return 1
    db = json.load(open(ARCH)) if os.path.exists(ARCH) else {
        "ultimo_blocco": None, "scelte": [], "riserve": {}}

    da = (db["ultimo_blocco"] or bn - FINESTRA) + 1
    a = min(bn, da + FINESTRA * GIRI)
    nuove = 0
    for i in range(GIRI):
        x0, x1 = da + FINESTRA * i, min(a, da + FINESTRA * (i + 1))
        if x1 <= x0:
            break
        lg = CP.log_di_finestra(CP.T_COMPRA, x0, x1)
        if lg is None:
            print(f"SMART | finestra {x0:,}-{x1:,} non letta: non avanzo")
            return 0
        # riserva corrente di ogni curva, aggiornata con cio' che si legge
        for ev in sorted(lg, key=lambda y: (int(y["blockNumber"], 16),
                                            int(y.get("logIndex", "0x0"), 16))):
            cur = ev["address"].lower()
            r = CP._riga(ev, "compra", {cur: (None, 18)})
            if not r or r["valuta"] <= 0:
                continue
            db["riserve"][cur] = round(db["riserve"].get(cur, 0.0) + r["valuta"], 5)
            chi = (r.get("chi_riceve") or r.get("chi_compra") or "").lower()
            db["scelte"].append({"chi": chi, "curva": cur, "blocco": r["blocco"],
                                 "riserva_allora": db["riserve"][cur]})
            nuove += 1
        lv = CP.log_di_finestra(CP.T_VENDE, x0, x1) or []
        for ev in lv:
            cur = ev["address"].lower()
            r = CP._riga(ev, "vende", {cur: (None, 18)})
            if r and r["valuta"] > 0 and cur in db["riserve"]:
                db["riserve"][cur] = round(db["riserve"][cur] - r["valuta"], 5)
    db["ultimo_blocco"] = a

    # il giudizio: le scelte abbastanza vecchie si confrontano con la riserva di adesso
    vecchie = [s for s in db["scelte"] if a - s["blocco"] >= ORE_PER_GIUDICARE * 36000]
    per_chi = {}
    cresc = []
    for s in vecchie:
        ora = db["riserve"].get(s["curva"])
        if ora is None:
            continue
        d = ora - s["riserva_allora"]
        cresc.append(d)
        per_chi.setdefault(s["chi"], []).append(d)
    json.dump(db, open(ARCH, "w"), indent=1)
    print(f"SMART | {nuove} scelte nuove, {len(db['scelte'])} in tutto, "
          f"{len(vecchie)} abbastanza vecchie per giudicarle")
    if len(cresc) < 30:
        print("SMART | troppo poche per una classifica: servono 30 scelte giudicabili")
        return 0
    medio = statistics.median(cresc)
    print(f"SMART | crescita mediana di una scelta qualunque dopo "
          f"{ORE_PER_GIUDICARE:.0f}h: {medio:+.3f} nativi")
    brav = [(statistics.median(v), len(v), k) for k, v in per_chi.items() if len(v) >= 4]
    brav.sort(reverse=True)
    if brav:
        print(f"\n   chi sceglie meglio (almeno 4 scelte giudicate):")
        for m, n, k in brav[:6]:
            print(f"      {k[:20]}…  {n:>3} scelte   crescita mediana {m:+.3f}  "
                  f"({'MEGLIO' if m > medio else 'peggio'} della media)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
