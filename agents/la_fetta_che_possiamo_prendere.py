"""Quanto di quel mercato e' raggiungibile con 52-300 euro?

Su Base: 25.000 EUR di debito ripagato in 48 ore, ma mediana 4 EUR e media 711.
Pochissime grosse portano tutto. Per liquidare serve CAPITALE pari al debito,
quindi la domanda non e' quanto vale il mercato: e' quanto vale la FETTA sotto
la nostra taglia. Il resto e' un business vero che richiede capitale, non
astuzia, e vale saperlo distinto.
"""
import sys, json, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
import dato_obbligatorio as DO
from keccak import firma, keccak256
MORPHO="0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb"
T=firma("Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)")
SEL_MP="0x"+keccak256(b"idToMarketParams(bytes32)").hex()[:8]
SEL_SYM="0x"+keccak256(b"symbol()").hex()[:8]; SEL_DEC="0x"+keccak256(b"decimals()").hex()[:8]
USD={"USDC":0.92,"USDT":0.92,"WETH":3030.0,"cbBTC":95000.0,"EURC":1.0,"wstETH":3600.0,"cbETH":3100.0}
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
FIN=int(4*24*3600/2.0)          # quattro giorni (una settimana supera la scadenza)
logs=B.log_di_finestra(T, ult-FIN, ult, indirizzo=MORPHO)
if logs is None: print("finestra non recuperata"); raise SystemExit
print(f"una settimana su Base: {len(logs)} liquidazioni ({len(logs)/7:.0f}/giorno)\n")
cache={}; righe=[]
for L in logs:
    mid=L["topics"][1]; d=L["data"][2:]
    if mid not in cache:
        r=B.chiama("eth_call",[{"to":MORPHO,"data":SEL_MP+mid[2:]},"latest"])
        if not r or len(r)<2+64*5: cache[mid]=None
        else:
            lt="0x"+r[2:2+64][-40:]
            cache[mid]=(testo(B.chiama("eth_call",[{"to":lt,"data":SEL_SYM},"latest"])),
                        DO.intero(B.chiama("eth_call",[{"to":lt,"data":SEL_DEC},"latest"]), "i decimali del gettone"))
    m=cache[mid]
    if not m: continue
    sim,ld=m
    if sim not in USD: continue
    righe.append((int(d[0:64],16)/10**ld*USD[sim], "0x"+L["topics"][2][-40:]))
if not righe: print("nessuna valutabile"); raise SystemExit
tot=sum(v for v,_ in righe)
for soglia in (52, 300, 1000, 10000, 10**9):
    f=[v for v,_ in righe if v<=soglia]
    et = "TUTTE" if soglia>10**8 else f"<= {soglia} EUR"
    print(f"   {et:<14} {len(f):>4} liquidazioni  debito {sum(f):>12,.0f} EUR"
          f"   premio 2,6% = {sum(f)*0.026:>9,.0f} EUR/settimana  = {sum(f)*0.026/7:>7,.0f}/giorno")
chi=collections.Counter(c for _v,c in righe)
print(f"\n   liquidatori: {len(chi)} | i primi due fanno {sum(n for _,n in chi.most_common(2))}/{len(righe)}")
print("\n   -> la fetta sotto la nostra taglia e' quella che conta: il resto e' un")
print("      business vero ma a capitale, non ad astuzia.")
