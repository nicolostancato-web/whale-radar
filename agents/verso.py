"""Da che parte sta il memecoin: token0 o token1. Senza questo, ogni prezzo e ogni vendita e' un
tiro di moneta.

IL DIFETTO CHE HA FATTO NASCERE QUESTO FILE (25/09, segnalato da Grok e verificato sui dati).
Negli eventi di scambio `a0` e `a1` sono le quantita' dei due token, col segno visto dal pool
(positivo = entra nel pool). Quale dei due sia il memecoin dipende dall'ORDINE DEGLI INDIRIZZI:
token0 e' semplicemente quello con l'indirizzo piu' piccolo. E' una proprieta' alfabetica, non
economica, e cambia da pool a pool.

`insieme.py` la ignorava. Usava `a0 > 0` per dire «vendita» e `a0/a1` per dire «prezzo».
Misurato sui 61.610 pool delle due chain:

    valuta = token0 (memecoin e' token1):  73,3% robinhood · 64,5% base
    valuta = token1 (memecoin e' token0):  12,5% robinhood · 24,9% base

Cosa vuol dire, esattamente:
  · dove la valuta e' token0 (la MAGGIORANZA), `a0 > 0` vuol dire «e' entrata VALUTA nel pool»,
    cioe' qualcuno ha COMPRATO. Contavamo i compratori come venditori.
  · dove la valuta e' token1, `a0/a1` e' memecoin-per-valuta, cioe' l'INVERSO del prezzo.
Nessuna delle due formule era giusta ovunque, e sbagliavano su sottoinsiemi diversi.

E' particolarmente amaro perche' il 24/09 avevamo corretto proprio questo: «il prezzo mediano di
tutti gli scambi e' quanto gli ALTRI pagano per entrare, non quanto io incasso per uscire».
Avevamo cambiato la regola e lasciato il segno sbagliato: nel 73% dei pool finivamo a misurare
esattamente la cosa che volevamo evitare.

IN POSITIVO: **prima di dare un segno a una quantita', stabilisci a quale token appartiene.**
Qui si stabilisce una volta per chain, e i due lettori (`insieme.py`, `cercatore.py`) lo chiedono.

COME SI RICONOSCE LA VALUTA senza una lista da mantenere: un token che compare in decine di pool
diversi e' una valuta (WETH, USDC, il nativo, gli hub della chain); un memecoin compare nel suo
pool e basta. Soglia a 50 pool. Dove non si capisce — due valute, o nessuna — si restituisce None e
il pool si dichiara non usabile invece di tirare a indovinare.
"""
import json
import os
from collections import Counter

SOGLIA_HUB = int(os.environ.get("SOGLIA_HUB", 50))


def carica(chain):
    """pool -> True se il MEMECOIN e' token0, False se e' token1, None se non si capisce."""
    p = f"data/multichain/{chain}/coppie.json"
    if not os.path.exists(p):
        return {}
    coppie = json.load(open(p)).get("coppie", {})
    freq = Counter()
    for v in coppie.values():
        for k in ("t0", "t1"):
            a = (v.get(k) or "").lower()
            if a:
                freq[a] += 1
    hub = {a for a, n in freq.items() if n >= SOGLIA_HUB}
    fuori = {}
    for pool, v in coppie.items():
        t0, t1 = (v.get("t0") or "").lower(), (v.get("t1") or "").lower()
        h0, h1 = t0 in hub, t1 in hub
        if h0 and not h1:
            fuori[pool.lower()] = False      # valuta t0 -> memecoin e' token1
        elif h1 and not h0:
            fuori[pool.lower()] = True       # valuta t1 -> memecoin e' token0
        else:
            fuori[pool.lower()] = None       # due valute o nessuna: non si tira a indovinare
    return fuori


def prezzo(x, meme_t0):
    """VALUTA PER MEMECOIN: quanto incasso per ogni gettone. Non l'inverso."""
    try:
        a0 = abs(float(x["a0"]))
        a1 = abs(float(x["a1"]))
    except Exception:
        return None
    if a0 <= 0 or a1 <= 0:
        return None
    return a1 / a0 if meme_t0 else a0 / a1


def e_vendita(x, meme_t0):
    """Vendita = il MEMECOIN entra nel pool (positivo dal punto di vista del pool)."""
    try:
        return float(x["a0" if meme_t0 else "a1"]) > 0
    except Exception:
        return False


def valuta(x, meme_t0):
    """Quanta VALUTA e' passata in questo scambio, in unita' grezze.

    Serve a mettere una taglia accanto a un prezzo. Un prezzo a 10x che ha scambiato polvere non e'
    un'uscita: e' una stampa. Le unita' sono grezze (non divise per i decimali) e quindi confrontabili
    solo fra pool che usano la stessa valuta — dentro una chain e' quasi sempre lo stesso hub, e per
    la domanda «ci stava dentro una posizione?» basta."""
    try:
        return abs(float(x["a1" if meme_t0 else "a0"]))
    except Exception:
        return 0.0
