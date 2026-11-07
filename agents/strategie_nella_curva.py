"""Stop loss e bersagli dentro la curva, provati sui cammini registrati.

LA RICHIESTA DI NICOLO' (11/10): «entrando a 1,5, mettendo un potenziale stop loss al 60%, e
magari ne perdi un po', pero' gli altri ti fanno per 3, per 4: deve essere tutto calcolato.»

Questo file e' la risposta, e vive dei dati che la prova registra ad ogni scambio: il cammino
di ogni posizione, con minimo e massimo. Senza quel cammino, provare uno stop al 60% vorrebbe
dire accendere un esperimento nuovo e aspettare giorni; con il cammino, si prova in un secondo
su tutte le posizioni gia' viste — comprese quelle ancora aperte, perche' lo stop e il bersaglio
si giudicano su cio' che e' giа' accaduto.

LE REGOLE DI ONESTA' sono quelle degli altri simulatori: si stampa TUTTA la griglia, mai la
riga migliore; ogni media con il suo intervallo; e con pochi casi si guarda la FORMA, perche'
provare venti combinazioni su dieci posizioni trova sempre qualcosa.
"""
import json
import os
import statistics
import sys

CHAIN = os.environ.get("CHAIN", "robinhood")
STATO = f"data/multichain/{CHAIN}/prova_nella_curva.json"
COSTO = 1.02


def simula(cam, diplomata, stop=None, bersaglio=None):
    """Cammina sui punti [blocco, x]. Torna il moltiplicatore al netto dei costi.

    Ordine dentro un punto: prima lo stop, poi il bersaglio. E' la scelta PRUDENTE — se in un
    punto il prezzo ha toccato entrambi, si assume il caso peggiore. L'alternativa (prima il
    bersaglio) farebbe sembrare ogni regola migliore di quanto e'.
    """
    for _b, x in cam:
        if stop and x <= stop:
            return stop / COSTO
        if bersaglio and x >= bersaglio:
            return bersaglio / COSTO
    ultimo = cam[-1][1] if cam else 1.0
    return ultimo / COSTO


def riga(nome, r):
    if not r:
        return
    sd = statistics.stdev(r) if len(r) > 1 else 0
    ic = 1.96 * sd / len(r) ** 0.5
    print(f"{nome:<34}{statistics.mean(r)*100:>8.0f}%{f'±{ic*100:.0f}':>9}"
          f"{statistics.median(r)*100:>9.0f}%{sum(1 for x in r if x > 0):>7}/{len(r)}")


def main():
    if not os.path.exists(STATO):
        print("STRATEGIE | la prova non e' ancora partita")
        return 0
    st = json.load(open(STATO))
    sogl = st["regole"].get("soglie_native") or [st["regole"].get("soglia_nativi")]
    for s0 in sogl:
        casi = [(p.get("cammino") or [], bool((p.get("esito") or {}).get("verso") == "diploma"))
                for p in st["posizioni"].values() if p.get("soglia") == s0]
        casi = [(c, d) for c, d in casi if c]
        print(f"\nSOGLIA {s0} — {len(casi)} posizioni con cammino registrato")
        if not casi:
            print("   nessun cammino ancora: la griglia si leggera' quando ci saranno posizioni")
            continue
        print(f"{'regola':<34}{'media':>9}{'interv.':>9}{'mediana':>9}{'in utile':>9}")
        print("-" * 70)
        riga("niente stop, si esce al diploma",
             [simula(c, d) - 1 for c, d in casi])
        for s in (0.4, 0.5, 0.6, 0.7):
            riga(f"stop a -{(1-s)*100:.0f}%", [simula(c, d, stop=s) - 1 for c, d in casi])
        for b in (2.0, 3.0, 4.0):
            riga(f"bersaglio {b:.0f}x", [simula(c, d, bersaglio=b) - 1 for c, d in casi])
        for s, b in ((0.6, 3.0), (0.5, 3.0), (0.6, 4.0), (0.4, 2.0)):
            riga(f"stop -{(1-s)*100:.0f}% e bersaglio {b:.0f}x",
                 [simula(c, d, stop=s, bersaglio=b) - 1 for c, d in casi])
        print("-" * 70)
        mx = sorted(max((x for _b, x in c), default=1.0) for c, _d in casi)
        mn = sorted(min((x for _b, x in c), default=1.0) for c, _d in casi)
        print(f"massimo toccato: mediana {statistics.median(mx):.2f}x, "
              f"sopra 2x in {sum(1 for x in mx if x >= 2)}/{len(mx)}, "
              f"sopra 3x in {sum(1 for x in mx if x >= 3)}/{len(mx)}")
        print(f"minimo toccato:  mediana {statistics.median(mn):.2f}x, "
              f"sotto 0,6 in {sum(1 for x in mn if x <= 0.6)}/{len(mn)}")
    print("\ncon pochi casi si guarda la forma, non la riga migliore: venti combinazioni su "
          "dieci\nposizioni trovano sempre qualcosa. Ogni media ha il suo intervallo al 95%.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
