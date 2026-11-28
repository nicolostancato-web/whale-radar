"""L'IPOTESI CHE LE TRE CHAIN INDICANO INSIEME: conta la liquidita' PRIMA di comprare?

In tutte e tre le chain la colonna che decide non e' la resa, e' quante posizioni restano
BLOCCATE — senza nessuno a cui vendere. Su Base, nei pool nuovi, l'82%. Su Solana, dal 22% al
75% a seconda del gettone. E dove si esce quasi sempre, i numeri migliorano.

Ma «quante restano bloccate» si sa DOPO. La domanda onesta e': **l'attivita' osservabile prima
di comprare predice se si riuscira' a uscire, e cambia il risultato?**

Si prova qui perche' costa zero: 17 milioni di scambi di Robinhood gia' sul disco.

E le posizioni senza uscita NON si scartano: si riportano in due modi, all'ultimo prezzo visto
e a zero. Scartarle e' l'errore che ha prodotto il +122% su Base.
"""
import collections, glob, gzip, json, os, statistics, sys

RITARDO, ORIZZONTE = 11, 3225          # 1 secondo, 5 minuti (blocchi da 0,093s)
FINESTRA_PRIMA = 645                   # un minuto prima: cio' che si vede al momento di comprare
FASCE = [("meno di 5", 0, 5), ("5-20", 5, 20), ("20-60", 20, 60), ("oltre 60", 60, 10 ** 9)]


def main():
    agg = collections.defaultdict(lambda: {"chiuse": [], "bloccate": 0, "tot": 0})
    nm = 0
    for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl*")):
        ap = gzip.open if f.endswith(".gz") else open
        for r in ap(f, "rt"):
            try:
                d = json.loads(r)
            except Exception:
                continue
            P = []
            for b, a0, a1, sq in d["s"]:
                if a1 and a0:
                    p = abs(a0 / a1)
                    if p > 0:
                        P.append((b, p, a0 < 0))
            if len(P) < 30:
                continue
            nm += 1
            bl = [x[0] for x in P]
            import bisect
            for i, (b, p, compra) in enumerate(P):
                if not compra:
                    continue
                # cio' che si vede PRIMA di comprare: scambi nell'ultimo minuto
                prima = i - bisect.bisect_left(bl, b - FINESTRA_PRIMA)
                for et, a, z in FASCE:
                    if a <= prima < z:
                        fascia = et
                        break
                ing = next((j for j in range(i + 1, len(P)) if P[j][0] >= b + RITARDO and P[j][2]), None)
                if ing is None or P[ing][1] <= 0:
                    continue
                g = agg[fascia]
                g["tot"] += 1
                # LA TARATURA, PER FASCIA (22/10). Senza, non si puo' sapere se il +0,94%
                # della fascia tranquilla sia un guadagno o solo l'effetto di stampe rade:
                # e' la stessa forma dell'artefatto che su Base dava un falso +0,46%.
                sub = next((k for k in range(ing + 1, len(P)) if not P[k][2]), None)
                if sub is not None:
                    g.setdefault("tara", []).append(P[sub][1] / P[ing][1] - 1)
                usc = next((k for k in range(ing + 1, len(P))
                            if P[k][0] >= P[ing][0] + ORIZZONTE and not P[k][2]), None)
                if usc is None:
                    g["bloccate"] += 1
                else:
                    g["chiuse"].append(P[usc][1] / P[ing][1] - 1)
            if nm >= 1500:
                break
        if nm >= 1500:
            break
    print(f"LIQUIDITA' PRIMA | {nm:,} monete\n")
    print(f"   {'scambi nel minuto prima':<26}{'operazioni':>12}{'bloccate':>10}"
          f"{'TARATURA':>12}{'resa a 5 min':>15}{'differenza':>13}")
    print('   ' + '-' * 90)
    for et, _, _ in FASCE:
        g = agg.get(et)
        if not g or g["tot"] < 200:
            continue
        c = g["chiuse"]
        tutte = c + [-1.0] * g["bloccate"]
        ta = statistics.median(g.get("tara") or [0.0])
        re = statistics.median(tutte)
        print(f"   {et:<26}{g['tot']:>12,}{g['bloccate']/g['tot']*100:>9.1f}%"
              f"{ta*100:>+11.2f}%{re*100:>+14.2f}%{(re-ta)*100:>+12.2f}")
    print('   ' + '-' * 90)
    print("   TARATURA = comprare e rivendere subito: deve essere negativa in OGNI fascia.")
    print("   Se in una fascia e' positiva, quella riga non si legge: il guadagno e' della costruzione.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
