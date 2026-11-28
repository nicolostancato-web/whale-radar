"""La stessa regola a molte date, col controllo contemporaneo: il periodo o la bravura?

PERCHE' (5/10). Con UNA data di selezione il divario reggeva (3,68X contro 2,02X su robinhood),
ma i mediocri erano migliorati da soli — da 1,38X a 2,02X. Quindi una parte del divario era il
PERIODO: dopo quella data il mercato e' andato meglio per tutti, e senza un controllo
contemporaneo quella parte si confonde con la bravura.

IL TEST: la stessa regola applicata a dieci date diverse. A ogni data si seleziona con le sole
posizioni chiuse prima, si misura sulle sole posizioni aperte dopo e su gettoni mai visti, e
si confronta SEMPRE con il gruppo di controllo dello STESSO periodo. Se il divario sopravvive
a dieci periodi diversi non e' il periodo.

Le date si prendono ai decili delle chiusure: dichiarato prima, dipende dal volume dei dati e
non dagli esiti. Scegliere le date che danno il risultato migliore sarebbe il modo in cui si
trova sempre qualcosa cercando.
"""
import glob
import json
import os
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from quanto_e_poco import dillo                                   # noqa: E402

MIN_COSTO = float(os.environ.get("MIN_COSTO", 10.0))
SOGLIA = float(os.environ.get("SOGLIA", 2.0))
MIN_PRIMA = int(os.environ.get("MIN_PRIMA", 3))
MIN_DOPO = int(os.environ.get("MIN_DOPO", 3))


def carica(chain, cartella="/tmp/art"):
    det = {}
    for p in glob.glob(f"{cartella}/*/multichain/{chain}/dettaglio_candidati_pezzo_*.json"):
        for k, v in json.load(open(p)).items():
            det.setdefault(k, {}).update(v)
    return det


def a_una_data(det, T):
    bravi, scarsi = [], []
    for pools in det.values():
        prima = [v for v in pools.values()
                 if v.get("stato") == "chiuso" and v.get("multiplo")
                 and v.get("speso", 0) >= MIN_COSTO and v.get("ultimo") and v["ultimo"] < T]
        visti = {pid for pid, v in pools.items() if v.get("primo") and v["primo"] < T}
        dopo = [v for pid, v in pools.items()
                if v.get("stato") == "chiuso" and v.get("multiplo")
                and v.get("speso", 0) >= MIN_COSTO and v.get("primo") and v["primo"] >= T
                and pid not in visti]
        if len(prima) < MIN_PRIMA or len(dopo) < MIN_DOPO:
            continue
        mp = float(np.median([v["multiplo"] for v in prima]))
        md = float(np.median([v["multiplo"] for v in dopo]))
        (bravi if mp >= SOGLIA else scarsi).append(md)
    return bravi, scarsi


def main():
    # E NON LEGGEVA NEMMENO LA RIGA DI COMANDO (5/10). Peggio di un parametro ignorato: il
    # parametro non esisteva, quindi passare una cartella diversa non faceva assolutamente
    # niente e senza alcun segnale. Ora si legge, e si STAMPA quale cartella e quanti pezzi
    # sono stati letti: un agente che non dichiara la sua sorgente puo' misurare i dati di
    # ieri credendo di misurare quelli di oggi, ed e' esattamente quello che ha fatto.
    cartella = sys.argv[1] if len(sys.argv) > 1 else "/tmp/art"
    for chain in ("base", "robinhood"):
        # LA DIMENSIONE FANTASMA, RIFATTA DA ME (5/10). `main` accettava la cartella da riga
        # di comando e poi chiamava `carica(chain)` senza passarla: il parametro c'era
        # nell'interfaccia e il codice lo ignorava, quindi la corsa leggeva sempre /tmp/art.
        # Risultato: dopo aver corretto due difetti nei dati e ricostruito tutto, questo test
        # ha ristampato i numeri di IERI cifra per cifra — e li avrei riportati come «regge
        # anche sui dati corretti».
        # Me ne sono accorto SOLO perche' erano identici a sei decimali: se fossero stati
        # simili ma non uguali, avrei pubblicato una conferma falsa.
        # E' la stessa famiglia del 2/10 («dodici prove indipendenti con margini identici»):
        # un'interfaccia che dichiara una dimensione che il codice non usa. Due volte la
        # stessa trappola, la seconda scavata da me.
        det = carica(chain, cartella)
        print(f"   (letti {len(det)} portafogli da {cartella})")
        chiusure = [v["ultimo"] for pools in det.values() for v in pools.values()
                    if v.get("stato") == "chiuso" and v.get("ultimo")]
        if len(chiusure) < 100:
            print(f"\n=== {chain}: troppe poche chiusure ({len(chiusure)}) ===")
            continue
        date = [int(np.quantile(chiusure, q)) for q in np.arange(0.1, 0.95, 0.1)]
        print(f"\n=== {chain}: {len(date)} date ai decili delle chiusure ===")
        print(f"   {'data':>4} {'bravi':>6} {'scarsi':>7} {'bravi DOPO':>12} "
              f"{'scarsi DOPO':>12} {'divario':>9}")
        vinte = 0
        valide = 0
        for i, T in enumerate(date, 1):
            b, s = a_una_data(det, T)
            if len(b) < 5 or len(s) < 5:
                print(f"   {i:>4} {len(b):6} {len(s):7}   troppo pochi per giudicare")
                continue
            valide += 1
            mb, ms = float(np.median(b)), float(np.median(s))
            if mb > ms:
                vinte += 1
            print(f"   {i:>4} {len(b):6} {len(s):7} {mb:11.2f}X {ms:11.2f}X "
                  f"{mb-ms:+8.2f}")
        if valide:
            print(f"\n   " + dillo(vinte, valide, "date in cui i bravi battono i mediocri"))
            print("   Se il divario fosse il periodo, i bravi non vincerebbero "
                  "sistematicamente a date diverse.")
        else:
            print("\n   nessuna data giudicabile: il materiale non basta per questo test")


if __name__ == "__main__":
    main()
