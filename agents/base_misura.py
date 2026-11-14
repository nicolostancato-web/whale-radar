"""LA MISURA CALIBRATA SU BASE: seguire un acquisto paga, al netto del pedaggio?

Stesso identico metro costruito su Robinhood nella notte del 20-21/10, con dentro le quattro
lezioni pagate li' — e questa e' la ragione per cui si comincia da Base e non da Solana: lo
strumento si trasferisce intatto, inclusa la riga che ne prova la validita'.

 1. IL SEGNO: a0 NEGATIVO = l'utente COMPRA (verificato sulla chain su Robinhood incrociando
    gli Swap con i trasferimenti; su Base la convenzione Uniswap v4 e' la stessa, e la riga di
    taratura lo riverifica da sola).
 2. I DUE LATI DEL LIBRO: si ENTRA su una stampa di ACQUISTO (paghiamo noi) e si ESCE su una
    stampa di VENDITA (incassiamo noi). Mai «il primo prezzo qualunque».
 3. LA RIGA DI TARATURA: comprare e rivendere subito DEVE perdere, in proporzione alla
    commissione del pool. Se non lo fa, la tabella non si legge.
 4. STESSI CASI IN TUTTE LE COLONNE: un'operazione entra solo se esiste a ogni orizzonte.

UNA DIFFERENZA IMPORTANTE DI BASE: il blocco dura ~2 secondi invece di 0,093. Il nostro
secondo di ritardo vale MEZZO blocco, non undici. Si usa 1 blocco, che e' conservativo.
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_rpc as B

SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
ORE = float(os.environ.get("ORE", "4"))
RITARDO = 1                                   # ~2s su Base: conservativo
ORIZZONTI = [("taratura (subito)", 0), ("+1 minuto", 30), ("+5 minuti", 150), ("+30 minuti", 900)]
FUORI = "data/multichain/base/misura.json"


def main():
    t = B.testa()
    if not t:
        print("BASE | l'RPC non da la testa: non invento un blocco")
        return 1
    da = t - int(ORE * 3600 / B.BLOCCO)
    per = collections.defaultdict(list)
    fee = {}
    b = da
    n = 0
    while b <= t:
        f = min(b + B.FINESTRA - 1, t)
        lg = B.log_di_finestra(SW, b, f, indirizzo=B.GESTORE_V4)
        if lg is None:
            print(f"BASE | finestra {b}-{f} rifiutata: la salto e lo dico")
        for l in lg or []:
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
            print(f"   {b-da:,}/{t-da:,} blocchi, {len(per):,} pool, "
                  f"{sum(len(v) for v in per.values()):,} scambi", flush=True)
        time.sleep(0.2)
    vivi = {k: sorted(v) for k, v in per.items() if len(v) >= 80}
    print(f"\nBASE | {len(vivi):,} pool con almeno 80 scambi in {ORE} ore "
          f"(su {len(per):,} pool visti)\n", flush=True)

    def rese(P):
        out = {e: [] for e, _ in ORIZZONTI}
        for i, (b_, p, compra) in enumerate(P):
            if not compra:
                continue
            ing = next((j for j in range(i + 1, len(P))
                        if P[j][0] >= b_ + RITARDO and P[j][2]), None)
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

    gruppi = collections.defaultdict(list)
    for idp, P in vivi.items():
        f = fee.get(idp, 0)
        et = "dinamica" if f >= 8388608 else ("senza commissione" if f == 0 else f"commissione {f/10000:.2f}%")
        gruppi[et].append(P)
    print(f"   {'gruppo':<24}{'pool':>6}" + "".join(f"{e:>19}" for e, _ in ORIZZONTI))
    print('   ' + '-' * 106)
    salva = {}
    for et, elenco in sorted(gruppi.items(), key=lambda kv: -len(kv[1]))[:8]:
        tutte = [d for d in (rese(P) for P in elenco) if len(d[ORIZZONTI[0][0]]) >= 10]
        if len(tutte) < 8:
            continue
        riga = f"   {et:<24}{len(tutte):>6}"
        salva[et] = {}
        for e, _ in ORIZZONTI:
            m = statistics.median([statistics.median(d[e]) for d in tutte])
            salva[et][e] = m
            riga += f"{m*100:>+17.2f}% "
        print(riga, flush=True)
    print('   ' + '-' * 106)
    print("   prima colonna = TARATURA: deve essere negativa e crescere col costo del pool.")
    os.makedirs("data/multichain/base", exist_ok=True)
    json.dump(salva, open(FUORI, "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
