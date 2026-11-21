"""La documentazione non e' una prova: quanto vale davvero il referral di Zora?

Due domande:
  1. quanto flusso passa in un giorno sulle monete di Zora (la torta dello 0,20%)
  2. chi incassa quel referral: sempre il protocollo, o TANTI indirizzi diversi?
     Se sono tanti, la porta e' aperta nei fatti; se e' sempre lo stesso, e'
     disegnata ma chiusa.

Si parte dagli scambi con una trattenuta gia' riconosciuta e si guarda la
distribuzione dei destinatari e il volume su cui maturano.
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
SWAP4=firma("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)")
TRASF=firma("Transfer(address,address,uint256)")
UR="0x6ff5693b99212da76ad316178a184ab56d299b43"
WETH="0x4200000000000000000000000000000000000006"; USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
VAL={WETH:(18,3030.0), USDC:(6,0.92)}
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
ORE=2; FIN=int(ORE*3600/2.0)
tx=[]
for b in range(ult-FIN, ult, 900):
    L=B.log_di_finestra(SWAP3, b, min(b+899,ult))
    if L is None: continue
    tx += [x["transactionHash"] for x in L if "0x"+x["topics"][1][-40:]==UR]
tx=list(dict.fromkeys(tx))
print(f"{ORE} ore | {len(tx)} transazioni dal router | ne leggo 180\n")
dest=collections.Counter(); valore=collections.Counter(); vol_tot=0.0; letti=0
for h in tx[:180]:
    r=B.chiama("eth_getTransactionReceipt",[h])
    if not r: continue
    letti+=1
    chi=(r.get("from") or "").lower(); pool=set(); grande=0; tr=[]; vol_eur=0.0
    for L in r["logs"]:
        if not L.get("topics"): continue
        t0=L["topics"][0]
        if t0 == SWAP3:
            pool.add(L["address"].lower()); d=L["data"][2:]
            grande=max(grande, abs(sg(d[0:64])), abs(sg(d[64:128])))
        elif t0==TRASF and len(L["topics"])>=3:
            tok=L["address"].lower()
            try: v=int(L["data"],16)
            except Exception: continue
            tr.append((tok,"0x"+L["topics"][2][-40:],v))
            if tok in VAL:
                dec,pr=VAL[tok]; vol_eur=max(vol_eur, v/10**dec*pr)
    if not grande: continue
    vol_tot+=vol_eur
    for tok,a,v in tr:
        if a in pool or a==UR or a==chi or a=="0x"+"0"*40: continue
        f=v/grande
        if 0.0002 < f < 0.05:
            dest[a]+=1
            if tok in VAL:
                dec,pr=VAL[tok]; valore[a]+=v/10**dec*pr
print(f"   ricevute lette: {letti} | volume scambiato riconosciuto: {vol_tot:,.0f} EUR")
print(f"   destinatari distinti del referral: {len(dest)}")
q1=dest.most_common(1)[0][1]/sum(dest.values()) if dest else 0
print(f"   quota del primo destinatario: {q1:.0%}")
print("\n   i primi, per numero di incassi e per valore raccolto:")
for a,n in dest.most_common(8):
    print(f"      {a}  {n:>3} volte  {valore.get(a,0):>9,.2f} EUR")
print(f"\n   volume al giorno su questo flusso: {vol_tot*24/ORE:,.0f} EUR")
print(f"   lo 0,20% di quel volume: {vol_tot*24/ORE*0.002:,.0f} EUR al giorno (la torta del referral)")
print("   -> " + ("porta APERTA nei fatti: tanti destinatari diversi" if len(dest)>10 and q1<0.5
      else "pochi destinatari: la porta e' disegnata ma stretta"))
