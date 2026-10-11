"""IMPATTO REALE — quanto muove il prezzo un ordine, misurato invece che modellato.

Secondo pezzo del loop 1. Sostituisce lo slippage fisso al 15% per lato del vecchio motore.

PERCHE' NON USIAMO UNA LIBRERIA (22/09). Le librerie per AMM calcolano l'impatto di un ordine
PARTENDO DALLE RISERVE del pool. Noi le riserve non le abbiamo — ed e' esattamente quello il buco.
Una formula esatta alimentata da dati che non possediamo non e' piu' affidabile: e' solo piu'
convincente, che in questo progetto e' peggio.
Ricostruire le riserve dagli scambi, come avevo proposto nella v1 del metodo, e' anche peggio: la
revisione esterna ha fatto notare che omette aggiunte e rimozioni di liquidita', e che una curva a
prodotto costante non descrive ogni pool. Il risultato sarebbe il fantasma di agosto con una
matematica piu' credibile addosso.

COSA FACCIAMO INVECE. Ogni scambio registra le quantita' scambiate (`a0`, `a1`): il loro rapporto
e' il prezzo REALIZZATO di quell'operazione. Da due scambi consecutivi nello stesso pool si ricava
di quanto si e' mosso il prezzo, e di quale dimensione era l'ordine che l'ha mosso.
Non e' un modello di come il mercato dovrebbe comportarsi: e' come si e' comportato.

IL LIMITE, DICHIARATO. Gli scambi che osserviamo sono quelli RIUSCITI, e per lo piu' piccoli.
Un nostro ordine potrebbe essere piu' grande di tutti quelli visti in quel pool: in quel caso la
misura non risponde, e deve dirlo invece di estrapolare. Per questo l'impatto si riporta insieme
alla dimensione massima osservata: sopra quella soglia si scrive «non misurato», non si stima.

E' la differenza fra «non lo so» e un numero inventato — che e' la stessa distinzione su cui si e'
giocata tutta la notte sul database.
"""
import gzip
import json
import math
import os
import sys

CHAIN = os.environ.get("CHAIN", "base")
MIN_SCAMBI = int(os.environ.get("MIN_SCAMBI", 30))
FUORI = f"data/loop1/impatto_{CHAIN}.json"


def prezzo(r):
    """Il prezzo realizzato di uno scambio: quanto si e' pagato per unita'."""
    try:
        a0, a1 = abs(float(r["a0"])), abs(float(r["a1"]))
    except Exception:
        return None, None
    if a0 <= 0 or a1 <= 0:
        return None, None
    return a1 / a0, a0          # prezzo, e la dimensione in unita' del token 0


def coppie_consecutive(righe):
    """Coppie (dimensione dell'ordine, movimento di prezzo che ha prodotto).

    Si usano solo scambi ADIACENTI nel tempo: fra due scambi lontani il prezzo si muove per mille
    ragioni che non c'entrano con la dimensione dell'ordine."""
    righe = [r for r in righe if r.get("blocco") and r.get("a0") and r.get("a1")]
    righe.sort(key=lambda r: (r["blocco"], r.get("li", 0)))
    fuori = []
    for prec, succ in zip(righe, righe[1:]):
        p0, _ = prezzo(prec)
        p1, dim = prezzo(succ)
        if not p0 or not p1 or not dim:
            continue
        # SOLO SCAMBI VICINI NEL TEMPO: oltre qualche blocco il movimento non e' piu' attribuibile
        if succ["blocco"] - prec["blocco"] > 5:
            continue
        mov = abs(p1 - p0) / p0
        if 0 < mov < 5:          # oltre il 500% non e' impatto, e' un altro fenomeno
            fuori.append((dim, mov))
    return fuori


def curva(punti):
    """Come cresce l'impatto con la dimensione: pendenza su scala logaritmica.

    Su una curva a prodotto costante l'impatto e' circa proporzionale alla dimensione relativa,
    quindi in scala logaritmica la relazione e' quasi una retta. Stimare la PENDENZA invece di una
    costante permette di dire qualcosa su ordini piu' grandi di quello mediano — ma solo fino al
    piu' grande che abbiamo visto davvero."""
    p = [(math.log(d), math.log(m)) for d, m in punti if d > 0 and m > 0]
    if len(p) < MIN_SCAMBI:
        return None
    n = len(p)
    mx = sum(x for x, _ in p) / n
    my = sum(y for _, y in p) / n
    num = sum((x - mx) * (y - my) for x, y in p)
    den = sum((x - mx) ** 2 for x, _ in p)
    if den <= 0:
        return None
    b = num / den
    a = my - b * mx
    return {"pendenza": round(b, 3), "intercetta": round(a, 3), "punti": n}


def main():
    cartelle = [f"data/multichain/{CHAIN}/{c}" for c in ("storico", "vivo")]
    per_pool = {}
    for c in cartelle:
        if not os.path.isdir(c):
            continue
        for fn in os.listdir(c):
            pool = fn.split(".")[0]
            try:
                righe = [json.loads(l) for l in gzip.open(os.path.join(c, fn), "rt") if l.strip()]
            except Exception:
                continue
            per_pool.setdefault(pool, []).extend(righe)

    misurati = 0
    saltati = 0
    fuori = {}
    tutti_mov = []
    for pool, righe in per_pool.items():
        punti = coppie_consecutive(righe)
        if len(punti) < MIN_SCAMBI:
            saltati += 1
            continue
        c = curva(punti)
        if not c:
            saltati += 1
            continue
        dims = sorted(d for d, _ in punti)
        movs = sorted(m for _, m in punti)
        fuori[pool] = {**c,
                       "dim_mediana": dims[len(dims) // 2],
                       # OLTRE QUESTA DIMENSIONE NON ABBIAMO VISTO NIENTE: sopra, si dichiara
                       # «non misurato» invece di estrapolare.
                       "dim_massima_osservata": dims[-1],
                       "impatto_mediano": round(movs[len(movs) // 2], 5),
                       "impatto_90": round(movs[int(len(movs) * 0.9)], 5)}
        tutti_mov.extend(movs)
        misurati += 1

    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    json.dump(fuori, open(FUORI, "w"))
    tutti_mov.sort()
    print(f"IMPATTO | {CHAIN}: {misurati} pool misurati, {saltati} senza abbastanza scambi")
    if tutti_mov:
        def q(p):
            return 100 * tutti_mov[int(len(tutti_mov) * p)]
        print(f"   movimento di prezzo per scambio, su {len(tutti_mov)} osservazioni vere:")
        print(f"      25%: {q(0.25):.2f}%   mediano: {q(0.5):.2f}%   "
              f"75%: {q(0.75):.2f}%   90%: {q(0.9):.2f}%")
        print(f"   il vecchio motore usava 15,00% fisso per TUTTI i pool e TUTTE le dimensioni.")
    if misurati == 0:
        print("   nessun pool con abbastanza scambi adiacenti: non si stima, si dichiara.")
        sys.exit(1)
    print(f"   scritto {FUORI}")


if __name__ == "__main__":
    main()
