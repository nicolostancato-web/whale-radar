"""11.424% annuo e' cento volte tutto il resto: referto di guasto finche' non e'
dimostrato. Il sospetto: capitale misurato su UN lato e raddoppiato. In v3 la
liquidita' e' concentrata e i due lati possono essere sbilanciatissimi.

Qui si misurano ENTRAMBI i saldi, si conta il volume scambio per scambio, e si
stampano i numeri grezzi cosi' il conto e' ispezionabile invece che creduto.
"""
import sys, collections
sys.path.insert(0,"agents")
import base_rpc as B
import dato_obbligatorio as DO
from keccak import firma, keccak256
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
SEL_T0="0x0dfe1681"; SEL_T1="0xd21220a7"; SEL_FEE="0xddca3f43"
SEL_BAL="0x"+keccak256(b"balanceOf(address)").hex()[:8]
SEL_SYM="0x"+keccak256(b"symbol()").hex()[:8]; SEL_DEC="0x"+keccak256(b"decimals()").hex()[:8]
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
MIN=30; FIN=int(MIN*60/2.0)
logs=B.log_di_finestra(SWAP3, ult-FIN, ult)
if logs is None: print("finestra non recuperata"); raise SystemExit
per=collections.Counter(L["address"].lower() for L in logs)
STAB={"USDC","USDT","DAI","EURC","USDS"}
for p,n in per.most_common(120):
    t0=B.chiama("eth_call",[{"to":p,"data":SEL_T0},"latest"]); t1=B.chiama("eth_call",[{"to":p,"data":SEL_T1},"latest"])
    if not t0 or not t1: continue
    a="0x"+t0[-40:]; b="0x"+t1[-40:]
    sa=testo(B.chiama("eth_call",[{"to":a,"data":SEL_SYM},"latest"])).upper()
    sb=testo(B.chiama("eth_call",[{"to":b,"data":SEL_SYM},"latest"])).upper()
    if not (sa in STAB and sb in STAB): continue
    fee=DO.intero(B.chiama("eth_call",[{"to":p,"data":SEL_FEE},"latest"]), "la commissione del pool")
    da=DO.intero(B.chiama("eth_call",[{"to":a,"data":SEL_DEC},"latest"]), "i decimali del gettone")
    db=DO.intero(B.chiama("eth_call",[{"to":b,"data":SEL_DEC},"latest"]), "i decimali del gettone")
    b0=B.chiama("eth_call",[{"to":a,"data":SEL_BAL+"0"*24+p[2:]},"latest"])
    b1=B.chiama("eth_call",[{"to":b,"data":SEL_BAL+"0"*24+p[2:]},"latest"])
    if not b0 or not b1: continue
    c0=int(b0,16)/10**da; c1=int(b1,16)/10**db
    vol=0.0; cnt=0
    for L in logs:
        if L["address"].lower()!=p: continue
        vol+=abs(sg(L["data"][2:][0:64]))/10**da; cnt+=1
    cap=c0+c1
    comm=vol*fee/1e6
    print(f"\n   {sa}/{sb}  fee {fee/10000:.2f}%  pool {p[:14]}…")
    print(f"      saldi:  {sa} {c0:>14,.2f}   {sb} {c1:>14,.2f}   TOTALE {cap:>14,.2f}")
    print(f"      {cnt} scambi, volume {vol:,.2f}, commissioni {comm:,.4f} in {MIN} min")
    if cap>0:
        print(f"      resa annua con ENTRAMBI i lati: {comm*(24*60/MIN)*365/cap*100:,.1f}%")
        print(f"      (con un lato raddoppiato era:   {comm*(24*60/MIN)*365/(2*c0)*100:,.1f}%)")
