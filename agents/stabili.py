"""Quali caratteristiche si comportano allo stesso modo in TUTTI i periodi?

PERCHE' (24/09). Ieri ho prodotto quattro risultati promettenti e tutti sono caduti. Il metodo che
li produceva era sempre lo stesso: cercare fra molte combinazioni e tenere la vincente. Con
abbastanza tentativi si trova sempre qualcosa che ha funzionato NEL PASSATO ESAMINATO.

Qui si cambia il criterio. Non si cerca cosa ha funzionato meglio: si cerca cosa ha funzionato
**allo stesso modo in ogni periodo**. Una caratteristica che aiuta in un terzo del campione e non
negli altri due non e' un segnale debole: e' rumore che in un periodo ha avuto fortuna.

COME. Il campione si divide in tre periodi uguali per tempo. In ognuno, i pool si mettono in cinque
gruppi secondo la caratteristica, e si guarda la quota che fa +BERSAGLIO. Una caratteristica passa
solo se:
 1. la DIREZIONE (gruppo alto contro gruppo basso) e' la stessa in tutti e tre i periodi;
 2. il vantaggio e' almeno MINIMO_RAPPORTO in tutti e tre — non in media, in TUTTI.

E' un criterio severo apposta: preferisco scartare un segnale vero che accettarne uno falso, perche'
i falsi costano settimane e i veri, se esistono, si ripresentano.
"""
import gzip
import json
import os
import sys

CHAIN = os.environ.get("CHAIN", "robinhood")
BERSAGLIO = float(os.environ.get("BERSAGLIO", 0.5))
PERIODI = int(os.environ.get("PERIODI", 3))
MINIMO_RAPPORTO = float(os.environ.get("MINIMO_RAPPORTO", 1.3))
MIN_GRUPPO = int(os.environ.get("MIN_GRUPPO", 60))


def quinti(righe, campo):
    v = sorted(righe, key=lambda r: r[campo])
    n = len(v) // 5
    if n < MIN_GRUPPO:
        return None
    fuori = []
    for k in range(5):
        g = v[k * n:(k + 1) * n] if k < 4 else v[4 * n:]
        # SI CONTA CHI HA INCASSATO, non chi aveva un prezzo alto: `_uscita` e' il prezzo mediano
        # di chi ha VENDUTO, `_rend` era il prezzo a cui qualcuno COMPRAVA (25/09).
        fuori.append(sum(1 for r in g if r["_uscita"] >= BERSAGLIO) / len(g))
    return fuori


def main():
    # FILE COMPRESSO E RIFATTO DA UNA CORSIA (25/09): prima lo costruivo a mano sul portatile.
    p = f"data/loop1/insieme_{CHAIN}.jsonl.gz"
    righe = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
    # SOLO I POOL GIUDICABILI (25/09): nati abbastanza prima della fine della raccolta da avere un
    # esito. Il criterio e' l'eta', NON le ore in cui li abbiamo visti scambiare — quel secondo
    # criterio scarta i morti, cioe' le trappole, e abbellisce tutto di sette punti.
    prima_g = len(righe)
    righe = [r for r in righe if r.get("_giudicabile")]
    print(f"   tolti {prima_g-len(righe)} pool troppo giovani per avere un esito su {prima_g}")
    if not righe:
        print(f"STABILI | {CHAIN}: nessun pool giudicabile", flush=True)
        return
    # SOLO I POOL DA CUI SI PUO' USCIRE (24/09). Il 26% dei pool di robinhood non ha una sola
    # vendita nelle 24 ore, e proprio li' si concentrano i «vincenti»: il 26,6% di loro fa +50%
    # contro il 6,4% dei vendibili. Sono guadagni che non si possono incassare, e cercare pattern
    # senza toglierli significa trovare sempre e solo quelli.
    if os.environ.get("SOLO_VENDIBILI", "1") == "1":
        prima = len(righe)
        righe = [r for r in righe if r.get("_vendite_dopo", 1) > 0]
        print(f"   tolti {prima-len(righe)} pool invendibili su {prima} "
              f"({100*(prima-len(righe))/max(1,prima):.0f}%)")
    righe.sort(key=lambda r: r["_t"])
    nomi = sorted(k for k in righe[0] if not k.startswith("_"))
    n = len(righe)
    pezzi = [righe[i * n // PERIODI:(i + 1) * n // PERIODI] for i in range(PERIODI)]
    print(f"\n=== {CHAIN}: {n} pool in {PERIODI} periodi "
          f"({', '.join(str(len(x)) for x in pezzi)}) ===")
    for i, pz in enumerate(pezzi):
        q = sum(1 for r in pz if r["_rend"] >= BERSAGLIO) / len(pz)
        print(f"   periodo {i+1}: il {100*q:.1f}% dei pool fa +{100*BERSAGLIO:.0f}%")
    print(f"\n   passa solo chi ha la STESSA direzione e almeno {MINIMO_RAPPORTO}x "
          f"in TUTTI e {PERIODI} i periodi\n")
    passate = []
    for c in nomi:
        righe_per = [quinti(pz, c) for pz in pezzi]
        if any(x is None for x in righe_per):
            continue
        # per ogni periodo: il gruppo migliore e' l'alto o il basso? e quanto vale?
        alti = [q[4] / q[0] if q[0] > 0 else (float("inf") if q[4] > 0 else 1.0)
                for q in righe_per]
        bassi = [q[0] / q[4] if q[4] > 0 else (float("inf") if q[0] > 0 else 1.0)
                 for q in righe_per]
        for verso, rap in (("alto", alti), ("basso", bassi)):
            if all(x >= MINIMO_RAPPORTO for x in rap):
                passate.append((min(rap), c, verso, rap, righe_per))
                break
    if not passate:
        print("   NESSUNA caratteristica regge in tutti i periodi. E' un risultato, non un errore.")
        return
    passate.sort(reverse=True)
    print(f"   {'caratteristica':<30} {'verso':<7} {'vantaggio per periodo':<28} peggiore")
    for peggio, c, verso, rap, q in passate:
        r = " ".join(f"{x:.1f}x" if x != float("inf") else "inf" for x in rap)
        print(f"   {c:<30} {verso:<7} {r:<28} {peggio:.1f}x")
    print(f"\n   {len(passate)} su {len(nomi)} caratteristiche superano la prova.")


if __name__ == "__main__":
    main()
