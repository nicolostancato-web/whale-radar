"""Quanto incassa DAVVERO ogni app che preleva la commissione d'instradamento.

Finora avevo stimato il ricavo assumendo un volume. Qui non si assume niente:
si guarda chi riceve, e quanto, una per una.

Lezione «importo senza moneta»: si convertono in euro SOLO le commissioni
pagate in WETH o USDC, dove la moneta e il numero di decimali sono noti.
Le altre si contano a parte come «non valutabili», mai sommate a zero.
Accumula gli indirizzi in un file, cosi' i giri successivi si sommano.
"""
import sys, os, json, collections, statistics as st, datetime, glob
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
TRASF=firma("Transfer(address,address,uint256)")
UR="0x6ff5693b99212da76ad316178a184ab56d299b43"
WETH="0x4200000000000000000000000000000000000006"
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
FUORI="data/base/incassi_per_app.jsonl"; os.makedirs("data/base",exist_ok=True)
# prezzo ETH: ultima chiusura dall'archivio su disco, non inventato
eth=None
for f in ["data/binance/ETHUSDT.json"]+glob.glob("data/binance_*/ETHUSDT.json"):
    if os.path.exists(f):
        d=json.load(open(f)); k="t" if "t" in d[0] else "T"
        eth=max(d,key=lambda x:int(x[k]))["c"]; break
if eth is None: print("manca il prezzo ETH"); sys.exit(1)
EUR=1/1.08   # dollari -> euro, approssimazione dichiarata
print(f"   ETH {eth:.0f}$  |  cambio usato 1 EUR = 1.08 USD")
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
BL=1800
tx=[]
for b in range(ult-BL, ult, 900):
    L=B.log_di_finestra(SWAP3, b, min(b+899,ult))
    if L is None: continue
    tx += [x["transactionHash"] for x in L if "0x"+x["topics"][1][-40:]==UR]
tx=list(dict.fromkeys(tx))
import hashlib
tx.sort(key=lambda h: hashlib.sha256(h.encode()).hexdigest())
QUANTI=min(300,len(tx))
print(f"   {len(tx)} transazioni d'instradamento nell'ora, ne leggo {QUANTI}")
inc=collections.Counter(); nonval=collections.Counter(); letti=0; pag=0
for h in tx[:QUANTI]:
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
    visto=False
    for tok,a,v in tr:
        if a in pool or a==UR or a==chi or a=="0x"+"0"*40: continue
        if not (0.0002 < v/grande < 0.05): continue
        visto=True
        if tok==WETH: inc[a]+= v/1e18*eth*EUR
        elif tok==USDC: inc[a]+= v/1e6*EUR
        else: nonval[a]+=1
    if visto: pag+=1
ora=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M")
with open(FUORI,"a") as f:
    f.write(json.dumps({"ora":ora,"letti":letti,"paganti":pag,"quanti_tx_ora":len(tx),
                        "incassi":{a:round(x,4) for a,x in inc.items()},
                        "non_valutabili":dict(nonval)})+"\n")
scala = len(tx)/max(letti,1)        # dal campione all'ora intera
v=sorted(inc.values(), reverse=True)
print(f"   {letti} ricevute | {pag} con commissione | {len(inc)} app valutabili "
      f"| {len(nonval)} app in gettoni non valutabili")
if v:
    g=[x*scala*24 for x in v]
    print(f"\n   incasso stimato AL GIORNO per app (euro), scalato x{scala:.1f} e x24:")
    print(f"      la prima      {g[0]:>10.2f}")
    if len(g)>1: print(f"      la seconda    {g[1]:>10.2f}")
    print(f"      mediana       {st.median(g):>10.2f}")
    print(f"      la peggiore   {g[-1]:>10.2f}")
    print(f"      totale        {sum(g):>10.2f}   su {len(g)} app")
    print(f"      quota della prima: {g[0]/sum(g)*100:.0f}%")
print(f"\n   nota: una sola ora, un solo campione. Serve accumulare.")
