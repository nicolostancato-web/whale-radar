"""LA REGOLA INVARIATA SUL MERCATO NON-PONS, stessa chain.

== PERCHE' (8/10/2026, notte) ==

Su robinhood si creano pool anche da altre piattaforme di lancio (Bankr, Clanker...): misurato su
pool creati fra 2 e 6 ore fa, **853 non-Pons contro 306 di Pons**, e comprabili il **27%** contro
il **3%**. Circa 230 occasioni contro 9 nella stessa finestra.

Previsione registrata prima di misurare (`PREVISIONE_SETTIMA_8OTT.md`): la regola invariata dara'
piu' di +10% medio. **Mi aspetto di no**, e l'ho scritto: la forma «chi perde perde il 95-99%»
appartiene alla categoria memecoin, non alla piattaforma.

== LA REGOLA, IDENTICA A QUELLA DI PONS ==

entrata alla fine del primo minuto (600 blocchi dal primo scambio del pool, prezzo mediano degli
ultimi 5 scambi); uscita al primo prezzo che tocca 2x; altrimenti all'ultimo prezzo osservato.
Costi 1% + 1%, scivolamento misurato 1,71% a tratta per 200 $.

== IL CAMPIONE ==

Costruito **dalla chain**: evento `Initialize` del gestore dei pool, scartando i pool il cui
gettone risulta lanciato su Pons. Nessun file nostro — e' il difetto che oggi ha falsificato tre
numeri.

Per i decimali della valuta si chiede al contratto: un prezzo con la scala sbagliata non e' un
dato parziale, e' un dato falso (lezione del «2855x» che valeva 1,20x).
"""
import collections
import gzip
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402
import prima_la_prova as PP                                  # noqa: E402


# UNA SOLA LIBRERIA DI LETTURA (11/10, prescrizione di Astra). `curva_lanci` e `coppie` erano
# oggetti unici da 52 e 16,6 MB: per aggiungere un dato si riscriveva tutto, e ogni riscrittura
# entrava INTERA nella storia di git. Ora stanno a righe, e queste due funzioni nascondono quale
# forma c'e' sul disco: se cambia di nuovo, cambia in agents/archivio.py e non in dodici file.
def _lanci_interi():
    import archivio as _AR
    _t, _v = _AR.leggi("curva_lanci")
    _d = dict(_t)
    _d["da"] = _v
    return _d


def _coppie():
    import archivio as _AR
    return _AR.leggi("coppie", "coppie")[1]


CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
ARCH = f"{BASE}/mercato_non_pons.jsonl"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
ZERO = "0x" + "0" * 40
FIN = 600
COSTO = 1.02
SCIV = float(os.environ.get("SCIVOLAMENTO", "0.0171"))
BUDGET = int(os.environ.get("BUDGET_SEC", "2500"))
# finestra di pool da esaminare: creati fra 12 ore e 3 giorni fa, cosi' hanno avuto tempo di
# muoversi ma non sono cosi' vecchi da uscire dal nostro orizzonte di lettura
DA_ORE = float(os.environ.get("DA_ORE", "12"))
A_ORE = float(os.environ.get("A_ORE", "72"))

_dec = {}


def decimali(asset):
    a = (asset or "").lower()
    if a in _dec:
        return _dec[a]
    if a == ZERO:
        _dec[a] = 18
        return 18
    r = CP.chiama("eth_call", [{"to": a, "data": "0x313ce567"}, "latest"])
    try:
        _dec[a] = int(r, 16) if r and r != "0x" else None
    except Exception:
        _dec[a] = None
    return _dec[a]


def main():
    L = set(_lanci_interi()["da"])
    st = json.load(open(f"{BASE}/prova_in_avanti.json"))
    pons = L | set(st.get("lanci_visti") or [])
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("NON-PONS | la chain non risponde.")
        return 0
    da = bn - int(A_ORE * 3600 * 10)
    a = bn - int(DA_ORE * 3600 * 10)
    pool = []
    passo = 200000
    b = da
    while b <= a:
        fine = min(a, b + passo)
        r = CP.chiama("eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(fine),
                                       "address": GESTORE_V4, "topics": [INIT]}])
        if r is None:
            print(f"NON-PONS | lettura fallita fra {b:,} e {fine:,}: mi fermo qui invece di "
                  f"misurare su un campione con un buco dentro.")
            return 0
        for x in r:
            if len(x.get("topics") or []) < 4:
                continue
            c0 = "0x" + x["topics"][2][-40:]
            c1 = "0x" + x["topics"][3][-40:]
            if c0 in pons or c1 in pons:
                continue                    # questo e' di Pons: non e' il campione di qui
            # il gettone e' quello NON noto come valuta; la valuta e' l'altro lato
            for lato, g, val in (("t0", c0, c1), ("t1", c1, c0)):
                d = decimali(val)
                if d is None:
                    continue
                pool.append({"pool": x["topics"][1].lower(), "lato_gettone": lato,
                             "valuta": val, "dec": d, "creato": int(x["blockNumber"], 16)})
                break
        b = fine + 1
    print(f"NON-PONS | pool non-Pons creati fra {A_ORE:.0f} e {DA_ORE:.0f} ore fa: {len(pool)}",
          flush=True)

    fatte = set()
    if os.path.exists(ARCH):
        for l in open(ARCH):
            if l.strip():
                try:
                    fatte.add(json.loads(l)["pool"])
                except Exception:
                    pass
    t0 = time.time()
    n = 0
    with open(ARCH, "a", buffering=1) as f:
        for p in pool:
            if p["pool"] in fatte:
                continue
            if time.time() - t0 > BUDGET:
                print("NON-PONS | finito il tempo: l'archivio resta.", flush=True)
                break
            ev = CP.log_di_finestra(PP.SWAP_V4, p["creato"], min(bn, p["creato"] + 9999999),
                                    indirizzo=GESTORE_V4, secondo=p["pool"])
            if ev is None:
                continue
            n += 1
            s = []
            for x in ev:
                nn = CP._numeri(x.get("data", "0x"))
                if len(nn) < 2:
                    continue
                a0 = nn[0] - (1 << 256) if nn[0] >= (1 << 255) else nn[0]
                a1 = nn[1] - (1 << 256) if nn[1] >= (1 << 255) else nn[1]
                qt = a1 if p["lato_gettone"] == "t1" else a0
                qq = a0 if p["lato_gettone"] == "t1" else a1
                if qt == 0 or qq == 0:
                    continue
                vq = abs(qq) / (10 ** p["dec"])
                if vq < 1e-9:
                    continue
                s.append({"b": int(x["blockNumber"], 16),
                          "i": int(x.get("logIndex", "0x0"), 16),
                          "prezzo": vq / (abs(qt) / 1e18), "vende": qq < 0})  # VERSO INVERTITO, vedi cammino_posizioni (10/10): va messo `qq > 0`. Non lo cambio ora perche' questo agente e' di una fase chiusa e i suoi numeri sono gia' stati ritirati.
            s.sort(key=lambda d: (d["b"], d["i"]))
            rec = {"pool": p["pool"], "scambi": len(s), "valuta": p["valuta"]}
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
                        C = COSTO * (1 + SCIV) ** 2
                        rec["esito"] = "misurata"
                        rec["tocca_2x"] = 1 if tocca else 0
                        rec["rendimento"] = round((2.0 / C - 1) if tocca
                                                  else (dopo[-1]["prezzo"] / pe / C - 1), 4)
                        rec["max_x"] = round(max(z["prezzo"] for z in dopo) / pe, 3)
            f.write(json.dumps(rec) + "\n")
            time.sleep(0.2)
            if n % 50 == 0:
                print(f"NON-PONS | {n} fatti, {int(time.time()-t0)}s", flush=True)

    tutte = [json.loads(l) for l in open(ARCH) if l.strip()]
    c = collections.Counter(x["esito"] for x in tutte)
    print(f"\nNON-PONS | {len(tutte)} pool esaminati:")
    for k, v in c.most_common():
        print(f"   {v:4}  {k}  ({100*v/len(tutte):.1f}%)")
    mis = [x for x in tutte if x["esito"] == "misurata"]
    if len(mis) >= 80:
        r = [x["rendimento"] for x in mis]
        import math
        se = statistics.stdev(r) / math.sqrt(len(r))
        print(f"\nNON-PONS | su {len(mis)} comprabili, regola invariata a 200$:")
        print(f"   medio   {100*statistics.mean(r):+.1f}%  (intervallo 95%: "
              f"+/- {100*1.96*se:.1f})")
        print(f"   mediano {100*statistics.median(r):+.1f}%")
        print(f"   in guadagno {sum(1 for v in r if v>0)}/{len(r)}")
        m = statistics.mean(r)
        print(f"   VERDETTO: {'CONFERMATA' if m>0.10 else ('SMENTITA' if m<0 else 'NON DIMOSTRATA')}"
              f"  (soglia dichiarata +10%)")
        print(f"   per confronto, la stessa regola su Pons: -10,4%")
    else:
        print(f"\nNON-PONS | solo {len(mis)} comprabili: sotto 80 non guardo, come dichiarato.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
