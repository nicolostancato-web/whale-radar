"""La stessa meccanica, su una chain grande: Morpho su Base.

Su Robinhood il premio di liquidazione e' reale (+2,6% mediano, punte +17%) ma
tutta la chain produce ~40 EUR al giorno. Il meccanismo regge, il posto no.
Su Base lo stesso protocollo muove ordini di grandezza in piu'.
CAPIENZA PRIMA DEL SEGNO: quante liquidazioni al giorno, quanto grosse,
quanti concorrenti. Se la torta e' grande, allora si studia come entrarci.
"""
import sys, json, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
import dato_obbligatorio as DO
from keccak import firma, keccak256
MORPHO="0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb"
T=firma("Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)")
SEL_MP="0x"+keccak256(b"idToMarketParams(bytes32)").hex()[:8]
SEL_SYM="0x"+keccak256(b"symbol()").hex()[:8]
SEL_DEC="0x"+keccak256(b"decimals()").hex()[:8]
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
print(f"Base, ultimo blocco {ult:,}")
code=B.chiama("eth_getCode",[MORPHO,"latest"])
print(f"   Morpho Blue: {'PRESENTE' if code and len(code)>4 else 'ASSENTE'}")
BLOCCO=2.0; FIN=int(48*3600/BLOCCO)        # 48 ore
logs=B.log_di_finestra(T, ult-FIN, ult, indirizzo=MORPHO)
if logs is None:
    print("   finestra non recuperata entro la scadenza"); raise SystemExit
print(f"   liquidazioni in 48 ore: {len(logs)}  ({len(logs)/2:.0f}/giorno)\n")
chi=collections.Counter(); merc=collections.Counter(); ev=[]
for L in logs:
    d=L["data"][2:]
    chi["0x"+L["topics"][2][-40:]]+=1; merc[L["topics"][1]]+=1
    ev.append((L["topics"][1], int(d[0:64],16), int(d[128:192],16)))
print(f"   liquidatori distinti: {len(chi)} | mercati: {len(merc)}")
for a,n in chi.most_common(5): print(f"      {a[:22]}…  {n}")
cache={}
val=[]
for mid,rip,preso in ev[:40]:
    if mid not in cache:
        r=B.chiama("eth_call",[{"to":MORPHO,"data":SEL_MP+mid[2:]},"latest"])
        if not r or len(r)<2+64*5: cache[mid]=None
        else:
            lt="0x"+r[2:2+64][-40:]
            ld=DO.intero(B.chiama("eth_call",[{"to":lt,"data":SEL_DEC},"latest"]), "i decimali del gettone")
            cache[mid]=(testo(B.chiama("eth_call",[{"to":lt,"data":SEL_SYM},"latest"])), ld)
    m=cache[mid]
    if not m: continue
    sim,ld=m
    val.append((sim, rip/10**ld))
if val:
    da_usd={"USDC":0.92,"USDT":0.92,"WETH":3030.0,"eth":3030.0,"cbBTC":95000.0,"EURC":1.0}
    eur=[v*da_usd.get(s,1.0) for s,v in val if s in da_usd]
    print(f"\n   debiti ripagati (EUR), {len(eur)} valutati:")
    if eur:
        eur.sort()
        print(f"      mediana {st.median(eur):,.0f} | media {st.mean(eur):,.0f}")
        print(f"      sotto 300 EUR: {sum(1 for x in eur if x<=300)}/{len(eur)}")
        print(f"      totale ripagato nel campione: {sum(eur):,.0f} EUR")
        print(f"\n   premio al 2,6% su tutto: ~{sum(eur)*0.026:,.0f} EUR nel campione")
