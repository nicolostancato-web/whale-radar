"""Quanto e' stato pagato al validatore per quel blocco.

I relay di MEV pubblicano gratis il valore consegnato al proponente di ogni
blocco. Se nel blocco della liquidazione grossa il pagamento e' dell'ordine
del premio, il premio e' stato ribattuto via nella gara; se e' spiccioli,
resta al liquidatore.

Limite dichiarato: e' il valore dell'INTERO blocco, non solo della nostra
transazione. Vale come TETTO.
"""
import json, urllib.request, time
RELAY=["https://boost-relay.flashbots.net","https://bloxroute.max-profit.blxrbdn.com",
       "https://relay.ultrasound.money","https://agnostic-relay.net"]
def spot(s):
    r=urllib.request.Request(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={s}",
                             headers={"user-agent":"Mozilla/5.0"})
    return float(json.load(urllib.request.urlopen(r,timeout=20))["price"])
eth=spot("ETHUSDT"); EUR=1/1.08
BLOCCHI={26279102:"liquidazione 2.515 EUR", 26286758:"liquidazione 12.297 EUR"}
for bn,etichetta in BLOCCHI.items():
    trovato=False
    for base in RELAY:
        u=f"{base}/relay/v1/data/bidtraces/proposer_payload_delivered?block_number={bn}"
        try:
            r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r, timeout=25))
        except Exception:
            continue
        if not d: continue
        v=int(d[0]["value"])/1e18
        print(f"   blocco {bn} ({etichetta})")
        print(f"      pagato al validatore: {v:.5f} ETH = {v*eth*EUR:,.2f} EUR")
        print(f"      costruttore: {d[0].get('builder_pubkey','?')[:22]}...")
        trovato=True
        break
    if not trovato:
        print(f"   blocco {bn}: nessun relay espone questo blocco "
              f"(puo' essere un blocco costruito localmente dal validatore)")
    time.sleep(0.3)
print(f"\n   confronto: premio stimato al 5% = 125 EUR e 615 EUR")
