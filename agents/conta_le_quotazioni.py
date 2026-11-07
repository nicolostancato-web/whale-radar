"""Quante quotazioni nuove ci sono davvero negli archivi?
Prima di misurare: se gli eventi sono pochi, non c'e' potenza e il test
non va fatto (regola: calcolare l'n necessario PRIMA).
"""
import json, glob, os, datetime
def inizio(f):
    try: d=json.load(open(f))
    except Exception: return None
    if not isinstance(d,list) or not d: return None
    k="t" if "t" in d[0] else ("T" if "T" in d[0] else None)
    if not k: return None
    return min(int(x[k]) for x in d), len(d)
HL={}; BN={}
for f in glob.glob("data/candele3/*.json"):
    r=inizio(f)
    if r: HL[os.path.basename(f).replace(".json","")]=r
for d in ["data/binance","data/binance_piccoli","data/binance_f150","data/binance_f450","data/binance_f600"]:
    for f in glob.glob(d+"/*.json"):
        s=os.path.basename(f).replace("USDT.json","")
        r=inizio(f)
        if r and (s not in BN or r[0]<BN[s][0]): BN[s]=r
print(f"   Hyperliquid: {len(HL)} monete | Binance: {len(BN)} monete")
com=sorted(set(HL)&set(BN))
print(f"   in comune: {len(com)}")
dopo=[]; prima=[]
for s in com:
    th,_=HL[s]; tb,_=BN[s]
    g=(th-tb)/86400000
    if g>7: dopo.append((s,g,th))
    elif g<-7: prima.append((s,-g,tb))
print(f"\n   quotate su Hyperliquid DOPO Binance (>7gg): {len(dopo)}")
print(f"   quotate su Binance DOPO Hyperliquid (>7gg): {len(prima)}")
# quanti eventi hanno abbastanza storia sull'altra piazza prima e dopo?
usa=[x for x in dopo if x[1]>14]
print(f"   di cui con almeno 14 giorni di anticipo: {len(usa)}")
for s,g,t in sorted(usa,key=lambda x:-x[1])[:10]:
    print(f"      {s:<8} {g:>7.0f} giorni dopo  "
          f"({datetime.datetime.fromtimestamp(t/1000,datetime.UTC):%Y-%m-%d})")
print(f"\n   POTENZA: con n eventi e uno scarto tipico orario dell'1,5%,")
print(f"   per vedere un effetto di X% serve n ~ (2*1.5/X)^2")
for X in (0.5,1.0,2.0,3.0):
    print(f"      effetto {X}%: servono ~{int((2*1.5/X)**2)} eventi")
