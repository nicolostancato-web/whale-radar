"""SILENZIO REVISIONE — da quanti giorni nessuno ci guarda da fuori.

PERCHE' ESISTE (21/09). Il 17 settembre ho scoperto che la revisione esterna era ferma da SEI
GIORNI e nessuno se n'era accorto, perche' «era prevista». Una cosa prevista che non accade non fa
rumore: e' esattamente questo che la rende pericolosa. In quei sei giorni avevo trovato venti
difetti da solo — e non so quanti ne ho lasciati, perche' nessuno guardava con occhi diversi.

Il rimedio non puo' essere che me lo ricordi io. Me lo sono gia' dimenticato una volta, e una
promessa fatta in chat non sopravvive a un cambio di sessione. Quindi il silenzio si MISURA, e il
numero compare accanto a quelli del database ogni volta che si fa il punto.

IL PRIMO GIRO LO DEVE FARE IL FONDATORE, e non e' una limitazione aggirabile: Codex e' autenticato
col suo abbonamento. Io posso preparare il materiale, non posso premere invio al posto suo. Per
questo il numero deve essere visibile a LUI, non solo a me.

SI PARTE DALL'11 SETTEMBRE perche' e' l'ultima consulenza vera di cui abbiamo traccia.
Quando ne fate una nuova: `python3 agents/silenzio_revisione.py --fatta`
"""
import json
import os
import sys
import time

REG = "data/consulenze/ultima.json"
PRIMA_NOTA = "2026-09-11"          # ultima consulenza di cui abbiamo traccia certa


def leggi():
    try:
        return json.load(open(REG))
    except Exception:
        return {"ultima": PRIMA_NOTA, "quante": 0}


def giorni(d):
    try:
        t = time.mktime(time.strptime(d["ultima"], "%Y-%m-%d"))
    except Exception:
        return None
    return int((time.time() - t) / 86400)


def main():
    d = leggi()
    if "--fatta" in sys.argv:
        d = {"ultima": time.strftime("%Y-%m-%d"), "quante": d.get("quante", 0) + 1}
        os.makedirs(os.path.dirname(REG), exist_ok=True)
        json.dump(d, open(REG, "w"))
        print(f"REVISIONE | segnata la consulenza di oggi ({d['ultima']}), "
              f"{d['quante']} in tutto.", flush=True)
        return

    g = giorni(d)
    if g is None:
        print("REVISIONE | data illeggibile: NON so da quanto non ci guarda nessuno da fuori, "
              "che e' peggio che saperlo alto.", flush=True)
        return

    # LA SOGLIA E' BASSA DI PROPOSITO. Il ritmo concordato e' due al giorno: gia' a due giorni di
    # silenzio siamo a un quarto del previsto, e a sei giorni ci siamo passati senza accorgercene.
    if g >= 2:
        print(f"REVISIONE | SILENZIO DA {g} GIORNI. Il ritmo concordato e' due consulenze al "
              f"giorno; l'ultima e' del {d['ultima']}.", flush=True)
        print("REVISIONE | apri Codex (gratis, dentro l'abbonamento), collegalo al repo e incolla "
              "BRIEF_CODEX_REVISORE.md", flush=True)
    else:
        print(f"REVISIONE | ultima consulenza {d['ultima']} ({g} giorni fa), "
              f"{d.get('quante', 0)} in tutto.", flush=True)


if __name__ == "__main__":
    main()
