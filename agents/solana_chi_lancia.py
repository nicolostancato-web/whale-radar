"""IL PRIMO COMPRATORE E CHI VENDE SENZA AVER COMPRATO: le due strade che restano.

A) IL PRIMO COMPRATORE di un gettone pump.fun e' quasi sempre chi lo lancia (l'acquisto del
   dev). E' la posizione piu' favorevole che esista: prezzo di apertura, prima di tutti.
   Se nemmeno LUI guadagna, il lato creatore e' chiuso come su Robinhood (dove un lancio
   silenzioso incassava 0,55 EUR contro 1,71 di costo).

B) CHI VENDE SENZA AVER MAI COMPRATO in quella serie: i gettoni gli sono arrivati da fuori.
   Su Base era il 32% del venduto, ma non si poteva distinguere un regalo da un acquisto fatto
   altrove. Qui la serie e' la vita INTERA del gettone (verificato: nessuno tocca il tetto
   delle 400 firme), quindi «non ha mai comprato qui» vuol dire davvero «non l'ha comprato».

Nessun credito speso: i dati ci sono.
"""
import collections, json, os, statistics, sys

DENTRO = "data/multichain/solana/gettoni.jsonl"


def main():
    primi, altri = [], []
    quota_regalo, venduto_regalo = [], []
    for r in open(DENTRO):
        d = json.loads(r)
        P = sorted(d["s"])
        if len(P) < 25:
            continue
        # A) il primo compratore: quanto spende e quanto incassa su QUESTO gettone
        primo = next((x[3] for x in P if x[2]), None)
        if primo:
            sp = sum(x[1] for x in P if x[2] and x[3] == primo)
            inc = sum(x[1] for x in P if not x[2] and x[3] == primo)
            if sp > 0:
                primi.append(inc / sp - 1)
        # tutti gli altri compratori, come confronto
        comp = collections.defaultdict(lambda: [0.0, 0.0])
        for sl, p, compra, chi in P:
            comp[chi][0 if compra else 1] += p
        for chi, (sp, inc) in comp.items():
            if chi != primo and sp > 0:
                altri.append(inc / sp - 1)
        # B) chi vende senza aver mai comprato
        ha_comprato = {x[3] for x in P if x[2]}
        tot_v = sum(x[1] for x in P if not x[2])
        reg_v = sum(x[1] for x in P if not x[2] and x[3] not in ha_comprato)
        if tot_v > 0:
            quota_regalo.append(reg_v / tot_v)
            venduto_regalo.append((reg_v, len({x[3] for x in P if not x[2] and x[3] not in ha_comprato})))
    print(f"CHI LANCIA | {len(primi)} gettoni con un primo compratore identificabile\n")
    if primi:
        print(f"   A) IL PRIMO COMPRATORE (quasi sempre chi lancia)")
        print(f"      profitto mediano: {statistics.median(primi)*100:+.1f}%   in utile: "
              f"{sum(1 for x in primi if x>0)/len(primi)*100:.0f}%")
        print(f"      il migliore {max(primi)*100:+.0f}%, il peggiore {min(primi)*100:+.0f}%")
    if altri:
        print(f"      tutti gli ALTRI compratori, per confronto: mediana "
              f"{statistics.median(altri)*100:+.1f}%, in utile {sum(1 for x in altri if x>0)/len(altri)*100:.0f}%")
    if quota_regalo:
        print(f"\n   B) CHI VENDE SENZA AVER MAI COMPRATO")
        print(f"      quota mediana del venduto che viene da loro: {statistics.median(quota_regalo)*100:.0f}%")
        print(f"      gettoni dove superano meta' del venduto: "
              f"{sum(1 for x in quota_regalo if x>0.5)}/{len(quota_regalo)}")
        print(f"      venditori senza acquisto, mediana per gettone: "
              f"{statistics.median([n for _,n in venduto_regalo]):.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
