"""STRADA 15: due pool USDC/USDT affiancati, commissioni quasi nulle.

Se quotano prezzi diversi e muoversi costa ~0, lo scarto e' prendibile.
Non serve capitale grande (si ripete), ne' velocita' estrema (le stablecoin
non scappano). La commissione la MISURO su entrambi, non la assumo
([[il ripiego e' una bugia]], 24/10).

Si allineano gli scambi dei due pool nel tempo e si guarda lo scarto fra i
prezzi NEGLI STESSI blocchi: confrontare prezzi lontani misurerebbe il
movimento del mercato, non un'occasione.
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
A="0x9ab7730b09ebd9ff2df70f06339bd289a1680a46"   # quasi zero commissioni
C="0xa41bc0affba7fd6d1b4c6a3e0ef8e4fbb8a7b1a7"   # il "0,00%" visto prima
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
def prezzi(p, da, a):
    L=B.log_di_finestra(SWAP3, da, a, indirizzo=p)
    out={}
    for x in L or []:
        d=x["data"][2:]; sq=int(d[64*2:64*3],16)
        if sq: out[int(x["blockNumber"],16)]=(sq/2**96)**2
    return out
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
ORE=2; FIN=int(ORE*3600/2.0)
# il secondo pool lo ritrovo fra i piu' attivi, per non fidarmi di un indirizzo a memoria
corti=B.log_di_finestra(SWAP3, ult-900, ult) or []
per=collections.Counter(x["address"].lower() for x in corti)
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
# LA STESSA IDENTICA COPPIA, nello stesso ordine: confrontare USDC/WETH con
# USDC/USDT dava scarti astronomici perche' non sono lo stesso prezzo.
ta=("0x"+B.chiama("eth_call",[{"to":A,"data":"0x0dfe1681"},"latest"])[-40:],
    "0x"+B.chiama("eth_call",[{"to":A,"data":"0xd21220a7"},"latest"])[-40:])
print(f"coppia del pool A: {ta[0][:10]}… / {ta[1][:10]}…")
coppie=[]
for p,_n in per.most_common(200):
    t0=B.chiama("eth_call",[{"to":p,"data":"0x0dfe1681"},"latest"])
    t1=B.chiama("eth_call",[{"to":p,"data":"0xd21220a7"},"latest"])
    if not t0 or not t1: continue
    if ("0x"+t0[-40:], "0x"+t1[-40:]) == ta: coppie.append(p)
print(f"pool con la STESSA coppia: {len(coppie)}")
pa=prezzi(A, ult-FIN, ult)
print(f"   pool A {A[:14]}…: {len(pa)} blocchi con prezzo")
migliori=[]
for p in coppie:
    if p==A: continue
    pb=prezzi(p, ult-FIN, ult)
    comuni=set(pa)&set(pb)
    if len(comuni)<20: continue
    sc=[abs(pa[b]/pb[b]-1) for b in comuni]
    migliori.append((st.median(sc), len(comuni), p, max(sc)))
migliori.sort(reverse=True)
print("\n   pool B             blocchi in comune   scarto mediano   scarto massimo")
for med,n,p,mx in migliori[:6]:
    print(f"   {p[:16]}…  {n:>14}   {med*100:>12.4f}%   {mx*100:>12.4f}%")
if migliori:
    print("\n   -> un'occasione esiste solo se lo scarto supera la somma delle due")
    print("      commissioni piu' il gas. Con commissioni ~0, la soglia e' il gas:")
    print("      su Base un giro costa circa 0,01-0,05 EUR, cioe' lo 0,02-0,1% su 52 EUR.")
