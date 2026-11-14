"""Lo stesso paio di gettoni in due pool diversi: la differenza di prezzo
dura abbastanza perche' la prenda qualcuno che non e' velocissimo?

Perche' e' diverso da tutto il resto: lo scambio andata-e-ritorno e' ATOMICO.
Una sola transazione; se non conviene, non avviene. Si rischia il gas, mai
una posizione. Niente quattro gambe, niente attesa, niente rischio di prezzo.

La domanda non e' «esiste una differenza» (esiste sempre) ma «quanti BLOCCHI
dura». Un blocco = solo i professionisti della velocita'. Dieci blocchi =
chiunque.
"""
import sys, os, json, collections
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
FIN=900
print(f"   finestra: blocchi {ult-FIN}..{ult} (~30 minuti)")
L=[]
for b in range(ult-FIN, ult, 450):
    r=B.log_di_finestra(SWAP3, b, min(b+449,ult))
    if r: L+=r
print(f"   {len(L)} scambi")
# prezzo implicito dallo sqrtPriceX96 (parola 5 del dato) per pool e blocco
perpool=collections.defaultdict(dict)
for x in L:
    d=x["data"][2:]
    if len(d)<64*5: continue
    sq=int(d[64*4:64*5],16)
    if sq==0: continue
    bl=int(x["blockNumber"],16)
    perpool[x["address"].lower()][bl]=(sq/2**96)**2
print(f"   {len(perpool)} pool distinti")
# un pool e' confrontabile con un altro solo se hanno gli STESSI due gettoni:
# si chiedono i gettoni al contratto una volta sola per pool
import time
tok={}
for p in list(perpool):
    if len(perpool[p])<5: continue
    a=B.chiama("eth_call",[{"to":p,"data":"0x"+firma("token0()")[2:10]},"latest"])
    b_=B.chiama("eth_call",[{"to":p,"data":"0x"+firma("token1()")[2:10]},"latest"])
    if not a or not b_ or len(a)<42 or len(b_)<42: continue
    tok[p]=("0x"+a[-40:], "0x"+b_[-40:])
print(f"   {len(tok)} pool con gettoni leggibili e almeno 5 scambi")
gruppi=collections.defaultdict(list)
for p,(t0,t1) in tok.items(): gruppi[tuple(sorted((t0,t1)))].append(p)
mult={k:v for k,v in gruppi.items() if len(v)>1}
print(f"   paia presenti in PIU' pool: {len(mult)}")
if not mult:
    print("\n   nessun paio duplicato in questa finestra: non si puo' misurare.")
    sys.exit(0)
for paio,ps in list(mult.items())[:6]:
    print(f"\n   paio {paio[0][:10]}../{paio[1][:10]}..  in {len(ps)} pool")
    bl=sorted(set().union(*[set(perpool[p]) for p in ps]))
    ult_v={p:None for p in ps}; diffs=[]
    for b in bl:
        for p in ps:
            if b in perpool[p]: ult_v[p]=perpool[p][b]
        v=[x for x in ult_v.values() if x]
        if len(v)>1 and min(v)>0:
            diffs.append((b, max(v)/min(v)-1))
    if not diffs: continue
    sopra=[d for _,d in diffs if d>0.006]     # 0,3%+0,3% di due pool
    print(f"      {len(diffs)} blocchi confrontabili | "
          f"differenza mediana {sorted(d for _,d in diffs)[len(diffs)//2]*100:.3f}%")
    print(f"      blocchi oltre lo 0,6% (due commissioni): {len(sopra)} "
          f"({len(sopra)/len(diffs)*100:.0f}%)")
    # durata delle sequenze consecutive sopra soglia
    run=0; runs=[]
    for b,d in diffs:
        if d>0.006: run+=1
        elif run: runs.append(run); run=0
    if run: runs.append(run)
    if runs:
        print(f"      durata delle finestre aperte: mediana {sorted(runs)[len(runs)//2]} "
              f"blocchi, massima {max(runs)}")
