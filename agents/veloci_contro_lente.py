"""Le curve VELOCI a riempirsi pagano piu' delle lente? Sullo storico, non solo sul vivo.

L'INTUIZIONE DI NICOLO' (12/10): «quelli che arrivano prima a quella cifra hanno piu' pressione
d'acquisto, quindi possiamo scartare gli altri e prendere solo i forti.»

Sul vivo il segnale c'e': le curve che toccano 1,5 nativi in un minuto fanno +50% molto piu'
spesso di quelle che ci mettono tre minuti e mezzo (13 colpi grossi contro 24 altri, velocita'
3,3 volte maggiore). Ma e' una differenza trovata confrontando SEI caratteristiche su 37 casi:
su sei tentativi una differenza capita per caso con facilita'.

Qui si rifa' sullo storico, su curve diverse e piu' numerose, ricostruite dalla chain: per
ognuna si calcola in quanto tempo la riserva netta ha toccato la soglia, e cosa ha fatto il
prezzo dopo. Se il legame regge su un campione nuovo, non e' rumore.

ATTENZIONE AL CAMPIONE: si prendono TUTTE le curve native nate in una finestra, non solo quelle
diplomate. Prendere solo le diplomate sarebbe guardare i sopravvissuti, ed e' l'errore che in
questo progetto e' costato quattro numeri ritirati.
"""
import json
import os
import statistics
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import curva_pons as CP                                        # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
ARCH = f"data/multichain/{CHAIN}/veloci_contro_lente.json"
SOGLIA = float(os.environ.get("SOGLIA_NATIVI", "1.5"))
ZERO = "0x" + "0" * 40
ORE_INDIETRO = float(os.environ.get("ORE_INDIETRO", "30"))
QUANTE = int(os.environ.get("QUANTE", "40"))


def una(cur, nato, bn):
    ev = []
    for topic, verso in ((CP.T_COMPRA, "compra"), (CP.T_VENDE, "vende")):
        lg = CP.log_di_finestra(topic, nato, min(bn, nato + 400_000), indirizzo=cur)
        if lg is None:
            return None
        for x in lg:
            r = CP._riga(x, verso, {cur: (None, 18)})
            if r and r["valuta"] > 0 and r["gettoni"] > 0:
                ev.append((r["blocco"], int(x.get("logIndex", "0x0"), 16), verso,
                           r["valuta"], r["valuta"] / r["gettoni"]))
    if len(ev) < 5:
        return None
    ev.sort()
    ris = 0.0
    entrata = None
    b_entrata = None
    dopo = []
    for b, _o, verso, val, prezzo in ev:
        ris = ris + val if verso == "compra" else ris - val
        if entrata is None and ris >= SOGLIA and verso == "compra":
            entrata, b_entrata = prezzo, b
            continue
        if entrata:
            dopo.append(prezzo / entrata)
    if entrata is None or len(dopo) < 3:
        return None
    return {"minuti_per_la_soglia": round((b_entrata - nato) / 600, 2),
            "massimo_dopo": round(max(dopo), 3),
            "minimo_dopo": round(min(dopo), 3),
            "scambi_dopo": len(dopo)}


def main():
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    a = bn - int(ORE_INDIETRO * 36000)
    b = a + 300_000
    lg = CP.log_di_finestra(CP.T_LANCIO, a, b, indirizzo=CP.FABBRICA) or []
    nate = []
    for ev in lg:
        ind = [CP._indirizzo(x) for x in ev["topics"][1:]]
        if len(ind) < 2:
            continue
        d = ev.get("data", "0x")[2:]
        q = ("0x" + d[24:64]).lower() if len(d) >= 64 else None
        if q not in (ZERO, None):
            continue
        nate.append((ind[1].lower(), int(ev["blockNumber"], 16)))
    print(f"VELOCI | {len(nate)} curve native nate fra {ORE_INDIETRO:.0f} e "
          f"{ORE_INDIETRO-8:.0f} ore fa", flush=True)
    db = json.load(open(ARCH)) if os.path.exists(ARCH) else {}
    fatte = 0
    for cur, nato in nate:
        if cur in db or fatte >= QUANTE:
            continue
        r = una(cur, nato, bn)
        db[cur] = r or {"niente": True}
        fatte += 1
        json.dump(db, open(ARCH, "w"), indent=1)
    buone = [v for v in db.values() if v and not v.get("niente")]
    print(f"VELOCI | {len(buone)} curve hanno superato {SOGLIA} nativi e hanno un seguito\n")
    if len(buone) < 8:
        return 0
    med = statistics.median(v["minuti_per_la_soglia"] for v in buone)
    vel = [v for v in buone if v["minuti_per_la_soglia"] <= med]
    len_ = [v for v in buone if v["minuti_per_la_soglia"] > med]
    print(f"{'gruppo':<28}{'quante':>8}{'minuti alla soglia':>20}{'tocca +50%':>13}{'tocca 2x':>11}")
    for nome, g in (("VELOCI (sotto la mediana)", vel), ("lente (sopra la mediana)", len_)):
        if not g:
            continue
        m = statistics.median(x["minuti_per_la_soglia"] for x in g)
        c50 = sum(1 for x in g if x["massimo_dopo"] >= 1.5)
        c2 = sum(1 for x in g if x["massimo_dopo"] >= 2.0)
        print(f"{nome:<28}{len(g):>8}{m:>20.2f}{c50:>8}/{len(g):<4}{c2:>7}/{len(g)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
