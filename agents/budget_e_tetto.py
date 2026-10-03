"""Il budget di una corsia deve lasciare spazio alla consegna.

PERCHE' ESISTE (1/10). Tre corsie dichiaravano un budget di tempo quasi uguale al tempo
concesso: `vivo` 55 minuti su 70, `scoperta` 20 su 30, `iniziatori` 25 su 35. Il lavoro si
fermava in tempo, ma DOPO il lavoro restano il salvataggio e la consegna — e il giro veniva
annullato per tempo scaduto con tutto dentro. Misurato: vivo 77 minuti su 70 concessi, zero
giri riusciti su dieci.

L'errore non era il budget sbagliato: era aver pensato che fermare il LAVORO al limite fosse
fermarsi in tempo. In mezzo c'e' il mettere al sicuro, che e' la parte che non si puo' saltare.

LA REGOLA: budget <= 60% del tempo concesso. Il 40% resta per consegnare.
Meglio raccogliere meno e consegnarlo, che raccogliere tutto e buttarlo.
"""
import glob
import os
import re
import sys

QUOTA = 0.60


def guarda(cartella=".github/workflows"):
    guai = []
    visti = 0
    for f in sorted(glob.glob(os.path.join(cartella, "*.yml"))):
        t = open(f, encoding="utf-8").read()
        b = re.search(r'BUDGET_SEC: *"?(\d+)', t)
        m = re.search(r"timeout-minutes: *(\d+)", t)
        if not b or not m:
            continue
        visti += 1
        budget = int(b.group(1)) / 60.0
        tetto = int(m.group(1))
        if budget > QUOTA * tetto:
            guai.append(f"{os.path.basename(f)[:-4]}: budget {budget:.0f} min su un tetto di "
                        f"{tetto} min ({100*budget/tetto:.0f}%, massimo {100*QUOTA:.0f}%) — "
                        f"restano solo {tetto - budget:.0f} min per salvare e consegnare")
    return visti, guai


if __name__ == "__main__":
    visti, guai = guarda()
    for g in guai:
        print(f"   BUDGET TROPPO VICINO AL TETTO  {g}", flush=True)
    if guai:
        print(f"BUDGET E TETTO | {len(guai)} corsie su {visti} si fermano troppo tardi per "
              f"fare in tempo a consegnare.", flush=True)
        sys.exit(1)
    print(f"BUDGET E TETTO | tutte e {visti} le corsie col budget lasciano almeno il "
          f"{100*(1-QUOTA):.0f}% del tempo per consegnare", flush=True)
