"""QUANTO GUADAGNA CHI RICEVE GETTONI E LI VENDE.

Il criterio giusto non e' l'importo pagato ma la PROVENIENZA: se i gettoni arrivano da un
indirizzo e non dal mercato, e' una consegna. E se UN SOLO mittente fornisce la maggior parte
dei gettoni che entrano in un portafoglio, quel portafoglio non e' un trader: e' il terminale
di una distribuzione.

Qui si misura quel mestiere: quanto incassa, con che capitale, e quanto e' diffuso.
"""
import collections, json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solana_rpc as S

DENTRO = "data/multichain/solana/storia2.jsonl"
FUORI = "data/multichain/solana/regali.json"
TETTO = int(os.environ.get("TETTO", "400"))


def main():
    noti = json.load(open(FUORI)) if os.path.exists(FUORI) else {}
    chiam = 0
    righe = []
    for r in open(DENTRO):
        d = json.loads(r)
        w = d["w"]
        if len(d["ops"]) < 10:
            continue
        # per ogni gettone comprato: i gettoni arrivavano da un INDIRIZZO o dal mercato?
        per = collections.defaultdict(lambda: {"c": 0.0, "v": 0.0, "sig": None})
        for sl, p, compra, m, sol, get in d["ops"]:
            k = per[m]
            if compra:
                k["c"] += sol
            else:
                k["v"] += sol
        consegnati, comprati = {}, {}
        for m, k in per.items():
            chiave = f"{w[:8]}/{m[:8]}"
            if chiave in noti:
                mitt = noti[chiave]
            elif chiam < TETTO:
                mitt = None
                sig = S.rpc("getSignaturesForAddress", [m, {"limit": 60}]) or []
                chiam += 1
                for x in sig[-20:]:
                    if x.get("err") or chiam >= TETTO:
                        continue
                    t = S.rpc("getTransaction", [x["signature"],
                              {"maxSupportedTransactionVersion": 2, "encoding": "jsonParsed",
                               "commitment": "confirmed"}])
                    chiam += 1
                    if not t:
                        continue
                    meta = t["meta"]
                    pre = {y["accountIndex"]: float(y["uiTokenAmount"]["uiAmount"] or 0)
                           for y in meta.get("postTokenBalances", [])}
                    rec = any(y.get("owner") == w and y["mint"] == m
                              for y in meta.get("postTokenBalances", []))
                    if not rec:
                        continue
                    for y in meta.get("postTokenBalances", []):
                        if y["mint"] == m and y.get("owner") not in (None, w):
                            mitt = y.get("owner")
                            break
                    if mitt:
                        break
                noti[chiave] = mitt
            else:
                continue
            (consegnati if mitt else comprati)[m] = k
        if not consegnati and not comprati:
            continue
        inc_reg = sum(k["v"] for k in consegnati.values())
        cos_reg = sum(k["c"] for k in consegnati.values())
        righe.append({"w": w, "n_reg": len(consegnati), "n_comp": len(comprati),
                      "incassato": inc_reg, "speso": cos_reg,
                      "trading": sum(k["v"] - k["c"] for k in comprati.values())})
    json.dump(noti, open(FUORI, "w"))
    reg = [x for x in righe if x["n_reg"] > 0]
    print(f"ECONOMIA DEI REGALI | {len(righe)} portafogli esaminati, {len(reg)} ricevono gettoni\n")
    if reg:
        print(f"   {'portafoglio':<16}{'gettoni ricevuti':>18}{'speso':>9}{'incassato':>12}{'guadagno':>11}")
        print('   ' + '-' * 68)
        for x in sorted(reg, key=lambda y: -(y["incassato"] - y["speso"]))[:10]:
            print(f"   {x['w'][:14]:<16}{x['n_reg']:>18}{x['speso']:>9.3f}{x['incassato']:>12.2f}"
                  f"{x['incassato']-x['speso']:>+11.2f}")
        print('   ' + '-' * 68)
        g = [x["incassato"] - x["speso"] for x in reg]
        print(f"\n   guadagno mediano di chi riceve: {statistics.median(g):+.2f} SOL "
              f"= {statistics.median(g)*180:+,.0f} EUR")
        print(f"   in utile: {sum(1 for x in g if x>0)}/{len(g)}")
        print(f"   capitale speso mediano: {statistics.median([x['speso'] for x in reg]):.3f} SOL")
    print(f"\n   chiamate usate: {chiam}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
