"""La classifica contata per ATTORE, non per contratto.

Un attore puo' usare piu' contratti usa-e-getta: 77 indirizzi liquidatori
corrispondono a 45 creatori distinti. Contare i contratti gonfiava il numero
di «occasionali» di 1,56 volte. Stessa famiglia di «le righe non sono i casi».

Dove il creatore non e' noto, il contratto resta se stesso: non si fonde
con altri per comodita'.
"""
import json, collections
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
CRE=json.load(open("data/liquidazioni/creatori.json"))
FABBRICHE={"0x4e59b44847b379578588920ca78fbf26c0b4956c",
           "0x0000000000ffe8b47b3e2130213b802212439497",
           "0x7a0d94f55792c434d74a40883c6ed8545e406d12"}
EUR=1/1.08
def attore(a):
    v=CRE.get(a,{})
    c=v.get("creatore")
    # senza creatore noto, o creato da una fabbrica condivisa, il contratto
    # vale come attore a se': mai fondere estranei per comodita'
    return c if (c and c not in FABBRICHE) else a
def valore(a,q):
    v=PR.get(a)
    return None if not v else q/10**v["decimali"]*v["prezzo_usd"]*EUR
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
fatte=len(json.load(open("data/liquidazioni/finestre_fatte_v2.json")))
giorni=60*fatte/88
occ=collections.defaultdict(lambda:{"prem":0.0,"liq":None,"ign":0})
for e in ev:
    d=e["dati"][2:]
    if len(d)<64*3: continue
    o=occ[e["tx"]]; o["liq"]="0x"+d[64*2+24:64*3]
    vg=valore(e["gar"], int(d[64:128],16)); vd=valore(e["deb"], int(d[0:64],16))
    if vg is None or vd is None: o["ign"]+=1
    else: o["prem"]+=vg-vd
val=[o for o in occ.values() if o["ign"]==0 and o["prem"]>0]
print(f"   {giorni:.0f} giorni | {len(val)} occasioni positive\n")
for chiave, nome in ((lambda o:o["liq"],"per CONTRATTO"), (lambda o:attore(o["liq"]),"per ATTORE")):
    c=collections.Counter(chiave(o) for o in val)
    print(f"   {nome}: {len(c)} soggetti distinti")
    for soglia in (3,5):
        pro={a for a,n in c.items() if n>=soglia}
        vp=sum(o["prem"] for o in val if chiave(o) in pro)
        vo=sum(o["prem"] for o in val if chiave(o) not in pro)
        print(f"      «ricorrente» = {soglia}+ : {len(pro)} soggetti | "
              f"ai ricorrenti {vp/(vp+vo)*100:>4.0f}% ({vp/giorni:>7,.0f} EUR/gg)  "
              f"agli altri {vo/(vp+vo)*100:>4.0f}% ({vo/giorni:>7,.0f} EUR/gg)")
    print()
c=collections.Counter(attore(o["liq"]) for o in val)
print(f"   i piu' attivi PER ATTORE:")
for a,n in c.most_common(6):
    v=sum(o["prem"] for o in val if attore(o["liq"])==a)
    print(f"      {a[:26]}..  {n:>3} occasioni  {v:>11,.0f} EUR")
uno=[a for a,n in c.items() if n==1]
vu=sum(o["prem"] for o in val if attore(o["liq"]) in set(uno))
print(f"\n   attori con UNA sola occasione: {len(uno)} | valore {vu:,.0f} EUR "
      f"({vu/giorni:,.0f} EUR/giorno)")
