#!/usr/bin/env python3
"""LO STESSO MOTIVO SOTTO DUE NOMI CONTA META' DI QUELLO CHE E'.

Difetto mio del 7/11 sera. Ho dato un nome leggibile ai selettori dei
reverti mentre la finestra di misura era APERTA: i casi registrati prima
sono finiti sotto «0x2075cc10», quelli dopo sotto «garanzia da prendere
ZERO». Stessa causa, due righe, ognuna con meta' del peso -- e il motivo
dominante sembrava il 43% invece del 57%.

E' la famiglia «una costante, un nome» applicata alle etichette di un
contatore: rinominare una categoria mentre si conta spezza la serie.
La regola: quando si rinomina una categoria, si MIGRANO anche i conteggi
vecchi nello stesso momento -- e la lettura normalizza comunque, perche' un
file di stato puo' sempre contenere la forma vecchia.

Si lancia a mano dopo aver dato un nome nuovo a un selettore.
"""
import json, os, sys

D = "data/liquidazioni"
# selettore -> nome leggibile (deve coincidere con NOTI dentro sentinella.py)
NOMI = {
    "0x930bb771": "NON era liquidabile (HealthFactorNotBelowThreshold)",
    "0x4b6c4bfa": "caduta ma vendita insufficiente",
    "0x2075cc10": "garanzia da prendere ZERO (InvalidBurnAmount)",
}


def normalizza(motivi):
    fuori, spostati = {}, 0
    for k, v in (motivi or {}).items():
        nuovo = k
        for sel, nome in NOMI.items():
            if sel in k:
                nuovo = nome
                if nuovo != k:
                    spostati += v
                break
        fuori[nuovo] = fuori.get(nuovo, 0) + v
    return fuori, spostati


def main():
    f = f"{D}/avrebbero_funzionato.json"
    if not os.path.exists(f):
        print("   niente da unire")
        return 0
    d = json.load(open(f))
    tot = 0
    for dove in ("motivi",):
        d[dove], s = normalizza(d.get(dove))
        tot += s
    fin = d.get("finestra") or {}
    if fin:
        fin["motivi"], s = normalizza(fin.get("motivi"))
        tot += s
        d["finestra"] = fin
    t = f + ".tmp"
    json.dump(d, open(t, "w"), indent=1)
    os.replace(t, f)
    print(f"   {tot} conteggi spostati sotto il nome leggibile")
    fin = d.get("finestra") or {}
    n = fin.get("simulati", 0)
    print(f"\n   FINESTRA dopo l'unione: {n} esiti")
    for k, v in sorted((fin.get("motivi") or {}).items(),
                       key=lambda x: -x[1]):
        print(f"      {k[:52]:52s} {v:3d} ({100*v/max(n,1):.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
