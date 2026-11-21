"""La differenza persistente vale qualcosa solo se ci passa denaro.
Si misura la taglia degli scambi nel pool fermo: 1,3% di niente e' niente.
Il paio ha USDC (6 decimali) come uno dei due gettoni: li' l'importo e'
leggibile in dollari senza inventare un prezzo.
"""
import sys, collections
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
L=[]
for b in range(ult-900, ult, 450):
    r=B.log_di_finestra(SWAP3, b, min(b+449,ult))
    if r: L+=r
perpool=collections.defaultdict(list)
for x in L: perpool[x["address"].lower()].append(x)
# ritrova i pool del paio USDC / 0xb2000000...
cand=[]
for p,xs in perpool.items():
    if len(xs)<2 or len(xs)>60: 
        if len(xs)<2: continue
    a=B.chiama("eth_call",[{"to":p,"data":"0x"+firma("token0()")[2:10]},"latest"])
    b_=B.chiama("eth_call",[{"to":p,"data":"0x"+firma("token1()")[2:10]},"latest"])
    if not a or not b_ or len(a)<42: continue
    t=("0x"+a[-40:], "0x"+b_[-40:])
    if USDC in t and any(y.startswith("0xb2") for y in t):
        cand.append((p,t,xs))
print(f"   pool del paio trovati: {len(cand)}")
for p,t,xs in cand:
    idx = 0 if t[0]==USDC else 1
    imp=[]
    for x in xs:
        d=x["data"][2:]
        v=abs(sg(d[64*idx:64*(idx+1)]))/1e6
        if v>0: imp.append(v)
    if not imp: continue
    imp.sort()
    print(f"\n   pool {p[:12]}..  {len(xs)} scambi in 30 minuti")
    print(f"      taglia mediana {imp[len(imp)//2]:,.0f}$   massima {imp[-1]:,.0f}$")
    print(f"      totale passato {sum(imp):,.0f}$ in 30 minuti")
    print(f"      1,31% del totale = {sum(imp)*0.0131:,.2f}$ ogni 30 minuti "
          f"(lordo, se si catturasse TUTTO)")
