"""I POOL APPENA NATI SU BASE: li' il gioco ha una forma propria.

Su Robinhood le monete nuove erano Pons, con un pedaggio speciale (hook che preleva dopo lo
scambio, commissione di pool zero) che rendeva tutto impossibile. Su Base le fabbriche sono
altre e le commissioni sono normali: vale la pena misurare i pool NEI PRIMI MINUTI DI VITA,
che e' il momento in cui i memecoin si muovono davvero.

Stesso metro di sempre: taratura in cima, entrata su un acquisto, uscita su una vendita,
stessi casi in tutte le colonne.
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_rpc as B

SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
ORE = float(os.environ.get("ORE", "6"))
RITARDO = 1
ORIZZONTI = [("taratura (subito)", 0), ("+1 minuto", 30), ("+5 minuti", 150), ("+30 minuti", 900)]
ETA = [("primi 2 minuti", 0, 60), ("2-10 minuti", 60, 300),
       ("10-60 minuti", 300, 1800), ("oltre un'ora", 1800, 10 ** 9)]


def main():
    t = B.testa()
    if not t:
        print("BASE NUOVI | l'RPC non da la testa")
        return 1
    da = t - int(ORE * 3600 / B.BLOCCO)
    nascita = {}
    per = collections.defaultdict(list)
    fee = {}
    b = da
    n = 0
    while b <= t:
        f = min(b + B.FINESTRA - 1, t)
        for l in B.log_di_finestra(INIT, b, f, indirizzo=B.GESTORE_V4) or []:
            nascita[l["topics"][1]] = int(l["blockNumber"], 16)
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
        if n % 20 == 0:
            print(f"   {b-da:,}/{t-da:,} blocchi, nati {len(nascita):,}, pool con scambi {len(per):,}",
                  flush=True)
        time.sleep(0.2)
    nuovi = {k: sorted(v) for k, v in per.items() if k in nascita and len(v) >= 40}
    print(f"\nBASE NUOVI | pool NATI nelle ultime {ORE} ore: {len(nascita):,}")
    print(f"BASE NUOVI | di questi, con almeno 40 scambi: {len(nuovi):,}\n", flush=True)
    if len(nuovi) < 8:
        print("   troppo pochi per una tabella")
        return 0

    def rese(P, a, b_):
        """solo gli acquisti avvenuti fra a e b_ secondi dalla NASCITA del pool"""
        out = {e: [] for e, _ in ORIZZONTI}
        n0 = P[0][0]
        for i, (bl, p, compra) in enumerate(P):
            if not compra:
                continue
            eta = (bl - n0) * B.BLOCCO
            if not (a <= eta < b_):
                continue
            ing = next((j for j in range(i + 1, len(P)) if P[j][0] >= bl + RITARDO and P[j][2]), None)
            if ing is None or P[ing][1] <= 0:
                continue
            u = {}
            for e, salto in ORIZZONTI:
                j = next((k for k in range(ing + 1, len(P))
                          if P[k][0] >= P[ing][0] + salto and not P[k][2]), None)
                if j is None:
                    break
                u[e] = P[j][1] / P[ing][1] - 1
            if len(u) == len(ORIZZONTI):
                for e in u:
                    out[e].append(u[e])
        return out

    print(f"   {'eta del pool':<18}{'pool':>6}" + "".join(f"{e:>19}" for e, _ in ORIZZONTI))
    print('   ' + '-' * 100)
    for et, a, b_ in ETA:
        tutte = [d for d in (rese(P, a, b_) for P in nuovi.values())
                 if len(d[ORIZZONTI[0][0]]) >= 5]
        if len(tutte) < 8:
            print(f"   {et:<18}{len(tutte):>6}   (pochi)")
            continue
        riga = f"   {et:<18}{len(tutte):>6}"
        for e, _ in ORIZZONTI:
            riga += f"{statistics.median([statistics.median(d[e]) for d in tutte])*100:>+17.2f}% "
        print(riga, flush=True)
    print('   ' + '-' * 100)
    print("   prima colonna = TARATURA, deve essere negativa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
