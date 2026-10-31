"""Quanto varrebbero DAVVERO 52 euro in quel pool?

In v3 le commissioni vanno solo alla liquidita' IN FASCIA, non a tutto il
capitale depositato. Lo Swap porta dentro il campo `liquidity`: e' esattamente
la liquidita' attiva in quel momento. Quindi la nostra fetta non e'
52/capitale, ma (nostra liquidita')/(liquidita' attiva).

Per una fascia stretta [1-w, 1+w] attorno alla parita', il capitale V produce
liquidita'  L = V / (2*sqrt(p) - sqrt(pa) - p/sqrt(pb))  con p~1:
   L ~ V / (2 - sqrt(1-w) - 1/sqrt(1+w))
Piu' stretta la fascia, piu' liquidita' per euro. Per due stablecoin la fascia
stretta e' sensata perche' il prezzo non se ne va: e' il caso in cui
concentrare NON amplifica la selezione avversa come sulle monetine.
"""
import sys, math, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
P="0x9ab7730b09ebd9b2fc5b3b5e9b1b0b0d9b1e4e3f"   # sovrascritto sotto
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
# ritrovo il pool 0,30% USDC/USDT dal nome del file precedente
corti=B.log_di_finestra(SWAP3, ult-900, ult) or []
per=collections.Counter(L["address"].lower() for L in corti)
P=None
for p,_n in per.most_common(200):
    if p.startswith("0x9ab7730b09ebd9"): P=p; break
if P is None:
    for p,_n in per.most_common(200):
        fe=B.chiama("eth_call",[{"to":p,"data":"0xddca3f43"},"latest"])
        t0=B.chiama("eth_call",[{"to":p,"data":"0x0dfe1681"},"latest"])
        if fe and int(fe,16)==3000 and t0 and "0x"+t0[-40:]=="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913":
            P=p; break
if P is None: print("pool 0,30% USDC/USDT non ritrovato"); raise SystemExit
print(f"pool {P}  ({per.get(P,0)} scambi in 30 min)")
ORE=3; FIN=int(ORE*3600/2.0)
L6=B.log_di_finestra(SWAP3, ult-FIN, ult, indirizzo=P)
if L6 is None: print("   finestra non recuperata"); raise SystemExit
liq=[]; vol=0.0; prezzi=[]
for x in L6:
    d=x["data"][2:]
    vol+=abs(sg(d[0:64]))/1e6
    liq.append(int(d[64*3:64*4],16))
    sq=int(d[64*2:64*3],16)
    if sq: prezzi.append((sq/2**96)**2)
liq=[x for x in liq if x>0]
if not liq: print("   campo liquidita' vuoto: non si puo' concludere"); raise SystemExit
Lm=st.median(liq)
comm=vol*0.003
print(f"   {len(L6)} scambi in {ORE}h | volume {vol:,.0f} | commissioni {comm:,.0f} USDC")
print(f"   liquidita' attiva (mediana del campo): {Lm:,.0f}")
if prezzi:
    print(f"   prezzo: min {min(prezzi):.6f} max {max(prezzi):.6f} (parita' = 1,000000)")
print("\n   fascia      nostra L con 52 EUR   quota     commissioni/giorno   resa annua")
for w in (0.0005, 0.002, 0.01, 0.05):
    den = 2 - math.sqrt(1-w) - 1/math.sqrt(1+w)
    V = 52/0.92            # in dollari
    Lnos = V*1e6/den if den>0 else 0     # unita' coerenti col campo (6 decimali)
    q = Lnos/(Lnos+Lm)
    gg = comm*(24/ORE)*q
    print(f"   +/-{w*100:>5.2f}%  {Lnos:>18,.0f}  {q:>7.2%}  {gg:>16,.2f}   {gg*365/V*100:>9,.0f}%")
print("\n   NB: resa LORDA. Per due stablecoin la perdita da divergenza e' minima,")
print("       ma se una perde la parita' si resta con quella in mano.")
