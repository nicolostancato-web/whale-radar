"""Il numero che conta: quanto abbiamo adesso, e quanto e' cambiato.

PERCHE' ESISTE (14/10, richiesta di Nicolo'). Da quando siamo live il metro non e' piu' «quante
voci passano» o «quanti difetti ho corretto»: e' il saldo. Ogni messaggio del custode deve
aprirsi con la cassa e la sua variazione, altrimenti si finisce a raccontare il lavoro invece
del risultato.

La percentuale si calcola sui nativi, che e' esatta e non dipende dal cambio. Gli euro sono
indicativi, al cambio dichiarato qui sotto.
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot_curva as B                                          # noqa: E402

# AZZERATO IL 14/10 ALLE 19:30 (decisione di Nicolo'). Il conto da cui si misura non e'
# piu' quello di ieri sera: i primi 4,60 EUR persi erano il prezzo dei difetti, non del
# mercato, e tenerli dentro il metro avrebbe confuso per settimane il costo
# dell'apprendimento con il risultato della strategia. Da qui si parte puliti.
PARTENZA = 0.021954          # la cassa del 14/10 sera: inizio ufficiale del live
CAMBIO = 3000.0              # euro per nativo, indicativo
STORICO = "data/multichain/robinhood/cassa_storico.jsonl"


def saldo():
    """Il denaro liquido PIU' il valore delle posizioni ancora aperte.

    PERCHE' (15/10, falso allarme costato una notifica notturna). Contando solo il liquido,
    una posizione aperta risultava denaro sparito: con due posizioni aperte il misuratore
    segnava 54 EUR invece di 67, e ho fermato la macchina per una perdita che non esisteva.
    Un misuratore che vede meta' della ricchezza non misura la ricchezza: misura dove si
    trova in quel momento. Qui si somma anche quello che si incasserebbe vendendo adesso.
    """
    from eth_account import Account
    tot = 0.0
    for k in B.chiavi():
        b = B.chiama("eth_getBalance", [Account.from_key(k).address, "latest"])
        if b is None:
            return None
        tot += int(b, 16) / 1e18
    return tot + in_gettoni()


def in_gettoni():
    """Quanto varrebbe, venduto adesso, cio' che teniamo in gettoni."""
    f = "data/multichain/robinhood/mani_curva.json"
    if not os.path.exists(f):
        return 0.0
    reg = json.load(open(f))
    fuori = 0.0
    for p in reg.get("fatte", {}).values():
        if p.get("finita"):
            continue
        q = B.chiama("eth_call", [{"to": p["gettone"],
                                   "data": "0x70a08231" + "0" * 24 + p["portafoglio"][2:]},
                                  "latest"])
        q = int(q, 16) if q and q != "0x" else 0
        if not q:
            continue
        o = B.chiama("eth_call", [{"from": p["portafoglio"], "to": p["curva"],
                                   "data": B.dati_vendita(q, 1, p["portafoglio"]),
                                   "value": "0x0"}, "latest"])
        if o and len(o) >= 66:
            fuori += int(o[2:66], 16) / 1e18
    return fuori


def ieri(adesso):
    """Il saldo piu' vecchio registrato nelle ultime 24-36 ore, per dire «da ieri»."""
    if not os.path.exists(STORICO):
        return None
    vecchi = []
    for riga in open(STORICO):
        try:
            d = json.loads(riga)
        except Exception:
            continue
        if 20 * 3600 < adesso - d["quando"] < 40 * 3600:
            vecchi.append(d)
    return vecchi[0]["cassa"] if vecchi else None


def main():
    c = saldo()
    if c is None:
        print("CASSA | non riesco a leggere i portafogli")
        return 1
    ora = int(time.time())
    os.makedirs(os.path.dirname(STORICO), exist_ok=True)
    with open(STORICO, "a") as f:
        f.write(json.dumps({"quando": ora, "cassa": round(c, 8)}) + "\n")
    d = (c / PARTENZA - 1) * 100
    riga = (f"CASSA | {c * CAMBIO:.2f} EUR ({c:.6f} nativi) | "
            f"dalla partenza {d:+.1f}% ({(c - PARTENZA) * CAMBIO:+.2f} EUR)")
    y = ieri(ora)
    if y:
        riga += f" | da ieri {(c / y - 1) * 100:+.1f}%"
    print(riga)
    print(f"      pavimento a {B.PAVIMENTO * CAMBIO:.0f} EUR: mancano "
          f"{(c - B.PAVIMENTO) * CAMBIO:.2f} EUR allo stop automatico")
    return 0


if __name__ == "__main__":
    sys.exit(main())
