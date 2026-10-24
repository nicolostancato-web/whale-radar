"""La tabella delle promozioni: ogni posizione della prova in avanti, con il suo cammino.

COMANDO PERMANENTE DI NICOLO': «ti chiederò sempre il recap delle promozioni». Una riga per
moneta, con rendimento, durata, minimo e massimo toccati. Il minimo e il massimo vengono dal
database del cammino (cammino_posizioni.json), non dalla prova: la prova sa come e' finita,
il cammino sa cosa e' successo in mezzo.

IL TOTALE NON SI LEGGE PRIMA DI 50 CHIUSURE, e prima che le perdenti abbiano avuto la stessa
occasione delle vincenti: l'orizzonte e' 16,7 ore, quindi una posizione aperta stamattina non
ha ancora avuto il tempo che hanno avuto le chiuse. Fino a quel momento la media e' un numero
che lusinga, e la lezione del 24/09 e' che il campione che lusinga e' il piu' convincente.
"""
import json
import os
import statistics
import sys
import time

PROVA = "data/multichain/robinhood/prova_in_avanti.json"
CAMMINO = "data/multichain/robinhood/cammino_posizioni.json"
SERVONO = 50
ORIZZONTE_MINUTI = 600_000 / 10 / 60   # 600.000 blocchi a ~10 al secondo = 1.002 minuti


def main():
    d = json.load(open(PROVA))
    cam = json.load(open(CAMMINO)).get("monete", {})
    pos = d["posizioni"]
    ora = int(time.time())

    righe = []
    for tok, p in pos.items():
        if p["stato"] == "scartata":
            continue
        c = cam.get(tok, {})
        es = p.get("esito") or {}
        r = es.get("rendimento")
        ultimo = p.get("ultimo_prezzo")
        if r is None and ultimo and p.get("entrata"):
            r = ultimo / p["entrata"] - 1          # aperta: dove sta ADESSO
        righe.append({
            "tok": tok,
            "stato": p["stato"],
            "verso": es.get("verso", ""),
            "resa": r,
            "ore": (ora - p["aperta_il"]) / 3600,
            "min_x": c.get("min_x"), "max_x": c.get("max_x"),
            "max_min": c.get("max_dopo_minuti"),
            "scambi": c.get("scambi_dopo_entrata"),
        })
    righe.sort(key=lambda x: (x["stato"] != "aperta", -(x["resa"] or -9)))

    print(f"RECAP PROMOZIONE — {len(righe)} posizioni  "
          f"(blocco {d.get('ultimo_blocco', 0):,})\n")
    print(f"{'moneta':<16}{'stato':<10}{'come':<11}{'resa':>8}{'min':>7}{'max':>7}"
          f"{'max dopo':>10}{'ore':>7}{'scambi':>8}")
    print("-" * 84)
    for x in righe:
        # IL MASSIMO PUO' CADERE FUORI DALLA NOSTRA FINESTRA (10/10). Il cammino segue tutta
        # la vita della moneta; la prova esce all'orizzonte (600.000 blocchi = 16,7 ore = 1.002
        # minuti). Un max a 1.258 minuti accanto a una resa di -70% sembra un errore e non lo e':
        # quel massimo e' arrivato quando eravamo gia' fuori. Va marcato, o la tabella inganna.
        fuori = x["max_min"] is not None and x["max_min"] > ORIZZONTE_MINUTI
        mm = (f"{x['max_min']:.0f}m" + ("*" if fuori else "")) if x["max_min"] is not None else "-"
        resa = f"{x['resa']*100:+.0f}%" if x["resa"] is not None else "-"
        mn = f"{x['min_x']:.2f}" if x["min_x"] else "-"
        mx = f"{x['max_x']:.2f}" if x["max_x"] else "-"
        sc = x["scambi"] if x["scambi"] is not None else "-"
        print(f"{x['tok'][:14]:<16}{x['stato']:<10}{x['verso'][:10]:<11}{resa:>8}"
              f"{mn:>7}{mx:>7}{mm:>10}{x['ore']:>7.1f}{sc:>8}")

    oltre = [x for x in righe if x["max_min"] is not None and x["max_min"] > ORIZZONTE_MINUTI]
    if oltre:
        print(f"\n* il massimo e' arrivato OLTRE il nostro orizzonte di {ORIZZONTE_MINUTI:.0f} "
              f"minuti (16,7 ore): {len(oltre)} monete. Eravamo gia' uscite.")
    ch = [x for x in righe if x["stato"] == "chiusa"]
    vinte = [x for x in ch if (x["resa"] or 0) > 0]
    print("-" * 84)
    print(f"\nchiuse {len(ch)} su {SERVONO} che servono  |  vinte {len(vinte)}, "
          f"perse {len(ch)-len(vinte)}  |  aperte {len(righe)-len(ch)}")
    if len(ch) < SERVONO:
        print(f"IL TOTALE NON SI LEGGE: mancano {SERVONO-len(ch)} chiusure. Con {len(ch)} "
              f"posizioni l'intervallo e' cosi' largo che qualunque media contiene lo zero.")
    else:
        r = [x["resa"] for x in ch if x["resa"] is not None]
        sd = statistics.stdev(r) if len(r) > 1 else 0
        ic = 1.96 * sd / len(r) ** 0.5
        print(f"media {statistics.mean(r)*100:+.1f}% ± {ic*100:.1f} punti (95%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
