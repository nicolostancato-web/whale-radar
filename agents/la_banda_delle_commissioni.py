"""Due pool dello stesso paio possono differire SENZA arbitraggio fino alla
somma delle loro commissioni. Prima di chiamare occasione una differenza,
si leggono le commissioni vere dei due pool.

Lezione gia' pagata (fee inventata al 0,30%): la commissione si LEGGE dal
contratto, non si assume.
"""
import sys, collections
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
from dato_obbligatorio import *
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
L=[]
for b in range(ult-900, ult, 450):
    r=B.log_di_finestra(SWAP3, b, min(b+449,ult))
    if r: L+=r
perpool=collections.defaultdict(list)
for x in L: perpool[x["address"].lower()].append(x)
tok={}
for p,xs in perpool.items():
    if len(xs)<3: continue
    a=B.chiama("eth_call",[{"to":p,"data":"0x"+firma("token0()")[2:10]},"latest"])
    b_=B.chiama("eth_call",[{"to":p,"data":"0x"+firma("token1()")[2:10]},"latest"])
    if not a or not b_ or len(a)<42: continue
    tok[p]=tuple(sorted(("0x"+a[-40:],"0x"+b_[-40:])))
gr=collections.defaultdict(list)
for p,t in tok.items(): gr[t].append(p)
mult={k:v for k,v in gr.items() if len(v)>1}
print(f"   {len(mult)} paia in piu' pool\n")
def commissione(p):
    r=B.chiama("eth_call",[{"to":p,"data":"0x"+firma("fee()")[2:10]},"latest"])
    if not r or len(r)<4: return None
    try: return int(r,16)/1e6*100
    except Exception: return None
nascosta=0; vere=0; esaminati=0
for paio,ps in list(mult.items())[:14]:
    com=[(p,commissione(p)) for p in ps]
    if any(c is None for _,c in com):
        print(f"   paio {paio[0][:8]}../{paio[1][:8]}..  commissione NON leggibile "
              f"su {sum(1 for _,c in com if c is None)}/{len(com)} pool -> escluso")
        continue
    esaminati+=1
    # prezzo per pool nell'ultimo blocco visto
    pr={}
    for p in ps:
        xs=sorted(perpool[p], key=lambda x:int(x["blockNumber"],16))
        d=xs[-1]["data"][2:]
        if len(d)<64*5: continue
        sq=int(d[64*4:64*5],16)
        if sq: pr[p]=(sq/2**96)**2
    if len(pr)<2: continue
    a=max(pr.values()); b2=min(pr.values())
    diff=(a/b2-1)*100
    banda=sum(c for _,c in com if c is not None)/len(com)*2
    stato = "DENTRO la banda (nessun arbitraggio)" if diff<=banda else "OLTRE la banda"
    if diff<=banda: nascosta+=1
    else: vere+=1
    print(f"   {paio[0][:8]}../{paio[1][:8]}..  {len(ps)} pool  "
          f"commissioni {[f'{c:.2f}%' for _,c in com]}")
    print(f"      differenza {diff:.3f}%  banda senza arbitraggio {banda:.3f}%  -> {stato}")
print(f"\n   dentro la banda: {nascosta}/{esaminati}   oltre: {vere}/{esaminati}")
