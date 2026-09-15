#!/usr/bin/env python3
"""
ELENCO_RIGHE — dice al collettore ESATTAMENTE quali pool servono.

PERCHE' (15/09). Lo scavo della storia filtrava sui pool con una serie di prezzo: 4.671 su Base. Ma
solo 1.711 di quelli diventano una riga analizzabile — gli altri non hanno abbastanza candele, o
sono stati presi troppo tardi per avere un'entrata. Risultato: l'8% dello scavo finiva su pool che
non potranno mai rispondere a una domanda.

Il cervello sa gia' quali pool diventano righe: lo calcola ogni volta. Qui lo calcoliamo UNA volta e
lo scriviamo, cosi' il collettore scava solo dove serve. Non e' un'ottimizzazione di eleganza: a
parita' di chiamate al nodo, tre volte piu' dati utili.

Scrive data/multichain/<chain>/righe.json. Sola lettura, €0.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multichain_brain as B

CHAINS = ("base", "robinhood", "solana")


def main():
    for ch in CHAINS:
        try:
            righe = B.load_rows(ch)
        except Exception as e:
            print(f"ELENCO_RIGHE | {ch}: {type(e).__name__}", flush=True); continue
        if not righe: continue
        # oltre all'indirizzo si salva l'ISTANTE D'ENTRATA: al collettore serve per sapere QUALE
        # finestra di blocchi vale la pena leggere, invece di tenere tutto e buttare dopo.
        d = {r["pool"].lower(): {"ent": r["ent"], "t0": r.get("t0")} for r in righe if r.get("pool")}
        p = f"data/multichain/{ch}/righe.json"
        try:
            json.dump({"ts": int(time.time()), "n": len(d), "pool": d}, open(p, "w"))
            print(f"ELENCO_RIGHE | {ch}: {len(d)} pool che diventano righe", flush=True)
        except Exception as e:
            print(f"ELENCO_RIGHE | {ch}: non riesco a scrivere ({type(e).__name__})", flush=True)


if __name__ == "__main__":
    main()
