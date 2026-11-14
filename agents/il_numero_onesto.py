"""Il numero onesto, col passo di tick VERO.

Errore mio: avevo calcolato una fascia di +/-0,05%, ma in un pool allo 0,30% il
passo minimo e' 60 tick (~0,6%), quindi fasce piu' strette NON si possono fare.
Il conto va rifatto col vincolo del contratto, non con quello che vorrei.

tickSpacing si legge dal pool. Un tick vale 1,0001x, quindi N tick = 1,0001^N.
"""
import sys, math, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
import dato_obbligatorio as DO
from keccak import firma, keccak256
P="0x9ab7730b09ebd9ff2df70f06339bd289a1680a46"
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
SEL_TS="0x"+keccak256(b"tickSpacing()").hex()[:8]
SEL_FEE="0xddca3f43"
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ts=DO.intero(B.chiama("eth_call",[{"to":P,"data":SEL_TS},"latest"]), "il passo di tick")
fee=DO.intero(B.chiama("eth_call",[{"to":P,"data":SEL_FEE},"latest"]), "la commissione del pool")
larg=1.0001**ts - 1
print(f"pool {P[:16]}…  fee {fee/10000:.2f}%  passo {ts} tick = fascia minima {larg*100:.3f}%")
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
ORE=3; FIN=int(ORE*3600/2.0)
L=B.log_di_finestra(SWAP3, ult-FIN, ult, indirizzo=P)
if L is None: print("finestra non recuperata"); raise SystemExit
liq=[]; vol=0.0
for x in L:
    d=x["data"][2:]
    vol+=abs(sg(d[0:64]))/1e6
    v=int(d[64*3:64*4],16)
    if v: liq.append(v)
Lm=st.median(liq)
comm_gg=vol*fee/1e6*(24/ORE)
print(f"   {len(L)} scambi/{ORE}h | volume {vol:,.0f} | commissioni {comm_gg:,.0f} USDC al giorno")
print(f"   liquidita' attiva mediana: {Lm:,.0f}\n")
print("   fasce POSSIBILI (multipli del passo):")
print("   fascia     nostra L (52 EUR)    quota      al giorno    annuo lordo")
V=52/0.92
for mult in (1,2,4,10):
    w=(1.0001**(ts*mult))-1
    den=2-math.sqrt(1/(1+w))-math.sqrt(1+w)/(1+w)
    den=2-math.sqrt(1-w/(1+w))-1/math.sqrt(1+w)   # simmetrica attorno a p=1
    if den<=0: continue
    Ln=V*1e6/den
    q=Ln/(Ln+Lm)
    gg=comm_gg*q*0.92
    print(f"   +/-{w*100:>5.2f}%  {Ln:>18,.0f}  {q:>8.4%}  {gg:>9.3f} EUR  {gg*365/52*100:>9,.0f}%")
print("\n   NB: lordo. Da togliere il gas di entrata e uscita (su Base pochi centesimi)")
print("       e il rischio che il programma che paga quel lavaggio finisca domani.")
