"""La coppia scelta su robinhood, applicata a base senza ritoccare niente.

PERCHE' QUESTO E' IL TEST E NON LA CELEBRAZIONE. Su robinhood la pila di cinque filtri
dichiarati prima dava il massimo (+1,0%) al SECONDO passo, e poi peggiorava. L'ordine era
dichiarato prima, il PUNTO DI ARRESTO no. Fermarsi dove il numero e' piu' bello e' il modo
in cui si trova sempre qualcosa cercando: la regola «insider_storia + pressione_numero» e'
nata da una curva guardata.

IN POSITIVO: una regola nata guardando una chain si prova sull'ALTRA, con le soglie
ricalcolate sul suo pezzo di scelta e il conto letto sul suo pezzo mai visto. Se regge,
non e' il punto di arresto che l'ha fatta: e' l'attributo.
"""
import os
import numpy as np
from combinazioni import carica

MORTA = -0.99
COPPIA = ["insider_storia", "pressione_numero"]


def main():
    chain = os.environ.get("CHAIN", "base")
    righe = [x for x in carica(chain) if x.get("insider_quanti_noti")]
    n = len(righe)
    a = int(n * 0.72)
    scelgo, giudico = righe[:a], righe[a:]
    e = np.array([x["_bersaglio"] for x in giudico])
    masc = np.ones(len(giudico), bool)
    print(f"RIPETIZIONE | {chain}: la coppia nata su robinhood, soglie dal suo pezzo "
          f"di scelta ({len(scelgo):,}), conto su {len(giudico):,} mai visti")
    for k in COPPIA:
        v_sc = np.array([float(x.get(k) or 0.0) for x in scelgo])
        taglio = float(np.quantile(v_sc, 0.20))
        v = np.array([float(x.get(k) or 0.0) for x in giudico])
        masc = masc & (v > taglio)
        print(f"   + {k} > {taglio:+.4g}")
    ee = e[masc]
    print(f"\n   {'':<22} {'pool':>7} {'medio':>9} {'mediano':>9} {'muoiono':>9}")
    print(f"   {'tutto il mercato':<22} {len(e):7,} {np.mean(e):8.1%} "
          f"{np.median(e):8.1%} {np.mean(e <= MORTA):8.1%}")
    if len(ee) < 200:
        print(f"   la coppia lascia {len(ee):,} pool: troppo poco per giudicare")
        return
    print(f"   {'con la coppia':<22} {len(ee):7,} {np.mean(ee):8.1%} "
          f"{np.median(ee):8.1%} {np.mean(ee <= MORTA):8.1%}")
    print(f"\n   copre {len(ee)/len(e):.1%} · scarto {(np.mean(ee)-np.mean(e))*100:+.1f} punti "
          f"· distanza da zero {np.mean(ee)*100:+.1f} punti")


if __name__ == "__main__":
    main()
