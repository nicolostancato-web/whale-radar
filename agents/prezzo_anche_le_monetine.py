"""I 20-200 EUR/giorno erano un MINIMO: le app incassano soprattutto in
monetine che non sapevo prezzare. Qui si prezzano passando dal loro pool
contro ether, cosi' il numero diventa un totale invece che un pavimento.

Prezzo di una monetina = (riserva di ether nel pool) / (riserva di monetina),
letta dai saldi del pool canonico Uniswap v3 token/WETH.
Se il pool non esiste o e' vuoto, la moneta si DICHIARA non prezzabile e il
suo valore non si inventa.
"""
import sys, collections
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma, keccak256
TRASF=firma("Transfer(address,address,uint256)")
FAB="0x33128a8fc17869897dce68ed026d694621f6fdfd"
WETH="0x4200000000000000000000000000000000000006"
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
NOTI={USDC:(6,0.92), WETH:(18,3030.0)}
def sel(s): return "0x"+keccak256(s.encode()).hex()[:8]
def w(a): return a[2:].rjust(64,"0")
APP="0x0469a4bd3724dc86c9542f4694c976da13c450c0"
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
ORE=1; FIN=int(ORE*3600/2.0); PASSO=500
t2="0x"+"0"*24+APP[2:]
L=[]; falliti=0
for b in range(ult-FIN, ult, PASSO):
    r=B.chiama("eth_getLogs",[{"topics":[TRASF,[],[t2]],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}])
    if isinstance(r,list): L+=r
    else: falliti+=1
print(f"app {APP[:16]}… | {len(L)} entrate in {ORE} ore ({falliti} finestre fallite)")
per=collections.defaultdict(int)
for x in L:
    try: per[x["address"].lower()]+=int(x["data"],16)
    except Exception: pass
print(f"   gettoni distinti ricevuti: {len(per)}")
val=0.0; non_prez=0; righe=[]
for tok,amt in sorted(per.items(), key=lambda x:-x[1])[:14]:
    if tok in NOTI:
        dec,pr=NOTI[tok]; v=amt/10**dec*pr; val+=v
        righe.append((v,tok,"nota")); continue
    dec_h=B.chiama("eth_call",[{"to":tok,"data":sel("decimals()")},"latest"])
    if not dec_h: non_prez+=1; continue
    dec=int(dec_h,16)
    prezzo=None
    for fee in (10000,3000,500):
        d=sel("getPool(address,address,uint24)")+w(tok)+w(WETH)+("0"*58+f"{fee:04x}")[-64:]
        r=B.chiama("eth_call",[{"to":FAB,"data":d},"latest"])
        p="0x"+r[-40:] if r else None
        if not p or p=="0x"+"0"*40: continue
        bt=B.chiama("eth_call",[{"to":tok,"data":sel("balanceOf(address)")+w(p)},"latest"])
        be=B.chiama("eth_call",[{"to":WETH,"data":sel("balanceOf(address)")+w(p)},"latest"])
        if not bt or not be: continue
        rt=int(bt,16)/10**dec; re_=int(be,16)/1e18
        if rt>0 and re_>0: prezzo=re_/rt*3030.0; break
    if prezzo is None: non_prez+=1; continue
    v=amt/10**dec*prezzo; val+=v
    righe.append((v,tok,"prezzata dal pool"))
righe.sort(reverse=True)
for v,tok,come in righe[:8]:
    print(f"      {tok[:18]}…  {v:>10,.2f} EUR   ({come})")
print(f"\n   valore prezzabile delle entrate: {val:,.2f} EUR in {ORE} ore = {val*24/ORE:,.0f} EUR al giorno")
print(f"   gettoni non prezzabili (nessun pool con ether): {non_prez}")
print("   -> " + ("le monetine contano: il minimo di prima era molto sotto"
      if val > 40 else "le monetine aggiungono poco: il minimo di prima era vicino al vero"))
