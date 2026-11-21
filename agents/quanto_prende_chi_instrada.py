"""Quanto prende DAVVERO chi instrada? Lo 0,15% era una mia ipotesi.

Dopo l'errore della commissione inventata (24/10), ogni costante che entra in un
conto va misurata. Qui: nelle transazioni passate per un router, esiste un
trasferimento verso un TERZO indirizzo pari a una piccola frazione dello
scambio? Quella frazione e' la commissione dell'applicazione.
Si cerca un Transfer il cui importo stia fra lo 0,01% e il 2% del volume dello
scambio, verso un indirizzo che non sia ne' il pool ne' chi scambia.
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
TRASF=firma("Transfer(address,address,uint256)")
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
logs=B.log_di_finestra(SWAP3, ult-600, ult)
if not logs: print("finestra non recuperata"); raise SystemExit
per=collections.Counter("0x"+x["topics"][1][-40:] for x in logs)
print(f"{len(logs):,} scambi in 20 min | {len(per)} router\n")
for router,_n in per.most_common(5):
    tx=[x["transactionHash"] for x in logs if "0x"+x["topics"][1][-40:]==router][:12]
    quote=[]; visti=0
    for h in tx:
        r=B.chiama("eth_getTransactionReceipt",[h])
        if not r: continue
        visti+=1
        sw=[]; tr=[]
        for L in r["logs"]:
            if not L.get("topics"): continue
            if L["topics"][0]==SWAP3:
                d=L["data"][2:]; sw.append((abs(sg(d[0:64])), abs(sg(d[64:128])), L["address"].lower()))
            elif L["topics"][0]==TRASF and len(L["topics"])>=3:
                try: tr.append((L["address"].lower(), "0x"+L["topics"][2][-40:], int(L["data"],16)))
                except Exception: pass
        if not sw: continue
        grande=max(max(a,b) for a,b,_p in sw)
        pool={p for _a,_b,p in sw}
        for _tok,dest,v in tr:
            if dest in pool: continue
            f=v/grande if grande else 0
            if 0.0001 < f < 0.02: quote.append(f)
    if quote:
        print(f"   {router[:22]}…  su {visti} transazioni: {len(quote)} possibili commissioni" + ("  (incluso cio che resta al router)" if True else ""))
        print(f"      mediana {st.median(quote)*100:.3f}%  min {min(quote)*100:.3f}%  max {max(quote)*100:.3f}%")
    else:
        print(f"   {router[:22]}…  su {visti} transazioni: nessuna commissione riconoscibile")
