"""La commissione NON si legge dal contratto: la si MISURA dagli scambi.

Tutto il castello (5.390%, 7.435%, 10.697%) poggiava su un valore che avevo
messo io come ripiego quando fee() non rispondeva. Mai piu': se il contratto
tace, si misura.

In un pool concentrato, muovere il prezzo da sqrtP0 a sqrtP1 richiede
   dx1 = L * (sqrtP1 - sqrtP0)      (lato token1)
   dx0 = L * (1/sqrtP1 - 1/sqrtP0)  (lato token0)
senza commissione. Quello che ENTRA davvero e' maggiore di quel tanto:
   entrata_vera = entrata_teorica / (1 - commissione)
quindi  commissione = 1 - entrata_teorica/entrata_vera.
Si usa la MEDIANA su molti scambi, e si stampa la dispersione: se i valori non
si addensano, la formula non si applica a questo pool e non si conclude.
"""
import sys, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
P="0x9ab7730b09ebd9ff2df70f06339bd289a1680a46"
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
L=B.log_di_finestra(SWAP3, ult-1800, ult, indirizzo=P)
if not L: print("nessuno scambio"); raise SystemExit
L.sort(key=lambda x:(int(x["blockNumber"],16), int(x.get("logIndex","0x0"),16)))
stime=[]
prec=None
for x in L:
    d=x["data"][2:]
    a0=sg(d[0:64]); a1=sg(d[64:128]); sq=int(d[64*2:64*3],16); liq=int(d[64*3:64*4],16)
    if prec and liq>0 and sq>0 and prec>0:
        s0=prec/2**96; s1=sq/2**96
        if s1!=s0:
            if a1>0:    # entra token1
                teor=liq*(s1-s0)
                if teor>0 and a1>0: stime.append(1-teor/a1)
            elif a0>0:  # entra token0
                teor=liq*(1/s1-1/s0)
                if teor>0 and a0>0: stime.append(1-teor/a0)
    prec=sq
if not stime:
    print("   nessuna stima ricavabile"); raise SystemExit
stime=[s for s in stime if -0.02 < s < 0.1]
stime.sort()
print(f"   {len(stime)} stime della commissione da scambi consecutivi")
print(f"      mediana {st.median(stime)*100:.4f}%   quartili {stime[len(stime)//4]*100:.4f}% / {stime[3*len(stime)//4]*100:.4f}%")
m=st.median(stime)
print(f"\n   commissione misurata ~{m*100:.3f}%  contro lo 0,300% che avevo ASSUNTO")
print(f"   -> tutti i rendimenti calcolati vanno divisi per {0.003/m:.1f}" if m>0 else "")
