"""E se uscissimo a un'ORA FISSA invece che al raddoppio? Misurato sul cammino.

PERCHE' (11/10, domanda di Nicolo'): «al di la' della nostra strategia, di tutti questi live ci
sono delle robe interessanti per essere proficui?»

Le uscite a tempo sono la famiglia di regole piu' onesta da provare su pochi casi: non scelgono
nulla, si applicano a TUTTE le monete allo stesso modo. Provare una selezione («compra solo
quelle con X») su 31 casi trova sempre qualcosa; provare «esci dopo 15 minuti, sempre» no — c'e'
una regola sola per riga, e la riga vince o perde su tutto il campione.

Il cancello e' lo stesso degli altri: la simulazione senza uscita a tempo deve ricostruire la
regola viva, altrimenti i numeri sotto non si leggono.
"""
import json
import statistics
import sys

PROVA = "data/multichain/robinhood/prova_in_avanti.json"
CAMMINO = "data/multichain/robinhood/cammino_posizioni.json"
ORIZZONTE = 600_000
COSTI = 0.95
BLOCCHI_AL_MINUTO = 600            # ~10 al secondo


def simula(cam, minuti=None, bersaglio=2.0, presa=None, prezzo_finale=None):
    """minuti: esce a tempo. bersaglio: esce al multiplo. presa: (quota, a_quale_x) parziale."""
    tetto = minuti * BLOCCHI_AL_MINUTO if minuti else ORIZZONTE
    tetto = min(tetto, ORIZZONTE)
    fatto, resa = 0.0, 0.0
    quota = 1.0
    ultimo = 1.0
    for p in cam:
        b, x = p[0], p[1]
        if b > tetto:
            break
        mx = p[3] if len(p) > 3 else x
        mn = p[2] if len(p) > 2 else x
        ultimo = x
        if presa and quota == 1.0 and mx >= presa[1]:
            resa += presa[0] * presa[1] * COSTI
            quota -= presa[0]
        if bersaglio and mx >= bersaglio:
            return resa + quota * bersaglio * COSTI
    # L'ULTIMO PREZZO VERO, QUANDO CE L'ABBIAMO (11/10). Il cammino campiona un prezzo ogni
    # cinque scambi: nell'istante dell'uscita l'ultimo campione non e' l'ultimo prezzo. Su due
    # monete in caduta rapida la simulazione dava -63% dove la realta' era -75%, cioe' era
    # OTTIMISTA sullo stare dentro. Importa la direzione: l'errore rendeva le righe a orizzonte
    # lungo migliori di quanto sono, quindi il «tempo e' nemico» era sottostimato, non gonfiato.
    if prezzo_finale is not None and tetto >= ORIZZONTE:
        ultimo = prezzo_finale
    return resa + quota * ultimo * COSTI


def riga(nome, r):
    sd = statistics.stdev(r) if len(r) > 1 else 0
    ic = 1.96 * sd / len(r) ** 0.5
    print(f"{nome:<34}{statistics.mean(r)*100:>8.1f}%{f'±{ic*100:.1f}':>10}"
          f"{statistics.median(r)*100:>9.1f}%{sum(1 for x in r if x > 0):>7}")


def main():
    pos = json.load(open(PROVA))["posizioni"]
    cam = json.load(open(CAMMINO))["monete"]
    casi, veri = [], []
    for t, p in pos.items():
        if p["stato"] != "chiusa":
            continue
        c = (cam.get(t) or {}).get("cammino")
        if not c:
            continue
        fin = None
        if p.get("ultimo_prezzo") and p.get("entrata"):
            fin = p["ultimo_prezzo"] / p["entrata"]
        casi.append((c, fin))
        veri.append((p.get("esito") or {}).get("rendimento"))
    ric = [simula(c, prezzo_finale=f) - 1 for c, f in casi]
    scarti = [abs(a - b) for a, b in zip(ric, veri) if b is not None]
    peggio = max(scarti) if scarti else 9
    print(f"TEMPO | {len(casi)} posizioni chiuse")
    print(f"controllo: ricostruisco la regola viva con uno scarto massimo di "
          f"{peggio*100:.1f} punti")
    if peggio > 0.25:
        print("SCARTO TROPPO GRANDE: non leggo il resto.")
        return 1
    print(f"\n{'regola':<34}{'media':>9}{'interv.':>10}{'mediana':>9}{'vinte':>7}")
    print("-" * 70)
    riga("2x secco (la regola viva)", ric)
    for m in (5, 15, 60, 240, 720):
        riga(f"esci dopo {m} min, qualunque sia",
             [simula(c, minuti=m, bersaglio=None, prezzo_finale=f) - 1 for c, f in casi])
    print("-" * 70)
    for m in (15, 60, 240):
        riga(f"2x, ma al massimo {m} min",
             [simula(c, minuti=m, prezzo_finale=f) - 1 for c, f in casi])
    print("-" * 70)
    for q, a in ((0.5, 1.5), (0.5, 1.3), (0.3, 1.5)):
        riga(f"prendi {q*100:.0f}% a {a}x, resto al 2x",
             [simula(c, presa=(q, a), prezzo_finale=f) - 1 for c, f in casi])
    print("-" * 70)
    print("se l'intervallo contiene lo zero, la riga non dimostra niente: con 31 casi\n"
          "si vedono solo differenze molto grandi (la dispersione misurata e' 80 punti).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
