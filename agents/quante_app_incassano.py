"""Base piu' larga per i due numeri su cui si decide:
   - quanto trattiene un'app (prima: 0,206% su 70 ricevute, 25 minuti)
   - quante app distinte lo fanno in un giorno

Non e' una strada nuova: e' rendere solido cio' che serve alla decisione.
Si legge su piu' ore e si contano le ricevute davvero lette, non quelle
sperate. I fallimenti si contano (lezione del falso zero).
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
TRASF=firma("Transfer(address,address,uint256)")
UR="0x6ff5693b99212da76ad316178a184ab56d299b43"
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
BLOCCHI=5400      # ~3 ore
tx=[]
for b in range(ult-BLOCCHI, ult, 900):
    L=B.log_di_finestra(SWAP3, b, min(b+899,ult))
    if L is None: continue
    tx += [x["transactionHash"] for x in L if "0x"+x["topics"][1][-40:]==UR]
tx=list(dict.fromkeys(tx))
print(f"~{BLOCCHI*2/3600:.1f} ore | {len(tx)} transazioni distinte dal router\n")
dest=collections.Counter(); quote=[]; letti=0; falliti=0
import random
camp = tx[:200]
for h in camp:
    r=B.chiama("eth_getTransactionReceipt",[h])
    if not r: falliti+=1; continue
    letti+=1
    chi=(r.get("from") or "").lower(); pool=set(); grande=0; tr=[]
    for L in r["logs"]:
        if not L.get("topics"): continue
        if L["topics"][0]==SWAP3:
            pool.add(L["address"].lower()); d=L["data"][2:]
            grande=max(grande, abs(sg(d[0:64])), abs(sg(d[64:128])))
        elif L["topics"][0]==TRASF and len(L["topics"])>=3:
            try: tr.append(("0x"+L["topics"][2][-40:], int(L["data"],16)))
            except Exception: pass
    if not grande: continue
    for a,v in tr:
        if a in pool or a==UR or a==chi or a=="0x"+"0"*40: continue
        f=v/grande
        if 0.0002 < f < 0.05: dest[a]+=1; quote.append(f)
print(f"   ricevute lette: {letti} (falliti {falliti})")
if quote:
    quote.sort()
    print(f"   transazioni con una trattenuta: {len(quote)} ({len(quote)/max(letti,1):.0%})")
    print(f"   quota trattenuta: mediana {st.median(quote)*100:.3f}%  "
          f"quartili {quote[len(quote)//4]*100:.3f}% / {quote[3*len(quote)//4]*100:.3f}%")
    print(f"   app distinte che incassano: {len(dest)}")
    for a,n in dest.most_common(8): print(f"      {a}  {n}")
    m=st.median(quote)
    print(f"\n   con questa tariffa, 500 EUR/giorno = {500/m:,.0f} EUR di volume al giorno")
