#!/usr/bin/env python3
"""ALCHEMY ARRIVA PRIMA DI PUBLICNODE, E DI QUANTO?

La domanda di Nicolo' (7/11): «questa chiave che vantaggio ulteriore ti da'?
e' un vantaggio tale da prendere qualche liquidazione?»
Finora ho UNA risposta misurata (abbiamo un fornitore solo e cade) e due
sperate. Questa misura trasforma la piu' importante delle due in un numero.

COME, senza bruciare la fonte. NON si apre un secondo ascoltatore su
publicnode: la sentinella armata e' gia' la', e il 5/11 due ascoltatori sulle
stesse porte ci hanno fatto mettere in castigo per troppe richieste.
Quindi si ascolta SOLO Alchemy, si segna l'ora di arrivo di ogni campanella,
e poi si incrocia per hash col registro della sentinella (`sentinella.jsonl`,
campo `tx_oracolo` + `quando`), che e' l'ora in cui l'ha vista publicnode.
La differenza e' il vantaggio, col segno.

ATTENZIONE AL SEGNO E AL SIGNIFICATO: `quando` della sentinella e' scritto
quando ha FINITO il giro, non nell'istante esatto dell'arrivo, quindi la
differenza va letta come un limite superiore del vantaggio di Alchemy, non
come una misura fine. Se esce un vantaggio grande e consistente e' un
segnale; se esce piccolo o rumoroso, non si conclude niente.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import occhio_alchemy as OA

D = "data/liquidazioni"
FUORI = f"{D}/chi_arriva_prima.json"


def main():
    secondi = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    arrivi = {}

    def senti(tx, _p):
        h = (tx.get("hash") or "").lower()
        if h and h not in arrivi:
            arrivi[h] = time.time()
            print(f"   alchemy: {h[:14]} verso {(tx.get('to') or '')[:12]}",
                  flush=True)

    t0 = time.time()
    try:
        OA.ascolta(senti, ferma=lambda: time.time() - t0 > secondi)
    except OSError as e:
        print("   non ho potuto ascoltare:", str(e)[:100])
        return 1
    print(f"\n   {len(arrivi)} campanelle da Alchemy in "
          f"{time.time()-t0:.0f} secondi")

    # incrocio col registro della sentinella
    visto_da_publicnode = {}
    try:
        for riga in open(f"{D}/sentinella.jsonl"):
            try:
                d = json.loads(riga)
            except ValueError:
                continue
            h = str(d.get("tx_oracolo") or "").lower()
            if h and d.get("quando"):
                visto_da_publicnode.setdefault(h, d["quando"])
    except OSError:
        pass

    comuni = [(h, arrivi[h], visto_da_publicnode[h])
              for h in arrivi if h in visto_da_publicnode]
    print(f"   di queste, {len(comuni)} viste anche da publicnode")
    if not comuni:
        print("   NON CONCLUDO NIENTE: nessuna campanella in comune")
    else:
        diff = sorted((pn - al) * 1000 for _h, al, pn in comuni)
        med = diff[len(diff) // 2]
        print(f"   vantaggio di Alchemy: mediana {med:+.0f} ms "
              f"(da {diff[0]:+.0f} a {diff[-1]:+.0f}) su {len(diff)} misure")
        print("   positivo = Alchemy prima. Ricorda che l'ora di publicnode "
              "e' la fine del giro, quindi e' un LIMITE SUPERIORE.")
    cu, fr, msg = OA.stato_consumo()
    print(f"   consumo Alchemy del mese: {cu:,.0f} CU "
          f"({fr*100:.2f}% del gratuito), {msg} messaggi")
    try:
        t = FUORI + ".tmp"
        json.dump({"quando": time.time(), "secondi": secondi,
                   "campanelle_alchemy": len(arrivi),
                   "in_comune": len(comuni),
                   "vantaggio_ms": [(pn - al) * 1000
                                    for _h, al, pn in comuni],
                   "cu_mese": cu, "frazione_gratuito": fr},
                  open(t, "w"), indent=1)
        os.replace(t, FUORI)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
