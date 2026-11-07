# -*- coding: utf-8 -*-
"""Ogni quanto cade, AL MESE, e che possibilita' abbiamo di prenderla.

Nicolo' (1/11), e aveva ragione: «in 9 giorni dici zero, ma non e' questo il
fatto. Fammela al mese. Perche' tu hai quel range da 57 giorni che va a
sballare tutto ogni 9 giorni.»
Esatto: su una finestra di 9 giorni un evento che capita ogni 40 non si vede,
e lo zero non significa «non succede» -- significa «finestra troppo corta».
Qui si usano gli 88 GIORNI di liquidazioni vere (568 eventi), e si conta
quante cadono al mese in ogni fascia di premio. Nessun modello: un conteggio.

Poi la seconda domanda, quella che interessa davvero: se cade, la prendiamo?
Non si puo' misurare su di noi -- non abbiamo mai vinto una gara, zero
tentativi. Ma si puo' misurare sugli ALTRI, e una cosa si misura bene:
quanta parte di ogni fascia va a chi compare UNA VOLTA SOLA in 88 giorni.
Se una fascia e' tutta dei soliti tre, un nuovo arrivato non entra. Se metta'
va a gente vista una volta, un nuovo arrivato entra. E' il miglior indizio
disponibile, e si chiama per quello che e': un indizio, non una nostra prova.
"""
import json, sys
from collections import defaultdict
sys.path.insert(0,"agents")
from pescatore import AMMESSI
D="data/liquidazioni"
def L(f,d=None):
    try: return json.load(open(f"{D}/{f}.json"))
    except Exception: return d if d is not None else []
PR=L("prezzi_oracolo",{}); S=L("novanta_giorni",{})
FAM={"0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"ETH","0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":"ETH",
"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"ETH","0xae78736cd615f374d3085123a210448e74fc6393":"ETH",
"0xf1c9acdc66974dfb6decb12aa385b9cd01190e38":"ETH","0xbe9895146f7af43049ca1c1ae358b0541ea49704":"ETH",
"0xa35b1b31ce002fbf2058d22f30f95d405200a15b":"ETH","0xd9a442856c234a39a81a089c06451ebaa4306a72":"ETH",
"0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"BTC","0x8236a87084f8b84306f72007f36f2618a5634494":"BTC",
"0x18084fba666a33d37592fa2633fd49a74dd93a88":"BTC","0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"BTC"}
fam=lambda a: FAM.get((a or "").lower(),"USD")
ev=list(S.get("eventi",{}).values())
bl=[e["blocco"] for e in ev]
GIORNI=(max(bl)-min(bl))*12/86400
r=[]
for e in ev:
    p=PR.get(e["debito"].lower())
    if not p: continue
    x=e["dati"][2:]
    if len(x)<64*3: continue
    r.append({"premio":int(x[0:64],16)/10**p["decimali"]*p["prezzo_usd"]*0.07,
      "ug":fam(e["garanzia"])==fam(e["debito"]),
      "chi":"0x"+x[128+24:192], "armata":e["garanzia"].lower() in AMMESSI})
# quante volte compare ciascun liquidatore in TUTTI gli 88 giorni
volte=defaultdict(int)
for x in r: volte[x["chi"]]+=1
SC=[(50_000,10**9,"oltre 50.000"),(15_000,50_000,"15.000 - 50.000"),
    (3_000,15_000,"3.000 - 15.000"),(300,3_000,"300 - 3.000"),(5,300,"sotto 300")]
# quante NOSTRE posizioni ci sono in ciascuna fascia (per sapere dove stiamo)
corta=L("lista_corta"); co=L("composizione",{}); T=L("tetti",{})
sal={x["indirizzo"].lower():x for x in corta}
nostre=defaultdict(int)
for u,v in co.items():
    g=v["garanzia_principale"].lower()
    if g not in AMMESSI: continue
    s=sal.get(u.lower())
    if not s: continue
    dus=s["debito"]*0.5; tet=T.get(g,100_000)
    if dus*1.07>tet: dus=tet/1.07
    pr=dus*0.07
    if pr<5: continue
    ug=fam(g)==fam(v["debito_principale"])
    for lo,hi,et in SC:
        if lo<=pr<hi: nostre[(et,ug)]+=1; break
def possibilita(quota_nuovi, n):
    """Da «quanta parte va ai nuovi arrivati» a un giudizio in tre livelli."""
    if n<3: return "non dicibile", f"solo {n} casi in 88 giorni"
    if quota_nuovi>=0.45: return "ALTA", f"il {quota_nuovi*100:.0f}% va a chi compare una volta sola"
    if quota_nuovi>=0.20: return "MEDIA", f"il {quota_nuovi*100:.0f}% va a chi compare una volta sola"
    return "BASSA", f"solo il {quota_nuovi*100:.0f}% va ai nuovi: fascia dei soliti"
print(f"MISURATO SU {GIORNI:.0f} GIORNI VERI — {len(r)} liquidazioni\n")
print("| premio | coppia | ne cadono al mese | premio tipico | nostre in attesa | nostra possibilita' | perche' |")
print("|---|---|---|---|---|---|---|")
for lo,hi,et in SC:
    for ug,nome in ((False,"diversa"),(True,"UGUALE")):
        g=[x for x in r if lo<=x["premio"]<hi and x["ug"]==ug]
        if not g:
            print(f"| {et} | {nome} | **nessuna in {GIORNI:.0f} giorni** | — | "
                  f"{nostre.get((et,ug),0)} | — | mai vista cadere |")
            continue
        al_mese=len(g)*30/GIORNI
        med=sorted(x["premio"] for x in g)[len(g)//2]
        soldi_nuovi=sum(x["premio"] for x in g if volte[x["chi"]]==1)
        quota=soldi_nuovi/sum(x["premio"] for x in g)
        liv,perche=possibilita(quota,len(g))
        qm=(f"**{al_mese:.1f} al mese**" if al_mese>=1
            else f"**una ogni {30/al_mese:.0f} giorni**")
        print(f"| {et} | {nome} | {qm} | EUR {med:,.0f} | {nostre.get((et,ug),0)} | "
              f"**{liv}** | {perche} |".replace(",","."))
print(f"\nTotale: {len(r)} liquidazioni in {GIORNI:.0f} giorni = "
      f"{len(r)*30/GIORNI:.0f} al mese.")
uno=[x for x in r if volte[x["chi"]]==1]
print(f"Di tutto il denaro, il {100*sum(x['premio'] for x in uno)/sum(x['premio'] for x in r):.0f}% "
      f"e' andato a liquidatori comparsi UNA VOLTA SOLA in {GIORNI:.0f} giorni "
      f"({len(uno)} prese su {len(r)}).")
