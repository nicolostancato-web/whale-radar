"""E' una commissione d'instradamento o una TASSA del gettone?

Distinzione decisiva: una commissione d'app dipende da CHI INSTRADA (la
stessa app la preleva su gettoni diversi). Una tassa dipende dal GETTONE
(lo stesso destinatario su scambi di quel gettone, chiunque li faccia).

Prova: per ogni destinatario, su quanti gettoni diversi incassa?
  - incassa su MOLTI gettoni  -> e' un'app che instrada
  - incassa su UN gettone solo -> e' la tesoreria di quel gettone
E al contrario: per ogni gettone, quanti destinatari diversi?
"""
import sys, os, json, collections, hashlib
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
TRASF=firma("Transfer(address,address,uint256)")
UR="0x6ff5693b99212da76ad316178a184ab56d299b43"
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
tx=[]
for b in range(ult-1800, ult, 900):
    L=B.log_di_finestra(SWAP3, b, min(b+899,ult))
    if L is None: continue
    tx += [x["transactionHash"] for x in L if "0x"+x["topics"][1][-40:]==UR]
tx=list(dict.fromkeys(tx)); tx.sort(key=lambda h: hashlib.sha256(h.encode()).hexdigest())
perdest=collections.defaultdict(set); pertok=collections.defaultdict(set)
coppie=0; letti=0
for h in tx[:250]:
    r=B.chiama("eth_getTransactionReceipt",[h])
    if not r: continue
    letti+=1
    chi=(r.get("from") or "").lower(); pool=set(); grande=0; tr=[]
    for L in r["logs"]:
        if not L.get("topics"): continue
        if L["topics"][0]==SWAP3:
            pool.add(L["address"].lower()); d=L["data"][2:]
            grande=max(grande, abs(sg(d[0:64])), abs(sg(d[64:128])))
        elif L["topics"][0]==TRASF and len(L["topics"])>=3:
            try: tr.append((L["address"].lower(),"0x"+L["topics"][2][-40:],int(L["data"],16)))
            except Exception: pass
    if not grande: continue
    for tok,a,v in tr:
        if a in pool or a==UR or a==chi or a=="0x"+"0"*40: continue
        if not (0.0002 < v/grande < 0.05): continue
        perdest[a].add(tok); pertok[tok].add(a); coppie+=1
print(f"   {letti} ricevute | {coppie} prelievi | {len(perdest)} destinatari | {len(pertok)} gettoni\n")
d=collections.Counter(len(v) for v in perdest.values())
print("   su quanti GETTONI incassa ogni destinatario:")
for n in sorted(d): print(f"      {n} gettone/i: {d[n]} destinatari")
uno=sum(c for n,c in d.items() if n==1)
print(f"   -> destinatari legati a un solo gettone: {uno}/{len(perdest)} "
      f"({uno/max(len(perdest),1)*100:.0f}%)")
t=collections.Counter(len(v) for v in pertok.values())
print("\n   quanti DESTINATARI per gettone:")
for n in sorted(t): print(f"      {n} destinatario/i: {t[n]} gettoni")
print("\n   VERDETTO: se la stragrande maggioranza dei destinatari incassa su")
print("   un gettone solo, non sono app che instradano: sono tesorerie di gettoni.")
