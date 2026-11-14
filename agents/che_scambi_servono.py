"""Che tipo di scambi servono le app che gia' incassano una commissione?

Serve a restringere la domanda «per chi costruire»: se servono tutte memecoin
la nicchia e' una, se servono trasferimenti fra stablecoin e' un'altra.
Si parte dalle transazioni in cui un'app incassa e si guarda QUALI gettoni
vengono scambiati li' dentro.
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents"); from keccak import keccak256
import base_rpc as B
SWAP3="0x"+keccak256(b"Swap(address,address,int256,int256,uint160,uint128,int24)").hex()
TRASF="0x"+keccak256(b"Transfer(address,address,uint256)").hex()
UR="0x6ff5693b99212da76ad316178a184ab56d299b43"
NOTI={"0x833589fcd6edb6e08f4c7c32d4f71b54bda02913":"USDC",
      "0x4200000000000000000000000000000000000006":"WETH",
      "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"cbBTC",
      "0x50c5725949a6f0c72e6c4a641f24049a917db0cb":"DAI"}
def sel(s): return "0x"+keccak256(s.encode()).hex()[:8]
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return None
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
L=B.log_di_finestra(SWAP3, ult-1200, ult)
tx=list(dict.fromkeys([x["transactionHash"] for x in (L or []) if "0x"+x["topics"][1][-40:]==UR]))
print(f"{len(tx)} transazioni dal router nell'ultima ora circa | ne leggo 70\n")
gettoni=collections.Counter(); con_comm=0; letti=0; nomi={}
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
for h in tx[:70]:
    r=B.chiama("eth_getTransactionReceipt",[h])
    if not r: continue
    letti+=1
    chi=(r.get("from") or "").lower(); pool=set(); grande=0; tr=[]; tok=set()
    for x in r["logs"]:
        if not x.get("topics"): continue
        if x["topics"][0]==SWAP3:
            pool.add(x["address"].lower()); d=x["data"][2:]
            grande=max(grande, abs(sg(d[0:64])), abs(sg(d[64:128])))
        elif x["topics"][0]==TRASF and len(x["topics"])>=3:
            tok.add(x["address"].lower())
            try: tr.append(("0x"+x["topics"][2][-40:], int(x["data"],16)))
            except Exception: pass
    if not grande: continue
    paga=any(0.0002 < v/grande < 0.05 for a,v in tr
             if a not in pool and a!=UR and a!=chi and a!="0x"+"0"*40)
    if not paga: continue
    con_comm+=1
    for t in tok:
        if t in NOTI: gettoni[NOTI[t]]+=1
        else:
            if t not in nomi:
                nomi[t]=testo(B.chiama("eth_call",[{"to":t,"data":sel("symbol()")},"latest"])) or "?"
            gettoni[nomi[t]]+=1
print(f"   ricevute lette {letti}, con commissione {con_comm}")
print(f"\n   gettoni coinvolti negli scambi che PAGANO una commissione:")
for g,n in gettoni.most_common(14):
    print(f"      {g:<16} {n}")
noti=sum(n for g,n in gettoni.items() if g in ("USDC","WETH","cbBTC","DAI"))
tot=sum(gettoni.values())
print(f"\n   quota di gettoni «seri» (USDC/WETH/cbBTC/DAI): {noti/max(tot,1):.0%}")
print("   -> " + ("servono soprattutto scambi fra gettoni noti" if noti/max(tot,1)>0.6
      else "servono soprattutto gettoni di nicchia / memecoin"))
