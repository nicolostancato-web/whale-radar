"""Leggere i registri della catena senza perdere pezzi in silenzio.

PERCHE' ESISTE (5/11 pomeriggio). Il punteggio delle occasioni si costruisce
leggendo gli eventi di liquidazione a fette di 400 blocchi. Misurato: su 18
fette, 2 NON RISPONDONO -- e in una prova ne hanno fallite tante da farmi
leggere ZERO liquidazioni in una finestra in cui ce n'erano quattro, fra cui
quella da 509.058 $.
Un punteggio che perde eventi in silenzio e' peggio di nessun punteggio:
direbbe "nessuna occasione" proprio quando ne passa una.

Due rimedi, insieme:
 1. PIU' FONTI. Il nostro nodo rifiuta certe letture; eth.drpc.org e
    blastapi rispondono (sono gli stessi che servono i saldi storici, che il
    nostro non serve). Si prova in ordine finche' una risponde.
 2. SI DICE QUANTO NON SI E' LETTO. Chi legge il risultato deve sapere se
    copre il 100% della finestra o il 60%.
"""
import json, time, urllib.request

FONTI = ("https://ethereum-rpc.publicnode.com",
         "https://eth.drpc.org",
         "https://eth-mainnet.public.blastapi.io")


def _chiedi(u, metodo, parametri, secondi=25):
    c = json.dumps({"jsonrpc": "2.0", "id": 1, "method": metodo,
                    "params": parametri}).encode()
    r = urllib.request.Request(u, c, {"content-type": "application/json",
                                      "user-agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(r, timeout=secondi))
    if "error" in d:
        raise RuntimeError(str(d["error"])[:80])
    return d.get("result")


def eventi(indirizzo, firma, da, a, passo=400):
    """Tutti gli eventi fra due blocchi. Torna (eventi, fette_lette, fette_perse).

    La terza voce e' la piu' importante: dice quanto del mondo NON abbiamo
    visto. Chi la ignora costruisce una media su un campione che non conosce.
    """
    fuori, lette, perse = [], 0, 0
    for x in range(da, a, passo):
        y = min(x + passo - 1, a)
        p = [{"address": indirizzo, "topics": [firma],
              "fromBlock": hex(x), "toBlock": hex(y)}]
        preso = None
        for u in FONTI:
            for _ in range(2):
                try:
                    preso = _chiedi(u, "eth_getLogs", p)
                    break
                except Exception:
                    time.sleep(0.4)
            if preso is not None:
                break
        if preso is None:
            perse += 1
        else:
            lette += 1
            fuori.extend(preso)
    return fuori, lette, perse


def blocco(n, con_transazioni=False):
    for u in FONTI:
        try:
            return _chiedi(u, "eth_getBlockByNumber",
                           [hex(n), con_transazioni])
        except Exception:
            continue
    return None
