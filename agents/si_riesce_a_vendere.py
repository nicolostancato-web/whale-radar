"""La garanzia scomoda si riesce a vendere, e a che sconto?

E' la prova che decide la fetta scoperta. Se sUSDe si muove solo a -8%,
il premio del 5% sparisce e i professionisti la evitano per un'ottima
ragione — non per distrazione.

Preventivi da CoW Protocol: gratis, senza chiave, e sono gli stessi prezzi
che otterrebbe chi vende davvero.
"""
import json, urllib.request, time
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
EUR=1/1.08
USDC="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
WETH="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
PROVE=[("sUSDe","0x9d39a5de30e57443bff2a8307a4256c8797a3497",18,USDC,6),
       ("rsETH","0xa1290d69c65a6fe4df752f95823fae25cb99e5a7",18,WETH,18),
       ("wstETH","0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",18,WETH,18),
       ("WETH",WETH,18,USDC,6)]
CHI="0x0000000000000000000000000000000000000001"
def preventivo(vend, dec_v, comp, dec_c, quanti):
    corpo=json.dumps({
      "sellToken":vend,"buyToken":comp,"from":CHI,"receiver":CHI,
      "sellAmountBeforeFee":str(int(quanti*10**dec_v)),
      "kind":"sell","partiallyFillable":False,
      "validTo":int(time.time())+1200,
      "appData":"0x0000000000000000000000000000000000000000000000000000000000000000",
      "signingScheme":"eip712","onchainOrder":False}).encode()
    r=urllib.request.Request("https://api.cow.fi/mainnet/api/v1/quote", data=corpo,
        headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        d=json.load(urllib.request.urlopen(r, timeout=40))
    except urllib.error.HTTPError as e:
        try: return None, json.load(e)["errorType"]
        except Exception: return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)[:40]
    q=d.get("quote",{})
    return (int(q["buyAmount"])/10**dec_c, int(q.get("feeAmount",0))/10**dec_v)
for nome, ind, dec, comp, decc in PROVE:
    pv=PR.get(ind,{}).get("prezzo_usd"); pc=PR.get(comp,{}).get("prezzo_usd")
    if not pv or not pc: print(f"   {nome}: prezzo oracolo mancante"); continue
    print(f"\n   {nome} -> {'USDC' if comp==USDC else 'WETH'}   "
          f"(oracolo: {pv:,.2f} USD)")
    for eur in (1000, 10000, 50000, 200000):
        q = eur/EUR/pv
        r, erro = (preventivo(ind, dec, comp, decc, q) + (None,))[:2] \
                  if isinstance(preventivo(ind, dec, comp, decc, q), tuple) else (None,None)
        res = preventivo(ind, dec, comp, decc, q)
        if res[0] is None:
            print(f"      {eur:>7,}€  preventivo rifiutato: {res[1]}")
        else:
            ott, fee = res
            val_ott = ott*pc*EUR
            print(f"      {eur:>7,}€  ricavo {val_ott:>10,.0f}€  "
                  f"sconto {(1-val_ott/eur)*100:>6.2f}%")
        time.sleep(1.0)
