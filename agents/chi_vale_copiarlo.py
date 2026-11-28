"""CHI VALE COPIARLO: i portafogli misurati come li vivremmo NOI, non come li vive lui.

== LA DOMANDA, RESA UN NUMERO (20/10) ==

Seguendo OGNI acquisto del mercato — 6,4 milioni di operazioni, entrata 11 blocchi dopo
(il nostro secondo misurato), bersaglio 2x e stop -50% dichiarati prima — i raddoppi sono il
**29,36%** e il pareggio col costo vero del giro (~6%) sta al **37,3%**.

Quindi un portafoglio vale copiarlo se, seguendo i SUOI acquisti con la stessa identica regola,
i raddoppi salgono dal 29,36% al 37,3%. Non «quanto ha guadagnato lui»: quello lo ha incassato
al suo prezzo, che noi non possiamo avere.

== LE DUE PROTEZIONI, SCRITTE PRIMA DI GUARDARE ==

1. META' DEL PERIODO PER CERCARE, META' MAI VISTA PER GIUDICARE. Cercando fra migliaia di
   portafogli si trova sempre qualcuno con una striscia fortunata: vale solo se tiene dopo.
2. SI CONTANO LE MONETE, NON LE OPERAZIONI. Un portafoglio con 300 acquisti su 4 monete ha
   quattro casi, non trecento.
"""
import glob, gzip, json, os, statistics, sys
from collections import defaultdict

BERS, STOP, RITARDO = 2.0, 0.5, 11
MIN_MONETE = int(os.environ.get("MIN_MONETE", "8"))


def serie():
    """prezzi per pool: [(blocco, prezzo, e_un_acquisto)]"""
    S = {}
    for f in sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl*")):
        ap = gzip.open if f.endswith(".gz") else open
        for r in ap(f, "rt"):
            try:
                d = json.loads(r)
            except Exception:
                continue
            if d["pool"] in S:
                continue
            P = []
            for b, a0, a1, sq in d["s"]:
                if a1 and a0:
                    p = abs(a0 / a1)
                    if p > 0:
                        P.append((b, p, a0 > 0))
            if len(P) >= 10:
                S[d["pool"]] = (P, [x[0] for x in P], indice(P))
    return S


import bisect

PASSO_B = 64


def indice(P):
    """Un indice a blocchi da 64: massimo e minimo dei prezzi di VENDITA in ogni blocco.

    PERCHE' (20/10). Cercare in avanti riga per riga, per ogni acquisto di ogni moneta, e'
    quadratico: la prima versione non ha finito in dieci minuti. Con questo indice si saltano
    64 righe alla volta e si scende al dettaglio solo nel blocco dove la soglia puo' essere
    toccata. Stesso risultato, nessuna approssimazione.
    """
    B = P[0]
    mx, mn = [], []
    for i in range(0, len(P), PASSO_B):
        f = [p for _, p, c in P[i:i + PASSO_B] if not c]
        mx.append(max(f) if f else -1.0)
        mn.append(min(f) if f else float("inf"))
    return mx, mn


def esito(P, blocchi, IDX, blocco):
    """Cosa succede a NOI se compriamo 11 blocchi dopo il suo acquisto."""
    j0 = bisect.bisect_left(blocchi, blocco + RITARDO)
    if j0 >= len(P) or P[j0][1] <= 0:
        return None
    p0 = P[j0][1]
    alto, basso = BERS * p0, STOP * p0
    mx, mn = IDX
    j = j0 + 1
    while j < len(P):
        k = j // PASSO_B
        fine = min((k + 1) * PASSO_B, len(P))
        if mx[k] < alto and mn[k] > basso:
            j = fine
            continue
        for t in range(j, fine):
            if P[t][2]:
                continue
            x = P[t][1]
            if x >= alto:
                return 1
            if x <= basso:
                return 0
        j = fine
    return 1 if P[-1][1] >= alto else 0


def main():
    S = serie()
    print(f"COPIABILITA | serie di prezzo per {len(S):,} monete", flush=True)
    # per portafoglio: lista di (blocco, pool, esito)
    per = defaultdict(list)
    nf = 0
    saltati = 0
    for f in sorted(glob.glob("data/multichain/robinhood/registro_portafogli_*_p*.jsonl*")):
        # UN FILE PUO' SPARIRE MENTRE LO LEGGO: il raccoglitore ruota i pezzi e li comprime.
        # Non e' un guasto, e' il funzionamento normale. Si prova la versione compressa e, se
        # manca anche quella, si salta CONTANDO: un salto taciuto diventa un buco invisibile.
        try:
            ap = gzip.open if f.endswith(".gz") else open
            fh = ap(f, "rt")
        except FileNotFoundError:
            try:
                fh = gzip.open(f + ".gz", "rt")
            except Exception:
                saltati += 1
                continue
        for r in fh:
            try:
                d = json.loads(r)
            except Exception:
                continue
            tup = S.get(d["pool"])
            if not tup:
                continue
            P, blocchi, IDX = tup
            nf += 1
            for b, i, h, chi, verso, g, nat, sq, conf in d["r"]:
                if verso != "c" or conf != "c" or not nat or nat < 0.003:
                    continue
                e = esito(P, blocchi, IDX, b)
                if e is not None:
                    per[chi].append((b, d["pool"], e))
    print(f"COPIABILITA | {nf:,} monete lette, {len(per):,} portafogli compratori"
          + (f", {saltati} file saltati perche' in rotazione" if saltati else ""), flush=True)
    tagli = sorted(x[0] for v in per.values() for x in v)
    meta = tagli[len(tagli) // 2]
    base_a = [x[2] for v in per.values() for x in v if x[0] < meta]
    base_b = [x[2] for v in per.values() for x in v if x[0] >= meta]
    print(f"\n   riferimento: tutti gli acquisti del mercato")
    print(f"      prima meta  {sum(base_a)/len(base_a)*100:.2f}% di raddoppi su {len(base_a):,}")
    print(f"      meta mai vista {sum(base_b)/len(base_b)*100:.2f}% su {len(base_b):,}")
    print(f"      serve il 37,3% per pareggiare col costo del giro\n")
    # IL CONFRONTO DEVE ESSERE ALLA PARI (20/10). La prima versione collassava sulla moneta i
    # SOLI scelti e li confrontava col riferimento NON collassato: 23,4% contro 32,6% sembrava
    # un crollo, ma erano due misure diverse. Qui entrambi si collassano sulle STESSE monete.
    def per_moneta(lista):
        d = defaultdict(list)
        for bl, pool, e in lista:
            d[pool].append(e)
        return d

    rif_b = per_moneta([x for v in per.values() for x in v if x[0] >= meta])
    print(f"   {'soglia':<10}{'scelti':>8}{'monete':>8}{'loro %':>9}{'rif. %':>9}{'scarto':>9}{'+/-':>8}")
    print('   ' + '-' * 62)
    for soglia in (0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00):
        scelti = []
        for w, v in per.items():
            a = [x for x in v if x[0] < meta]
            if len({x[1] for x in a}) < MIN_MONETE:
                continue
            if a and sum(x[2] for x in a) / len(a) >= soglia:
                scelti.append(w)
        b = [x for w in scelti for x in per[w] if x[0] >= meta]
        if len(b) < 60:
            continue
        pm = per_moneta(b)
        # il riferimento si calcola SOLO sulle monete che loro hanno toccato: altrimenti si
        # confronta la loro scelta di monete col mercato intero, e vince la scelta, non l'abilita'
        # lo scarto si misura MONETA PER MONETA e poi si media: cosi' l'intervallo e' sulle
        # monete, che sono i casi indipendenti, non sulle operazioni.
        coppie = [(statistics.mean(v), statistics.mean(rif_b[k])) for k, v in pm.items() if k in rif_b]
        diff = [a - b for a, b in coppie]
        loro = statistics.mean([a for a, _ in coppie])
        rif = statistics.mean([b for _, b in coppie])
        ic = 1.96 * statistics.stdev(diff) / len(diff) ** 0.5 if len(diff) > 2 else float("nan")
        print(f"   {int(soglia*100):>3}%{'':<6}{len(scelti):>8,}{len(pm):>8,}"
              f"{loro*100:>8.2f}%{rif*100:>8.2f}%{(loro-rif)*100:>+8.2f}{ic*100:>8.2f}")
    print('   ' + '-' * 54)
    print("   «rif.» = tutti gli acquisti sulle STESSE monete, cosi' si misura la bravura")
    print("   e non il merito di aver scelto monete migliori.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
