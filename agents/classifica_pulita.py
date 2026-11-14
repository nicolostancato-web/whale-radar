"""LA CLASSIFICA CHE CONTIENE SOLO TRADING — tolto tutto quello che non lo e'.

Cinque voci che in questi giorni sono state scambiate per profitto, e che qui escono dal conto:
 1. BONIFICI: soldi che il proprietario manda al portafoglio operativo. Un portafoglio
    risultava il migliore con +12,54 SOL: aveva ricevuto un bonifico da 28.
 2. CAUZIONI: i ~0,0015 SOL che tornano chiudendo il conto di un gettone.
 3. PAGAMENTI per servizi: importi fissi e ripetuti da mittenti diversi.
 4. GETTONI RICEVUTI: 12 milioni di gettoni pagati con la sola cauzione, via un contratto di
    rilascio. Il lettore li leggeva come «comprati a 27 centesimi».
 5. LE VENDITE DI QUEI GETTONI: riconosciuto il regalo ma contata la vendita, il profitto
    diventava infinito. Un gettone ricevuto esce dal conto INSIEME alla sua vendita.

Resta solo: comprato dal mercato, venduto al mercato.
"""
import collections, json, os, statistics, sys

DENTRO = "data/multichain/solana/storia2.jsonl"


def main():
    R = []
    for r in open(DENTRO):
        d = json.loads(r)
        regalati = {g[1] for g in d.get("regali", [])}
        ops = [o for o in d["ops"] if o[3] not in regalati]
        if len(ops) < 10:
            continue
        comp = sum(o[4] for o in ops if o[2])
        vend = sum(o[4] for o in ops if not o[2])
        # quanto valeva la roba regalata, tenuta fuori ma mostrata
        vend_reg = sum(o[4] for o in d["ops"] if o[3] in regalati and not o[2])
        R.append({"w": d["w"], "n": len(ops), "g": len({o[3] for o in ops}),
                  "trading": vend - comp, "comp": comp,
                  "regali": len(regalati), "da_regali": vend_reg})
    if not R:
        print("CLASSIFICA | niente da misurare")
        return 0
    print(f"CLASSIFICA PULITA | {len(R)} portafogli, solo comprato-e-venduto sul mercato\n")
    print(f"   {'portafoglio':<16}{'scambi':>8}{'gettoni':>8}{'investito':>11}{'TRADING':>10}"
          f"{'regali':>8}{'venduto da regali':>19}")
    print('   ' + '-' * 82)
    for x in sorted(R, key=lambda y: -y["trading"])[:12]:
        print(f"   {x['w'][:14]:<16}{x['n']:>8}{x['g']:>8}{x['comp']:>11.2f}{x['trading']:>+10.2f}"
              f"{x['regali']:>8}{x['da_regali']:>19.2f}")
    print('   ' + '-' * 82)
    T = [x["trading"] for x in R]
    inv = [x["comp"] for x in R]
    print(f"\n   TRADING: mediana {statistics.median(T):+.3f} SOL   in utile {sum(1 for x in T if x>0)}/{len(T)}")
    print(f"   capitale investito, mediana {statistics.median(inv):.2f} SOL")
    rel = [x["trading"] / x["comp"] for x in R if x["comp"] > 0.05]
    if rel:
        print(f"   resa sul capitale: mediana {statistics.median(rel)*100:+.1f}%  "
              f"su {len(rel)} portafogli con almeno 0,05 SOL investiti")
    print(f"   portafogli che hanno ricevuto gettoni in regalo: {sum(1 for x in R if x['regali'])}/{len(R)}")
    print(f"   valore venduto proveniente da regali, totale: {sum(x['da_regali'] for x in R):.2f} SOL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
