"""Il verdetto di H7 — sigillato, e incapace di essere sbirciato.

H7 CHIEDE UNA COSA SOLA: la capienza del pool, misurata PRIMA di comprare, predice l'esito?
Le condizioni di morte sono state scritte in `IPOTESI_H7.md` la sera del 26/09, prima di vedere un
solo numero. Qui diventano CODICE, e il motivo e' che in prosa non vincolano nessuno.

LE DUE TRAPPOLE CHE QUESTO FILE RENDE IMPOSSIBILI.

 1. **Sbirciare presto.** Con 150 casi si trova sempre un taglio che sembra buono: e' cosi' che sono
    morte H6 e H6b, sembravano vive su pochi dati. Il minimo di 600 pool e' stato dichiarato prima,
    e qui lo script **esce senza stampare i terzi** finche' non ci siamo. Non si puo' dare
    un'occhiata «tanto per vedere»: non c'e' proprio niente da vedere.

 2. **Vendere la sopravvivenza come guadagno.** Il caso piu' probabile e' che i pool capienti
    muoiano di meno ma rendano uguale. Sarebbe utile — togliere le perdite totali vale molto — ma
    NON sarebbe un vantaggio. Quindi il verdetto porta sempre un campo che lo dice a voce alta.
"""
import gzip
import json
import os
import statistics as st
import sys

# --- le tre condizioni, copiate da IPOTESI_H7.md e non piu' toccabili ---
MINIMO_POOL = 600            # sotto questo non si guarda: dichiarato il 26/09
CALO_SENZA_USCITA = 8.0      # punti in meno di «senza alcuna uscita» fra terzo alto e terzo basso
MEDIA_TAGLIATA_MINIMA = -2.0 # la media tolto l'1% piu' alto deve stare sopra questo
CHAIN = os.environ.get("CHAIN", "robinhood")
ORIZZONTE_ORE = 24


def esito(x):
    return -0.98 if x.get("_uscita_min1") is None else x["_uscita_min1"]


def carica():
    p = f"data/loop1/insieme_{CHAIN}.jsonl.gz"
    if not os.path.exists(p):
        return []
    r = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
    if not r:
        return []
    fine = max(x["_t"] + x.get("_ore_osservate", 0) * 3600 for x in r)
    return [x for x in r
            if fine - x["_t"] >= ORIZZONTE_ORE * 3600
            and x.get("_liq_copertura", 0) > 0.9
            and x.get("_liq_prima")]


def main():
    g = carica()
    if len(g) < MINIMO_POOL:
        print(f"H7 | {len(g)} pool su {MINIMO_POOL}: NON SI GUARDA ANCORA.", flush=True)
        print("     (la soglia e' stata fissata il 26/09 prima di vedere i dati: sbirciare adesso "
              "renderebbe il risultato inutilizzabile)", flush=True)
        return 0

    g.sort(key=lambda x: x["_liq_prima"])
    n = len(g) // 3
    terzi = [("bassa", g[:n]), ("media", g[n:2*n]), ("alta", g[2*n:])]
    misure = {}
    print(f"H7 | {len(g)} pool giudicabili con capienza nota, divisi in terzi\n")
    print(f"   {'capienza':10} {'pool':>6} {'senza uscita':>13} {'media':>8} {'senza 1% alto':>14}")
    for nome, s in terzi:
        v = sorted(esito(x) for x in s)
        senza = 100 * sum(1 for x in s if x.get("_uscita_min1") is None) / len(s)
        tagliata = 100 * st.mean(v[:int(len(v) * 0.99)])
        misure[nome] = {"senza_uscita": senza, "media": 100 * st.mean(v), "tagliata": tagliata}
        print(f"   {nome:10} {len(s):6} {senza:12.1f}% {100*st.mean(v):+7.1f}% {tagliata:+13.1f}%")

    c1 = misure["bassa"]["senza_uscita"] - misure["alta"]["senza_uscita"] >= CALO_SENZA_USCITA
    c2 = misure["alta"]["tagliata"] > MEDIA_TAGLIATA_MINIMA
    c3 = (misure["bassa"]["senza_uscita"] >= misure["media"]["senza_uscita"] >= misure["alta"]["senza_uscita"]
          and misure["bassa"]["tagliata"] <= misure["media"]["tagliata"] <= misure["alta"]["tagliata"])
    viva = c1 and c2 and c3

    # LA TRAPPOLA DICHIARATA PRIMA, MISURATA SEMPRE: sopravvive di piu' ma non rende di piu'?
    sopravvivenza_senza_guadagno = c1 and not c2

    print(f"\n   1. cala di almeno {CALO_SENZA_USCITA} punti chi non esce: "
          f"{'SI' if c1 else 'NO'} ({misure['bassa']['senza_uscita']-misure['alta']['senza_uscita']:+.1f})")
    print(f"   2. media tagliata sopra {MEDIA_TAGLIATA_MINIMA}%: "
          f"{'SI' if c2 else 'NO'} ({misure['alta']['tagliata']:+.1f}%)")
    print(f"   3. monotona su tutti e tre i terzi: {'SI' if c3 else 'NO'}")
    print(f"\n   H7 {'VIVA' if viva else 'MORTA'}")
    if sopravvivenza_senza_guadagno:
        print("   ATTENZIONE: sopravvivenza SENZA guadagno — i pool capienti muoiono di meno e")
        print("   rendono uguale. E' utile, NON e' un vantaggio, e non va raccontato come tale.")

    fuori = {"chain": CHAIN, "pool": len(g), "viva": viva, "condizioni": [c1, c2, c3],
             "sopravvivenza_senza_guadagno": sopravvivenza_senza_guadagno, "terzi": misure}
    os.makedirs("data/loop1", exist_ok=True)
    json.dump(fuori, open(f"data/loop1/verdetto_h7_{CHAIN}.json", "w"), indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
