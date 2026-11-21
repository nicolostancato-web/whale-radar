# -*- coding: utf-8 -*-
"""CHI POTREBBE ESSERE LA PRIMA BOLLA: le candidate piu' vicine, pronte a
sparare, ordinate per quanto manca alla caduta.

Chiesto da Nicolo' (1/11): «una matrix dove vedo quello che pende in bolla,
le 4-5 piu' allettanti».

COSA ENTRA E PERCHE':
  - solo quelle con la vendita GIA' PRONTA: su una senza vendita il pacchetto
    non si compone in tempo, quindi non e' una candidata, e' un'illusione;
  - prima le COPPIE DIVERSE: cadono l'11,2% in 9 giorni contro lo 0,7% delle
    uguali, perche' su una coppia uguale garanzia e debito si muovono insieme;
  - ordinate per CALO NECESSARIO, non per premio: la prima bolla la fa quella
    che cade, non quella che vale piu'.
Le bombe a coppia uguale si mostrano a parte: premio enorme, caduta rara.
"""
import json, sys, time
sys.path.insert(0,"agents")
from pescatore import AMMESSI
D="data/liquidazioni"
def L(f,d=None):
    try: return json.load(open(f"{D}/{f}.json"))
    except Exception: return d if d is not None else []
FAM={"0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"ETH","0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":"ETH",
"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"ETH","0xae78736cd615f374d3085123a210448e74fc6393":"ETH",
"0xf1c9acdc66974dfb6decb12aa385b9cd01190e38":"ETH","0xbe9895146f7af43049ca1c1ae358b0541ea49704":"ETH",
"0xa35b1b31ce002fbf2058d22f30f95d405200a15b":"ETH","0xd9a442856c234a39a81a089c06451ebaa4306a72":"ETH",
"0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"BTC","0x8236a87084f8b84306f72007f36f2618a5634494":"BTC",
"0x18084fba666a33d37592fa2633fd49a74dd93a88":"BTC","0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"BTC"}
NOMI={"0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"wstETH","0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":"weETH",
"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"WETH","0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"WBTC",
"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":"USDC","0xdac17f958d2ee523a2206206994597c13d831ec7":"USDT",
"0x9d39a5de30e57443bff2a8307a4256c8797a3497":"sUSDe","0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f":"GHO",
"0xc139190f447e929f090edeb554d95abb8b18ac1c":"USDtb","0x4c9edd5852cd905f086c759e8383e09bff1e68b3":"USDe",
"0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"cbBTC","0xf1c9acdc66974dfb6decb12aa385b9cd01190e38":"ETHx",
"0x6c3ea9036406852006290770bedfcaba0e23a0e8":"PYUSD","0x6b175474e89094c44da98b954eedeac495271d0f":"DAI",
"0xdc035d45d973e3ec169d2276ddab16f1e407384f":"USDS","0x83f20f44975d03b1b09e64809b757c47f942beea":"sDAI"}
fam=lambda a: FAM.get((a or "").lower(),"USD")
nm=lambda a: NOMI.get((a or "").lower(),(a or "?")[:8])
co=L("composizione",{}); VP=L("vendite_pronte",{}); T=L("tetti",{})
corta={x["indirizzo"].lower():x for x in L("lista_corta")}
righe=[]
for u,v in co.items():
    g=v["garanzia_principale"].lower(); d=v["debito_principale"]
    if g not in AMMESSI: continue
    vv=VP.get(u) or VP.get(u.lower()) or {}
    pronta=bool(vv.get("chiamata") or vv.get("stesso"))
    s=corta.get(u.lower())
    if not s: continue
    dus=s["debito"]*0.5; tet=T.get(g,100_000)
    tagliato=dus*1.07>tet
    if tagliato: dus=tet/1.07
    premio=dus*0.07
    if premio<5: continue
    righe.append({"u":u,"salute":s["salute"],
        "calo":(1-1/s["salute"])*100 if s["salute"]>0 else 0,
        "gar":nm(g),"deb":nm(d),"uguale":fam(g)==fam(d),
        "premio":premio,"pronta":pronta,"tagliato":tagliato})
div=[r for r in righe if not r["uguale"] and r["pronta"]]
ug =[r for r in righe if r["uguale"] and r["pronta"]]
div.sort(key=lambda r:r["calo"])
ug.sort(key=lambda r:-r["premio"])
fuori={"quando":int(time.time()),
       "quante_pronte":sum(1 for r in righe if r["pronta"]),
       "quante_armate":len(righe),
       "diverse":div[:8],"bombe":ug[:5]}
json.dump(fuori, open(f"{D}/prima_bolla.json","w"), indent=1)
eur=lambda n: f"{n:,.0f}".replace(",",".")
print(f"   {fuori['quante_pronte']} pronte su {fuori['quante_armate']} armate\n")
print("   LE PIU' VICINE, COPPIA DIVERSA (quelle che cadono davvero):")
print(f"   {'calo':>7} {'salute':>8}  {'coppia':<16} {'premio':>11}")
for r in div[:8]:
    print(f"   {r['calo']:>6.2f}% {r['salute']:>8.4f}  "
          f"{r['gar']+'/'+r['deb']:<16} EUR {eur(r['premio']):>9}"
          + ("  (tetto)" if r["tagliato"] else ""))
print("\n   LE BOMBE A COPPIA UGUALE (premio enorme, caduta rara):")
for r in ug[:5]:
    print(f"   {r['calo']:>6.2f}% {r['salute']:>8.4f}  "
          f"{r['gar']+'/'+r['deb']:<16} EUR {eur(r['premio']):>9}")
