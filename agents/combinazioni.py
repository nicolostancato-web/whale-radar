"""Cerca STRATEGIE fatte di condizioni incrociate, non manopole singole.

PERCHE' ESISTE (30/09). Decisione di Nicolo' del 23/09, che avevo perso per sette giorni:

  «Io mi aspetto una strategia mostruosa, dove si analizzano migliaia di combinazioni tutte
  perfette. Entriamo quando la pressione e' X%, poi si concatena con una percentuale costi
  cosi', oppure una percentuale di buyer che subentra in base alla liquidita', e poi si
  interseca questo settore. Una roba molto piu' complicata, tecnica, tutta fatta di parametri
  incrociati.»

Il 30/09 gli ho portato «compra al 5o scambio, $25, tieni una settimana»: UNA manopola.

LA TRAPPOLA DI QUESTO MESTIERE, E COME SI DISINNESCA.
Provando migliaia di combinazioni se ne trova SEMPRE una che sul passato sembra oro. Non e'
un rischio: e' una certezza matematica. Le tre difese, tutte obbligatorie:

  1. TRE PEZZI DI TEMPO, non due. Si cerca sul primo, si sceglie sul secondo, si giudica sul
     TERZO che non e' stato usato ne' per cercare ne' per scegliere.
  2. IL CONTROLLO SUL RUMORE. La stessa ricerca gira su esiti MESCOLATI, dove per costruzione
     non c'e' niente da trovare. Se la migliore sul vero non batte la migliore sul rumore,
     abbiamo trovato il rumore. Questo numero si stampa SEMPRE, anche quando e' scomodo.
  3. QUANTE NE HO PROVATE. Si dichiara. Una su mille che sembra buona, su mille provate, e'
     quello che ci si aspetta dal caso.

Le condizioni sono costruite solo su attributi noti PRIMA di comprare (nessun underscore):
e' il vincolo che agents/dati.py protegge da giorni.
"""
import gzip
import itertools
import json
import os
import sys

import numpy as np

MIN_POOL = 150          # sotto questo una combinazione non si giudica: e' aneddoto
MAX_CONDIZIONI = 3      # quante condizioni si incrociano al massimo
QUANTILI = (0.2, 0.5, 0.8)


COSTO = 0.018
RITARDO = int(os.environ.get("RITARDO", 1))   # scambi di latenza: 1 e' il minimo reale
# LA TAGLIA FA PARTE DELLA STRATEGIA (1/10): un vantaggio che esiste solo a $25 e muore a
# $100 non e' un vantaggio, e' una curiosita'. Misurato il 30/09: fra quelle due taglie
# ballano quindici punti di fondale.
SOLDI = float(os.environ.get("SOLDI", 25.0))


def esito_con_ritardo(x, soldi=None, ritardo=None):
    """L'esito comprando al prezzo OTTENIBILE, cioe' quello dello scambio successivo.

    IL PREZZO CHE VEDI NON E' QUELLO CHE PAGHI (30/09 notte). Il prezzo d'ingresso usato finora
    era quello dello scambio a cui entriamo: uno scambio avvenuto, ma non il nostro. Per comprare
    si manda una transazione, eseguita dopo quelle davanti.
    Misurato: con UN solo scambio di ritardo il fondale passa da +23,3% a −11,4% e la migliore
    combinazione da +207% a +0,9%. Cercare sul vecchio esito significa cercare l'irraggiungibile.
    """
    r = RITARDO if ritardo is None else ritardo
    soldi = SOLDI if soldi is None else soldi
    cam = x.get("_cammino") or []
    if len(cam) <= r:
        return None
    p = 1.0 if r == 0 else cam[r - 1][1]
    if p <= 0:
        return None
    riemp = inc = 0.0
    for _, pr, q in cam[r:]:
        if riemp >= soldi:
            break
        quota = min(q, soldi - riemp)
        riemp += quota
        inc += quota * (pr / p)
    if riemp <= 0:
        return -0.98
    u = inc / soldi - 1 - COSTO
    return max(-0.99, min(20.0, u))


def carica(chain, suffisso="_sc5"):
    p = f"data/loop1/insieme_{chain}{suffisso}.jsonl.gz"
    r = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
    r = [x for x in r if x.get("_giudicabile") and x.get("_cammino")]
    # l'esito su cui si cerca e' quello col prezzo ottenibile, non l'osservato
    for x in r:
        x["_bersaglio"] = esito_con_ritardo(x)
    r = [x for x in r if x["_bersaglio"] is not None]
    r.sort(key=lambda x: x["_t"])
    return r


def condizioni(righe, nomi):
    """Ogni condizione e' «attributo sopra/sotto una soglia», con la soglia presa dai quantili.

    Le soglie si calcolano SOLO sul pezzo di ricerca: prenderle su tutto sarebbe gia' guardare
    il futuro, in una forma sottile che non si vede finche' non la si nomina.
    """
    fuori = []
    for k in nomi:
        v = np.array([float(x.get(k) or 0.0) for x in righe])
        if not np.isfinite(v).all() or v.std() == 0:
            continue
        for q in QUANTILI:
            s = float(np.quantile(v, q))
            fuori.append((f"{k}>{s:.4g}", k, ">", s))
            fuori.append((f"{k}<{s:.4g}", k, "<", s))
    return fuori


def maschera(righe, cond):
    _, k, verso, s = cond
    v = np.array([float(x.get(k) or 0.0) for x in righe])
    return v > s if verso == ">" else v < s


def cerca(righe_cerca, righe_scegli, esiti_cerca, esiti_scegli, nomi, rimescola=False, seme=0):
    """Torna (descrizione, media sul pezzo di scelta, quante righe) della combinazione migliore."""
    if rimescola:
        rng = np.random.default_rng(seme)
        esiti_cerca = rng.permutation(esiti_cerca)
        esiti_scegli = rng.permutation(esiti_scegli)
    conds = condizioni(righe_cerca, nomi)
    mc = {c[0]: maschera(righe_cerca, c) for c in conds}
    ms = {c[0]: maschera(righe_scegli, c) for c in conds}
    # si tengono solo le condizioni che da sole promettono qualcosa sul pezzo di RICERCA
    buone = []
    for c in conds:
        m = mc[c[0]]
        if m.sum() < MIN_POOL:
            continue
        buone.append((float(esiti_cerca[m].mean()), c[0]))
    buone.sort(reverse=True)
    buone = [n for _, n in buone[:40]]            # le 40 piu' promettenti, per non esplodere
    provate = 0
    classifica = []
    for quante in range(1, MAX_CONDIZIONI + 1):
        for combo in itertools.combinations(buone, quante):
            provate += 1
            m = np.ones(len(righe_cerca), bool)
            for n in combo:
                m &= mc[n]
            if m.sum() < MIN_POOL:
                continue
            # promossa dalla ricerca: ora si MISURA sul pezzo di scelta, mai visto finora
            m2 = np.ones(len(righe_scegli), bool)
            for n in combo:
                m2 &= ms[n]
            if m2.sum() < MIN_POOL // 2:
                continue
            r = float(esiti_scegli[m2].mean())
            classifica.append((r, " E ".join(combo), int(m2.sum())))
    # LE DIECI MIGLIORI, NON LA PRIMA (30/09 notte). Con 10.700 combinazioni, la migliore sul
    # pezzo di scelta e' anche la piu' fortunata: giudicarla da sola confonde il talento con la
    # fortuna. Se il segnale c'e', le dieci migliori battono il fondale IN MEDIA sul terzo pezzo.
    # Se non c'e', si disperdono intorno al fondale — ed e' una risposta piu' solida di una sola.
    classifica.sort(reverse=True)
    return classifica[:10], provate


def main():
    chain = os.environ.get("CHAIN", "robinhood")
    righe = carica(chain)
    nomi = sorted(k for k in righe[0] if not k.startswith("_"))
    esiti = np.array([x["_bersaglio"] for x in righe])
    n = len(righe)
    a, b = int(n * 0.45), int(n * 0.72)
    # TRE PEZZI DI TEMPO: cerco / scelgo / giudico. Il terzo non lo tocco fino alla fine.
    rc, rs, rg = righe[:a], righe[a:b], righe[b:]
    ec, es, eg = esiti[:a], esiti[a:b], esiti[b:]
    print(f"COMBINAZIONI | {chain}: {n:,} pool — cerco su {len(rc):,}, scelgo su {len(rs):,}, "
          f"giudico su {len(rg):,} mai visti", flush=True)

    dieci, provate = cerca(rc, rs, ec, es, nomi)
    if not dieci:
        print("   nessuna combinazione con abbastanza pool: non si giudica", flush=True)
        return
    r_vero, desc, quanti = dieci[0]
    print(f"   provate {provate:,} combinazioni di 1-{MAX_CONDIZIONI} condizioni incrociate",
          flush=True)
    print(f"   migliore sul pezzo di scelta: {100*r_vero:+.1f}% su {quanti} pool", flush=True)
    print(f"   -> {desc}", flush=True)

    # IL CONTROLLO SUL RUMORE: la stessa ricerca dove per costruzione non c'e' niente da trovare.
    finti = []
    for s in range(5):
        d, _ = cerca(rc, rs, ec, es, nomi, rimescola=True, seme=s)
        if d:
            finti.append(d[0][0])
    soglia = float(np.max(finti))
    print(f"   sul RUMORE la migliore fa {100*np.mean(finti):+.1f}% in media, "
          f"{100*soglia:+.1f}% nel caso migliore su 5 prove", flush=True)

    if r_vero <= soglia:
        print(f"   VERDETTO: la migliore sul vero NON batte la migliore sul rumore. "
              f"Non abbiamo trovato niente.", flush=True)
        return

    # e solo se supera il rumore si apre il terzo pezzo, quello mai toccato
    conds = {c[0]: c for c in condizioni(rc, nomi)}
    print(f"\n   LE DIECI MIGLIORI, GIUDICATE SUL PEZZO MAI VISTO "
          f"(fondale {100*float(eg.mean()):+.1f}%):", flush=True)
    esiti_giudizio = []
    for r_s, d, _ in dieci:
        m = np.ones(len(rg), bool)
        for nome in d.split(" E "):
            if nome in conds:
                m &= maschera(rg, conds[nome])
        if m.sum() < MIN_POOL // 3:
            print(f"      {100*r_s:+7.1f}% -> solo {int(m.sum())} pool, non giudicabile",
                  flush=True)
            continue
        g = float(eg[m].mean())
        esiti_giudizio.append(g)
        print(f"      {100*r_s:+7.1f}% sulla scelta -> {100*g:+7.1f}% sul giudizio "
              f"({int(m.sum())} pool)   {d[:70]}", flush=True)
    if esiti_giudizio:
        med = float(np.mean(esiti_giudizio))
        fon = float(eg.mean())
        print(f"\n   IN MEDIA le dieci migliori fanno {100*med:+.1f}% contro un fondale di "
              f"{100*fon:+.1f}%: {'SEGNALE' if med > fon + 0.05 else 'NIENTE'}", flush=True)


if __name__ == "__main__":
    main()
