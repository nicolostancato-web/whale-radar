"""15% al giorno non resta sul tavolo: chi se lo mangia?

Ipotesi che spiegherebbe tutto: chi fornisce la liquidita' e chi scambia sono
LA STESSA MANO — qualcuno che si paga commissioni da solo (per gonfiare il
volume, o per raccogliere un incentivo). In quel caso entrare funziona finche'
lui non smette, e va saputo PRIMA di metterci un euro.
Si confrontano i depositanti (Mint) con chi scambia (Swap).
"""
import sys, collections
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
P="0x9ab7730b09ebd9ff2df70f06339bd289a1680a46"
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
MINT=firma("Mint(address,address,int24,int24,uint128,uint256,uint256)")
BURN=firma("Burn(address,int24,int24,uint128,uint256,uint256)")
COLL=firma("Collect(address,address,int24,int24,uint128,uint128)")
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
ORE=12; FIN=int(ORE*3600/2.0)
for nome,t in (("Mint",MINT),("Burn",BURN),("Collect",COLL)):
    L=B.log_di_finestra(t, ult-FIN, ult, indirizzo=P)
    if L is None: print(f"   {nome}: finestra non recuperata"); continue
    chi=collections.Counter("0x"+x["topics"][1][-40:] for x in L if len(x["topics"])>1)
    print(f"   {nome:<8} {len(L):>4} eventi | {len(chi)} indirizzi")
    for a,n in chi.most_common(3): print(f"      {a}  {n}")
Ls=B.log_di_finestra(SWAP3, ult-int(3*3600/2), ult, indirizzo=P)
if Ls:
    sw=collections.Counter("0x"+x["topics"][1][-40:] for x in Ls)   # sender
    rc=collections.Counter("0x"+x["topics"][2][-40:] for x in Ls)   # recipient
    print(f"\n   chi CHIAMA lo scambio (3h): {len(sw)} indirizzi")
    for a,n in sw.most_common(4): print(f"      {a}  {n}")
    print(f"   quota del primo: {sw.most_common(1)[0][1]/len(Ls):.0%}")
