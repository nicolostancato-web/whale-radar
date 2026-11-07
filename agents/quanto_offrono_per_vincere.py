"""Quanto paga di mancia chi vince un'occasione grossa?

Se su un premio da 50.000 EUR qualcuno offre migliaia per entrare nel
blocco, e' un'asta feroce e il margine vero e' molto piu' basso del premio.
Se paga la tariffa base, nessuno sta competendo davvero.

Si confronta la mancia (gas pagato x gas usato) col premio dell'occasione.
"""
import json, collections, statistics as st
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
EUR=1/1.08
WETH="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
eth_usd=PR[WETH]["prezzo_usd"]
def valore(a,q):
    v=PR.get(a)
    return None if not v else q/10**v["decimali"]*v["prezzo_usd"]*EUR
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
occ=collections.defaultdict(lambda:{"prem":0.0,"gas":0,"gp":0,"ign":0})
for e in ev:
    d=e["dati"][2:]
    if len(d)<64*3: continue
    o=occ[e["tx"]]
    vg=valore(e["gar"], int(d[64:128],16)); vd=valore(e["deb"], int(d[0:64],16))
    if vg is None or vd is None: o["ign"]+=1
    else: o["prem"]+=vg-vd
    try:
        o["gas"]=int(e["gasUsed"],16); o["gp"]=int(e["gasPrice"],16)
    except Exception: pass
righe=[]
for tx,o in occ.items():
    if o["ign"] or not o["gas"]: continue
    costo=o["gas"]*o["gp"]/1e18*eth_usd*EUR
    righe.append((o["prem"], costo, o["gp"]/1e9))
righe.sort(key=lambda x:-x[0])
print(f"   {len(righe)} occasioni con premio e costo noti\n")
print(f"   {'fascia di premio':<22}{'n':>5}{'premio mediano':>17}"
      f"{'costo mediano':>16}{'costo/premio':>14}")
for lo,hi,nome in [(5000,1e12,"oltre 5.000"),(1000,5000,"1.000-5.000"),
                   (100,1000,"100-1.000"),(1,100,"1-100"),(-1e9,1,"sotto 1")]:
    g=[r for r in righe if lo<=r[0]<hi]
    if not g: continue
    pm=st.median([r[0] for r in g]); cm=st.median([r[1] for r in g])
    print(f"   {nome:<22}{len(g):>5}{pm:>16,.2f}€{cm:>15,.2f}€"
          f"{(cm/pm*100 if pm>0 else 0):>13.2f}%")
gr=[r for r in righe if r[0]>=5000]
if gr:
    print(f"\n   le occasioni oltre 5.000 EUR, una per una:")
    for p,c,gp in gr:
        print(f"      premio {p:>11,.0f}€   costo {c:>8,.2f}€   "
              f"gas {gp:>7.3f} gwei   resta {p-c:>11,.0f}€ ({(p-c)/p*100:.1f}%)")
