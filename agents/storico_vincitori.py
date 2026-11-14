# -*- coding: utf-8 -*-
"""LO STORICO DEI VINCITORI: chi vince, quanto spesso, e quanto si prende.

Perche' esiste (4/11, su domanda di Nicolo'). Il tabellone guarda il VIVO,
ultime sei ore. Ma il vivo non puo' dire una cosa che decide la strategia:
**se i vincitori sono sempre gli stessi.** Con due campioni avevo concluso
"sono gente di passaggio"; con trenta giorni la risposta e' l'opposto.

MISURATO su 30 giorni (212 liquidazioni, $822.330 di premio, $27.400 al giorno):
  - 50 vincitori distinti, ma 35 vincono PIU' DI UNA VOLTA e si prendono
    il 99,8% del premio -> e' un mestiere di professionisti, non di passanti
  - i primi TRE si prendono il 78,5%
  - il primo (0xeef1b06e..., lo stesso che ci ha portato via i $302.094)
    ha vinto 8 volte per $309.769, il 37,7% di tutto
  - premio MEDIANO per liquidazione: $85
  - solo 25 su 177 valgono piu' di $1.000; solo NOVE piu' di $10.000

CONSEGUENZA SULLA STRATEGIA: la maggior parte delle liquidazioni non vale
niente. I soldi stanno in nove eventi al mese -- uno ogni tre giorni -- e
quelli sono il terreno dei tre professionisti. La prima bolla piccola
(sotto i mille) e' terreno molto meno contestato; le grosse vanno vinte
contro chi fa questo di mestiere.

LEZIONE SUL METODO: con due campioni si vede quello che si vuole. Prima di
trarre una conclusione sul MERCATO serve lo storico, non la cronaca.
"""
import json, os, sys, time, collections, statistics
sys.path.insert(0, "agents")
from keccak import firma
import vendita_curve as VC
D = "data/liquidazioni"
FUORI = f"{D}/storico_vincitori.json"
POOL = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
EV = firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
PASSO = 40000
GIORNI = int(os.environ.get("GIORNI", "30"))
def main():
    PR = json.load(open(f"{D}/prezzi_oracolo.json"))
    testa = VC._rpc("eth_blockNumber", [])
    if not testa: print("   la catena non risponde"); return 1
    t = int(testa, 16)
    finestre = int(GIORNI*7200/PASSO)+1
    liq = []
    for i in range(finestre):
        a, b = t-(i+1)*PASSO, t-i*PASSO
        log = VC._rpc("eth_getLogs", [{"address": POOL, "topics": [EV],
               "fromBlock": hex(a), "toBlock": hex(b)}])
        if log: liq.extend(log)
    righe = []
    for l in liq:
        tp = l.get("topics") or []; d = l.get("data", "0x")[2:]
        if len(tp) < 4 or len(d) < 192: continue
        gar = ("0x"+tp[1][-40:]).lower(); deb = ("0x"+tp[2][-40:]).lower()
        pd, pg = PR.get(deb), PR.get(gar)
        if not pd or not pg: continue
        du = int(d[0:64],16)/10**pd["decimali"]*pd["prezzo_usd"]
        gu = int(d[64:128],16)/10**pg["decimali"]*pg["prezzo_usd"]
        righe.append({"chi": ("0x"+d[128:192][-40:]).lower(),
                      "premio": gu-du, "debito": du})
    if len(righe) < 20:
        print(f"   solo {len(righe)} liquidazioni valutate: non sovrascrivo"); return 1
    tot = sum(r["premio"] for r in righe)
    quante = collections.Counter(); presi = collections.Counter()
    for r in righe: quante[r["chi"]] += 1; presi[r["chi"]] += r["premio"]
    rip = [x for x, n in quante.items() if n > 1]
    pr = [r["premio"] for r in righe if r["premio"] > 0]
    top3 = sum(v for _, v in presi.most_common(3))
    out = {"quando": time.time(), "giorni": GIORNI,
           "liquidazioni": len(righe), "premio_totale": round(tot, 2),
           "premio_al_giorno": round(tot/GIORNI, 2),
           "vincitori_distinti": len(quante),
           "vincitori_ripetuti": len(rip),
           "quota_dei_ripetuti": round(100*sum(presi[x] for x in rip)/tot, 1),
           "quota_dei_primi_tre": round(100*top3/tot, 1),
           "premio_mediano": round(statistics.median(pr), 2),
           "premio_massimo": round(max(pr), 2),
           "sopra_mille": sum(1 for x in pr if x > 1000),
           "sopra_diecimila": sum(1 for x in pr if x > 10000),
           "classifica": [{"chi": k, "quante": quante[k], "premio": round(presi[k], 2),
                           "quota": round(100*presi[k]/tot, 1)}
                          for k, _ in presi.most_common(12)]}
    json.dump(out, open(FUORI, "w"), indent=2)
    print(f"   {GIORNI} giorni: {len(righe)} liquidazioni, ${tot:,.0f} di premio "
          f"(${tot/GIORNI:,.0f} al giorno)")
    print(f"   {len(quante)} vincitori, di cui {len(rip)} ripetuti: si prendono "
          f"il {out['quota_dei_ripetuti']}%")
    print(f"   i primi tre: il {out['quota_dei_primi_tre']}%")
    print(f"   premio mediano ${out['premio_mediano']:,.0f} | sopra $1.000: "
          f"{out['sopra_mille']} | sopra $10.000: {out['sopra_diecimila']}")
    return 0
if __name__ == "__main__":
    sys.exit(main())
