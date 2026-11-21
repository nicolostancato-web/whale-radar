"""La tabella del PRE-DIPLOMA: le posizioni aperte dentro la curva, e le soglie.

COMANDO DI NICOLO' (11/10): «ti chiedero' recap metrics pre-diploma o post-diploma».
  pre-diploma  -> questo file                (agents/recap_curva.py)
  post-diploma -> la tabella delle promozioni (agents/recap_promozione.py)

Oltre alle posizioni, qui si stampa la cosa che vale piu' delle posizioni stesse: quante curve
toccano ogni soglia di riserva e quante di quelle si diplomano. E' la risposta alla domanda
aperta — «3,6 e' la soglia giusta, o si entra a meno?» — e si costruisce dal cammino di TUTTE le
curve, non solo di quelle in cui siamo entrati. Con una posizione ogni sette ore, aspettare che
le posizioni rispondano costerebbe settimane.
"""
import json
import os
import statistics
import sys
import time

CHAIN = os.environ.get("CHAIN", "robinhood")
STATO = f"data/multichain/{CHAIN}/prova_nella_curva.json"
SERVONO = 20


def main():
    if not os.path.exists(STATO):
        print("PRE-DIPLOMA | la prova non e' ancora partita")
        return 0
    st = json.load(open(STATO))
    r = st["regole"]
    pos = st["posizioni"]
    cur = st["curve"]
    ora = int(time.time())
    sogl = sorted({x["soglia"] for x in (r.get("strategie") or [])}) or \
        (r.get("soglie_native") or [r.get("soglia_nativi")])
    print(f"RECAP PRE-DIPLOMA — due regole in parallelo, entrata a riserva netta "
          f"{' e '.join(str(x) for x in sogl)} nativi; uscita al diploma, stop a "
          f"{r['stop']*100:.0f}% dell'entrata, orizzonte {r['orizzonte']//36000}h\n")

    righe = []
    for t, p in pos.items():
        e = p.get("esito") or {}
        righe.append((f"{p.get('soglia','?')}  {(p.get('gettone') or t)[:12]}",
                      p["stato"], e.get("verso", ""), e.get("rendimento"),
                      (ora - p["aperta_il"]) / 3600, p["min_x"], p["max_x"],
                      p.get("riserva_all_entrata")))
    righe.sort(key=lambda x: (x[1] != "aperta", -(x[3] if x[3] is not None else -9)))
    if righe:
        print(f"{'soglia / moneta':<21}{'stato':<9}{'come':<10}{'resa':>7}{'min':>7}{'max':>7}"
              f"{'ore':>6}{'riserva':>9}")
        print("-" * 76)
        for t, s, v, re_, ore, mn, mx, ris in righe:
            print(f"{t:<21}{s:<9}{v[:9]:<10}"
                  f"{(f'{re_*100:+.0f}%' if re_ is not None else '-'):>7}"
                  f"{mn:>7.2f}{mx:>7.2f}{ore:>6.1f}{(ris or 0):>9.2f}")
        print("-" * 76)
    else:
        print("nessuna posizione ancora: nessuna curva ha toccato la soglia")

    print()
    nomi = [x["nome"] for x in (r.get("strategie") or [])] or [str(x) for x in sogl]
    print(f"{'strategia':<14}{'aperte':>7}{'chiuse':>7}{'media':>9}{'vinte':>8}"
          f"{'da 100 euro, un decimo per volta':>35}")
    print("-" * 80)
    for nome in nomi:
        suoi = [p for p in pos.values() if p.get("strategia") == nome]
        c0 = [p for p in suoi if p["stato"] == "chiusa"]
        c0.sort(key=lambda p: p["aperta_il"])
        v0 = [(p.get("esito") or {}).get("rendimento") for p in c0]
        v0 = [x for x in v0 if x is not None]
        cap = 100.0
        for x in v0:
            cap = cap * 0.9 + cap * 0.1 * (1 + x)
        med = f"{statistics.mean(v0)*100:+.0f}%" if v0 else "-"
        vin = f"{sum(1 for x in v0 if x > 0)}/{len(v0)}" if v0 else "-"
        soldi = f"{cap:.2f} euro" if v0 else "-"
        print(f"{nome:<14}{len(suoi)-len(c0):>7}{len(c0):>7}{med:>9}{vin:>8}{soldi:>35}")
    print("-" * 80)
    print("il conto da 100 euro mette in gioco un decimo del capitale per operazione: e' il\n"
          "dimensionamento che sopravvive alle code grasse (reinvestire tutto no).\n")
    for s0 in sogl:
        suoi = [p for p in pos.values() if p.get("soglia") == s0]
        c0 = [p for p in suoi if p["stato"] == "chiusa"]
        v0 = [(p.get("esito") or {}).get("rendimento") for p in c0]
        v0 = [x for x in v0 if x is not None]
        riga = f"soglia {s0}: aperte {len(suoi)-len(c0)}, chiuse {len(c0)}"
        if len(v0) >= SERVONO:
            sd = statistics.stdev(v0) if len(v0) > 1 else 0
            riga += (f", media {statistics.mean(v0)*100:+.1f}% "
                     f"± {1.96*sd/len(v0)**0.5*100:.1f}")
        elif v0:
            riga += f", il totale non si legge prima di {SERVONO}"
        print("   " + riga)
    ch = [x for x in righe if x[1] == "chiusa"]
    ap = [x for x in righe if x[1] == "aperta"]
    print(f"\nchiuse {len(ch)} su {SERVONO} che servono  |  aperte {len(ap)}  |  "
          f"curve native seguite {len(cur):,}")
    if len(ch) >= SERVONO:
        v = [x[3] for x in ch if x[3] is not None]
        sd = statistics.stdev(v) if len(v) > 1 else 0
        print(f"media {statistics.mean(v)*100:+.1f}% ± {1.96*sd/len(v)**0.5*100:.1f} punti (95%)")
    elif ch:
        print(f"IL TOTALE NON SI LEGGE: mancano {SERVONO-len(ch)} chiusure.")

    # LA DOMANDA SULLA SOGLIA, dal cammino di tutte le curve
    print(f"\nquante curve toccano ogni soglia, e quante poi si diplomano:")
    print(f"{'soglia':>8}{'curve':>8}{'diplomate':>11}{'quota':>8}")
    for s0 in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.6, 4.0):
        q = d = 0
        for c in cur.values():
            top = max((x[1] for x in (c.get("cammino") or [])),
                      default=c.get("cumulato") or 0.0)
            if top >= s0:
                q += 1
                d += 1 if c.get("diplomata") else 0
        if q:
            print(f"{s0:>8.1f}{q:>8}{d:>11}{(100*d/q):>7.0f}%")
    print("\nla quota di diplomi per soglia e' la risposta a «dove conviene entrare»: una soglia\n"
          "bassa entra presto e sbaglia spesso, una alta entra tardi e guadagna poco. Il punto\n"
          "migliore si legge qui, non si indovina.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
