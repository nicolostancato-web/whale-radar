"""LA PROVA IN AVANTI SU BASE: la regola congelata, misurata sui pool accumulati.

La regola e' stata scritta in agents/base_accumulo.py PRIMA di raccogliere qualsiasi dato:
  entrata su una stampa di ACQUISTO entro i primi 120 secondi di vita del pool, un blocco
  dopo il segnale; uscita su una stampa di VENDITA a +30 minuti; si confronta con la
  TARATURA dello stesso insieme (comprare e rivendere subito), e serve che la differenza
  resti sopra un punto.

Qui non si tocca nulla di quella regola: si legge soltanto quanto fa, e quanti casi abbiamo.
"""
import json, os, statistics, sys

DENTRO = "data/multichain/base/accumulo_nuovi.jsonl"
FINESTRA_ETA = 120 / 2.0        # 120 secondi = 60 blocchi su Base
SALTO = 900                     # 30 minuti
RITARDO = 1


def op(P, salto):
    """entrata su un ACQUISTO, uscita su una VENDITA dopo `salto` blocchi"""
    out = []
    n0 = P[0][0]
    for i, (b, p, compra) in enumerate(P):
        if not compra or (b - n0) > FINESTRA_ETA:
            continue
        ing = next((j for j in range(i + 1, len(P)) if P[j][0] >= b + RITARDO and P[j][2]), None)
        if ing is None or P[ing][1] <= 0:
            continue
        usc = next((k for k in range(ing + 1, len(P))
                    if P[k][0] >= P[ing][0] + salto and not P[k][2]), None)
        if usc is None:
            # NESSUNA VENDITA DOPO L'ORIZZONTE = restiamo col sacco in mano. Non e' «non
            # misurabile»: e' il caso peggiore della strategia e va contato. Si riporta nei
            # due modi onesti: all'ultimo prezzo visto, e a zero.
            out.append(("bloccata", P[-1][1] / P[ing][1] - 1))
            continue
        out.append(("chiusa", P[usc][1] / P[ing][1] - 1))
    return out


def main():
    if not os.path.exists(DENTRO):
        print("PROVA AVANTI | niente accumulato ancora")
        return 0
    tar, res, res0, bloc, pool = [], [], [], [], 0
    for r in open(DENTRO):
        try:
            d = json.loads(r)
        except Exception:
            continue
        P = sorted(d["s"])
        a = [x for _, x in op(P, 0)]
        bb = op(P, SALTO)
        if len(a) >= 3 and len(bb) >= 3:
            tar.append(statistics.median(a))
            res.append(statistics.median([x for _, x in bb]))
            res0.append(statistics.median([x if s_ == "chiusa" else -1.0 for s_, x in bb]))
            bloc.append(sum(1 for s_, _ in bb if s_ == "bloccata") / len(bb))
            pool += 1
    if pool < 5:
        print(f"PROVA AVANTI | {pool} pool validi: troppo pochi, servono almeno 100")
        return 0
    d0 = [b - a for a, b in zip(tar, res)]
    ic = 1.96 * statistics.stdev(d0) / len(d0) ** 0.5 if len(d0) > 2 else float("nan")
    print(f"PROVA AVANTI SU BASE — regola congelata, pool mai visti quando l'ho scritta\n")
    print(f"   pool accumulati e validi: {pool}")
    print(f"   taratura (compra e rivendi subito): {statistics.median(tar)*100:+.2f}%")
    print(f"   la regola (+30 minuti):             {statistics.median(res)*100:+.2f}%")
    print(f"   DIFFERENZA:                         {statistics.mean(d0)*100:+.2f}%  +/-{ic*100:.2f}")
    print(f"   pool in cui la regola batte la taratura: {sum(1 for x in d0 if x>0)/len(d0)*100:.0f}%")
    print(f"\n   quota di operazioni rimaste BLOCCATE (nessuno a cui vendere): "
          f"{statistics.mean(bloc)*100:.0f}%")
    print(f"   la regola contando le bloccate a ZERO: {statistics.median(res0)*100:+.2f}%")
    print(f"\n   soglia dichiarata prima: serve una differenza sopra +1,00 punto, su 100+ pool.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
