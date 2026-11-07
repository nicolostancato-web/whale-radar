# -*- coding: utf-8 -*-
"""Prova la ROTTA DI VENDITA di ogni gettone candidato, alla taglia vera.
Un gettone entra nell'elenco ammessi solo se: (a) l'aggregatore da' una
rotta, (b) i dollari che torna sono >= 97% di quelli dell'oracolo, (c)
l'importo si trova UNA volta sola nella calldata (altrimenti il contratto
scriverebbe il numero nel campo sbagliato).
Si smette al primo rifiuto per troppe richieste: la fonte non si brucia.
"""
import json, sys, time
sys.path.insert(0, "agents")
from pescatore import preventivo, trova_posizione
PR = json.load(open("data/liquidazioni/prezzi_oracolo.json"))
T  = json.load(open("data/liquidazioni/tetti.json"))
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
CAND = {"0xa1290d69c65a6fe4df752f95823fae25cb99e5a7":"rsETH",
        "0xf1c9acdc66974dfb6decb12aa385b9cd01190e38":"osETH",
        "0x4c9edd5852cd905f086c759e8383e09bff1e68b3":"USDe",
        "0x356b8d89c1e1239cbbb9de4815c39a1474d5ba7d":"syrupUSDT",
        "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"cbBTC",
        "0xbe9895146f7af43049ca1c1ae358b0541ea49704":"cbETH",
        "0xae78736cd615f374d3085123a210448e74fc6393":"rETH",
        "0x8236a87084f8b84306f72007f36f2618a5634494":"LBTC",
        "0x18084fba666a33d37592fa2633fd49a74dd93a88":"tBTC",
        "0x68749665ff8d2d112fa859aa293f07a622782f38":"XAUt"}
TAGLIA = 100_000.0
esiti = {}
print(f"{'gettone':10s} {'verso':6s} {'venduto':>12s} {'tornato':>12s} "
      f"{'reso':>7s}  esito")
for a, nome in CAND.items():
    p = PR.get(a)
    if not p:
        print(f"{nome:10s} {'-':6s} {'':>12s} {'':>12s} {'':>7s}  nessun prezzo")
        continue
    q = int(TAGLIA / p["prezzo_usd"] * 10**p["decimali"])
    buono = None
    for dst, dn, dd in ((USDC,"USDC",6), (WETH,"WETH",18)):
        if dst == a: continue
        sede, dati, pos, _app = preventivo(a, dst, q, p["decimali"], dd)
        if not sede:
            if "429" in str(dati) or "Too Many" in str(dati):
                print("   la fonte dice troppe richieste: mi fermo qui")
                json.dump(esiti, open("data/liquidazioni/rotte_candidati.json","w"), indent=1)
                sys.exit(0)
            print(f"{nome:10s} {dn:6s} {'':>12s} {'':>12s} {'':>7s}  "
                  f"nessuna rotta: {str(dati)[:40]}")
            time.sleep(1.5); continue
        # quanto torna, in dollari, secondo la rotta stessa
        import urllib.request
        r = urllib.request.Request(
            f"https://api.paraswap.io/prices?srcToken={a}&destToken={dst}"
            f"&amount={q}&srcDecimals={p['decimali']}&destDecimals={dd}"
            f"&side=SELL&network=1",
            headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
        pr = json.load(urllib.request.urlopen(r, timeout=12))["priceRoute"]
        out = int(pr["destAmount"]) / 10**dd
        pd_ = PR.get(dst, {}).get("prezzo_usd", 1.0)
        dollari = out * pd_
        reso = dollari / TAGLIA
        ok = reso >= 0.97
        print(f"{nome:10s} {dn:6s} {TAGLIA:12,.0f} {dollari:12,.0f} "
              f"{100*reso:6.2f}%  {'OK' if ok else 'PERDE TROPPO'} "
              f"(importo a offset {pos})")
        if ok and (buono is None or reso > buono[1]):
            buono = (dn, reso, pos)
        time.sleep(1.5)
    esiti[a] = {"nome":nome, "migliore":buono[0] if buono else None,
                "reso":round(buono[1],4) if buono else None,
                "ammissibile":bool(buono)}
json.dump(esiti, open("data/liquidazioni/rotte_candidati.json","w"), indent=1)
ok = [v["nome"] for v in esiti.values() if v["ammissibile"]]
no = [v["nome"] for v in esiti.values() if not v["ammissibile"]]
print(f"\nammissibili ({len(ok)}): {', '.join(ok)}")
print(f"da escludere ({len(no)}): {', '.join(no)}")
