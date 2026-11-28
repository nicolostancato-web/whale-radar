"""LA PROVA DEL RITARDO: dopo che qualcuno compra, resta qualcosa da prendere?

== COSA RISPONDE, E PERCHE' VIENE PRIMA DEL DATABASE DEI PORTAFOGLI ==

Copiare vuol dire arrivare dopo. Il suo acquisto ha gia' mosso il prezzo, quindi il nostro
guadagno non parte dal SUO prezzo ma da quello che c'e' DOPO di lui, piu' il nostro ritardo.
Nel pre-diploma questa distinzione valeva tutto: +11,50% nell'istante, +1,25% un secondo dopo.

Qui si misura, su TUTTI gli acquisti e senza sapere chi li ha fatti, quanto resta da prendere
dopo che qualcuno ha comprato. Se non basta a coprire il costo del giro, nessun portafoglio al
mondo rende redditizia la copia, perche' copiando possiamo prendere solo quel movimento li'.

== PERCHE' NON SI GUARDA SOLO LA MEDIA ==

Un portafoglio bravo sceglie, e una media negativa non esclude che qualcuno becchi i casi buoni.
Quindi si riporta anche la QUOTA di acquisti seguiti da un movimento che copre i costi: quella
quota e' l'asticella che un selezionatore deve battere, e saperla prima di costruire il
database dice se vale la pena.

== IL COSTO VERO ==

Il campo `fee` dello Swap vale zero: l'hook di Pons preleva dal delta (~1%) e sopra c'e' la
tassa del creatore. Qui si usa un costo di giro dichiarato come costante unica, e si stampa la
tabella a piu' costi cosi' il lettore vede dove sta il confine.
"""
import gzip, json, os, statistics, sys

import glob
DENTRO = sorted(glob.glob("data/multichain/robinhood/scambi_postdiploma_*.jsonl"))
BLOCCO = 0.093
# il nostro ritardo misurato: ~1 secondo = 11 blocchi. Gli altri orizzonti servono a vedere
# la forma della curva, non a scegliere il migliore a posteriori.
ORIZZONTI = [("subito", 0), ("+1 blocco", 1), ("+11 blocchi (1s)", 11),
             ("+1 minuto", int(60 / BLOCCO)), ("+5 minuti", int(300 / BLOCCO)),
             ("+1 ora", int(3600 / BLOCCO))]
COSTI = [0.0, 0.02, 0.04, 0.06]


def prezzi(s):
    """(blocco, prezzo, nativi, e' un acquisto) per ogni scambio. Prezzo = nativo per gettone."""
    out = []
    for b, a0, a1, sq in s:
        if a1 == 0:
            continue
        out.append((b, abs(a0 / a1), abs(a0), a0 > 0))
    return out


def dopo(P, i, salto):
    """Il primo prezzo a o dopo (blocco dell'acquisto + salto). Nessuna interpolazione."""
    bersaglio = P[i][0] + salto
    for j in range(i + 1, len(P)):
        if P[j][0] >= bersaglio:
            return P[j][1]
    return None


def main():
    minimo = float(os.environ.get("MINIMO_NATIVI", "0.0003"))   # ~1 EUR: la polvere non conta
    per_oriz = {e: [] for e, _ in ORIZZONTI}
    monete = acquisti = 0
    rotte = [0]
    for f_ in DENTRO:
      for riga in open(f_):
        # UNA RIGA A META' NON E' UN GUASTO: e' il raccoglitore che sta ancora scrivendo.
        # Si salta e SI CONTA, perche' un salto taciuto diventa un buco invisibile.
        try:
            d = json.loads(riga)
        except json.JSONDecodeError:
            rotte[0] += 1
            continue
        P = prezzi(d["s"])
        if len(P) < 3:
            continue
        monete += 1
        for i, (b, p, nat, compra) in enumerate(P):
            if not compra or nat < minimo:
                continue
            acquisti += 1
            for et, salto in ORIZZONTI:
                q = dopo(P, i, salto)
                if q is not None:
                    per_oriz[et].append(q / p - 1)
    print(f"PROVA DEL RITARDO | {monete:,} monete, {acquisti:,} acquisti sopra {minimo} nativi"
          + (f" | {rotte[0]} righe ancora in scrittura, saltate" if rotte[0] else "") + "\n")
    print(f"   {'quando compriamo noi':<20}{'casi':>9}{'resa lorda':>12}{'+/-':>7}"
          + "".join(f"{'oltre '+str(int(c*100))+'%':>11}" for c in COSTI[1:]))
    print('   ' + '-' * 72)
    for et, _ in ORIZZONTI:
        v = per_oriz[et]
        if len(v) < 50:
            continue
        sd = statistics.stdev(v)
        quote = "".join(f"{sum(1 for x in v if x > c)/len(v)*100:>10.1f}%" for c in COSTI[1:])
        print(f"   {et:<20}{len(v):>9,}{statistics.mean(v)*100:>+11.2f}%"
              f"{1.96*sd/len(v)**0.5*100:>7.1f}{quote}")
    print('   ' + '-' * 72)
    print("   le ultime colonne sono la QUOTA di acquisti seguiti da un movimento che supera")
    print("   quel costo: e' l'asticella che un selezionatore di portafogli deve battere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
