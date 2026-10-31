"""PANINO — quante volte, entrando, saremmo stati aggrediti.

Quarto pezzo del loop 1. Idea trovata il 22/09 nel loop di ricerca su GitHub, ed e' un punto cieco
che non avevamo: stavamo simulando entrate su questi mercati SENZA considerare che qualcuno ci si
infila davanti.

COS'E'. Un operatore vede arrivare il tuo ordine, compra un istante PRIMA di te facendo salire il
prezzo, ti lascia comprare piu' caro, e rivende subito DOPO incassando la differenza. Tu sei il
ripieno. Il costo non e' una commissione: e' un prezzo di entrata peggiore, e non compare da
nessuna parte se non lo si cerca apposta.

COME SI RICONOSCE, e ci servono solo dati che abbiamo gia':
  - lo STESSO indirizzo compare due volte nello stesso pool e nello stesso blocco;
  - la prima volta compra, la seconda vende (versi opposti);
  - IN MEZZO, fra le due, c'e' almeno un altro indirizzo che ha scambiato.
Quello in mezzo e' la vittima. Se fossimo entrati in quel momento, la vittima saremmo noi.

PERCHE' CONTA PIU' DI QUANTO SEMBRI. Il nostro modello di costo, anche adesso che l'impatto e'
misurato sui dati veri, guarda quanto si muove il prezzo IN MEDIA. Ma un'aggressione non e' un
movimento medio: e' mirata, arriva proprio quando entri, e colpisce proprio gli ordini che
valgono la pena di essere colpiti — cioe' i piu' grandi, che sono quelli che faremmo noi se il
segnale fosse buono.

IL LIMITE, DICHIARATO. Misuriamo le aggressioni AVVENUTE agli altri, non quelle che avremmo subito
noi. E' una stima per analogia: se in un pool il 30% degli scambi finisce in mezzo a un panino, e'
ragionevole aspettarsi di finirci anche noi. Non e' una previsione, e' un ordine di grandezza — e
va scritto cosi'.
"""
import gzip
import json
import os
import sys
from collections import defaultdict

CHAIN = os.environ.get("CHAIN", "base")
FUORI = f"data/loop1/panino_{CHAIN}.json"


def verso(r):
    try:
        a0 = float(r.get("a0") or 0)
    except Exception:
        return None
    return None if a0 == 0 else (1 if a0 > 0 else -1)


def panini_nel_blocco(righe):
    """Trova i panini fra gli scambi di UN pool in UN blocco.

    Torna (quanti panini, quante vittime). Gli scambi sono gia' ordinati per posizione: l'ordine
    dentro il blocco e' cio' che rende possibile l'aggressione, e infatti e' la cosa che chi
    aggredisce paga per controllare."""
    per_w = defaultdict(list)
    for i, r in enumerate(righe):
        w = (r.get("w") or "").lower()
        if w:
            per_w[w].append(i)
    panini = 0
    vittime = set()
    for w, pos in per_w.items():
        if len(pos) < 2:
            continue
        for a, b in zip(pos, pos[1:]):
            if b - a < 2:
                continue                      # serve qualcuno IN MEZZO
            va, vb = verso(righe[a]), verso(righe[b])
            if not va or not vb or va == vb:
                continue                      # deve comprare e poi vendere, non due volte uguale
            in_mezzo = [k for k in range(a + 1, b)
                        if (righe[k].get("w") or "").lower() != w]
            if not in_mezzo:
                continue
            panini += 1
            vittime.update(in_mezzo)
    return panini, len(vittime)


def main():
    cartelle = [f"data/multichain/{CHAIN}/{c}" for c in ("storico", "vivo")]
    per_pool = defaultdict(list)
    for c in cartelle:
        if not os.path.isdir(c):
            continue
        for fn in os.listdir(c):
            try:
                righe = [json.loads(l) for l in gzip.open(os.path.join(c, fn), "rt") if l.strip()]
            except Exception:
                continue
            per_pool[fn.split(".")[0]].extend(righe)

    tot_scambi = tot_panini = tot_vittime = 0
    esiti = {}
    for pool, righe in per_pool.items():
        per_blocco = defaultdict(list)
        for r in righe:
            if r.get("blocco"):
                per_blocco[r["blocco"]].append(r)
        p = v = n = 0
        for b, rr in per_blocco.items():
            if len(rr) < 3:
                continue                      # sotto tre scambi un panino non ci sta
            rr.sort(key=lambda x: (x.get("ti", 0), x.get("li", 0)))
            pp, vv = panini_nel_blocco(rr)
            p += pp
            v += vv
            n += len(rr)
        if n:
            esiti[pool] = {"scambi_in_blocchi_affollati": n, "panini": p, "vittime": v}
            tot_scambi += n
            tot_panini += p
            tot_vittime += v

    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    json.dump(esiti, open(FUORI, "w"))
    colpiti = sum(1 for e in esiti.values() if e["panini"])
    print(f"PANINO | {CHAIN}: {len(esiti)} pool con blocchi affollati")
    print(f"   pool in cui e' successo almeno una volta: {colpiti} = "
          f"{100*colpiti/max(1,len(esiti)):.1f}%")
    print(f"   aggressioni trovate: {tot_panini}")
    print(f"   scambi finiti in mezzo (vittime): {tot_vittime} su {tot_scambi} "
          f"= {100*tot_vittime/max(1,tot_scambi):.2f}%")
    print()
    if tot_vittime:
        print(f"   Se fossimo entrati in uno di quei momenti, la vittima saremmo stati noi.")
        print(f"   Questo costo NON e' nel modello: l'impatto misurato guarda il movimento medio,")
        print(f"   un'aggressione e' mirata e arriva proprio quando entri.")
    else:
        print(f"   Nessuna aggressione trovata: o non avviene su questa chain, o la nostra")
        print(f"   raccolta non vede abbastanza scambi dello stesso blocco per accorgersene.")
    print(f"   scritto {FUORI}")
    if not esiti:
        sys.exit(1)


if __name__ == "__main__":
    main()
