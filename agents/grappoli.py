"""CHI COMPRA NELLA STESSA TRANSAZIONE E' UNA PERSONA SOLA.

== PERCHE' ESISTE (7/10/2026) ==

Il primo caso che ha passato i tre requisiti faceva 5,05x. Aprendo la sua transazione d'acquisto
ci ho trovato dentro **9 CurveBuy a 9 portafogli diversi**: una sola transazione che compra per
nove. E chi la firma era a sua volta nella mia classifica, a 4,10x.

Quindi i «nove vincenti» non erano nove persone brave: erano **una decisione sola**, pagata una
volta, ripetuta nove volte nel conteggio. Sul totale il fenomeno e' raro (12 portafogli su 1.594,
lo 0,8%) ma **in cima pesa**: 6 delle 31 posizioni sopra 2x venivano da quel singolo grappolo, il
19%.

Senza questa regola, una classifica di «chi fa piu' X» e' in parte la stessa persona contata nove
volte — ed e' esattamente il tipo di numero che mi ha fatto portare a Nicolo' dei portafogli che
non fanno soldi.

== COSA NON FA ==

Non pretende di trovare TUTTE le identita' multiple: chi usa portafogli diversi in transazioni
diverse qui non si vede (per quello serve il finanziatore comune, che e' un altro lavoro). Questa
regola cattura il caso certo — stessa transazione, stesso mandante — e lo dichiara. Una regola
che cattura il 19% e lo dice vale piu' di una che promette il 100%.
"""
import collections


def grappoli_da_transazioni(righe, chiave_chi="chi", chiavi_tx=("tx_compra",)):
    """Unisce i portafogli che compaiono nella stessa transazione. Torna (capo_di, grappoli).

    `capo_di[portafoglio]` e' il rappresentante del suo grappolo (se e' solo, e' se stesso).
    Si usa un'unione-insiemi: se A e B sono nella tx1 e B e C nella tx2, A, B e C sono uno.
    """
    padre = {}

    def trova(x):
        padre.setdefault(x, x)
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    def unisci(a, b):
        ra, rb = trova(a), trova(b)
        if ra != rb:
            padre[rb] = ra

    per_tx = collections.defaultdict(set)
    for r in righe:
        chi = r.get(chiave_chi)
        if not chi:
            continue
        trova(chi)
        for k in chiavi_tx:
            for h in (r.get(k) or []):
                per_tx[h].add(chi)
    for h, w in per_tx.items():
        w = sorted(w)
        for x in w[1:]:
            unisci(w[0], x)
    capo_di = {x: trova(x) for x in padre}
    grappoli = collections.defaultdict(set)
    for x, c in capo_di.items():
        grappoli[c].add(x)
    return capo_di, {c: w for c, w in grappoli.items() if len(w) > 1}


def referto(righe, chiave_chi="chi", chiavi_tx=("tx_compra",)):
    """Il referto da stampare: quanti sono, quanto pesano. Si dichiara sempre, anche se zero."""
    capo_di, gr = grappoli_da_transazioni(righe, chiave_chi, chiavi_tx)
    dentro = {x for w in gr.values() for x in w}
    tot = len({r.get(chiave_chi) for r in righe if r.get(chiave_chi)})
    return capo_di, gr, {
        "portafogli": tot,
        "grappoli": len(gr),
        "portafogli_in_grappolo": len(dentro),
        "quota_pct": round(100 * len(dentro) / max(tot, 1), 1),
        "piu_grande": max((len(w) for w in gr.values()), default=0),
        "nota": ("i portafogli che comprano nella stessa transazione sono una persona sola: "
                 "contarli separatamente moltiplica un successo per il numero di portafogli."),
    }


if __name__ == "__main__":
    # prova con il caso vero del 7/10: nove portafogli in una transazione
    finte = [{"chi": f"0x{i:040x}", "tx_compra": ["0xaaa"]} for i in range(9)]
    finte += [{"chi": "0xsolo", "tx_compra": ["0xbbb"]}]
    capo, gr, ref = referto(finte)
    assert ref["grappoli"] == 1 and ref["piu_grande"] == 9
    assert len({capo[f["chi"]] for f in finte[:9]}) == 1
    assert capo["0xsolo"] == "0xsolo"
    print("prova superata:", ref)
