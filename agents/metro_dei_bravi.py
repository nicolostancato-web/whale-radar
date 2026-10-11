"""ESISTONO OPERATORI SISTEMATICAMENTE MIGLIORI? Il metro che regge, e i sei che non reggevano.

== LA DOMANDA ==

Fra chi compera memecoin appena nate sulla curva, c'e' qualcuno che guadagna in modo ripetibile,
o sono tutti sorteggi? Non basta trovare chi ha guadagnato: con 1.285 operatori, qualcuno guadagna
sempre. Serve sapere QUANTI ne spiegherebbe il caso.

== IL CRITERIO DI VALIDITA', FISSATO PRIMA DI GUARDARE I RISULTATI ==

Un metro vuoto e' valido solo se i portafogli FINTI partono dalla stessa mediana dei VERI
(scarto < 0,03). Se il finto tipico perde piu' del vero tipico, il metro dichiara bravo chiunque.

Il 6/10 ho costruito SEI metri e li ho buttati tutti, perche' nessuno passava questo criterio:

  1. rimescolare tutte le posizioni            finti 0,581x contro veri 0,848x   (-27 punti)
  2. appaiato per periodo e taglia             0,581x                            (-27)
  3. appaiato anche sul tipo di operatore      0,688x                            (-16)
  4. pescare il multiplo, tenere la puntata    0,689x                            (-16)
  5. peso uguale per portafoglio               0,595x                            (-25)

Il difetto comune: nel mazzo c'erano i portafogli CHE NON VENDONO MAI. Sono 451 su 1.841, comprano
50-130 monete e non ne vendono nessuna — **verificato sulla chain, non e' un buco dei nostri dati:
su 8 portafogli e 24 curve controllate, zero vendite mancanti.** E su una curva si puo' sempre
rivendere, anche in perdita: quindi non e' impossibilita', e' una scelta. Sono un comportamento
diverso, non un termine di paragone.

Il settimo metro confronta **chi vende con chi vende**, nello stesso periodo e nella stessa taglia:
finti 0,931x contro veri 0,943x, scarto **0,012**. Passa.

== IL RISULTATO (6/10/2026, copertura ancora parziale su 3 fette su 10) ==

  osservati  : 181 operatori su 1.285 guadagnano in ENTRAMBE le meta' della propria storia
  caso       : mediana 17, massimo 24 su venti giri
  eccesso    : 164 operatori oltre quelli che il caso spiega  (7,5 volte il massimo del caso)

Quindi **il vantaggio esiste**. Ma e' sottile: ritorno mediano dei 181 = 1,049x, il migliore
1,517x, solo 20 sopra 1,2x e uno solo sopra 1,5x.

**Non dimostra che sia copiabile.** Dimostra che non e' sorteggio.
"""
import collections
import glob
import gzip
import json
import math
import os
import random
import statistics
import sys
import time

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
SOMME = os.environ.get("SOMME", f"{BASE}/curva_somme_pezzo_*.json.gz")
FUORI = os.environ.get("FUORI", f"{BASE}/metro_dei_bravi.json")
MIN_OP = int(os.environ.get("MIN_OPERAZIONI", "50"))
TAGLIA = (float(os.environ.get("TAGLIA_MIN", "0.01")), float(os.environ.get("TAGLIA_MAX", "0.2")))
GIRI = int(os.environ.get("GIRI", "20"))
SCARTO_MAX = 0.03          # il criterio di validita', dichiarato qui e non altrove
NAT = "0x" + "0" * 40


def _sca(x):
    """Lo scaglione (periodo, taglia): si confronta solo chi aveva opportunita' comparabili."""
    return (int(x[0] // 500000), int(math.log10(max(1e-9, x[1])) * 4))


def main():
    pl = f"{BASE}/curva_lanci.json.gz"
    if not os.path.exists(pl):
        raise SystemExit(f"METRO | manca {pl}: senza l'elenco dei lanci non so la valuta "
                         f"di ogni curva ne' chi e' il lanciatore")
    dl = json.load(gzip.open(pl, "rt"))
    asset = {v["curva"].lower(): ((v.get("quote") or "").lower() or None)
             for v in dl["da"].values()}
    lanciatori = {(v.get("creatore") or "").lower() for v in dl["da"].values() if v.get("creatore")}

    P = collections.defaultdict(list)
    mai_vendono = collections.Counter()
    for p in sorted(glob.glob(SOMME, recursive=True)):
        try:
            d = json.load(gzip.open(p, "rt")).get("da", {})
        except Exception as e:
            print(f"   {os.path.basename(p)} illeggibile ({str(e)[:50]}): lo salto e lo dico")
            continue
        for k, v in d.items():
            w, cu = k.split("|")
            if asset.get(cu) != NAT or v.get("grezzo") or v["compra_valuta"] <= 0:
                continue
            if not (TAGLIA[0] <= v["compra_valuta"] <= TAGLIA[1]):
                continue
            if v["n_vende"] <= 0:
                mai_vendono[w] += 1
                continue
            if v["compra_gettoni"] <= 0:
                continue
            # i gettoni venduti devono essere quelli comprati: senza, il rapporto fra due cifre
            # di denaro non riguarda la stessa merce (il «157x» del 6/10 cadeva qui)
            if not (0.9 <= v["vende_gettoni"] / v["compra_gettoni"] <= 1.1):
                continue
            P[w].append((v.get("primo") or 0, v["compra_valuta"], v["vende_valuta"]))
        del d
    for w in list(P):
        if w in lanciatori:
            del P[w]
    V = {w: sorted(L) for w, L in P.items() if len(L) >= MIN_OP}
    if len(V) < 50:
        print(f"METRO | solo {len(V)} operatori con >= {MIN_OP} posizioni: troppo pochi per un "
              f"metro. Non scrivo un verdetto su niente.")
        return 0
    print(f"METRO | {len(V):,} operatori che vendono, con >= {MIN_OP} posizioni pulite "
          f"(esclusi {len(mai_vendono):,} che non vendono mai: comportamento diverso, "
          f"verificato sulla chain)", flush=True)

    mazzo = collections.defaultdict(list)
    for L in V.values():
        for x in L:
            mazzo[_sca(x)].append(x[2] / x[1])
    lista = list(V.values())
    rit = lambda L: sum(x[2] for x in L) / sum(x[1] for x in L)

    def regge(L, mm):
        h = len(L) // 2
        g = lambda S, M: sum(a[1] * b for a, b in zip(S, M)) / sum(a[1] for a in S)
        return g(L[:h], mm[:h]) > 1 and g(L[h:], mm[h:]) > 1

    oss = sum(1 for L in lista if regge(L, [x[2] / x[1] for x in L]))
    veri = [rit(L) for L in lista]
    esiti, med = [], []
    for s in range(GIRI):
        random.seed(1000 + s)
        n, rr = 0, []
        for L in lista:
            mm = [(random.choice(mazzo[_sca(x)]) if mazzo[_sca(x)] else x[2] / x[1]) for x in L]
            rr.append(sum(a[1] * b for a, b in zip(L, mm)) / sum(a[1] for a in L))
            if regge(L, mm):
                n += 1
        esiti.append(n)
        med.append(statistics.median(rr))
    mv, mf = statistics.median(veri), statistics.median(med)
    valido = abs(mv - mf) < SCARTO_MAX
    print(f"METRO | mediana veri {mv:.3f}x, finti {mf:.3f}x, scarto {abs(mv-mf):.3f} "
          f"-> {'VALIDO' if valido else 'NON VALIDO, il verdetto non si scrive'}", flush=True)
    if not valido:
        print(f"METRO | un metro che parte piu' in basso dichiara bravo chiunque. "
              f"Il 6/10 ne ho buttati sei per questo.")
        json.dump({"acq": int(time.time()), "valido": False, "mediana_veri": mv,
                   "mediana_finti": mf, "scarto": abs(mv - mf)}, open(FUORI, "w"), indent=1)
        return 0

    esiti.sort()
    buoni = [L for L in lista if regge(L, [x[2] / x[1] for x in L])]
    r = [rit(L) for L in buoni]
    print(f"METRO | OSSERVATI {oss} su {len(lista):,}  |  caso: min {esiti[0]}, "
          f"mediana {statistics.median(esiti):.0f}, max {esiti[-1]}", flush=True)
    print(f"METRO | eccesso {oss - int(statistics.median(esiti)):,} operatori, "
          f"{oss/max(1,esiti[-1]):.1f} volte il massimo del caso", flush=True)
    print(f"METRO | i {len(buoni)} che reggono: ritorno mediano {statistics.median(r):.3f}x, "
          f"migliore {max(r):.3f}x, sopra 1,2x: {sum(1 for x in r if x > 1.2)}", flush=True)

    classifica = sorted(((rit(L), w) for w, L in V.items() if regge(L, [x[2]/x[1] for x in L])),
                        reverse=True)
    json.dump({"acq": int(time.time()), "chain": CHAIN, "valido": True,
               "criterio_validita": f"scarto fra mediane < {SCARTO_MAX}",
               "mediana_veri": mv, "mediana_finti": mf, "scarto": abs(mv - mf),
               "operatori": len(lista), "min_operazioni": MIN_OP, "taglia": TAGLIA,
               "osservati": oss, "caso_min": esiti[0], "caso_mediana": statistics.median(esiti),
               "caso_max": esiti[-1], "giri": GIRI,
               "ritorno_mediano_dei_buoni": statistics.median(r), "migliore": max(r),
               "non_dimostra": ("che sia copiabile: dimostra che non e' sorteggio. "
                                "Serve il test del copiatore con regola congelata."),
               "primi_50": [{"portafoglio": w, "ritorno": t} for t, w in classifica[:50]]},
              open(FUORI, "w"), indent=1)
    print(f"METRO | scritto {FUORI}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
