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

QUESTA GUARDIA GRIDAVA E NON LA LEGGEVO (4/10). Il 4 ottobre ho visto sei fette uccise a
meta', ho indagato, ho scoperto che sette corsie avevano un budget piu' lungo del loro
timeout — `nascite` e `storico` dichiaravano 9000 secondi dentro 600, cioe' venivano uccise
a dieci minuti a ogni singolo giro — e ho scritto una guardia nuova per rilevarlo.
Era inutile due volte: questa guardia esisteva gia', e la sua soglia (60%) era PIU' SEVERA
della mia (80%). E soprattutto: stava gridando da giorni nell'uscita del pubblicatore, e io
non l'avevo letta.

DUE REGOLE, scritte qui perche' questo e' il file che si rilegge quando il caso ritorna:
  1. prima di costruire un controllo, cercare se c'e' gia' — e se c'e', usare LA SUA soglia,
     non inventarne una piu' comoda;
  2. un allarme che nessuno legge non e' un allarme. Quando una guardia grida e il lavoro
     continua, il guasto e' nella lettura, non nella guardia.
Un controllo in piu' non aggiunge sicurezza se il problema era l'attenzione.
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
        # LA SOMMA, NON IL PRIMO (5/10). Qui si cercava UN SOLO BUDGET_SEC con `search`, che
        # restituisce il primo. La corsia «candidati» ne ha TRE passi di fila nello stesso
        # lavoro — 900 + 360 + 420 = 1.680 secondi, ventotto minuti dentro un tetto di
        # venticinque — e la guardia diceva «va bene» guardando solo i 900.
        # Il tempo si somma dentro un lavoro: tre passi da dieci minuti non sono un passo da
        # dieci minuti. La guardia controllava una cosa vera e insufficiente, che e' il modo
        # piu' silenzioso di sbagliare — e la corsia e' morta «cancelled», la parola che mi
        # ha ingannato cinque volte.
        tutti = [int(x) for x in re.findall(r'BUDGET_SEC: *"?(\d+)', t)]
        m = re.search(r"timeout-minutes: *(\d+)", t)
        if not tutti or not m:
            continue
        visti += 1
        budget = sum(tutti) / 60.0
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
