"""Un simulatore che vede quanto vede la macchina, e che si fa esaminare sul passato.

PERCHE' (15/10). Il simulatore sulla serie vera prometteva +28/+34% per operazione; la cassa,
sulle stesse 68 operazioni, ha dato -5,31%. Trentatre punti di scarto. Le cause misurate, in
ordine di peso:
  - NON il prezzo d'entrata: paghiamo solo il +2,8% rispetto a quello assunto;
  - vendere al prezzo di chi compra: pesa 5,6 punti, corretto;
  - IL GROSSO: la macchina vede il 54% degli scambi. Nella finestra di una posizione ne
    avvengono 87, noi ne registriamo 43. Il simulatore usciva su picchi che noi non abbiamo
    mai visto passare: non simulava la nostra strategia, simulava un onnisciente.

Qui il tempo scorre a FINESTRE: la macchina guarda ogni GIRO secondi, vede solo l'ultimo
prezzo della finestra, e se decide di uscire la vendita arriva una finestra dopo. E' il modo
in cui funziona davvero.

LA PROVA D'ESAME: prima di proporre qualunque cosa, questo simulatore deve indovinare le 68
operazioni che abbiamo gia' pagato. Se sbaglia, e' lui a essere sbagliato, non il mercato.
"""
import json
import os
import statistics
import sys

SEC = 0.093
GIRO = float(os.environ.get("GIRO_SEC", "6"))
BLOCCHI_GIRO = max(1, int(GIRO / SEC))


def a_finestre(serie, b0):
    """Quello che la macchina vede: l'ultimo prezzo di ogni finestra, acquisti e vendite a parte."""
    dentro = [x for x in serie if x[0] >= b0]
    if not dentro:
        return []
    fuori, fine, ultimo = [], dentro[0][0] + BLOCCHI_GIRO, None
    for b, p, v in dentro:
        if b >= fine:
            if ultimo:
                fuori.append(ultimo)
            while b >= fine:
                fine += BLOCCHI_GIRO
            ultimo = None
        ultimo = [b, p, v]
    if ultimo:
        fuori.append(ultimo)
    return fuori


def esito(serie, b0, stop, bers):
    """Resa di una posizione come la vivrebbe la macchina."""
    dentro = [x for x in serie if x[0] >= b0]
    ent = [x for x in dentro if x[2] == "compra"]
    if not ent:
        return None
    p0 = ent[0][1]
    visti = a_finestre(serie, ent[0][0])
    if len(visti) < 2:
        return None
    for i, (b, p, _v) in enumerate(visti):
        x = p / p0
        if x <= stop or (bers and x >= bers):
            # la vendita arriva una finestra dopo, e al prezzo di una VENDITA vera
            for b2, p2, v2 in visti[i + 1:]:
                if v2 == "vende":
                    return p2 / p0 - 1
            # nessuna vendita osservabile dopo: si esce all'ultimo prezzo visto
            return visti[-1][1] / p0 - 1
    return visti[-1][1] / p0 - 1


def esame(reg, st, serie, parla=True):
    """Fa indovinare al simulatore le operazioni gia' pagate. Torna lo scarto medio."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import bot_curva as B
    import curva_pons as CP
    cop = []
    for k, f in reg["fatte"].items():
        g = f.get("gettone")
        p = st["posizioni"].get(k, {})
        h = f.get("uscita")
        if g not in serie or not p.get("blocco_entrata") or not str(h).startswith("0x"):
            continue
        rc = B.chiama("eth_getTransactionReceipt", [h])
        if not rc or rc["status"] != "0x1":
            continue
        inc = 0
        for l in (rc.get("logs") or []):
            if (l.get("topics") or [""])[0].lower() == CP.T_VENDE.lower():
                inc = int(l["data"][2:][64:128], 16) / 1e18
        s = esito(serie[g], p["blocco_entrata"], p.get("stop", 0.95), p.get("bersaglio"))
        if s is None:
            continue
        cop.append((s, inc / f.get("nativi", 0.0007) - 1))
    if not cop:
        return None
    sim = statistics.mean([x[0] for x in cop])
    vero = statistics.mean([x[1] for x in cop])
    if parla:
        print(f"   ESAME su {len(cop)} operazioni gia' pagate")
        print(f"      il simulatore dice {sim*100:+7.2f}% | la cassa ha detto {vero*100:+7.2f}%")
        print(f"      scarto {abs(sim-vero)*100:.1f} punti")
    return sim - vero


def main():
    serie = {}
    for r in open("data/multichain/robinhood/serie_vera.jsonl"):
        d = json.loads(r)
        serie[d["gettone"]] = d["serie"]
    reg = json.load(open("data/multichain/robinhood/mani_curva.json"))
    st = json.load(open("data/multichain/robinhood/prova_nella_curva.json"))
    print(f"SIMULATORE ONESTO — finestra di {GIRO:.0f}s ({BLOCCHI_GIRO} blocchi)\n")
    esame(reg, st, serie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
