"""Perche' pagano lo 0,30%? Il prezzo si muove dello 0,009%: non sono
arbitraggisti (pagherebbero trenta volte il guadagno possibile). Resta che
ottengano ALTRO: punti, un airdrop, volume da esibire.

La firma del lavaggio e' precisa: scambi AVANTI E INDIETRO a breve distanza,
della stessa taglia, dallo stesso indirizzo. Se c'e', le commissioni sono
reddito vero per chi fornisce liquidita', e durano quanto il programma che le
paga: cosa da sapere prima di entrare, non dopo.
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
P="0x9ab7730b09ebd9ff2df70f06339bd289a1680a46"
SWAP3=firma("Swap(address,address,int256,int256,uint160,uint128,int24)")
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
ORE=3; FIN=int(ORE*3600/2.0)
L=B.log_di_finestra(SWAP3, ult-FIN, ult, indirizzo=P)
if L is None: print("finestra non recuperata"); raise SystemExit
sc=[]
for x in L:
    d=x["data"][2:]
    sc.append((int(x["blockNumber"],16), "0x"+x["topics"][1][-40:], "0x"+x["topics"][2][-40:],
               sg(d[0:64])/1e6))
sc.sort()
print(f"{len(sc)} scambi in {ORE} ore\n")
per=collections.defaultdict(list)
for b,mitt,dest,a0 in sc: per[dest].append((b,a0))
print("   destinatario            scambi  andate/ritorni  taglia mediana  giro medio(blocchi)")
tot_coppie=0
for dest,v in sorted(per.items(), key=lambda x:-len(x[1]))[:6]:
    v.sort()
    pos=sum(1 for _b,a in v if a>0); neg=len(v)-pos
    coppie=[]; usati=set()
    for i,(b,a) in enumerate(v):
        if i in usati: continue
        for j in range(i+1, min(i+6, len(v))):
            if j in usati: continue
            b2,a2=v[j]
            if a*a2<0 and abs(abs(a2)-abs(a))/max(abs(a),1e-9) < 0.25:
                coppie.append(b2-b); usati.add(i); usati.add(j); break
    tot_coppie+=len(coppie)
    med=st.median([abs(a) for _b,a in v])
    g=st.median(coppie) if coppie else float("nan")
    print(f"   {dest[:22]}…  {len(v):>5}   {pos:>4}/{neg:<5}  {med:>12,.2f}  {g:>10.1f}  ({len(coppie)} giri)")
print(f"\n   giri avanti-e-indietro riconosciuti: {tot_coppie} su {len(sc)} scambi "
      f"({2*tot_coppie/len(sc):.0%} degli scambi)")
print("   -> " + ("LAVAGGIO: pagano per avere altro, e le commissioni sono vere per noi"
      if 2*tot_coppie/len(sc) > 0.4 else "non e' lavaggio: la spiegazione e' un'altra"))
