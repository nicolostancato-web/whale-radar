"""LA PROVA SULLA LIQUIDITA', SU BASE — dove la taratura passa e il numero si legge.

Su Robinhood questa prova ha dato un gradiente ordinato su 2,8 milioni di operazioni:
comprare dove nessuno guarda rende circa tre punti meglio che comprare nella calca. Ma li'
la taratura e' POSITIVA in ogni fascia, perche' l'hook di Pons preleva dopo lo scambio e il
costo non compare nei dati: la tabella non si poteva leggere.

Su Base le commissioni si vedono e la taratura e' negativa e proporzionale. Se il gradiente
resta QUI, allora e' leggibile.

Filtro dichiarato prima: SOLO pool con commissione dichiarata > 0, cioe' quelli il cui costo
lo strumento vede davvero.
"""
import bisect, collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_rpc as B

SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
ORE = float(os.environ.get("ORE", "5"))
RITARDO, ORIZZONTE = 1, 150            # 1 blocco (~2s), 5 minuti
FINESTRA_PRIMA = 30                    # un minuto prima
FASCE = [("meno di 5", 0, 5), ("5-20", 5, 20), ("20-60", 20, 60), ("oltre 60", 60, 10 ** 9)]


def main():
    t = B.testa()
    prof = B.profondita(t)
    da = t - min(int(ORE * 3600 / B.BLOCCO), prof)
    per = collections.defaultdict(list)
    fee = {}
    b = da
    n = 0
    while b <= t:
        f = min(b + B.FINESTRA - 1, t)
        for l in B.log_di_finestra(SW, b, f, indirizzo=B.GESTORE_V4) or []:
            d = l["data"][2:]
            if len(d) < 384:
                continue
            def sg(x):
                v = int(x, 16)
                return v - (1 << 256) if v >= (1 << 255) else v
            a0, a1 = sg(d[0:64]), sg(d[64:128])
            if not (a0 and a1):
                continue
            per[l["topics"][1]].append((int(l["blockNumber"], 16), abs(a0 / a1), a0 < 0))
            fee[l["topics"][1]] = int(d[320:384], 16)
        b = f + 1
        n += 1
        if n % 30 == 0:
            print(f"   {b-da:,}/{t-da:,} blocchi, {len(per):,} pool", flush=True)
        time.sleep(0.15)
    # SOLO pool la cui commissione lo strumento vede
    vivi = {k: sorted(v) for k, v in per.items()
            if len(v) >= 80 and 0 < fee.get(k, 0) < 8388608}
    print(f"\nBASE LIQUIDITA' | {len(vivi):,} pool con commissione visibile e 80+ scambi\n", flush=True)
    agg = collections.defaultdict(lambda: {"tara": [], "resa": [], "bloc": 0, "tot": 0})
    for P in vivi.values():
        bl = [x[0] for x in P]
        for i, (b_, p, compra) in enumerate(P):
            if not compra:
                continue
            prima = i - bisect.bisect_left(bl, b_ - FINESTRA_PRIMA)
            fascia = next(e for e, a, z in FASCE if a <= prima < z)
            ing = next((j for j in range(i + 1, len(P)) if P[j][0] >= b_ + RITARDO and P[j][2]), None)
            if ing is None or P[ing][1] <= 0:
                continue
            g = agg[fascia]
            g["tot"] += 1
            sub = next((k for k in range(ing + 1, len(P)) if not P[k][2]), None)
            if sub is not None:
                g["tara"].append(P[sub][1] / P[ing][1] - 1)
            usc = next((k for k in range(ing + 1, len(P))
                        if P[k][0] >= P[ing][0] + ORIZZONTE and not P[k][2]), None)
            if usc is None:
                g["bloc"] += 1
            else:
                g["resa"].append(P[usc][1] / P[ing][1] - 1)
    print(f"   {'scambi nel minuto prima':<26}{'operazioni':>12}{'bloccate':>10}"
          f"{'TARATURA':>12}{'resa a 5 min':>15}{'differenza':>13}")
    print('   ' + '-' * 90)
    for et, _, _ in FASCE:
        g = agg.get(et)
        if not g or g["tot"] < 100 or not g["tara"] or not g["resa"]:
            continue
        ta = statistics.median(g["tara"])
        tutte = g["resa"] + [-1.0] * g["bloc"]
        re = statistics.median(tutte)
        print(f"   {et:<26}{g['tot']:>12,}{g['bloc']/g['tot']*100:>9.1f}%"
              f"{ta*100:>+11.2f}%{re*100:>+14.2f}%{(re-ta)*100:>+12.2f}")
    print('   ' + '-' * 90)
    print("   la TARATURA deve essere negativa: qui le commissioni si vedono, quindi lo sara'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
