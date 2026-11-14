# -*- coding: utf-8 -*-
"""Il recap come lo vuole Nicolo': NON percentuali, ma «una ogni N giorni».

Sue parole (1/11): «non mi dare la probabilita' percentuale, 0,5 non vuol
dire niente. Vorrei una roba tipo: ne ho 3 grosse da 100.000, coppia uguale,
succede una volta nei tre mesi. Poi X da 15.000 con probabilita' una ogni 7
giorni. A me interessa solo posizione, premio, quanto incassiamo.»

LA CONVERSIONE, che e' il punto:
  una probabilita' per posizione non si puo' leggere da sola, perche' quello
  che conta e' quanto aspetti prima che UNA QUALSIASI del gruppo cada.
  Se n posizioni hanno ciascuna probabilita' p di cadere in 9 giorni, in 9
  giorni ne cadono in media n*p, quindi l'attesa per la prima e':
        giorni = 9 / (n * p)
  E' per questo che 40 posizioni allo 0,7% valgono piu' di 3 al 2,8%: la
  dimensione del gruppo entra nel conto. «0,5%» per posizione e «una ogni
  32 giorni» per il gruppo sono lo stesso numero detto in modo utile.

Le probabilita' sono MISURATE (agents/difendono.py, prima/dopo su 300
posizioni fra il blocco di 9 giorni fa e oggi), divise per taglia perche'
le posizioni grosse sono difese.
"""
import json, sys
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
fam=lambda a: FAM.get((a or "").lower(),"USD")
# LE CADUTE MISURATE, cosi' come sono state CONTATE. Niente riempimenti.
#
# Il mio primo tentativo metteva 0,7% sulle coppie uguali grosse, preso dal
# tasso COMPLESSIVO delle coppie uguali (1 caduta su 148). Ma quell'unica
# caduta era una posizione PICCOLA: estenderla ai colossi da 130.000 dava un
# incasso atteso di 377.300 euro in 30 giorni, cioe' l'85% di TUTTO il premio
# che il mercato Aave paga in un mese. Impossibile -> il numero era mio.
# Un tasso complessivo non si presta alle sottoclassi dove non e' stato
# osservato: e' la stessa cosa di feedback_le_grosse_sono_difese, un giro
# dopo e sullo stesso errore.
#
# Dove le cadute osservate sono ZERO non si da' una frequenza: si dice
# «0 su N». Non e' prudenza, e' quello che dicono i dati.
BANDE=[(0,10_000),(10_000,100_000),(100_000,1_000_000),(1_000_000,10**15)]
CONTATE={                 # (coppia_uguale, banda) -> (cadute, osservate)
 (False,0):(12,43), (False,1):(4,64), (False,2):(1,36), (False,3):(0,9),
 (True, 0):( 1,40), (True, 1):(0,46), (True, 2):(0,30), (True, 3):(0,32),
}
def prob(ug,banda):
    k,n=CONTATE[(ug,banda)]
    return (k/n) if k>0 else None     # None = nessuna caduta osservata
corta=L("lista_corta"); co=L("composizione",{}); T=L("tetti",{})
NOMI={"0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"wstETH","0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":"weETH",
"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"WETH","0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"WBTC",
"0x9d39a5de30e57443bff2a8307a4256c8797a3497":"sUSDe","0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":"USDC",
"0xdac17f958d2ee523a2206206994597c13d831ec7":"USDT","0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f":"GHO",
"0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9":"AAVE","0x514910771af9ca656af840dff83e8264ecf986ca":"LINK",
"0xc139190f447e929f090edeb554d95abb8b18ac1c":"USDtb","0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"cbBTC"}
sal={x["indirizzo"].lower():x for x in corta}
pos=[]
for u,v in co.items():
    g=v["garanzia_principale"].lower()
    if g not in AMMESSI: continue
    s=sal.get(u.lower())
    if not s: continue
    dus=s["debito"]*0.5; tet=T.get(g,100_000)
    if dus*1.07>tet: dus=tet/1.07
    premio=dus*0.07
    if premio<5: continue
    ug=fam(g)==fam(v["debito_principale"])
    banda=next(i for i,(a,b) in enumerate(BANDE) if a<=s["debito"]<b)
    pos.append({"premio":premio,"ug":ug,"p":prob(ug,banda),"banda":banda,
                "salute":s["salute"],
                "gar":NOMI.get(g,g[:8]),"deb":NOMI.get(v["debito_principale"].lower(),"?")})
# raggruppamento per TAGLIA DI PREMIO, che e' l'unica cosa che interessa
SCAGLIONI=[(50_000,10**9,"oltre 50.000"),(15_000,50_000,"15.000 - 50.000"),
           (3_000,15_000,"3.000 - 15.000"),(300,3_000,"300 - 3.000"),
           (5,300,"sotto 300")]
def quando(n_attese_per_9gg):
    """Da «quante ne cadono in 9 giorni» a una frase leggibile."""
    if n_attese_per_9gg<=0: return "mai, per quanto si e' misurato"
    g=9/n_attese_per_9gg
    if g<1.5:  return f"una ogni {g*24:.0f} ore"
    if g<60:   return f"una ogni {g:.0f} giorni"
    if g<700:  return f"una ogni {g/30:.1f} mesi"
    return f"una ogni {g/365:.1f} anni"
print("| premio | quante | coppia | ogni quanto ne cade una | se cade |")
print("|---|---|---|---|---|")
tot_att=0
for lo,hi,et in SCAGLIONI:
    for ug,nome in ((True,"UGUALE"),(False,"diversa")):
        g=[p for p in pos if lo<=p["premio"]<hi and p["ug"]==ug]
        if not g: continue
        med=sorted(p["premio"] for p in g)[len(g)//2]
        noti=[p for p in g if p["p"] is not None]
        if not noti:
            oss=sum(CONTATE[(p["ug"],p["banda"])][1] for p in g)//max(1,len(g))
            n_oss=CONTATE[(g[0]["ug"],g[0]["banda"])][1]
            frase=f"**nessuna caduta vista** (0 su {n_oss} in 9 giorni)"
        else:
            att=sum(p["p"] for p in noti); tot_att+=att
            frase=f"**{quando(att)}**"
            if len(noti)<len(g): frase+=f" (su {len(noti)} delle {len(g)})"
        print(f"| {et} | **{len(g)}** | {nome} | {frase} | "
              f"EUR {med:,.0f} circa |".replace(",","."))
print(f"\nIN TOTALE: {len(pos)} posizioni sorvegliate, "
      f"{quando(tot_att)} fra tutte.")
print(f"Premio se cadessero tutte: EUR {sum(p['premio'] for p in pos):,.0f}".replace(",","."))
# e il valore atteso, che resta il numero per decidere dove guardare
mis=[p for p in pos if p["p"] is not None]
att30=sum(p["premio"]*p["p"]*30/9 for p in mis)
print(f"Incasso atteso in 30 giorni, contando SOLO le {len(mis)} posizioni dove"
      f" una caduta e' stata vista: EUR {att30:,.0f}".replace(",","."))
try:
    m=L("ogni_quanto",{})
    mercato=m["al_giorno"]*30
    print(f"Controllo: tutto il mercato Aave paga EUR {mercato:,.0f} al mese -> "
          f"il nostro atteso e' il {100*att30/mercato:.0f}%".replace(",","."))
except Exception: pass
print(f"Le altre {len(pos)-len(mis)} posizioni (premio EUR "
      f"{sum(p['premio'] for p in pos if p['p'] is None):,.0f}) non hanno una "
      f"frequenza: nessuna delle loro simili e' caduta nella finestra misurata."
      .replace(",","."))
