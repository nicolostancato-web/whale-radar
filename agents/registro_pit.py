#!/usr/bin/env python3
"""
REGISTRO_PIT — il libro mastro, in sola aggiunta, di COSA abbiamo saputo e QUANDO.

PERCHE' ESISTE (14/09, indicazione del revisore avversariale). L'audit ha trovato che non possiamo
verificare la domanda che decide la validita' di ogni ricerca: «questo dato ce l'avevamo, al momento
in cui la strategia avrebbe deciso?». La storia git non serve — il nostro GC l'ha schiacciata l'11/09
e ha cancellato ogni traccia precedente.

Il revisore e' stato netto su cosa fare per primo: «correggere l'embargo senza poter provare quando
il dato e' arrivato produce semplicemente un embargo piu' elegante ma non verificabile».
Quindi prima il libro mastro, poi l'embargo.

TRE PROPRIETA', e servono tutte e tre:
  1. SOLA AGGIUNTA: non si riscrive e non si riordina. Una riga scritta resta com'e'.
  2. OGNI RIGA SI BASTA: istante, agente, fonte, chain, che cosa e' entrato, quanto, e l'identificativo
     del giro. Chi legge fra sei mesi non deve dedurre niente.
  3. FUORI DALLA PORTATA DELLA MANUTENZIONE: il GC puo' potare i dati, non questo. Chi lo pota
     cancella la prova che i dati erano leciti.

Non contiene i dati: contiene il fatto che li abbiamo ricevuti, e quando. €0.
"""
import json, os, time

REG = "data/registro_pit.jsonl"


def giro():
    """L'identificativo del giro: su GitHub Actions e' il numero della corsa, fuori e' l'ora."""
    return (os.environ.get("GITHUB_RUN_ID") or os.environ.get("GITHUB_RUN_NUMBER")
            or f"locale-{int(time.time())}")


def annota(agente, fonte, chain, quanti, dettaglio=None):
    """Una riga per ogni raccolta andata a buon fine. Non fallisce mai in modo rumoroso: se il libro
    non si puo' scrivere, la raccolta deve comunque proseguire — ma lo dice."""
    riga = {"acq": int(time.time()), "agente": agente, "fonte": fonte, "chain": chain,
            "quanti": int(quanti), "giro": giro()}
    if dettaglio: riga["dettaglio"] = dettaglio
    try:
        os.makedirs(os.path.dirname(REG), exist_ok=True)
        with open(REG, "a") as f:          # SOLA AGGIUNTA: mai "w", mai riscrittura
            f.write(json.dumps(riga) + "\n")
        return True
    except Exception as e:
        print(f"REGISTRO_PIT | non sono riuscito ad annotare: {type(e).__name__}", flush=True)
        return False


def riepilogo():
    """Quanto indietro arriva il libro, e con che continuita'. Serve a sapere da quando in poi una
    verifica point-in-time e' possibile — prima di quella data, non lo sara' mai."""
    if not os.path.exists(REG): return None
    righe = []
    try:
        for l in open(REG):
            if l.strip():
                try: righe.append(json.loads(l))
                except Exception: pass
    except Exception:
        return None
    if not righe: return None
    ts = [r.get("acq", 0) for r in righe if r.get("acq")]
    per_agente = {}
    for r in righe: per_agente[r.get("agente", "?")] = per_agente.get(r.get("agente", "?"), 0) + 1
    return {"righe": len(righe), "dal": min(ts), "al": max(ts), "per_agente": per_agente}


if __name__ == "__main__":
    r = riepilogo()
    if not r:
        print("REGISTRO_PIT | ancora vuoto: la verifica point-in-time comincia dalla prima riga")
    else:
        print(f"REGISTRO_PIT | {r['righe']} annotazioni | dal {time.strftime('%d/%m %H:%M', time.gmtime(r['dal']))} "
              f"al {time.strftime('%d/%m %H:%M', time.gmtime(r['al']))} | {r['per_agente']}")
