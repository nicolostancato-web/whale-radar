"""Il piatto e' grande (74.000 EUR/giorno su Base), ma si divide per CAPITALE.
Quindi la domanda vera: quanto rende depositare 52 euro?

Si misura il capitale dentro i pool piu' attivi (saldo dei due gettoni) e si
rapporta alle commissioni che quegli stessi pool producono. Il rendimento e'
commissioni/capitale, e la nostra fetta e' proporzionale.
Niente estrapolazioni nascoste: si dichiara quanti pool si sono guardati.
"""
import sys, collections
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma, keccak256
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"; WETH="0x4200000000000000000000000000000000000006"
VAL={USDC:(6,0.92), WETH:(18,3030.0)}
SEL_T0="0x0dfe1681"; SEL_T1="0xd21220a7"; SEL_FEE="0xddca3f43"
SEL_BAL="0x"+keccak256(b"balanceOf(address)").hex()[:8]
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
MIN=30; FIN=int(MIN*60/2.0)
logs=B.log_di_finestra(SWAP3, ult-FIN, ult)
if logs is None: print("finestra non recuperata"); raise SystemExit
per_pool=collections.Counter(L["address"].lower() for L in logs)
scelti=[p for p,_ in per_pool.most_common(40)]
info={}
for p in scelti:
    t0=B.chiama("eth_call",[{"to":p,"data":SEL_T0},"latest"]); t1=B.chiama("eth_call",[{"to":p,"data":SEL_T1},"latest"])
    fe=B.chiama("eth_call",[{"to":p,"data":SEL_FEE},"latest"])
    if t0 and t1: info[p]=("0x"+t0[-40:], "0x"+t1[-40:], int(fe,16) if fe else 3000)
comm=collections.Counter()
for L in logs:
    p=L["address"].lower()
    if p not in info: continue
    a,b,fee=info[p]; d=L["data"][2:]
    if a in VAL: dec,pr=VAL[a]; amt=abs(sg(d[0:64]))/10**dec*pr
    elif b in VAL: dec,pr=VAL[b]; amt=abs(sg(d[64:128]))/10**dec*pr
    else: continue
    comm[p]+=amt*fee/1e6
cap={}
for p,(a,b,fee) in info.items():
    tot=0.0; ok=False
    for t in (a,b):
        if t not in VAL: continue
        r=B.chiama("eth_call",[{"to":t,"data":SEL_BAL+"0"*24+p[2:]},"latest"])
        if r:
            dec,pr=VAL[t]; tot+=int(r,16)/10**dec*pr; ok=True
    if ok: cap[p]=tot*2 if sum(1 for t in (a,b) if t in VAL)==1 else tot
righe=[(comm[p], cap[p], p) for p in cap if cap[p]>1000 and comm[p]>0]
righe.sort(reverse=True)
print(f"Base, {MIN} minuti | {len(righe)} pool con capitale e commissioni misurati\n")
print("   commissioni(30min)   capitale        resa annua   su 52 EUR")
C=0; K=0
for c,k,p in righe[:10]:
    anno=c*(24*60/MIN)*365/k
    print(f"   {c:>14,.2f}  {k:>14,.0f}  {anno*100:>10.1f}%  {52*anno:>9,.2f} EUR/anno")
for c,k,_ in righe: C+=c; K+=k
if K:
    anno=C*(24*60/MIN)*365/K
    print(f"\n   INSIEME: capitale {K:,.0f} EUR, commissioni {C*(24*60/MIN):,.0f} EUR/giorno")
    print(f"   resa annua lorda: {anno*100:.1f}%  ->  su 52 EUR fa {52*anno:,.2f} EUR all'anno")
    print("   (LORDA: senza la perdita da variazione di prezzo, che su queste coppie e' reale)")
