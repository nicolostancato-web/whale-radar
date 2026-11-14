"""Metro del peso del repository.

PERCHE' ESISTE (10/10, lezione pagata lo stesso giorno):
ho stimato la crescita a 1,70 GB/giorno contando le riscritture dei file grossi
nei commit delle ultime 24 ore, e ne ho dedotto "0,9 giorni di margine". Era
SBAGLIATO: 34 di quelle 49 riscritture erano commit di FUSIONE, che rielencano il
file senza cambiarne il contenuto, e git un contenuto identico lo conserva una
volta sola. La stima gonfiava la crescita di quasi quattro volte.

LA REGOLA, in positivo: la crescita si MISURA registrando il peso nel tempo e
guardando la differenza fra due letture vere. Non si deduce dai commit.
"""
import json, os, re, sys, time, urllib.request

ARCHIVIO = "data/peso_repository.jsonl"
LIMITE_GB = 10.0

def chiave():
    p = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
    return re.search(r'ghp_[A-Za-z0-9]+', open(p).read()).group(0)

def peso_ora(tok):
    r = urllib.request.Request("https://api.github.com/repos/nicolostancato-web/whale-radar",
                               headers={"Authorization": f"token {tok}"})
    return json.load(urllib.request.urlopen(r, timeout=60))["size"] / 1e6  # GB

def leggi():
    if not os.path.exists(ARCHIVIO):
        return []
    fuori = []
    for riga in open(ARCHIVIO):
        riga = riga.strip()
        if riga:
            try: fuori.append(json.loads(riga))
            except json.JSONDecodeError: pass   # una riga troncata non deve uccidere il metro
    return fuori

def main():
    tok = chiave()
    gb = peso_ora(tok)
    ora = int(time.time())
    with open(ARCHIVIO, "a", buffering=1) as f:
        f.write(json.dumps({"quando": ora, "gb": round(gb, 4)}) + "\n")

    st = leggi()
    print(f"PESO | {gb:.2f} GB su {LIMITE_GB:.0f} — margine {LIMITE_GB-gb:.2f} GB ({len(st)} letture)")

    # IL PESO SI MUOVE A SCATTI, NON IN MODO CONTINUO (10/10, secondo errore dello stesso metro).
    # Le letture di oggi: 8,39 -> 9,00 -> 8,99 -> 9,06. GitHub ricalcola quel numero quando gli
    # pare, non quando scriviamo: fra due letture a cavallo di uno scatto il "ritmo" risultava
    # +21 GB al giorno, e il metro ha stampato «il limite arriva fra 0,2 giorni». Falso allarme,
    # e un falso allarme e' grave come un falso via libera.
    # LA REGOLA, in positivo: su una misura a scatti si legge la DIFFERENZA fra due letture
    # lontane (almeno mezza giornata), e si dichiara che e' una differenza, non una velocita'.
    ORE_MINIME = 12
    lontane = [x for x in st if ora - x["quando"] >= ORE_MINIME * 3600]
    if not lontane:
        piu = max((ora - x["quando"]) / 3600 for x in st) if st else 0
        salti = sum(1 for a, b in zip(st, st[1:]) if abs(b["gb"] - a["gb"]) > 0.02)
        print(f"PESO | la differenza non e' ancora leggibile: servono {ORE_MINIME}h fra due "
              f"letture (la piu' vecchia e' di {piu:.1f}h). Scatti visti finora: {salti}.")
        if LIMITE_GB - gb < 0.5:
            print(f"PESO | ATTENZIONE comunque: il margine e' sotto il mezzo giga.")
        return 0
    v = lontane[0]
    ore = (ora - v["quando"]) / 3600
    diff = gb - v["gb"]
    print(f"PESO | in {ore:.0f}h e' cambiato di {diff:+.2f} GB "
          f"(da {v['gb']:.2f} a {gb:.2f}) — questa e' una differenza, non una velocita'")
    if diff > 0.05:
        print(f"PESO | se continuasse cosi', il margine di {LIMITE_GB-gb:.2f} GB basta per "
              f"circa {(LIMITE_GB-gb)/diff*ore/24:.1f} giorni")
    else:
        print("PESO | non cresce in modo apprezzabile")
    return 0


if __name__ == "__main__":
    sys.exit(main())
