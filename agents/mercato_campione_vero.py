"""IL MERCATO DOPO IL DIPLOMA, su un campione CASUALE VERO.

== PERCHE' (8/10/2026) ==

Il +18,9% della regola senza selezione era misurato su monete estratte da `coppie.json`, che copre
**un pool su dodici** e contiene quelli che i raccoglitori avevano visto *scambiare*: i piu'
attivi. Su un primo campione casuale costruito dalla chain, 27 diplomate su 35 avevano un pool che
non scambia mai e solo il 17% era comprabile.

Qui la misura si rifa' sul campione casuale vero: lanci presi a caso -> diploma verificato sulla
chain -> id del pool dall'evento Initialize -> scambi del pool.

== LE CATEGORIE, TENUTE SEPARATE ==

Un referto che mescola «escluso da una regola nota all'entrata» con «escluso perche' non l'ho
letto» non si puo' interpretare. Qui si contano separatamente:
  - **non comprabile**: meno di 5 scambi nel primo minuto -> legittimo, lo si sa comprando;
  - **pool muto**: nessuno scambio -> legittimo, non c'e' niente da comprare;
  - **lettura fallita** -> difetto mio, e non si conclude su cio' che non si e' letto.
"""
import gzip
import json
import os
import statistics
import sys
import time
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402
import prima_la_prova as PP                                  # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
DENTRO = f"{BASE}/diplomate_vere.jsonl"
ARCH = f"{BASE}/mercato_campione_vero.jsonl"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
FIN = 600
COSTO = 1.02
SCIV = float(os.environ.get("SCIVOLAMENTO", "0.0171"))
BUDGET = int(os.environ.get("BUDGET_SEC", "2500"))


def scambi(pid, nato, bn):
    ev = CP.log_di_finestra(PP.SWAP_V4, nato, min(bn, nato + 9999999),
                            indirizzo=GESTORE_V4, secondo=pid)
    if ev is None:
        return None
    s = []
    for x in ev:
        n = CP._numeri(x.get("data", "0x"))
        if len(n) < 2:
            continue
        a0 = n[0] - (1 << 256) if n[0] >= (1 << 255) else n[0]
        a1 = n[1] - (1 << 256) if n[1] >= (1 << 255) else n[1]
        v0, v1 = abs(a0) / 1e18, abs(a1) / 1e18
        if v0 == 0 or v1 == 0:
            continue
        # il lato della VALUTA e' il piccolo: il memecoin ha 18 decimali e importi enormi.
        # Non e' un'assunzione gratuita: su questi pool la valuta e' ETH e i gettoni sono
        # miliardi. Dove i due lati sono comparabili, la riga si scarta invece di indovinare.
        if min(v0, v1) * 1000 > max(v0, v1):
            continue
        vq, qt = (v0, v1) if v0 < v1 else (v1, v0)
        if vq < 1e-6:
            continue
        s.append({"b": int(x["blockNumber"], 16), "i": int(x.get("logIndex", "0x0"), 16),
                  "prezzo": vq / qt, "denaro": vq,
                  "vende": (a0 < 0) if v0 < v1 else (a1 < 0)})
    s.sort(key=lambda d: (d["b"], d["i"]))
    return s


def main():
    righe = [json.loads(l) for l in open(DENTRO) if l.strip()]
    dip = [d for d in righe if d.get("diplomata") and d.get("pool") not in (None, "senza id")]
    fatte = set()
    if os.path.exists(ARCH):
        for l in open(ARCH):
            if l.strip():
                try:
                    fatte.add(json.loads(l)["moneta"])
                except Exception:
                    pass
    print(f"VERO | {len(righe):,} lanci casuali, {len(dip)} diplomate con id del pool, "
          f"{len(fatte)} gia' fatte", flush=True)
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("VERO | la chain non risponde.")
        return 0
    t0 = time.time()
    n = 0
    with open(ARCH, "a", buffering=1) as f:
        for d in dip:
            if d["moneta"] in fatte:
                continue
            if time.time() - t0 > BUDGET:
                print("VERO | finito il tempo: l'archivio resta.", flush=True)
                break
            s = scambi(d["pool"], d["nato"], bn)
            if s is None:
                continue                      # lettura fallita: non si scrive
            n += 1
            rec = {"moneta": d["moneta"], "scambi": len(s)}
            if not s:
                rec["esito"] = "pool muto"
            else:
                b0 = s[0]["b"]
                dentro = [z for z in s if z["b"] <= b0 + FIN]
                dopo = [z for z in s if z["b"] > b0 + FIN]
                if len(dentro) < 5:
                    rec["esito"] = "non comprabile"
                elif not dopo:
                    rec["esito"] = "nessuno scambio dopo la finestra"
                else:
                    pe = statistics.median([z["prezzo"] for z in dentro[-5:]])
                    if pe <= 0:
                        rec["esito"] = "prezzo non valido"
                    else:
                        tocca = any(z["prezzo"] >= 2 * pe for z in dopo)
                        rec["esito"] = "misurata"
                        rec["tocca_2x"] = 1 if tocca else 0
                        rec["rendimento"] = round(
                            (2.0 / (COSTO * (1 + SCIV) ** 2) - 1) if tocca
                            else (dopo[-1]["prezzo"] / pe / (COSTO * (1 + SCIV) ** 2) - 1), 4)
                        rec["max_x"] = round(max(z["prezzo"] for z in dopo) / pe, 3)
            f.write(json.dumps(rec) + "\n")
            time.sleep(0.25)
            if n % 50 == 0:
                print(f"VERO | {n} fatte, {int(time.time()-t0)}s", flush=True)

    tutte = [json.loads(l) for l in open(ARCH) if l.strip()]
    c = collections.Counter(x["esito"] for x in tutte)
    print(f"\nVERO | {len(tutte)} diplomate esaminate:")
    for k, v in c.most_common():
        print(f"   {v:4}  {k}  ({100*v/len(tutte):.1f}%)")
    mis = [x for x in tutte if x["esito"] == "misurata"]
    if len(mis) >= 40:
        r = [x["rendimento"] for x in mis]
        print(f"\nVERO | su {len(mis)} comprabili, a 200$ con scivolamento misurato:")
        print(f"   medio   {100*statistics.mean(r):+.1f}%    (campione del registro: +15,2%)")
        print(f"   mediano {100*statistics.median(r):+.1f}%")
        print(f"   in guadagno {sum(1 for x in r if x>0)}/{len(r)}")
        mx = sorted(x["max_x"] for x in mis)
        print(f"   massimo raggiunto: mediana {mx[len(mx)//2]:.2f}x, "
              f"90% {mx[int(.9*len(mx))]:.2f}x, migliore {mx[-1]:.1f}x")
    else:
        print(f"\nVERO | solo {len(mis)} comprabili: sotto 40 non concludo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
