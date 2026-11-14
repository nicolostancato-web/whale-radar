"""LO SCARTO AL DIPLOMA, misurato leggendo ENTRAMBI i lati dalla chain.

== DUE DIFETTI PAGATI PRIMA DI CREDERE AL NUMERO (20/10) ==

La prima versione dava uno scarto mediano del +172%, e la verifica caso per caso l'ha demolita:
 1. il prezzo di curva veniva da tassa_zero.jsonl, la cui serie NON arriva al blocco del
    diploma: su un caso l'ultimo prezzo del file era di 24.000 blocchi prima e valeva un sesto
    di quello vero. Un prezzo vecchio confrontato con uno nuovo inventa un salto che non c'e'.
 2. la mappa gettone->curva mancava e la prima versione cercava un campo inesistente: ZERO
    monete, senza un solo errore.

Qui l'ultimo prezzo della curva si legge dall'ULTIMO CurveBuy prima del diploma, direttamente
dalla chain, e il primo prezzo del pool dal primo scambio raccolto. Campione casuale, non le
80 monete che per caso stavano in entrambi i file: quelle erano un campione di noi.

CRITERIO DI MORTE, scritto prima di guardare: lo scarto mediano deve superare il costo del
giro (~6%) su ENTRAMBE le meta' del periodo.
"""
import glob, gzip, json, os, random, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

MAN = "data/multichain/robinhood/manifesto_graduati.json"
FUORI = "data/multichain/robinhood/salto_del_diploma.json"
QUANTI = int(os.environ.get("QUANTI", "400"))


def main():
    man = json.load(open(MAN))["pool"]
    CR = json.load(open("data/multichain/robinhood/creatori.json"))
    # gettone -> curva, dai 701.036 lanci
    tok2cur = {v["gettone"].lower(): k for k, v in CR.items()}
    # primo prezzo del pool, dalla raccolta di stanotte (filtro per pool verificato buono)
    pool = {}
    for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl*")):
        ap = gzip.open if f.endswith(".gz") else open
        for r in ap(f, "rt"):
            try:
                d = json.loads(r)
            except Exception:
                continue
            for b, a0, a1, sq in d["s"]:
                if a1 and a0 and abs(a0 / a1) > 0:
                    pool.setdefault(d["moneta"].lower(), (b, abs(a0 / a1)))
                    break
    print(f"SALTO | primo prezzo di pool per {len(pool):,} monete", flush=True)
    cand = [(k, v) for k, v in man.items()
            if int(v["valuta"], 16) == 0 and v["moneta"].lower() in pool
            and v["moneta"].lower() in tok2cur]
    camp = random.Random(2010).sample(cand, min(QUANTI, len(cand)))
    print(f"SALTO | campione casuale di {len(camp)} monete su {len(cand):,} possibili", flush=True)
    salti = []
    for i, (idp, v) in enumerate(camp):
        tok = v["moneta"].lower()
        cur = tok2cur[tok]
        dip = v["diploma"]
        lg = C.log_di_finestra(C.T_COMPRA, dip - 200_000, dip, indirizzo=cur)
        if not lg:
            continue
        # LO SPAREGGIO DENTRO IL BLOCCO (20/10). Con max() sul solo numero di blocco, quando
        # nel blocco del diploma ci sono piu' acquisti si pesca il PRIMO invece dell'ultimo:
        # e il primo prezzo della curva e' ~12 volte piu' basso di quello di diploma, perche'
        # la curva di Pons sale di 12,25x per costruzione. I tre "salti" piu' grandi (+1.175%,
        # +1.141%, +1.117%) erano tutti questo. Si ordina per (blocco, posizione nel blocco).
        ultimo = max(lg, key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
        n = C._numeri(ultimo["data"])
        if not n[1]:
            continue
        p_curva = n[0] / n[1]
        b_curva = int(ultimo["blockNumber"], 16)
        b_pool, p_pool = pool[tok]
        salti.append({"moneta": tok, "diploma": dip, "blocchi_prima": dip - b_curva,
                      "p_curva": p_curva, "p_pool": p_pool, "salto": p_pool / p_curva - 1})
        if (i + 1) % 50 == 0:
            print(f"   {i+1}/{len(camp)} ...", flush=True)
        time.sleep(0.2)
    json.dump(salti, open(FUORI, "w"))
    salti.sort(key=lambda x: x["diploma"])
    mz = len(salti) // 2
    print(f"\n   monete misurate: {len(salti)}")
    print(f"   {'periodo':<16}{'monete':>8}{'salto mediano':>16}{'media':>10}{'sopra +6%':>12}")
    print('   ' + '-' * 62)
    for et, fetta in (("prima meta", salti[:mz]), ("seconda meta", salti[mz:]), ("tutte", salti)):
        if not fetta:
            continue
        x = [s["salto"] for s in fetta]
        print(f"   {et:<16}{len(x):>8,}{statistics.median(x)*100:>+15.2f}%"
              f"{statistics.mean(x)*100:>+9.2f}%{sum(1 for q in x if q > 0.06)/len(x)*100:>11.0f}%")
    print('   ' + '-' * 62)
    d = [s["blocchi_prima"] for s in salti]
    print(f"   quanto e' vecchio il prezzo di curva usato: mediana {statistics.median(d):.0f} blocchi "
          f"({statistics.median(d)*0.093:.0f} secondi) prima del diploma")
    return 0


if __name__ == "__main__":
    sys.exit(main())
