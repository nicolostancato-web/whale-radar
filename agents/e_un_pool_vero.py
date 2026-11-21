"""E' un pool CANONICO o una trappola?

Passo di tick 1 con commissione 0,30% non e' una combinazione che Uniswap crea
(allo 0,30% il passo standard e' 60). Un pool fuori standard su cui gira finto
volume ha l'aria della trappola, e va escluso PRIMA di pensare ai soldi.

Prova decisiva: la fabbrica ufficiale di Uniswap v3 su Base tiene un registro
getPool(token0, token1, fee). Se l'indirizzo che risponde non e' il nostro
pool, il nostro pool non e' suo.
"""
import sys
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import keccak256
P="0x9ab7730b09ebd9ff2df70f06339bd289a1680a46"
FAB="0x33128a8fc17869897dce68ed026d694621f6fdfd"      # Uniswap v3 Factory su Base
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
def sel(s): return "0x"+keccak256(s.encode()).hex()[:8]
def w(x): return x[2:].rjust(64,"0") if x.startswith("0x") else x.rjust(64,"0")
t0=B.chiama("eth_call",[{"to":P,"data":sel("token0()")},"latest"])
t1=B.chiama("eth_call",[{"to":P,"data":sel("token1()")},"latest"])
a="0x"+t0[-40:]; b="0x"+t1[-40:]
fee=int(B.chiama("eth_call",[{"to":P,"data":sel("fee()")},"latest"]),16)
print(f"pool    {P}")
print(f"token0  {a}\ntoken1  {b}\nfee     {fee}")
fab_del_pool=B.chiama("eth_call",[{"to":P,"data":sel("factory()")},"latest"])
fp = "0x"+fab_del_pool[-40:] if fab_del_pool else None
print(f"\n   la fabbrica DICHIARATA dal pool: {fp}")
print(f"   fabbrica ufficiale Uniswap v3 Base: {FAB}")
print(f"   -> {'CORRISPONDE' if fp==FAB else 'NON CORRISPONDE: non e un pool Uniswap v3 ufficiale'}")
d=sel("getPool(address,address,uint24)")+w(a)+w(b)+w(hex(fee))
r=B.chiama("eth_call",[{"to":FAB,"data":d},"latest"])
reg = "0x"+r[-40:] if r else None
print(f"\n   la fabbrica ufficiale, per questa coppia e questa fee, registra: {reg}")
print(f"   -> {'E IL NOSTRO POOL' if reg and reg.lower()==P else 'un ALTRO pool: il nostro non e nel registro ufficiale'}")
for et,sym in (("token0",a),("token1",b)):
    nm=B.chiama("eth_call",[{"to":sym,"data":sel("name()")},"latest"])
    try:
        n=int(nm[2+64:2+128],16); testo=bytes.fromhex(nm[2+128:2+128+n*2]).decode(errors="replace")
    except Exception: testo="?"
    print(f"   {et} si chiama: {testo!r}  {'<-- USDC vero' if sym==USDC else ''}")
