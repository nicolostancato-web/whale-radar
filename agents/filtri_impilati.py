"""Impilare i filtri: quanto si avvicina a zero, e a che prezzo di copertura.

Ogni filtro si aggiunge SOLO se la sua soglia e' fissata sul pezzo di scelta e il
rendimento si legge sul pezzo mai visto. La copertura si stampa a ogni passo: la
tentazione qui e' impilare finche' il numero diventa positivo su quarantadue pool.
"""
import os
import numpy as np
from combinazioni import carica

MORTA = -0.99
MIN_POOL = 300
# scelti perche' hanno battuto il metro misurato sul bersaglio-azzeramento, non dopo
CANDIDATI = {
    "robinhood": ["insider_storia", "pressione_numero", "quota_acquisti",
                  "quota_solo_compra", "pressione_delta"],
    "base": ["insider_storia", "pers_quota_prima", "impatto_tipico", "gap_mediano"],
}


def main():
    chain = os.environ.get("CHAIN", "robinhood")
    righe = [x for x in carica(chain) if x.get("insider_quanti_noti")]
    n = len(righe)
    a = int(n * 0.72)
    scelgo, giudico = righe[:a], righe[a:]
    e = np.array([x["_bersaglio"] for x in giudico])
    print(f"IMPILATI | {chain}: soglie dal pezzo di scelta ({len(scelgo):,} pool), "
          f"conto sul pezzo mai visto ({len(giudico):,})\n")
    print(f"   {'filtri attivi':<52} {'pool':>7} {'copre':>7} {'medio':>8} {'muoiono':>8}")
    print(f"   {'(nessuno)':<52} {len(e):7,} {1.0:6.1%} {np.mean(e):7.1%} "
          f"{np.mean(e <= MORTA):7.1%}")
    masc = np.ones(len(giudico), bool)
    attivi = []
    for k in CANDIDATI.get(chain, []):
        v_sc = np.array([float(x.get(k) or 0.0) for x in scelgo])
        taglio = float(np.quantile(v_sc, 0.20))
        v = np.array([float(x.get(k) or 0.0) for x in giudico])
        prova = masc & (v > taglio)
        if prova.sum() < MIN_POOL:
            print(f"   + {k} > {taglio:+.3g}: scenderebbe a {int(prova.sum()):,} pool, "
                  f"sotto {MIN_POOL}: NON lo aggiungo")
            continue
        masc = prova
        attivi.append(k)
        ee = e[masc]
        print(f"   {' + '.join(attivi):<52} {len(ee):7,} {len(ee)/len(e):6.1%} "
              f"{np.mean(ee):7.1%} {np.mean(ee <= MORTA):7.1%}")
    ee = e[masc]
    if len(ee):
        print(f"\n   scarto totale contro il mercato: "
              f"{(np.mean(ee) - np.mean(e))*100:+.1f} punti, "
              f"copertura finale {len(ee)/len(e):.1%}")
        print(f"   distanza da zero: {np.mean(ee)*100:+.1f} punti")


if __name__ == "__main__":
    main()
