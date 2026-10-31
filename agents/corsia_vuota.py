"""Un lavoro senza passi rende il file illeggibile a GitHub, e la corsia fallisce a ogni suonata.

PERCHE' ESISTE (2/10). Propagando la rimozione del riarmo che dorme a undici corsie, in
`riserve` il riarmo era un LAVORO separato e non un passo: lo script ha tolto il passo e ha
lasciato `steps:` vuoto. GitHub non riesce a leggere il file, quindi la corsia non gira e
FALLISCE ogni volta — tredici fallimenti in un'ora, cioe' tredici email a Nicolo', che mi aveva
chiesto proprio di farle sparire.

E il mio controllo strutturale, scritto un'ora prima, era passato: verificava che `steps:`
CI FOSSE, non che fosse PIENO. Guardare la presenza invece del contenuto e' lo stesso errore di
tutta la notte — l'eta' dal lancio invece che dall'esito, la soglia sulle righe invece che sui
confronti, il verdetto del giro invece dei lavori dentro.

IN POSITIVO: qui si guarda che ogni `steps:` abbia almeno un passo, e la bocciatura ferma la
pubblicazione. Il riconoscimento, stavolta: tredici minuti dal primo fallimento.
"""
import glob
import os
import sys


def vuoti(testo):
    """Le righe dove un `steps:` non ha nemmeno un passo sotto di se'."""
    r = testo.splitlines()
    out = []
    for k, l in enumerate(r):
        if l.strip() != "steps:":
            continue
        rientro = len(l) - len(l.lstrip())
        pieno = False
        for m in range(k + 1, len(r)):
            x = r[m]
            if not x.strip() or x.lstrip().startswith("#"):
                continue
            if (len(x) - len(x.lstrip())) <= rientro:
                break
            if x.lstrip().startswith("-"):
                pieno = True
            break
        if not pieno:
            out.append(k + 1)
    return out


def orfani(testo):
    """`needs:` che puntano a un lavoro che non esiste piu'."""
    import re
    return [m.group(1).strip() for m in re.finditer(r"needs: *([a-z_]+)", testo)
            if f"  {m.group(1).strip()}:" not in testo]


if __name__ == "__main__":
    guai = []
    for f in sorted(glob.glob(".github/workflows/*.yml")):
        t = open(f, encoding="utf-8").read()
        n = os.path.basename(f)[:-4]
        for riga in vuoti(t):
            guai.append(f"{n}: un lavoro senza nessun passo (riga {riga}) — GitHub non legge "
                        f"il file e la corsia fallisce a ogni suonata")
        for o in orfani(t):
            guai.append(f"{n}: «needs: {o}» punta a un lavoro che non c'e' piu'")
    for g in guai:
        print(f"   CORSIA ILLEGGIBILE  {g}", flush=True)
    if guai:
        print(f"CORSIA VUOTA | {len(guai)} corsie non sono leggibili: non si pubblica.",
              flush=True)
        sys.exit(1)
    print(f"CORSIA VUOTA | tutte le corsie hanno almeno un passo per lavoro e nessun needs "
          f"orfano", flush=True)
