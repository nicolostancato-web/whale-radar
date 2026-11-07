"""Simulatore secondo tentativo: il prezzo si legge liscio, l'incasso si prende dai fatti.

PERCHE' IL PRIMO NON ANDAVA (15/10). Azzeccava la media (-4,37% contro -5,31%) ma sbagliava
la forma: mediana -41,93% contro -5,35%, e solo 10 operazioni su 68 entro dieci punti. La
media coincideva per compensazione fra perdite enormi e guadagni enormi, nessuno dei due
reale. Un modello che azzecca solo la media non e' tarato: e' una coincidenza con un
parametro dentro.

DUE CORREZIONI, entrambe dai fatti e non dall'immaginazione:
1. IL PREZZO SI LEGGE LISCIO. Un singolo scambio a prezzo strano faceva «toccare» stop o
   bersaglio a livelli che il mercato non ha mai davvero attraversato. La macchina vera non
   reagisce a un prezzo solo: qui si usa la mediana degli ultimi K scambi.
2. L'INCASSO SI PRENDE DALLE 68 OPERAZIONI VERE. Non si indovina quanto si incassa al tocco:
   si usa il rapporto MISURATO fra quello che la regola voleva e quello che la cassa ha
   dato — 0,908/0,950 sugli stop, 1,203/1,500 sui bersagli.
"""
import json
import os
import statistics
import sys

K = int(os.environ.get("LISCIO", "5"))
RESA_STOP = float(os.environ.get("RESA_STOP", "0.956"))      # 0,908 / 0,950, misurato
RESA_BERS = float(os.environ.get("RESA_BERS", "0.802"))      # 1,203 / 1,500, misurato


def esito(serie, b0, stop, bers):
    dentro = [x for x in serie if x[0] >= b0]
    ent = [x for x in dentro if x[2] == "compra"]
    if not ent:
        return None
    p0 = ent[0][1]
    fin = [x for x in dentro if x[0] >= ent[0][0]]
    if len(fin) < K + 2:
        return None
    for i in range(K, len(fin)):
        liscio = statistics.median([fin[j][1] for j in range(i - K, i)])
        x = liscio / p0
        if x <= stop:
            return stop * RESA_STOP - 1
        if bers and x >= bers:
            return bers * RESA_BERS - 1
    ultimo = statistics.median([fin[j][1] for j in range(len(fin) - K, len(fin))])
    return ultimo / p0 * RESA_STOP - 1


def esame(parla=True):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import bot_curva as B
    import curva_pons as CP
    reg = json.load(open("data/multichain/robinhood/mani_curva.json"))
    st = json.load(open("data/multichain/robinhood/prova_nella_curva.json"))
    serie = {}
    for r in open("data/multichain/robinhood/serie_vera.jsonl"):
        d = json.loads(r)
        serie[d["gettone"]] = d["serie"]
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
    sim = [x[0] for x in cop]
    vero = [x[1] for x in cop]
    vicini = sum(1 for a, b in cop if abs(a - b) < 0.10)
    if parla:
        print(f"   ESAME su {len(cop)} operazioni vere (liscio su {K} scambi)")
        print(f"      media    simulatore {statistics.mean(sim)*100:+7.2f}% | cassa "
              f"{statistics.mean(vero)*100:+7.2f}%")
        print(f"      mediana  simulatore {statistics.median(sim)*100:+7.2f}% | cassa "
              f"{statistics.median(vero)*100:+7.2f}%")
        print(f"      in utile {sum(1 for x in sim if x>0)}/{len(sim)} contro "
              f"{sum(1 for x in vero if x>0)}/{len(vero)}")
        print(f"      operazioni azzeccate entro 10 punti: {vicini}/{len(cop)}")
    return vicini / len(cop)


if __name__ == "__main__":
    print("SIMULATORE v2\n")
    esame()
