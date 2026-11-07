# -*- coding: utf-8 -*-
"""LA MATRICE: ogni fascia di premio, cosa dicono i dati e cosa possiamo noi.

Due colonne tenute SEPARATE a proposito:
  - «chi vince oggi»: misurato sugli ALTRI (quanta parte di quella fascia va
    a liquidatori comparsi una volta sola in 88 giorni). Non cambia perche'
    noi siamo migliorati: parla di loro.
  - «cosa possiamo noi»: fatti misurati sulle NOSTRE caratteristiche.
Tenerle separate e' il punto. Alzare la prima perche' e' migliorata la
seconda sarebbe spostare un'opinione e chiamarla misura -- l'ho già fatto
tre volte in questo progetto e tre volte ho dovuto ritirarlo.

La terza colonna, il verdetto, dice a voce alta cosa e' misurato e cosa no.
"""
import json, sys
from collections import defaultdict
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
PR=L("prezzi_oracolo",{}); S=L("novanta_giorni",{})
ev=list(S.get("eventi",{}).values())
bl=[e["blocco"] for e in ev]; GG=(max(bl)-min(bl))*12/86400
r=[]
for e in ev:
    p=PR.get(e["debito"].lower())
    if not p: continue
    x=e["dati"][2:]
    if len(x)<64*3: continue
    r.append({"premio":int(x[0:64],16)/10**p["decimali"]*p["prezzo_usd"]*0.07,
      "ug":fam(e["garanzia"])==fam(e["debito"]),"chi":"0x"+x[128+24:192]})
volte=defaultdict(int)
for x in r: volte[x["chi"]]+=1
SC=[(50_000,10**9,"oltre 50.000"),(15_000,50_000,"15.000 - 50.000"),
    (3_000,15_000,"3.000 - 15.000"),(300,3_000,"300 - 3.000"),(5,300,"sotto 300")]
corta=L("lista_corta"); co=L("composizione",{}); T=L("tetti",{})
VP=L("vendite_pronte",{})
sal={x["indirizzo"].lower():x for x in corta}
nostre=defaultdict(lambda:[0,0])   # [quante, quante con vendita pronta]
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
        if lo<=pr<hi:
            nostre[(et,ug)][0]+=1
            vv=VP.get(u) or VP.get(u.lower())
            if vv and vv.get("chiamata"): nostre[(et,ug)][1]+=1
            break
eur=lambda n: f"{n:,.0f}".replace(",",".")
print("| premio | coppia | ne cadono al mese | premio tipico | nostre in attesa | pronte a sparare | chi vince oggi | la nostra possibilita' |")
print("|---|---|---|---|---|---|---|---|")
for lo,hi,et in SC:
    for ug,nome in ((False,"diversa"),(True,"UGUALE")):
        g=[x for x in r if lo<=x["premio"]<hi and x["ug"]==ug]
        n_nostre,n_pronte=nostre.get((et,ug),[0,0])
        if not g:
            print(f"| {et} | {nome} | **mai vista in {GG:.0f} giorni** | — | "
                  f"{n_nostre} | {n_pronte} | — | non dicibile |")
            continue
        al_mese=len(g)*30/GG
        med=sorted(x["premio"] for x in g)[len(g)//2]
        nuovi=sum(x["premio"] for x in g if volte[x["chi"]]==1)
        quota=100*nuovi/sum(x["premio"] for x in g)
        qm=(f"**{al_mese:.1f} al mese**" if al_mese>=1
            else f"**una ogni {30/al_mese:.0f} giorni**")
        if len(g)<3: chi="troppo pochi casi"
        elif quota>=20: chi=f"ai nuovi il {quota:.0f}%"
        else: chi=f"**ai soliti** (nuovi {quota:.0f}%)"
        # ORDINE DEI CONTROLLI: prima «quanti casi», poi la quota. DIFETTO
        # appena corretto: sulla fascia con DUE soli casi il codice cadeva
        # sul ramo della quota e concludeva «si apre ai nuovi». Con due casi
        # non si conclude niente, e una quota calcolata su due casi non e'
        # una quota. Stessa famiglia di feedback_recap_a_frequenze.
        if n_pronte==0:   poss="non siamo in gara: nessuna pronta"
        elif len(g)<3:    poss="in gara, ma i casi sono troppo pochi per dire"
        elif quota>=20:   poss="**in gara, e la fascia si apre ai nuovi**"
        else:             poss="in gara, ma qui finora hanno vinto solo i soliti"
        print(f"| {et} | {nome} | {qm} | EUR {eur(med)} | {n_nostre} | "
              f"**{n_pronte}** | {chi} | {poss} |")
print()
tp=sum(v[0] for v in nostre.values()); tpr=sum(v[1] for v in nostre.values())
print(f"TOTALE: {tp} posizioni armate, {tpr} con la vendita GIA' PRONTA "
      f"(sparabili in 438 ms)")
print(f"Mercato: {len(r)} liquidazioni in {GG:.0f} giorni = {len(r)*30/GG:.0f} al mese")
