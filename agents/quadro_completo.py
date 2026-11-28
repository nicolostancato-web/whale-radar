"""Il quadro completo delle liquidazioni, a copertura crescente.

Tutte le misure insieme, cosi' si vede se si muovono quando arrivano dati:
tasso, premio, concentrazione nel tempo, concorrenti. Le monete ignote si
contano a parte, mai come zero.
"""
import json, collections, datetime, statistics as st, urllib.request, os
# 28/10: i prezzi NON si assumono piu'. wstETH era prezzato come ETH e vale
# 1,25 volte tanto: decine di liquidazioni risultavano in perdita e la somma
# dei premi veniva negativa. Ora si leggono dall'oracolo di Aave, che e'
# anche il prezzo con cui il protocollo decide le liquidazioni.
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
EUR=1/1.08
def valore(asset, quantita):
    """Valore in euro, o None se l'asset non e' noto: mai zero per comodita'."""
    v=PR.get(asset)
    if not v: return None
    return quantita/10**v["decimali"]*v["prezzo_usd"]*EUR

ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
fatte=len(json.load(open("data/liquidazioni/finestre_fatte_v2.json")))
cop=fatte/90
print(f"   {len(ev)} eventi | copertura {fatte}/90 ({cop*100:.0f}%) "
      f"= {60*cop:.1f} giorni effettivi\n")
occ=collections.defaultdict(lambda:{"prem":0.0,"n":0,"ora":0,"liq":None,"ign":0})
for e in ev:
    d=e["dati"][2:]
    if len(d)<64*3: continue
    o=occ[e["tx"]]; o["n"]+=1; o["ora"]=e["ora"]
    o["liq"]="0x"+d[64*2+24:64*3]
    vg=valore(e["gar"], int(d[64:128],16))
    vd=valore(e["deb"], int(d[0:64],16))
    if vg is None or vd is None: o["ign"]+=1
    else: o["prem"] += vg-vd
val=[o for o in occ.values() if o["ign"]==0]
print(f"   {len(occ)} occasioni, {len(val)} interamente valutabili")
print(f"   TASSO: {len(occ)/(60*cop):.1f} occasioni al giorno\n")
p=sorted((o["prem"] for o in val), reverse=True)
print(f"   PREMIO per occasione (EUR)")
print(f"      mediana {st.median(p):>10,.2f}   somma {sum(p):>12,.0f}")
for s_ in (100,1000,5000):
    g=[x for x in p if x>=s_]
    print(f"      oltre {s_:>5}: {len(g):>3} occasioni "
          f"({len(g)/(60*cop):.2f} al giorno)  somma {sum(g):>11,.0f}")
print(f"      le 5 maggiori: " + ", ".join(f"{x:,.0f}" for x in p[:5]))
print(f"\n   VALORE AL GIORNO (tutti i liquidatori): {sum(p)/(60*cop):,.0f} EUR")
gg=collections.defaultdict(float)
for o in val:
    gg[datetime.datetime.fromtimestamp(o["ora"],datetime.UTC).date()]+=o["prem"]
d=sorted(gg.values(), reverse=True); tot=sum(d)
print(f"\n   CONCENTRAZIONE: {len(gg)} giorni osservati")
for k in (1,3,5):
    if len(d)>=k: print(f"      i {k} migliori = {sum(d[:k])/tot*100:.0f}% del valore")
c=collections.Counter(o["liq"] for o in occ.values() if o["liq"])
print(f"\n   CONCORRENTI: {len(c)} indirizzi diversi su {len(occ)} occasioni")
print(f"      il primo {c.most_common(1)[0][1]/len(occ)*100:.0f}%, "
      f"i primi tre {sum(n for _,n in c.most_common(3))/len(occ)*100:.0f}%")
gr=[o for o in val if o["prem"]>=1000]
if gr:
    cg=collections.Counter(o["liq"] for o in gr)
    print(f"      sulle {len(gr)} occasioni sopra 1.000 EUR: {len(cg)} vincitori diversi")
