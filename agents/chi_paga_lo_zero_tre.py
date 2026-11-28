"""Perche' pagare lo 0,30% per dollaro-contro-dollaro quando accanto c'e' lo 0,00%?

Finche' non lo so, il 5.390% annuo non e' un'occasione: e' un'anomalia non
capita. Due verifiche:
  1. DURA? sei ore invece di trenta minuti. Se e' un lampo, non e' un reddito.
  2. CHI PAGA? se e' sempre lo stesso indirizzo, e' un bot che fa altro e noi
     saremmo il suo fornitore finche' gli serve; se sono in tanti, e' domanda vera.
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma, keccak256
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
SEL_BAL="0x"+keccak256(b"balanceOf(address)").hex()[:8]
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
# ritrovo il pool 0,30% USDC/USDT piu' attivo
logs=B.log_di_finestra(SWAP3, ult-900, ult)
per=collections.Counter(L["address"].lower() for L in logs or [])
P=None
for p,_n in per.most_common(150):
    t0=B.chiama("eth_call",[{"to":p,"data":"0x0dfe1681"},"latest"])
    fe=B.chiama("eth_call",[{"to":p,"data":"0xddca3f43"},"latest"])
    if t0 and fe and "0x"+t0[-40:]==USDC and int(fe,16)==3000:
        P=p; break
if not P: print("pool non ritrovato nella finestra breve"); raise SystemExit
print(f"pool {P}\n")
ORE=6; FIN=int(ORE*3600/2.0)
tutti=B.log_di_finestra(SWAP3, ult-FIN, ult, indirizzo=P)
if tutti is None: print("   sei ore non recuperate entro la scadenza"); raise SystemExit
print(f"   {len(tutti)} scambi in {ORE} ore  ({len(tutti)/ORE:.0f}/ora)")
# volume e distribuzione nel tempo
per_ora=collections.Counter(); vol=0.0; chi=collections.Counter(); tagli=[]
for L in tutti:
    d=L["data"][2:]; v=abs(sg(d[0:64]))/1e6
    vol+=v; tagli.append(v)
    per_ora[(int(L["blockNumber"],16)-(ult-FIN))//1800]+=1
    chi["0x"+L["topics"][2][-40:]]+=1      # recipient
bal=B.chiama("eth_call",[{"to":USDC,"data":SEL_BAL+"0"*24+P[2:]},"latest"])
print(f"   volume {vol:,.0f} USDC | commissioni {vol*0.003:,.0f} USDC in {ORE} ore")
print(f"   taglio mediano {st.median(tagli):,.2f} USDC")
print(f"   scambi per ora: {[per_ora.get(i,0) for i in range(ORE)]}")
print(f"\n   destinatari distinti: {len(chi)}")
for a,n in chi.most_common(5): print(f"      {a[:24]}…  {n}")
q=chi.most_common(1)[0][1]/len(tutti) if chi else 0
print(f"   quota del primo: {q:.0%}")
print("   -> " + ("UN SOLO indirizzo: e' un bot, non domanda vera" if q>0.6 else
      "molti indirizzi: sembra domanda vera, allora e' instradamento"))
