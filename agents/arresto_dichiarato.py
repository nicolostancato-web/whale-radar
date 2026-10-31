"""Il punto di arresto si sceglie sul pezzo di SCELTA, e i costi si contano.

LE DUE COSE CHE MANCAVANO A A_ZERO_NON_SOTTO.md, dichiarate qui prima di girare.

1. IL PUNTO DI ARRESTO. Ieri la pila di cinque filtri dava il massimo al secondo passo
   (+1,0% -> -1,1% -> -2,1%) e io ho riferito il secondo. L'ordine era dichiarato prima, il
   punto di arresto no: fermarsi dove il numero e' piu' bello e' il modo in cui si trova
   sempre qualcosa cercando.
   IN POSITIVO: quante soglie impilare si decide sul pezzo di SCELTA — il miglior k secondo
   quel pezzo — e poi si legge il pezzo mai visto UNA volta sola, con quel k. Se il k scelto
   sulla scelta non e' quello migliore sul giudizio, lo si vede e si dice.

2. I COSTI. «A cavallo dello zero» prima dei costi vuol dire sotto zero dopo. I livelli si
   dichiarano QUI, prima di guardare: andata+ritorno all'1%, 2% e 5%. L'1% e' circa la sola
   commissione di scambio sulle due gambe; il 5% e' quello che uccise crypto-radar, dove lo
   slittamento su monete sottili mangio' tutto.
   Il costo si applica al capitale, quindi va sottratto al rendimento lordo — e NON si applica
   a chi e' morto: se la pool va a zero hai perso tutto comunque, non -100% meno il 2%.
"""
import os
import numpy as np
from combinazioni import carica

MORTA = -0.99
MIN_POOL = 300
COSTI = [0.0, 0.01, 0.02, 0.05]
ORDINE = {
    "robinhood": ["insider_storia", "pressione_numero", "quota_acquisti",
                  "quota_solo_compra", "pressione_delta"],
    "base": ["insider_storia", "pers_quota_prima", "impatto_tipico", "gap_mediano"],
}


def al_netto(e, costo):
    """Il rendimento dopo il costo di andata e ritorno. Chi e' morto resta morto."""
    out = e - costo
    out[e <= MORTA] = e[e <= MORTA]
    return out


def pile(righe, ordine, soglie):
    """La maschera cumulativa per ogni k, da 0 a len(ordine)."""
    masc = np.ones(len(righe), bool)
    fuori = [masc.copy()]
    for k in ordine:
        v = np.array([float(x.get(k) or 0.0) for x in righe])
        prova = masc & (v > soglie[k])
        if prova.sum() < MIN_POOL:
            break
        masc = prova
        fuori.append(masc.copy())
    return fuori


def main():
    chain = os.environ.get("CHAIN", "robinhood")
    ing = os.environ.get("ENTRATA_SCAMBIO", "5")
    righe = [x for x in carica(chain) if x.get("insider_quanti_noti")]
    n = len(righe)
    a, b = int(n * 0.45), int(n * 0.72)
    cerco, scelgo, giudico = righe[:a], righe[a:b], righe[b:]
    if len(righe) < 3 * MIN_POOL:
        # FALLIRE DICENDO PERCHE' (4/10). Qui c'era np.quantile su una lista vuota, e
        # l'errore parlava di «index -1 out of bounds»: venti righe di traccia che non
        # nominano la causa. La causa era che lo storico dei compratori non era sul disco,
        # quindi NESSUNA riga aveva `insider_quanti_noti` e il mazzo era vuoto.
        # Un programma che muore senza dire perche' costa piu' di uno che non gira.
        raise SystemExit(
            f"ARRESTO | {chain}: solo {len(righe):,} pool col passato dei compratori noto. "
            f"Serve data/multichain/{chain}/insider.json.gz: senza quello l'attributo "
            f"insider_storia non esiste e non c'e' niente da filtrare.")
    ordine = ORDINE[chain]
    # le soglie vengono dal pezzo di RICERCA, mai dai due dopo
    soglie = {k: float(np.quantile(
        np.array([float(x.get(k) or 0.0) for x in cerco]), 0.20)) for k in ordine}

    e_s = np.array([x["_bersaglio"] for x in scelgo])
    e_g = np.array([x["_bersaglio"] for x in giudico])
    m_s, m_g = pile(scelgo, ordine, soglie), pile(giudico, ordine, soglie)
    print(f"ARRESTO | {chain} ingresso {ing}: soglie dal pezzo di ricerca "
          f"({len(cerco):,}), k dal pezzo di scelta ({len(scelgo):,}), "
          f"conto su {len(giudico):,} mai visti")

    # il k si scegli sul pezzo di scelta, al costo del 2% (livello centrale dichiarato)
    punteggi = [float(np.mean(al_netto(e_s[m], 0.02))) if m.sum() >= MIN_POOL else -9.0
                for m in m_s]
    k = int(np.argmax(punteggi))
    print(f"   k scelto sul pezzo di scelta: {k} filtri "
          f"(punteggi: {', '.join(f'{p:+.1%}' for p in punteggi)})")
    if k >= len(m_g):
        print("   quel k non e' disponibile sul pezzo di giudizio")
        return
    print(f"   filtri attivi: {' + '.join(ordine[:k]) if k else '(nessuno)'}")

    masc = m_g[k]
    print(f"\n   {'costo a/r':>10} {'mercato':>10} {'con i filtri':>14} {'scarto':>9}")
    for c in COSTI:
        tutto = float(np.mean(al_netto(e_g, c)))
        filtrato = float(np.mean(al_netto(e_g[masc], c)))
        print(f"   {c:9.0%} {tutto:10.1%} {filtrato:14.1%} "
              f"{(filtrato - tutto)*100:+8.1f}")
    print(f"\n   copre {masc.sum()/len(e_g):.1%} ({int(masc.sum()):,} pool) · "
          f"muoiono {np.mean(e_g[masc] <= MORTA):.1%} contro "
          f"{np.mean(e_g <= MORTA):.1%}")
    # e si dice se il k scelto era quello giusto anche sul giudizio: onesta', non vanto
    veri = [float(np.mean(al_netto(e_g[m], 0.02))) if m.sum() >= MIN_POOL else -9.0
            for m in m_g]
    kv = int(np.argmax(veri))
    print(f"   il k migliore sul pezzo mai visto sarebbe stato {kv} "
          f"({veri[kv]:+.1%} contro {veri[k]:+.1%} col k scelto in anticipo)")


if __name__ == "__main__":
    main()
