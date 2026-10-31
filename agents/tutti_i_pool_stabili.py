"""Misura di TUTTI i pool fra stablecoin, ognuno con il suo indirizzo stampato.

La confusione precedente: due misure incompatibili (49.000 di volume in 30 min
contro 5.502 in 6 ore) perche' erano due pool diversi, e non avevo stampato
l'indirizzo. Regola: ogni riga porta il suo identificativo, sempre.
Si misura su SEI ORE, non trenta minuti: un lampo non e' un reddito.
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
import dato_obbligatorio as DO
from keccak import firma, keccak256
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
SEL_BAL="0x"+keccak256(b"balanceOf(address)").hex()[:8]
SEL_SYM="0x"+keccak256(b"symbol()").hex()[:8]; SEL_DEC="0x"+keccak256(b"decimals()").hex()[:8]
STAB={"USDC","USDT","DAI","EURC","USDS","USDBC"}
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
corti=B.log_di_finestra(SWAP3, ult-900, ult) or []
per=collections.Counter(L["address"].lower() for L in corti)
cand=[]
for p,n in per.most_common(140):
    t0=B.chiama("eth_call",[{"to":p,"data":"0x0dfe1681"},"latest"]); t1=B.chiama("eth_call",[{"to":p,"data":"0xd21220a7"},"latest"])
    if not t0 or not t1: continue
    a="0x"+t0[-40:]; b="0x"+t1[-40:]
    sa=testo(B.chiama("eth_call",[{"to":a,"data":SEL_SYM},"latest"])).upper()
    sb=testo(B.chiama("eth_call",[{"to":b,"data":SEL_SYM},"latest"])).upper()
    if sa in STAB and sb in STAB: cand.append((p,a,b,sa,sb))
print(f"{len(cand)} pool fra stablecoin fra i piu' attivi\n")
ORE=6; FIN=int(ORE*3600/2.0)
for p,a,b,sa,sb in cand:
    fee=DO.intero(B.chiama("eth_call",[{"to":p,"data":"0xddca3f43"},"latest"]), "la commissione del pool")
    da=DO.intero(B.chiama("eth_call",[{"to":a,"data":SEL_DEC},"latest"]), "i decimali del gettone")
    db=DO.intero(B.chiama("eth_call",[{"to":b,"data":SEL_DEC},"latest"]), "i decimali del gettone")
    L6=B.log_di_finestra(SWAP3, ult-FIN, ult, indirizzo=p)
    if L6 is None: print(f"   {p[:16]}… {sa}/{sb}: sei ore non recuperate"); continue
    vol=sum(abs(sg(x["data"][2:][0:64]))/10**da for x in L6)
    b0=B.chiama("eth_call",[{"to":a,"data":SEL_BAL+"0"*24+p[2:]},"latest"])
    b1=B.chiama("eth_call",[{"to":b,"data":SEL_BAL+"0"*24+p[2:]},"latest"])
    cap=(int(b0,16)/10**da if b0 else 0)+(int(b1,16)/10**db if b1 else 0)
    comm=vol*fee/1e6
    anno = comm*(24/ORE)*365/cap if cap>0 else 0
    print(f"   {p[:16]}…  {sa}/{sb:<5} fee {fee/10000:>5.2f}%  {len(L6):>5} scambi/{ORE}h"
          f"  vol {vol:>12,.0f}  cap {cap:>12,.0f}  resa {anno*100:>9.1f}%")
