"""Grida se una corsia ha un orologio e nessuna guardia. L'elenco si ricava, non si ricorda.

PERCHE' (4/10). Ieri ho dichiarato «28 corsie su 28 sorvegliate». Vero sulla mia lista e falso
sul mondo: le corsie con un orologio erano 39, e dieci non avevano nessuna guardia — fra cui
`database`, `ricerca` e `loop0`, cioe' il cuore del progetto. Una di quelle poteva fermarsi
per giorni senza che nessuno lo sapesse.
Terza ricaduta della famiglia del DENOMINATORE (dopo «le flotte comprano in scia», dove
5 pool su 6 nascevano da 73 finanziatori risolti su 11.275). Un rapporto senza il suo
denominatore non e' una misura.

IN POSITIVO: la verita' su quali corsie esistono sta nei file delle corsie, non nella mia
memoria. Qui si legge quella, e si confronta. Una lista che si ricava non puo' restare
indietro; una che si ricorda lo fa sempre.
"""
import glob
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)


def intervallo(cron):
    """Minuti fra due colpi d'orologio. Prudente: se non e' chiaro, il piu' corto."""
    p = cron.split()
    if len(p) < 5:
        return None
    mi, ho = p[0], p[1]
    if mi.startswith("*/"):
        return int(mi[2:])
    if ho.startswith("*/"):
        return int(ho[2:]) * 60
    n = len([x for x in mi.split(",") if x.strip()]) if mi != "*" else 60
    if ho == "*":
        return max(60 // max(n, 1), 1)
    nh = len([x for x in ho.split(",") if x.strip()])
    return max((24 * 60) // max(n * nh, 1), 1)


def con_orologio():
    fuori = {}
    for f in sorted(glob.glob(os.path.join(RADICE, ".github/workflows/*.yml"))):
        s = open(f, encoding="utf-8", errors="replace").read()
        nm = re.search(r"^name:\s*(\S+)", s, re.M)
        if not nm or not re.search(r"^\s*schedule:", s, re.M):
            continue
        crons = re.findall(r'- cron:\s*"([^"]+)"', s)
        iv = [i for i in (intervallo(c) for c in crons) if i]
        if iv:
            fuori[nm.group(1)] = min(iv)
    return fuori


def sorvegliate():
    p = os.path.join(QUI, "dal_di_fuori.sh")
    if not os.path.exists(p):
        return None
    m = re.search(r'CRITICHE="([^"]+)"', open(p, encoding="utf-8").read())
    if not m:
        return None
    return {v.split(":")[0]: int(v.split(":")[1]) for v in m.group(1).split()}


def main():
    orologi, viste = con_orologio(), sorvegliate()
    if viste is None:
        print("CORSIA NON VISTA | non trovo l'elenco delle guardie: CIECA, non tranquilla")
        return 0
    scoperte = sorted(set(orologi) - set(viste))
    print(f"CORSIA NON VISTA | {len(orologi)} corsie con l'orologio, "
          f"{len(viste)} nell'elenco delle guardie")
    for w in scoperte:
        print(f"   GRAVE  {w}: ha un orologio ogni ~{orologi[w]} min e NESSUNA guardia. "
              f"Aggiungere «{w}:{max(orologi[w]*3, 60)}» a CRITICHE in dal_di_fuori.sh")
    # un limite piu' corto dell'orologio fa rilanciare una corsia che sta solo aspettando
    for w, lim in sorted(viste.items()):
        if w in orologi and lim < orologi[w] * 2:
            print(f"   avviso {w}: limite {lim} min contro un orologio di {orologi[w]} — "
                  f"troppo stretto, la rilancia mentre aspetta il suo turno")
    if not scoperte:
        print("   tutte le corsie con un orologio hanno una guardia")
    return 1 if scoperte else 0


if __name__ == "__main__":
    sys.exit(main())
