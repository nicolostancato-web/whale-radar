"""E su Base, chi instrada? Su Robinhood un solo contratto fa il 99,7%: la chain
E' l'app. Se la porta del pedaggio esiste da qualche parte, e' dove il flusso
arriva da molte applicazioni diverse.
Nello Swap v3 il campo `sender` e' il contratto che ha chiamato il pool.
Si misura la concentrazione per VOLUME in euro sul lato noto (USDC o WETH),
scartando i pool di cui non si conosce l'unita' (un importo senza la sua moneta
non e' un numero).
"""
import sys, collections
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma, keccak256
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"; WETH="0x4200000000000000000000000000000000000006"
VAL={USDC:(6,0.92), WETH:(18,3030.0)}
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
MIN=20; FIN=int(MIN*60/2.0)
logs=B.log_di_finestra(SWAP3, ult-FIN, ult)
if logs is None: print("finestra non recuperata"); raise SystemExit
per=collections.Counter(x["address"].lower() for x in logs)
info={}
for p,_c in per.most_common(80):
    t0=B.chiama("eth_call",[{"to":p,"data":"0x0dfe1681"},"latest"])
    t1=B.chiama("eth_call",[{"to":p,"data":"0xd21220a7"},"latest"])
    if t0 and t1: info[p]=("0x"+t0[-40:], "0x"+t1[-40:])
n=collections.Counter(); vol=collections.Counter(); tot=0.0; scartati=0
for x in logs:
    p=x["address"].lower()
    if p not in info: scartati+=1; continue
    a,b=info[p]; d=x["data"][2:]
    if a in VAL: dec,pr=VAL[a]; amt=abs(sg(d[0:64]))/10**dec*pr
    elif b in VAL: dec,pr=VAL[b]; amt=abs(sg(d[64:128]))/10**dec*pr
    else: scartati+=1; continue
    s="0x"+x["topics"][1][-40:]
    n[s]+=1; vol[s]+=amt; tot+=amt
print(f"Base, {MIN} min | {len(logs):,} scambi, {scartati:,} scartati per unita' ignota")
print(f"   volume valutato: {tot:,.0f} EUR | contratti che instradano: {len(n)}\n")
print("   contratto                   scambi      volume(EUR)   quota")
for a,v in vol.most_common(10):
    print(f"   {a[:22]}…  {n[a]:>7}  {v:>14,.0f}  {v/tot:>6.1%}")
q3=sum(v for _,v in vol.most_common(3))/max(tot,1)
acc=0;k=0
for _a,v in vol.most_common():
    acc+=v;k+=1
    if acc/tot>=0.9: break
print(f"\n   quota dei primi 3: {q3:.1%} | ne servono {k} per il 90% del volume")
print("   -> " + ("anche qui pochi padroni" if q3>0.8 else "CODA LUNGA: il mercato dell'instradamento e' contendibile"))
