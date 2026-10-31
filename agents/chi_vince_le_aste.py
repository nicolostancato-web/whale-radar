"""Chi vince le aste dei solver di CoW, e quanto resta a un nuovo arrivato.

Il piatto misurato era ~13.000 EUR/giorno: il piu' grande fra i mestieri a
cottimo trovati, e l'unico posto dove il mercato paga l'ABILITA' e non il
capitale. La domanda mai fatta: quanto ne prende uno nuovo.

Si guarda: quanti solver gareggiano per asta, quanto e' concentrata la
vittoria, e che distanza c'e' fra il primo e il secondo (se e' minima, un
bravo nuovo entra; se e' grande, c'e' un muro).
"""
import json, os, time, urllib.request, collections, statistics as st
def get(u, t=30):
    r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
    return json.load(urllib.request.urlopen(r, timeout=t))
B="https://api.cow.fi/mainnet/api/v2/solver_competition"
ult=get(B+"/latest")
aid=int(ult["auctionId"])
print(f"   ultima asta: {aid}")
righe=[]
f="data/cow/aste.jsonl"
if os.path.exists(f):
    righe=[json.loads(x) for x in open(f)]
visti={r["id"] for r in righe}
nuovi=0
for i in range(300):
    a=aid-i
    if a in visti: continue
    try: d=get(f"{B}/{a}")
    except Exception: continue
    sol=d.get("solutions") or []
    if not sol: continue
    per=[]
    for s in sol:
        per.append({"solver": s.get("solver") or s.get("solverAddress"),
                    "ranking": s.get("ranking"),
                    "score": s.get("score"),
                    "ordini": len(s.get("orders") or [])})
    righe.append({"id": a, "n": len(sol), "sol": per})
    nuovi+=1
    if nuovi%40==0: print(f"      {nuovi} aste nuove")
    time.sleep(0.12)
with open(f,"w") as g:
    for r in righe: g.write(json.dumps(r)+"\n")
print(f"   {len(righe)} aste in archivio ({nuovi} nuove)\n")
conc=[r for r in righe if r["n"]>0]
print(f"   solver per asta: mediana {st.median([r['n'] for r in conc])}, "
      f"max {max(r['n'] for r in conc)}")
vinc=collections.Counter()
secondi=collections.Counter()
dist=[]
for r in conc:
    s=sorted(r["sol"], key=lambda x: (x["ranking"] if x["ranking"] is not None else 999))
    if not s: continue
    vinc[s[0]["solver"]]+=1
    if len(s)>1:
        secondi[s[1]["solver"]]+=1
        try:
            a=float(s[0]["score"]); b=float(s[1]["score"])
            if a>0: dist.append((a-b)/a*100)
        except Exception: pass
tot=sum(vinc.values())
print(f"\n   {len(vinc)} solver diversi hanno vinto almeno un'asta su {tot}")
for s,n in vinc.most_common(8):
    print(f"      {str(s)[:42]:<44}{n:>5}  {n/tot*100:>5.1f}%")
if dist:
    dist.sort()
    print(f"\n   distanza fra primo e secondo (in % del punteggio):")
    print(f"      mediana {st.median(dist):.2f}%   "
          f"quarto basso {dist[len(dist)//4]:.2f}%   "
          f"quarto alto {dist[3*len(dist)//4]:.2f}%")
    print(f"      aste decise per meno dell'1%: "
          f"{sum(1 for x in dist if x<1)/len(dist)*100:.0f}%")
