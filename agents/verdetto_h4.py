"""Il verdetto di H4 — la successione di pattern messa alla prova sul futuro.

Scritto il 23/09 alle 08:35, PRIMA che il primo esito fosse disponibile, cosi' che le soglie non
possano essere ritoccate dopo aver visto i numeri. E' la stessa disciplina dell'esame del database:
chi scrive il metro dopo aver visto la gara non sta misurando, sta raccontando.

LA CONDIZIONE DI MORTE, da IPOTESI.md, non modificabile qui:
  su 150 pool SCELTI distinti, se la quota che fa +50% non arriva almeno al 7%,
  oppure se non supera di almeno DUE VOLTE la quota del gruppo di controllo, H4 e' morta.

Perche' servono entrambe le condizioni: la prima dice che il segnale e' abbastanza forte da pagare
i costi, la seconda che il merito e' della REGOLA e non del mercato. Un mese in cui tutto sale
supererebbe la prima da solo.
"""
import collections
import json
import os

REG = "data/loop1/segnali.jsonl"
IPOTESI = os.environ.get("IPOTESI", "H5")   # H4 misurava un altro momento: non si mescola
BERSAGLIO = 0.50          # cosa chiamiamo "colpo grosso"
QUOTA_MINIMA = 0.07       # soglia assoluta, da IPOTESI.md
RAPPORTO_MINIMO = 2.0     # quante volte il controllo, da IPOTESI.md


def esiti():
    """L'ULTIMO stato scritto per ogni segnale: il registro e' ad aggiunte, non a sovrascritture."""
    ultimo = {}
    for riga in open(REG):
        riga = riga.strip()
        if not riga:
            continue
        try:
            r = json.loads(riga)
        except Exception:
            continue
        if r.get("ipotesi", "").startswith(IPOTESI):
            ultimo[r["id"]] = r
    return list(ultimo.values())


def main():
    if not os.path.exists(REG):
        print("VERDETTO | manca il registro")
        return
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    aperti = collections.Counter()
    for r in esiti():
        gruppo = "scelto" if "scelto" in r["ipotesi"] else "controllo"
        chain = r["chain"]
        if r["stato"] == "finestra_aperta":
            aperti[(chain, gruppo)] += 1
            continue
        # Un pool che NON si e' riusciti a comprare non e' un successo mancato: e' una domanda
        # a cui il mercato non ha risposto. Si conta a parte, MAI come perdita e mai come vittoria.
        if r["stato"] == "tentato_fallito":
            per[chain][gruppo + ":non_eseguibile"].append(r)
            continue
        rend = r.get("rendimento")
        if rend is None:
            continue
        per[chain][gruppo].append(rend)

    if not per:
        # Il silenzio e' ambiguo: puo' voler dire «tutto aperto» o «il giudice e' rotto».
        # Va detto quale dei due.
        tot = sum(aperti.values())
        print(f"VERDETTO | nessun esito ancora chiuso. {tot} previsioni con la finestra aperta "
              f"({aperti[('robinhood','scelto')]} scelti su robinhood). Si aspetta.")
        return

    for chain in sorted(per):
        sc = per[chain].get("scelto", [])
        co = per[chain].get("controllo", [])
        ne_s = len(per[chain].get("scelto:non_eseguibile", []))
        ne_c = len(per[chain].get("controllo:non_eseguibile", []))
        print(f"\n=== {chain} ===")
        print(f"   chiusi: {len(sc)} scelti, {len(co)} di controllo | "
              f"ancora aperti: {aperti[(chain,'scelto')]} e {aperti[(chain,'controllo')]}")
        if ne_s or ne_c:
            tot_s = len(sc) + ne_s
            print(f"   non eseguibili (non si e' riusciti a comprare): {ne_s} scelti "
                  f"({100*ne_s/max(1,tot_s):.0f}%), {ne_c} di controllo")
        if not sc:
            print("   nessun esito chiuso fra gli scelti: niente da giudicare")
            continue
        qs = sum(1 for x in sc if x >= BERSAGLIO) / len(sc)
        qc = (sum(1 for x in co if x >= BERSAGLIO) / len(co)) if co else 0.0
        rapporto = (qs / qc) if qc > 0 else float("inf")
        print(f"   fanno +50%: scelti {100*qs:.1f}%  |  controllo {100*qc:.1f}%  |  "
              f"rapporto {rapporto:.1f}x")
        mediana_s = sorted(sc)[len(sc)//2]
        mediana_c = sorted(co)[len(co)//2] if co else 0
        print(f"   mediana: scelti {100*mediana_s:+.1f}%  |  controllo {100*mediana_c:+.1f}%")

        if len(sc) < 150:
            print(f"   ANCORA PRESTO: {len(sc)}/150 esiti chiusi fra gli scelti. Non si giudica.")
            continue
        passa_quota = qs >= QUOTA_MINIMA
        passa_rapporto = rapporto >= RAPPORTO_MINIMO
        print(f"   quota >= {100*QUOTA_MINIMA:.0f}%: {'SI' if passa_quota else 'NO'}   "
              f"rapporto >= {RAPPORTO_MINIMO}x: {'SI' if passa_rapporto else 'NO'}")
        if passa_quota and passa_rapporto:
            print("   VERDETTO: H4 REGGE sulla prova in avanti.")
        else:
            print("   VERDETTO: H4 E' MORTA. Si butta e si riparte dalla ricerca.")


if __name__ == "__main__":
    main()
