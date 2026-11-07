"""Assottiglia le letture di liquidita' dei pool piu' voluminosi.

PERCHE'. Il 23/09 un singolo file di riserve era a 61,8 MB: GitHub avvisa a 50 MB e BLOCCA a 100.
Se quel file arriva a 100, le spinte si fermano e TUTTA la raccolta muore. Quel pool aveva
3.105.329 letture di liquidita' a fronte di 308 scambi nostri: tremila misure per ogni operazione
che ci interessa.

COSA FA. Tiene UNA lettura ogni GRANO blocchi (25 di default: su base sono ~50 secondi), scartando
le intermedie. La curva della liquidita' resta, la sua risoluzione al secondo no.

PERCHE' E' SICURO, e va detto chiaro visto che si cancella:
 1. serve la liquidita' AL MOMENTO DELLA DECISIONE, che e' due ore dopo il primo scambio: una
    risoluzione di cinquanta secondi e' gia' molto piu' fine del necessario;
 2. le riserve sono RI-OTTENIBILI dalla catena in qualunque momento — dimostrato il 22/09:
    202.752 letture su 4.169 pool in 75 secondi. Non e' un dato irripetibile;
 3. si tocca solo cio' che supera SOGLIA_MB; i file piccoli restano intatti;
 4. scrive prima il file nuovo e sostituisce solo a scrittura riuscita.

Con PROVA=1 non scrive niente e dice solo quanto risparmierebbe.
"""
import gzip
import json
import os

GRANO = int(os.environ.get("GRANO", 25))
SOGLIA_MB = float(os.environ.get("SOGLIA_MB", 5))
PROVA = os.environ.get("PROVA", "0") == "1"


def assottiglia(p):
    tenute = {}
    n = 0
    for riga in gzip.open(p, "rt"):
        riga = riga.strip()
        if not riga:
            continue
        try:
            r = json.loads(riga)
        except Exception:
            continue
        n += 1
        b = r.get("blocco")
        if b is None:
            tenute[("x", n)] = r          # senza blocco non si sa raggrupparla: si TIENE
            continue
        # dentro ogni gruppo si tiene l'ULTIMA: e' la piu' vicina al momento successivo
        tenute[b // GRANO] = r
    return n, list(tenute.values())


def main():
    tot_prima = tot_dopo = 0
    toccati = 0
    for ch in ("base", "robinhood"):
        d = f"data/multichain/{ch}/riserve"
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            s = os.path.getsize(p)
            if s < SOGLIA_MB * 1024 * 1024:
                continue
            n, righe = assottiglia(p)
            if not righe or len(righe) >= n:
                continue
            tmp = p + ".nuovo"
            with gzip.open(tmp, "wt") as f:
                for r in righe:
                    f.write(json.dumps(r) + "\n")
            s2 = os.path.getsize(tmp)
            tot_prima += s
            tot_dopo += s2
            toccati += 1
            print(f"   {fn[:18]}… {n:,} -> {len(righe):,} righe | "
                  f"{s/1e6:.1f} -> {s2/1e6:.1f} MB", flush=True)
            if PROVA:
                os.remove(tmp)
            else:
                os.replace(tmp, p)        # sostituzione atomica: o il vecchio o il nuovo, mai un mozzicone
    print(f"\nASSOTTIGLIA | {toccati} file: {tot_prima/1e6:.0f} -> {tot_dopo/1e6:.0f} MB "
          f"(risparmio {(tot_prima-tot_dopo)/1e6:.0f} MB)"
          + ("  [PROVA: non ho scritto niente]" if PROVA else ""))


if __name__ == "__main__":
    main()
