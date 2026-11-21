"""STRADA 14: resa alta DOVE il prezzo non puo' divergere.

Il cerchio di stamattina: l'alta resa per euro esiste solo dove la perdita da
prezzo la annulla. Ma c'e' un'eccezione strutturale: le coppie fra attivita'
che si muovono INSIEME (due stablecoin, ether contro un suo derivato). Li' la
perdita da divergenza e' quasi zero per costruzione, non per fortuna.

Si cercano su Base i pool fra attivita' affini, si misura la resa per euro di
capitale, e si VERIFICA sulla chain quanto il prezzo e' davvero divergito nelle
ultime ore invece di assumerlo.
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
import dato_obbligatorio as DO
from keccak import firma, keccak256
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
SEL_T0="0x0dfe1681"; SEL_T1="0xd21220a7"; SEL_FEE="0xddca3f43"
SEL_BAL="0x"+keccak256(b"balanceOf(address)").hex()[:8]
SEL_SYM="0x"+keccak256(b"symbol()").hex()[:8]; SEL_DEC="0x"+keccak256(b"decimals()").hex()[:8]
STABILI={"USDC","USDT","DAI","USDBC","EURC","USDS","GHO","USDE","SUSDS","USD+","EURA"}
ETHER={"WETH","CBETH","WSTETH","RETH","EZETH","WEETH","SUPEROETHB","MSETH"}
BTC={"CBBTC","WBTC","TBTC","LBTC"}
def affini(a,b):
    A,Bx=a.upper(),b.upper()
    for g in (STABILI,ETHER,BTC):
        if A in g and Bx in g: return True
    return False
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
print(f"Base, {MIN} min, {len(logs):,} scambi su {len(per):,} pool\n")
ris=[]
for p,n in per.most_common(90):
    t0=B.chiama("eth_call",[{"to":p,"data":SEL_T0},"latest"]); t1=B.chiama("eth_call",[{"to":p,"data":SEL_T1},"latest"])
    if not t0 or not t1: continue
    a="0x"+t0[-40:]; b="0x"+t1[-40:]
    sa=testo(B.chiama("eth_call",[{"to":a,"data":SEL_SYM},"latest"]))
    sb=testo(B.chiama("eth_call",[{"to":b,"data":SEL_SYM},"latest"]))
    if not affini(sa,sb): continue
    fee=DO.intero(B.chiama("eth_call",[{"to":p,"data":SEL_FEE},"latest"]), "la commissione del pool")
    da=DO.intero(B.chiama("eth_call",[{"to":a,"data":SEL_DEC},"latest"]), "i decimali del gettone")
    ba=B.chiama("eth_call",[{"to":a,"data":SEL_BAL+"0"*24+p[2:]},"latest"])
    if not ba: continue
    cap_tok=int(ba,16)/10**da
    vol=0.0; prezzi=[]
    for L in logs:
        if L["address"].lower()!=p: continue
        d=L["data"][2:]; a0=sg(d[0:64]); a1=sg(d[64:128])
        vol+=abs(a0)/10**da
        if a1: prezzi.append(abs(a0/a1))
    if not prezzi or cap_tok<=0: continue
    # il capitale totale e' ~2x il lato misurato per una coppia bilanciata
    comm_30 = vol*fee/1e6
    resa_anno = comm_30*(24*60/MIN)*365/(2*cap_tok)
    div = (max(prezzi)/min(prezzi)-1) if len(prezzi)>1 else 0.0
    ris.append((resa_anno, div, sa, sb, fee, 2*cap_tok, n))
ris.sort(reverse=True)
print("   coppia              fee    capitale(unita')   resa annua   divergenza 30min")
for r,div,sa,sb,fee,cap,n in ris[:12]:
    print(f"   {sa:>9}/{sb:<9} {fee/10000:>5.2f}%  {cap:>14,.0f}  {r*100:>10.2f}%   {div*100:>8.3f}%")
if ris:
    print(f"\n   {len(ris)} pool fra attivita' affini su {len(per)} totali")
    print("   -> se la resa e' alta E la divergenza e' quasi nulla, questa e' la")
    print("      combinazione che mancava: niente rischio che annulli il rendimento.")
