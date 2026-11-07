"""Il PREMIO: di quanto il perpetuo si discosta dal prezzo di riferimento.

Diverso dal tasso di finanziamento, che e' limitato e smussato: il premio e'
lo scarto grezzo, e ha un motivo meccanico per rientrare — se il perpetuo vale
piu' del sottostante, chi arbitra lo riporta in linea.

Filtri rispettati: non e' storia dei prezzi, e' meccanico, lungo-corto,
osservazioni NON sovrapposte, e ce ne sono centinaia di migliaia.
Soglia relativa a ciascun mercato (percentile sulle ultime 500 ore), quindi
nota prima di entrare. Costo 0,094% a giro. Si stampano entrambi i versi: la
loro media deve dare -costo, ed e' la taratura.
"""
import json, glob, os, statistics as st
COSTO=0.00094
mercati=[]
for f in sorted(glob.glob("data/finanziamento/*.json")):
    c=os.path.basename(f).replace(".json","")
    p=f"data/candele_hl/{c}.json"
    if not os.path.exists(p): continue
    d=json.load(open(f))
    prem={x["time"]//3600000: float(x.get("premium",0)) for x in d}
    prz={x["t"]//3600000: x["c"] for x in json.load(open(p))}
    ore=sorted(set(prem)&set(prz))
    if len(ore)>1500: mercati.append((c,prem,prz,ore))
print(f"{len(mercati)} mercati | {sum(len(m[3]) for m in mercati):,} ore\n")
def prova(verso, oriz, soglia=0.9):
    v=[]
    for c,prem,prz,ore in mercati:
        storia=[]; libero=0
        for k,o in enumerate(ore):
            storia.append(prem[o])
            if k<500 or k>=len(ore)-oriz or k<libero: continue
            fin=sorted(storia[-500:])
            alto, basso = fin[int(soglia*len(fin))], fin[int((1-soglia)*len(fin))]
            x=prem[o]
            if x>=alto: seg=-1          # premio alto: il perpetuo e' caro -> corto
            elif x<=basso: seg=+1
            else: continue
            if verso=="segui lo scarto": seg=-seg
            v.append(seg*(prz[ore[k+oriz]]/prz[o]-1)-COSTO)
            libero=k+oriz
    if len(v)<300: return None
    return st.mean(v)*100, 1.96*st.stdev(v)/len(v)**0.5*100, len(v)
print("   verso                oriz     resa media            esito")
for verso in ("contrasta lo scarto","segui lo scarto"):
    for oriz in (4,8,24):
        r=prova(verso,oriz)
        if not r: continue
        m,e,n=r
        esito="SOPRA ZERO" if m-e>0 else ("sotto zero" if m+e<0 else "non dimostrato")
        print(f"   {verso:<20} {oriz:>3}h   {m:+7.4f}% +/-{e:6.4f} n={n:<6} {esito}")
print("\n   media dei due versi = -0,094% se non c'e' segnale (taratura)")
