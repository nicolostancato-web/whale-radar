"""LA TARATURA SU SOLANA: lo strumento misura, o e' girato?

Stessa prova che ha salvato Robinhood e validato Base: comprare e rivendere SUBITO deve
PERDERE, perche' si paga lo scarto fra i due lati del libro. Se viene positivo, il lettore ha
il verso sbagliato e nessun numero successivo vale.

Qui la prova conta doppio: su Solana il lettore e' NUOVO, scritto stanotte. La taratura e'
l'unico modo di saperlo senza fidarsi di me.

COSTO DICHIARATO: ~1 credito Helius per transazione letta. Con i valori di default sono circa
2.000 crediti, cioe' lo 0,2% della dotazione mensile gratuita.
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solana_rpc as S

POOL = "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2"   # mercato molto attivo: serve a TROVARE i gettoni
GETTONI = int(os.environ.get("GETTONI", "8"))
PER_GETTONE = int(os.environ.get("PER_GETTONE", "150"))


def main():
    if not S.url():
        print("TARATURA SOL | nessuna chiave Helius valida")
        return 1
    # 1) scoprire gettoni attivi leggendo un po' di scambi recenti
    r = S.rpc("getSignaturesForAddress", [POOL, {"limit": 60}]) or []
    buone = [x["signature"] for x in r if not x.get("err")]
    conta = collections.Counter()
    letti = 0
    for s in buone:
        e = S.scambio(s)
        letti += 1
        if e:
            conta[e[4]] += 1
    gettoni = [g for g, _ in conta.most_common(GETTONI)]
    print(f"TARATURA SOL | {letti} transazioni lette, {len(conta)} gettoni visti, "
          f"ne seguo {len(gettoni)}", flush=True)
    # 2) per ogni gettone, la sua serie
    righe = []
    costo = letti
    for g in gettoni:
        sig = S.rpc("getSignaturesForAddress", [g, {"limit": PER_GETTONE}]) or []
        serie = []
        for x in sig:
            if x.get("err"):
                continue
            e = S.scambio(x["signature"])
            costo += 1
            if e and e[4] == g:
                serie.append((e[0], e[1], e[2]))
            time.sleep(0.02)
        serie.sort()
        if len(serie) >= 20:
            righe.append((g, serie))
        print(f"   {g[:12]}: {len(serie)} scambi utilizzabili su {len(sig)} firme", flush=True)
    print(f"\nTARATURA SOL | costo: ~{costo:,} crediti Helius", flush=True)
    if not righe:
        print("   nessun gettone con abbastanza scambi")
        return 0
    # 3) la taratura: compra e rivendi alla prima vendita successiva
    def giro(serie):
        out = []
        for i, (sl, p, compra) in enumerate(serie):
            if not compra:
                continue
            for j in range(i + 1, min(i + 12, len(serie))):
                if not serie[j][2] and p > 0:
                    out.append(serie[j][1] / p - 1)
                    break
        return out
    med = []
    for g, serie in righe:
        v = giro(serie)
        if len(v) >= 5:
            med.append(statistics.median(v))
            print(f"   {g[:12]}: giro istantaneo {statistics.median(v)*100:+.2f}%  su {len(v)} giri")
    if med:
        m = statistics.median(med)
        print(f"\n   TARATURA COMPLESSIVA: {m*100:+.2f}%  su {len(med)} gettoni")
        print("   deve essere NEGATIVA. Se e' positiva, il lettore e' girato e nulla di Solana vale.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
