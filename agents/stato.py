# -*- coding: utf-8 -*-
"""Lo STATO in una tabella sola, per il recap a ogni giro.

Chiesto da Nicolo' l'1/11: «ogni volta che vai avanti mi metti una tabella,
status, perche' devo un attimo capire». Generato, non scritto a mano: una
tabella compilata a mano invecchia e mente.
"""
import json, os, sys, time
sys.path.insert(0,"agents")
from pescatore import AMMESSI
D="data/liquidazioni"
def L(f, d=None):
    try: return json.load(open(f"{D}/{f}.json"))
    except Exception: return d if d is not None else []
FAM={"0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"ETH","0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":"ETH",
"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"ETH","0xae78736cd615f374d3085123a210448e74fc6393":"ETH",
"0xf1c9acdc66974dfb6decb12aa385b9cd01190e38":"ETH","0xbe9895146f7af43049ca1c1ae358b0541ea49704":"ETH",
"0xa35b1b31ce002fbf2058d22f30f95d405200a15b":"ETH","0xd9a442856c234a39a81a089c06451ebaa4306a72":"ETH",
"0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"BTC","0x8236a87084f8b84306f72007f36f2618a5634494":"BTC",
"0x18084fba666a33d37592fa2633fd49a74dd93a88":"BTC","0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"BTC"}
fam=lambda a: FAM.get((a or "").lower(),"USD")
NOMI={"0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"wstETH","0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":"weETH",
"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"WETH","0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"WBTC",
"0x9d39a5de30e57443bff2a8307a4256c8797a3497":"sUSDe","0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":"USDC",
"0xdac17f958d2ee523a2206206994597c13d831ec7":"USDT","0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f":"GHO",
"0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9":"AAVE","0x514910771af9ca656af840dff83e8264ecf986ca":"LINK",
"0xc139190f447e929f090edeb554d95abb8b18ac1c":"USDtb","0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"cbBTC",
"0xf1c9acdc66974dfb6decb12aa385b9cd01190e38":"ETHx","0x4c9edd5852cd905f086c759e8383e09bff1e68b3":"USDe"}
nm=lambda a: NOMI.get((a or "").lower(), (a or "?")[:8])
deb=L("debitori"); fin=L("finestre_debitori_v3"); corta=L("lista_corta")
co=L("composizione",{}); viv=L("pescatore_vivo",{}); T=L("tetti",{})
g1=L("guardia_in_acqua",{}); g2=L("guardia_quaderno",{})
freq=L("ogni_quanto",{})
arm={k:v for k,v in co.items() if v["garanzia_principale"].lower() in AMMESSI}
ug=sum(1 for v in arm.values() if fam(v["garanzia_principale"])==fam(v["debito_principale"]))
sal={x["indirizzo"].lower():x for x in corta}
occ=[]
for u,v in arm.items():
    s=sal.get(u.lower())
    if not s: continue
    gg=v["garanzia_principale"].lower()
    dus=s["debito"]*0.5; tet=T.get(gg,100_000)
    if dus*1.07>tet: dus=tet/1.07
    occ.append({"salute":s["salute"],"gar":nm(gg),"deb":nm(v["debito_principale"]),
      "uguale":fam(gg)==fam(v["debito_principale"]),"premio":dus*0.07,
      "calo":(1-1/s["salute"])*100 if s["salute"]>0 else 0})
occ.sort(key=lambda x:x["salute"])
dv=[o for o in occ if not o["uguale"]]
def fresco(nome):
    """Quanti secondi fa e' stato scritto. Si usa l'ORA DEL FILE, non la
    stringa dentro: la prima versione faceva la conversione a mano col fuso
    e dava «7209 secondi» per un battito di 45 secondi. Un orario scritto
    come testo va riconvertito, e la riconversione e' un posto dove si
    sbaglia; l'ora del file non ha fuso da indovinare."""
    try: return int(time.time()-os.path.getmtime(f"{D}/{nome}.json"))
    except Exception: return None
eta=fresco("guardia_in_acqua"); eta2=fresco("guardia_quaderno")
etap=fresco("pescatore_vivo")
eur=lambda n: f"{n:,.0f}".replace(",",".")
print("| | |")
print("|---|---|")
print(f"| **Presa** | {'*** AVVENUTA ***' if os.path.exists(f'{D}/preso.flag') else 'nessuna'} |")
print(f"| **Armato** | {'si' if viv.get('armato') else 'NO'}, **{len(arm)} posizioni** "
      f"({ug} coppia uguale, {len(arm)-ug} diversa) |")
print(f"| **Reazione** | giro da {viv.get('minuti',0)*60/max(1,viv.get('giri',1)):.1f}s "
      f"| {viv.get('vicine','?')} vicine a ogni giro |")
print(f"| **Occhio** | vede {viv.get('viste','?')}, **{viv.get('mute','?')} mute** |")
print(f"| **Laghetto** | {eur(len(deb))} debitori -> {len(corta)} a rischio -> "
      f"{len(co)} composte -> **{len(arm)} armate** |")
print(f"| **Storia letta** | {len(fin)}/202 finestre (**{100*len(fin)/202:.0f}%** di Aave v3) |")
print(f"| **Guardie** | in_acqua: {g1.get('stato','?')} ({eta}s fa) | "
      f"quaderno: {g2.get('stato','?')} ({eta2}s fa) |")
print(f"| **Battito pescatore** | {etap}s fa "
      f"{'(FERMO: oltre 240s)' if (etap or 0)>240 else ''}|")
print(f"| **Piu' malata** | **{viv.get('piu_malata','?')}** |")
print(f"| **Sotto 1,01** | {sum(1 for o in occ if o['salute']<1.01)} posizioni, "
      f"di cui {sum(1 for o in dv if o['salute']<1.01)} a coppia diversa |")
print(f"| **Premio in stalla** | EUR {eur(sum(o['premio'] for o in occ))} se cadessero tutte |")
if freq:
    print(f"| **Ritmo misurato** | una oltre EUR 100k ogni {freq['frequenza'][-1][2]:.0f} giorni, "
          f"{freq['sopra_minimo_al_giorno']}/giorno sopra il minimo |")
print("\nLE 6 PIU' VICINE A COPPIA DIVERSA (quelle che cadono davvero):")
print("| salute | calo | coppia | premio |")
print("|---|---|---|---|")
for o in dv[:6]:
    print(f"| {o['salute']:.4f} | {o['calo']:.2f}% | {o['gar']}/{o['deb']} | EUR {eur(o['premio'])} |")
