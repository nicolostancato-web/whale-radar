"""Rifiuta le chiavi doppie nelle corsie, come fa GitHub.

IL CONTROLLO CHE ACCETTAVA IL ROTTO (29/09). Il 29/09 ho messo due volte `if:` nello stesso
passo. Il mio controllo usava `yaml.safe_load`, che davanti a due chiavi uguali tiene l'ULTIMA
e non dice niente: ha risposto «ok». GitHub invece rifiuta il FILE INTERO con un 422, e per
mezz'ora nessuna variante e' potuta partire.

Scritto senza il lettore yaml apposta: il python di sistema non ce l'ha, e una porta che non
puo' girare ovunque e' una porta che prima o poi si salta.
"""
import glob
import sys


def doppie(percorso):
    """Torna [(riga, chiave, indentazione)] delle chiavi ripetute nello stesso blocco."""
    righe = open(percorso, encoding="utf-8").read().splitlines()
    fuori, viste, fine_blocco = [], {}, None
    for n, riga in enumerate(righe, 1):
        if not riga.strip() or riga.lstrip().startswith("#"):
            continue
        ind = len(riga) - len(riga.lstrip())
        # dentro un blocco di testo (`run: |`) non ci sono chiavi: e' contenuto e va saltato
        if fine_blocco is not None:
            if ind > fine_blocco:
                continue
            fine_blocco = None
        corpo = riga.lstrip()
        if corpo.startswith("- "):
            # un elemento di elenco apre un blocco nuovo: le chiavi di prima non contano piu'
            for k in [k for k in viste if k[0] > ind]:
                viste.pop(k, None)
            corpo, ind = corpo[2:], ind + 2
        if ":" not in corpo:
            continue
        chiave = corpo.split(":", 1)[0].strip()
        if not chiave or " " in chiave.strip("'\"") and not chiave.startswith(("'", '"')):
            continue
        valore = corpo.split(":", 1)[1].strip()
        # si esce dai blocchi piu' interni: le loro chiavi non sono piu' vive
        for k in [k for k in viste if k[0] > ind]:
            viste.pop(k, None)
        if (ind, chiave) in viste:
            fuori.append((n, chiave, viste[(ind, chiave)]))
        viste[(ind, chiave)] = n
        if valore in ("|", ">", "|-", ">-", "|+", ">+"):
            fine_blocco = ind
    # SENZA QUESTA RIGA IL CONTROLLO NON PUO' FALLIRE (29/09): l'avevo scordata, e `or []` piu'
    # sotto nascondeva il None. Un controllo che non puo' dire di no non e' un controllo.
    return fuori


def principale():
    rotti = 0
    for f in sorted(glob.glob(".github/workflows/*.yml")):
        for n, chiave, prima in doppie(f):
            print(f"   {f}:{n}  CHIAVE DOPPIA «{chiave}» (gia' alla riga {prima}) — "
                  f"GitHub rifiuterebbe il file intero", flush=True)
            rotti += 1
    if rotti:
        sys.exit(1)
    print("   nessuna chiave doppia nelle corsie", flush=True)


if __name__ == "__main__":
    principale()
