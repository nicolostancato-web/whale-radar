"""Quanti portafogli possiamo DAVVERO giudicare, e solo dopo chi vince.

PERCHE' QUESTO FILE E PERCHE' IN QUEST'ORDINE (4/10, correzione di Nicolo').
Per tre giorni ho misurato il passato di un portafoglio con l'ESITO DELLA MONETA che aveva
toccato. Non e' la stessa cosa di quanto ha incassato LUI:
  · chi compra una moneta che fa dieci volte e vende subito in perdita, nel mio conto era BRAVO;
  · chi compra una moneta che va a zero ma esce al +300%, nel mio conto era SCARSO.
Esattamente al contrario di chi ha fatto i soldi. L'indicatore era di Nicolo', il metro no.

E PRIMA DELLA CLASSIFICA VIENE IL DENOMINATORE. Il guadagno vero si calcola solo dove vediamo
SIA l'acquisto SIA la vendita. Dove vediamo solo la vendita non sappiamo niente: e' come vedere
uno uscire da un negozio e vendere un quadro a mille euro senza sapere quanto l'ha pagato.
Quei portafogli NON sono perdenti: sono SCONOSCIUTI, e vanno tenuti da parte con scritto
perche' — non cancellati (regola: da veri analisti non si cancella niente).
Il rischio, se salto questo passo: la classifica non dice «i migliori», dice «quelli di cui
abbiamo visto tutto» — cioe' i piu' recenti, perche' chi era dentro prima che accendessimo la
telecamera lo vediamo solo quando vende. I piu' bravi potrebbero essere proprio quelli.
Terza ricaduta della famiglia del DENOMINATORE in tre giorni, e la prima dichiarata PRIMA.
"""
import gzip
import json
import os

import numpy as np

MIN_DOLLARI = 1.0        # sotto un dollaro chiuso non e' un affare, e' polvere


def carica(chain):
    p = f"data/multichain/{chain}/profitto.json.gz"
    if not os.path.exists(p):
        raise SystemExit(f"CHI INCASSA | manca {p}: senza i conti per persona non c'e' "
                         f"niente da giudicare. Lo costruisce agents/profitto_persone.py.")
    return json.load(gzip.open(p, "rt")).get("da", {})


def main():
    for chain in ("base", "robinhood"):
        d = carica(chain)
        tot = len(d)
        # IL DENOMINATORE, PRIMA DI TUTTO
        con_chiusi = {k: v for k, v in d.items() if v.get("pool_chiusi", 0) > 0}
        giudicabili = {k: v for k, v in con_chiusi.items()
                       if v.get("chiuso_speso", 0) >= MIN_DOLLARI}
        solo_vendite = sum(1 for v in d.values()
                           if v.get("pool_chiusi", 0) == 0
                           and v.get("pool_solo_uscite", 0) > 0)
        solo_aperte = sum(1 for v in d.values()
                          if v.get("pool_chiusi", 0) == 0
                          and v.get("pool_solo_uscite", 0) == 0)
        print(f"\n=== {chain} ===")
        print(f"   portafogli visti                     {tot:9,}")
        print(f"   con almeno una posizione CHIUSA      {len(con_chiusi):9,} "
              f"({len(con_chiusi)/tot:5.1%})")
        print(f"   ... e oltre {MIN_DOLLARI:.0f}$ chiuso = GIUDICABILI  {len(giudicabili):9,} "
              f"({len(giudicabili)/tot:5.1%})")
        print(f"   SCONOSCIUTI: solo vendite viste      {solo_vendite:9,} "
              f"({solo_vendite/tot:5.1%})")
        print(f"   SCONOSCIUTI: solo acquisti, mai usciti {solo_aperte:9,} "
              f"({solo_aperte/tot:5.1%})")
        if not giudicabili:
            print("   nessun portafoglio giudicabile: non si fa nessuna classifica")
            continue
        # SOLO ORA si guarda chi vince, e solo sul chiuso
        r = np.array([v["chiuso_incassato"] / v["chiuso_speso"] - 1.0
                      for v in giudicabili.values()])
        pool = np.array([v["pool_chiusi"] for v in giudicabili.values()])
        print(f"\n   fra i giudicabili: {np.mean(r > 0):.1%} hanno incassato piu' di "
              f"quanto hanno speso")
        print(f"   rendimento sul chiuso: mediano {np.median(r):+.1%}, "
              f"medio {np.mean(r):+.1%}")
        print(f"   posizioni chiuse per persona: mediana {np.median(pool):.0f}, "
              f"massima {pool.max():,}")
        # e un portafoglio con UNA sola posizione chiusa non e' un vincente, e' un caso
        for n in (1, 2, 3, 5, 10):
            m = pool >= n
            if m.sum() < 30:
                continue
            print(f"   con almeno {n:2d} posizioni chiuse: {int(m.sum()):7,} persone, "
                  f"{np.mean(r[m] > 0):5.1%} in guadagno, mediana {np.median(r[m]):+7.1%}")


if __name__ == "__main__":
    main()


def disposizione(chain):
    """Il tasso alto e' bravura o e' l'effetto di disposizione? (4/10, avviso di Grok del 3/10)

    «La gente vende i vincenti e tiene i perdenti.» Se e' cosi', una posizione entra fra le
    CHIUSE soprattutto quando e' andata bene, e i perdenti restano per sempre fra le APERTE,
    mai contati. Allora «ha dieci posizioni chiuse in guadagno» non vuol dire «e' bravo»:
    vuol dire «ha avuto dieci vincenti da vendere», e i suoi perdenti sono fuori dal campione.

    LA FIRMA SI VEDE SENZA PREZZARE NIENTE: se chi ha tante chiuse ne lascia aperte
    proporzionalmente ALTRETTANTE, il campione non e' selezionato e il tasso regge. Se invece
    chi ha tante chiuse lascia aperte MOLTE PIU' posizioni, il tasso misura la selezione.
    Le aperte NON si prezzano (regola di Astra: il residuo resta in gettoni) — qui si contano.
    """
    d = carica(chain)
    g = [v for v in d.values()
         if v.get("pool_chiusi", 0) > 0 and v.get("chiuso_speso", 0) >= MIN_DOLLARI]
    r = np.array([v["chiuso_incassato"] / v["chiuso_speso"] - 1.0 for v in g])
    ch = np.array([v["pool_chiusi"] for v in g], float)
    ap = np.array([v.get("pool_aperti", 0) for v in g], float)
    print(f"\n=== {chain}: il tasso e' bravura o selezione? ===")
    print(f"   {'chiuse':>8} {'persone':>8} {'in guadagno':>12} {'aperte per ogni chiusa':>24}")
    for lo, hi in ((1, 1), (2, 2), (3, 4), (5, 9), (10, 10**6)):
        m = (ch >= lo) & (ch <= hi)
        if m.sum() < 25:
            continue
        et = f"{lo}" if lo == hi else (f"{lo}+" if hi > 10**5 else f"{lo}-{hi}")
        print(f"   {et:>8} {int(m.sum()):8,} {np.mean(r[m] > 0):11.1%} "
              f"{np.median(ap[m] / ch[m]):23.1f}")
    # e la prova diretta: quanta parte di cio' che ha comprato NON ha mai venduto
    quota_aperta = ap / np.maximum(ch + ap, 1)
    print(f"\n   quota di posizioni mai chiuse, mediana: {np.median(quota_aperta):.1%}")
    tanti = ch >= 5
    pochi = ch == 1
    if tanti.sum() >= 25:
        print(f"   chi ha 1 sola chiusa  lascia aperto il {np.median(quota_aperta[pochi]):.1%}")
        print(f"   chi ha 5+ chiuse      lascia aperto il {np.median(quota_aperta[tanti]):.1%}")


if __name__ == "__main__" and os.environ.get("DISPOSIZIONE"):
    for c in ("base", "robinhood"):
        disposizione(c)


def puliti(chain):
    """I soli portafogli davvero giudicabili: hanno CHIUSO TUTTO quello che hanno comprato.

    Se una persona non lascia nessuna posizione aperta, non puo' averci nascosto i perdenti:
    vediamo tutti i suoi esiti, non solo quelli che le conveniva mostrare. E' il controllo piu'
    stretto disponibile senza prezzare i residui (che non si prezzano: regola di Astra).
    """
    d = carica(chain)
    g = [v for v in d.values()
         if v.get("pool_chiusi", 0) >= 2
         and v.get("chiuso_speso", 0) >= MIN_DOLLARI
         and v.get("pool_aperti", 0) == 0
         and v.get("pool_parziali", 0) == 0]
    if len(g) < 30:
        print(f"\n=== {chain}: solo {len(g)} portafogli hanno chiuso tutto: non si giudica ===")
        return
    r = np.array([v["chiuso_incassato"] / v["chiuso_speso"] - 1.0 for v in g])
    ch = np.array([v["pool_chiusi"] for v in g], float)
    print(f"\n=== {chain}: chi ha chiuso TUTTO ({len(g):,} persone) ===")
    print(f"   in guadagno: {np.mean(r > 0):.1%} · mediana {np.median(r):+.1%} · "
          f"media {np.mean(r):+.1%}")
    for lo, hi in ((2, 2), (3, 4), (5, 10**6)):
        m = (ch >= lo) & (ch <= hi)
        if m.sum() < 25:
            continue
        et = f"{lo}" if lo == hi else (f"{lo}+" if hi > 10**5 else f"{lo}-{hi}")
        print(f"   {et:>4} chiuse: {int(m.sum()):6,} persone, {np.mean(r[m] > 0):5.1%} "
              f"in guadagno, mediana {np.median(r[m]):+7.1%}")
    print(f"   NOTA: mediana e media distanti = pochi colpi grossi dominano. Il colpo grosso "
          f"vale solo se era vendibile a quella dimensione, e qui non e' verificato.")


if __name__ == "__main__" and os.environ.get("PULITI"):
    for c in ("base", "robinhood"):
        puliti(c)
