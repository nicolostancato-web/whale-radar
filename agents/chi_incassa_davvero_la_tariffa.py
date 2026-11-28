"""La documentazione dice che si puo'. Ma qualcuno lo fa DAVVERO?

Regola del progetto: prima la prova sulla chain, poi il numero. Grok ha letto
le tariffe pubblicate; qui si guarda se su Base esistono transazioni in cui
un'app TRATTIENE una fetta dello scambio passando dal router di Uniswap.

Come si riconosce: nella stessa transazione dello Swap c'e' un Transfer del
gettone verso un indirizzo che non e' il pool, non e' il router e non e' chi
scambia, di importo pari a una piccola frazione dello scambio. Quello e'
l'incasso di un'applicazione.
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
TRASF=firma("Transfer(address,address,uint256)")
UR="0x6ff5693b99212da76ad316178a184ab56d299b43"   # Universal Router su Base
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
MIN=25; FIN=int(MIN*60/2.0)
logs=B.log_di_finestra(SWAP3, ult-FIN, ult)
if not logs: print("finestra non recuperata"); raise SystemExit
tx=[x["transactionHash"] for x in logs if "0x"+x["topics"][1][-40:]==UR]
tx=list(dict.fromkeys(tx))
print(f"{len(logs):,} scambi in {MIN} min | {len(tx)} transazioni dal Universal Router")
dest=collections.Counter(); quote=[]; letti=0
for h in tx[:70]:
    r=B.chiama("eth_getTransactionReceipt",[h])
    if not r: continue
    letti+=1
    chi_scambia=(r.get("from") or "").lower()
    pool=set(); grande=0; tr=[]
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
        if a in pool or a==UR or a==chi_scambia or a=="0x"+"0"*40: continue
        f=v/grande
        if 0.0002 < f < 0.05:
            dest[a]+=1; quote.append(f)
print(f"   ricevute lette: {letti}")
if quote:
    print(f"\n   trattenute riconosciute: {len(quote)} su {letti} transazioni ({len(quote)/letti:.0%})")
    print(f"   quota mediana trattenuta: {st.median(quote)*100:.3f}%  "
          f"(min {min(quote)*100:.3f}%, max {max(quote)*100:.3f}%)")
    print("   chi le riceve:")
    for a,n in dest.most_common(6): print(f"      {a}  {n}")
    print("\n   -> la porta e' aperta NEI FATTI, non solo nella documentazione")
else:
    print("\n   nessuna trattenuta riconosciuta: sul Universal Router di Base")
    print("   nessuno sta incassando una commissione d'app in questa finestra.")
    print("   -> la porta e' aperta nella documentazione ma NON la usa nessuno qui:")
    print("      o il flusso retail non passa da qui, o le app incassano altrove.")
