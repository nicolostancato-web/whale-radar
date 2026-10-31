"""Cerca un FILTRO SULL'ENTRATA che regga all'esecuzione vera.

La famiglia stop/bersaglio e' morta (15/10): con l'uscita simulata sei secondi dopo il tocco,
zero regole su 56 sopravvivono. Quindi la domanda cambia: non «come esco» ma «su quali curve
entro». Qui si prendono le caratteristiche note al momento dell'entrata — la riserva, quanto
in fretta e' stata raccolta, il punteggio di andamento — e si guarda se una fetta rende dove
l'insieme non rende.

LE DUE PROVE CHE OGNI CANDIDATO DEVE PASSARE:
  1. si cerca sulla PRIMA meta' del periodo e si verifica sulla SECONDA, mai vista;
  2. l'uscita e' quella vera: il prezzo osservato RITARDO secondi dopo il tocco.
Un filtro che passa la prima e non la seconda non e' un filtro: e' un ricordo.
"""
import json
import os
import statistics
import sys

SEC = 0.093
COSTO = 1.0591
RITARDO = float(os.environ.get("RITARDO_SEC", "6"))
STATO = "data/multichain/robinhood/prova_nella_curva.json"


def cammino_intero(p):
    return (p.get("cammino") or []) + (p.get("dopo_uscita") or [])


def esito(cam, stop, bers):
    for i, (b, x) in enumerate(cam):
        if x <= stop or (bers and x >= bers):
            for b2, x2 in cam[i:]:
                if (b2 - b) * SEC >= RITARDO:
                    return x2 / COSTO - 1
            return cam[-1][1] / COSTO - 1
    return cam[-1][1] / COSTO - 1


def valuta(gruppo, stop, bers):
    r = [esito(cammino_intero(p), stop, bers) for p in gruppo]
    if len(r) < 20:
        return None
    sd = statistics.stdev(r) if len(r) > 1 else 0
    return statistics.mean(r), 1.96 * sd / len(r) ** 0.5, len(r)


def main():
    st = json.load(open(STATO))
    pos = [p for p in st["posizioni"].values()
           if p.get("dopo_uscita") and len(p.get("cammino") or []) > 2]
    pos.sort(key=lambda p: p.get("aperta_il", 0))
    mz = len(pos) // 2
    A, B = pos[:mz], pos[mz:]
    print(f"FILTRI SULL'ENTRATA — {len(pos)} posizioni, uscita {RITARDO:.0f}s dopo il tocco\n")

    campi = ["riserva_all_entrata", "punteggio", "minuti_alla_soglia"]
    regole = [(0.9, 1.5), (0.95, 1.3), (0.98, 1.2), (0.9, 2.0)]
    trovati = []
    for campo in campi:
        v = sorted(p[campo] for p in pos if p.get(campo) is not None)
        if len(v) < 100:
            continue
        tagli = [v[int(len(v) * q)] for q in (0.2, 0.4, 0.6, 0.8)]
        for t in tagli:
            for verso in ("sopra", "sotto"):
                sel = (lambda p, t=t, c=campo, w=verso:
                       p.get(c) is not None and (p[c] >= t if w == "sopra" else p[c] < t))
                for stop, bers in regole:
                    a = valuta([p for p in A if sel(p)], stop, bers)
                    b = valuta([p for p in B if sel(p)], stop, bers)
                    if not a or not b:
                        continue
                    if a[0] > 0 and b[0] - b[1] > 0:
                        trovati.append((b[0], b[1], campo, verso, t, stop, bers, a[0], b[2]))
    trovati.sort(reverse=True)
    if not trovati:
        print("   nessun filtro supera le due prove.")
        return 0
    print(f"{'filtro':<42}{'cerca':>9}{'verifica':>11}{'casi':>7}")
    print("-" * 70)
    for b0, ic, campo, verso, t, stop, bers, a0, n in trovati[:10]:
        et = f"{campo} {verso} {t:.3f} | stop {stop} bers {bers}"
        print(f"{et:<42}{a0*100:>+8.2f}%{b0*100:>+10.2f}%{n:>7}")
    print("-" * 70)
    print(f"   candidati che passano entrambe le prove: {len(trovati)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
