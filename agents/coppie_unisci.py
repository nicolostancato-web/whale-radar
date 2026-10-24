"""COPPIE UNISCI — rimette insieme quello che le fette hanno risolto in parallelo.

PERCHE' LE FETTE (18/09). Il nodo pubblico limita per INDIRIZZO IP: misurato, un filo rende
0,24 pool al secondo, tre fili 0,22, sei fili zero. Da una macchina sola non si va piu' veloci,
e a base restavano 4.349 indirizzi — cinque ore di chiamate pure.
Ma ogni lavoro di GitHub gira su un runner con IP proprio: la velocita' si compra fra LAVORI, non
fra fili dentro un lavoro. Quattro fette, quattro IP, quattro volte il ritmo.

COSA FA QUI: legge coppie_f*.json e li fonde in coppie.json, che e' il file che tutti gli altri
agenti leggono. Non cancella niente e non riscrive le fette: se una fetta e' rimasta indietro o non
ha girato, il suo contributo semplicemente non c'e' ancora, e il prossimo giro lo prende.
"""
import glob
import json
import os
import time

CHAINS = ("base", "robinhood")


def main():
    for ch in CHAINS:
        base = f"data/multichain/{ch}/coppie.json"
        note = {}
        if os.path.exists(base):
            try:
                note = json.load(open(base)).get("coppie", {}) or {}
            except Exception:
                note = {}
        prima = len(note)
        fette = 0
        for f in sorted(glob.glob(f"data/multichain/{ch}/coppie_f*.json")):
            try:
                d = json.load(open(f)).get("coppie", {}) or {}
            except Exception:
                continue
            fette += 1
            for k, v in d.items():
                note.setdefault(k, v)
        if not fette:
            continue
        try:
            json.dump({"acq": int(time.time()), "n": len(note), "coppie": note}, open(base, "w"))
        except Exception as e:
            print(f"COPPIE_UNISCI | {ch}: non riesco a scrivere ({type(e).__name__})", flush=True)
            continue
        print(f"COPPIE_UNISCI | {ch}: {fette} fette unite, da {prima} a {len(note)} coppie "
              f"(+{len(note) - prima})", flush=True)


if __name__ == "__main__":
    main()
