# -*- coding: utf-8 -*-
"""Quanto se ne vende DAVVERO, per ogni garanzia, prima che lo scivolamento
si mangi il premio.

Il premio e' il 7,00%. Si fissa il tetto dove lo scivolamento arriva
all'1,0%: resta un margine abbondante per gas e imprevisti.

Perche' esiste questo script (31/10): i tetti erano SCRITTI A MANO e
coprivano 6 asset. Poi la misura sulle liquidazioni vere ha detto che il
60% cade su garanzia WETH e il 28% su USDT -- due asset che non erano
nella lista, cioe' eravamo ciechi sul 88% del mercato. Un numero scritto
a mano non si accorge di quello che non contiene.

DIFETTO del primo tentativo, corretto subito: confrontavo la quota LIVE di
Paraswap contro il prezzo dell'oracolo Aave letto ORE PRIMA. Venivano fuori
scivolamenti NEGATIVI (-3,24% su USDC, -1,52% su LINK) e un assurdo 3,99%
su WBTC a 20 mila dollari. Uno scivolamento negativo non esiste: quella era
la DERIVA del mio riferimento, non il costo di vendere.
Ora il metro e' INTERNO: si chiede la stessa quota a una taglia piccola e a
una grande, dalla stessa fonte nello stesso momento, e lo scivolamento e'
quanto peggiora il cambio fra le due. Immune ai prezzi vecchi.

Paraswap /prices e' gratuito e senza chiave: costo di questa misura = 0.
"""
import json, sys, time, urllib.request, urllib.parse
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
USDC="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
WETH="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
CANDIDATI={   # garanzia -> verso cosa si vende per ripagare il debito tipico
 "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":("WETH", USDC),
 "0xdac17f958d2ee523a2206206994597c13d831ec7":("USDT", USDC),
 "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":("USDC", WETH),
 "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":("wstETH", WETH),
 "0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":("weETH", WETH),
 "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":("WBTC", USDC),
 "0x514910771af9ca656af840dff83e8264ecf986ca":("LINK", USDC),
 "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9":("AAVE", USDC),
 "0x9d39a5de30e57443bff2a8307a4256c8797a3497":("sUSDe", USDC),
}
BASE=5_000        # la taglia "piccola": il cambio di riferimento
TAGLIE=[20_000, 100_000, 500_000, 2_000_000, 8_000_000]
LIMITE=1.0        # per cento di peggioramento ammesso rispetto alla piccola
def quota(da, a, grezzo):
    q=urllib.parse.urlencode({"srcToken":da,"destToken":a,"amount":str(grezzo),
      "srcDecimals":PR[da]["decimali"],"destDecimals":PR[a]["decimali"],
      "side":"SELL","network":"1"})
    try:
        r=urllib.request.Request("https://api.paraswap.io/prices?"+q,
          headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
        d=json.load(urllib.request.urlopen(r,timeout=30))
        p=d.get("priceRoute")
        if not p: return None
        dato=int(p["destAmount"])/10**PR[a]["decimali"]
        dentro=int(p["srcAmount"])/10**PR[da]["decimali"]
        sede=(p.get("bestRoute",[{}])[0].get("swaps",[{}])[0]
               .get("swapExchanges",[{}])[0].get("exchange","?"))
        return dato/dentro, sede        # cambio per unita' di garanzia
    except Exception:
        return None
try: tetti=json.load(open("data/liquidazioni/tetti.json"))
except Exception: tetti={}
nuovi={}
for gar,(nome,verso) in CANDIDATI.items():
    pg=PR.get(gar); pv=PR.get(verso)
    if not pg or not pv: print(f"   {nome}: prezzo mancante, salto"); continue
    # il cambio di riferimento, su una taglia piccola
    gb=int(BASE/pg["prezzo_usd"]*10**pg["decimali"])
    rb=quota(gar,verso,gb)
    if not rb:
        print(f"\n   {nome}: nessuna quota nemmeno a ${BASE:,} -> ESCLUSO"); continue
    cambio0, sede0 = rb
    print(f"\n   {nome} -> cambio di riferimento a ${BASE:,}: "
          f"{cambio0:.8g} via {sede0}")
    tetto=None
    for usd in TAGLIE:
        grezzo=int(usd/pg["prezzo_usd"]*10**pg["decimali"])
        r=quota(gar,verso,grezzo)
        if not r:
            print(f"     ${usd:>10,}  nessuna quota -> fermo qui"); break
        cambio, sede = r
        sciv=(1-cambio/cambio0)*100
        ok = sciv<=LIMITE
        print(f"     ${usd:>10,}  peggiora {sciv:>6.2f}%  {'ok' if ok else 'TROPPO'}"
              f"   via {sede}")
        if ok: tetto=usd
        else: break
        time.sleep(0.8)
    if tetto:
        nuovi[gar]=tetto
        vecchio=tetti.get(gar)
        segno = "" if vecchio==tetto else f"  (era {vecchio if vecchio else 'ASSENTE'})"
        print(f"     TETTO {nome}: ${tetto:,}{segno}")
    else:
        print(f"     {nome}: non regge ${TAGLIE[0]:,} -> ESCLUSO")
json.dump(nuovi, open("data/liquidazioni/tetti_misurati.json","w"), indent=1)
print(f"\n   {len(nuovi)} tetti misurati in data/liquidazioni/tetti_misurati.json")
print(f"   (NON sovrascrivo tetti.json: lo fa un passo esplicito dopo il controllo)")
