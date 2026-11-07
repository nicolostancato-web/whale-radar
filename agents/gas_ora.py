#!/usr/bin/env python3
"""QUANTO COSTA UN COLPO ADESSO, letto da chi decide se sparare.

Misurato il 7/11. La guardia economica del pescatore era
    max(GUADAGNO_MINIMO_USD, premio x 0,25)
e NON conteneva il gas. Col gas di adesso (0,04 gwei) un colpo costa 0,10 $
e la cosa non si vedeva; ma i premi grossi delle 12 perse sono arrivati tutti
in un grappolo a 8-10 gwei, dove lo stesso colpo costa 24,60 $. In quel
momento una posizione da 2 $ di premio PASSAVA la guardia perdendo 23 $.
Cioe' la guardia era cieca esattamente nelle ore in cui compaiono i soldi.

Nicolo' (7/11): «quando cambia il gas noi dobbiamo essere flessibili... il
premio e' cosi' alto in confronto al gas che ce ne frega». Vero sui premi
grossi, falso sulla polvere: la flessibilita' va nei due versi, e per averla
bisogna che chi decide SAPPIA il gas. Prima non lo sapeva.

Il valore lo scrive chi guarda gia' la testa della catena (la sentinella, a
ogni blocco nuovo) e lo legge chi decide. Se il file e' vecchio o assente si
torna None: chi legge usa la sua costante prudente. Qui il ripiego non e' una
bugia perche' la costante resta un valore difendibile -- ma la differenza va
DETTA, non nascosta, percio' `leggi` dice anche quanto e' vecchio.
"""
import json, os, time

DOVE = "data/liquidazioni/gas_ora.json"
VECCHIO_MAX = 120.0     # oltre due minuti non e' piu' "adesso"


def scrivi(base_fee_wei, blocco=None, prezzo_eth=None):
    try:
        tmp = DOVE + ".tmp"
        json.dump({"base_fee_gwei": base_fee_wei / 1e9, "blocco": blocco,
                   "prezzo_eth": prezzo_eth, "quando": time.time()},
                  open(tmp, "w"))
        os.replace(tmp, DOVE)
        return True
    except Exception:
        return False


def leggi():
    """(base_fee_gwei, prezzo_eth, eta_secondi) oppure (None, None, None)."""
    try:
        d = json.load(open(DOVE))
    except Exception:
        return None, None, None
    eta = time.time() - d.get("quando", 0)
    if eta > VECCHIO_MAX:
        return None, None, eta
    return d.get("base_fee_gwei"), d.get("prezzo_eth"), eta


def costo_colpo_usd(gas=1_400_000, prezzo_eth=None):
    """quanto ci costa in dollari un colpo adesso; None se non lo sappiamo"""
    bf, pe, _ = leggi()
    pe = prezzo_eth or pe
    if not bf or not pe:
        return None
    return gas * bf * 1e-9 * pe


if __name__ == "__main__":
    bf, pe, eta = leggi()
    if bf is None:
        print("   GAS ORA: non lo so" + (f" (vecchio di {eta:.0f}s)"
                                        if eta else " (file assente)"))
    else:
        c = costo_colpo_usd()
        print(f"   GAS ORA: {bf:.3f} gwei, ETH ${pe or 0:.0f}, "
              f"un colpo da 1,4M gas costa ${c:.2f} "
              f"(letto {eta:.0f}s fa)")
