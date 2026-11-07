"""Quanto sono GRANDI le torte, in assoluto? La domanda che viene prima.

Cinque strade chiuse in una notte, e tutte per lo stesso motivo: la torta intera
vale 40-94 EUR al giorno. Quando la causa si ripete, non e' delle strategie: e'
dell'ambiente. Quindi invece di provare la strada quattordici, si misura il
TETTO: quanto denaro passa, ogni giorno, nei posti dove uno potrebbe prenderne.

Qui: le commissioni pagate dai compratori su Uniswap v3 su Base, cioe' il
reddito complessivo di chi fornisce liquidita' li'. Si misura su una finestra
piccola e si DICHIARA l'estrapolazione, invece di fingere di aver visto tutto.
Swap v3: (sender indexed, recipient indexed, amount0, amount1, sqrtP, liq, tick)
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
# monete di conto note su Base, per valutare il lato giusto dello scambio
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"; WETH="0x4200000000000000000000000000000000000006"
VAL={USDC:(6,0.92), WETH:(18,3030.0)}
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
MIN=30; FIN=int(MIN*60/2.0)
print(f"Base, finestra di {MIN} minuti (blocco {ult:,})")
logs=B.log_di_finestra(SWAP3, ult-FIN, ult)
if logs is None: print("   finestra non recuperata entro la scadenza"); raise SystemExit
print(f"   scambi v3 letti: {len(logs):,}")
# il volume si valuta sul lato in moneta nota: serve sapere i gettoni del pool.
# Per non fare migliaia di chiamate, si campionano i pool piu' attivi.
per_pool=collections.Counter()
for L in logs: per_pool[L["address"].lower()]+=1
print(f"   pool distinti: {len(per_pool):,}")
SEL_T0="0x0dfe1681"; SEL_T1="0xd21220a7"; SEL_FEE="0xddca3f43"
tot=0.0; coperti=0; campione=per_pool.most_common(60)
info={}
for p,_n in campione:
    t0=B.chiama("eth_call",[{"to":p,"data":SEL_T0},"latest"]); t1=B.chiama("eth_call",[{"to":p,"data":SEL_T1},"latest"])
    fe=B.chiama("eth_call",[{"to":p,"data":SEL_FEE},"latest"])
    if not t0 or not t1: continue
    info[p]=("0x"+t0[-40:], "0x"+t1[-40:], int(fe,16) if fe else 3000)
vol_noti=0.0; comm=0.0; n_usati=0
for L in logs:
    p=L["address"].lower()
    if p not in info: continue
    a,b,fee=info[p]; d=L["data"][2:]
    if a in VAL: dec,pr=VAL[a]; amt=abs(sg(d[0:64]))/10**dec*pr
    elif b in VAL: dec,pr=VAL[b]; amt=abs(sg(d[64:128]))/10**dec*pr
    else: continue
    vol_noti+=amt; comm+=amt*fee/1e6; n_usati+=1
quota = n_usati/max(len(logs),1)
print(f"\n   campionati i {len(info)} pool piu' attivi: coprono {quota:.1%} degli scambi")
print(f"   volume in quella fetta: {vol_noti:,.0f} EUR in {MIN} min")
print(f"   commissioni pagate:     {comm:,.0f} EUR in {MIN} min")
if quota>0:
    gg=comm*(24*60/MIN)
    print(f"\n   STIMA sulla sola fetta campionata: {gg:,.0f} EUR al giorno di commissioni")
    print(f"   (se il resto degli scambi somigliasse a questi: ~{gg/quota:,.0f} EUR/giorno in tutto)")
print("\n   NB: estrapolazione da 30 minuti e da 60 pool. E' un ordine di grandezza,")
print("       non una misura: serve a sapere se il piatto e' da decine o da milioni.")
