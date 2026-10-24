"""Quanto guadagna DAVVERO una delle app che incassano su Base?

Sei indirizzi incassano commissioni d'app. Se prendono trenta euro al giorno la
porta da' su un cortile; se ne prendono mille e' un'altra storia. E' il numero
che serve per decidere, piu' di qualunque tariffa pubblicata.

Si sommano i Transfer IN ENTRATA verso quegli indirizzi, valutando solo i
gettoni di cui si conosce l'unita' (un importo senza la sua moneta non e' un
numero) e dichiarando quanti se ne scartano.
"""
import sys, collections, statistics as st
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
TRASF=firma("Transfer(address,address,uint256)")
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"; WETH="0x4200000000000000000000000000000000000006"
CBBTC="0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf"
VAL={USDC:(6,0.92), WETH:(18,3030.0), CBBTC:(8,87000.0)}
APP=["0x67421e82e0157a3ca9508ee92f6417a93bbf59cb",
     "0x7bf90111ad7c22bec9e9dff8a01a44713cc1b1b6",
     "0x0469a4bd3724dc86c9542f4694c976da13c450c0",
     "0xc8d077444625eb300a427a6dfb2b1dbf9b159040",
     "0xee3f9501deb1eddefd9cd49548856fb58a221753",
     "0xe9b96074db017f043e71165ca5b046e57ee1cba2"]
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
ORE=3; FIN=int(ORE*3600/2.0)
print(f"Base, ultime {ORE} ore\n")
print("   app                                         entrate(EUR)   n   al giorno")
tot=0.0
for a in APP:
    topic2="0x"+"0"*24+a[2:]
    L=B.log_di_finestra(TRASF, ult-FIN, ult, indirizzo=None, secondo=None) if False else None
    # filtro per destinatario: topic2 = chi riceve
    L=[]; falliti=[0]
    PASSO=500   # 3.000 blocchi vengono rifiutati quando il filtro non ha indirizzo
    for b in range(ult-FIN, ult, PASSO):
        # l'RPC RIFIUTA None come jolly nei topic e risponde nulla: con
        # `if isinstance(r,list)` quel rifiuto diventava "zero incassi".
        # Jolly corretto = lista vuota. E i fallimenti si CONTANO.
        r=B.chiama("eth_getLogs",[{"topics":[TRASF,[],[topic2]],
                                   "fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}])
        if isinstance(r,list): L+=r
        else: falliti[0]+=1
    val=0.0; n=0; scart=0
    for x in L:
        t=x["address"].lower()
        if t not in VAL: scart+=1; continue
        dec,pr=VAL[t]
        try: v=int(x["data"],16)
        except Exception: continue
        val+=v/10**dec*pr; n+=1
    tot+=val
    print(f"   {a}  {val:>12,.2f}  {n:>4}  {val*24/ORE:>9,.0f}"
          + (f"   ({scart} gettoni ignoti)" if scart else "")
          + (f"   [{falliti[0]} FINESTRE FALLITE]" if falliti[0] else ""))
print(f"\n   totale delle sei: {tot:,.0f} EUR in {ORE} ore = {tot*24/ORE:,.0f} EUR al giorno")
print(f"   media per app: {tot*24/ORE/len(APP):,.0f} EUR al giorno")
print("\n   NB: entrate TOTALI di quegli indirizzi, non solo commissioni d'app:")
print("       e' un tetto superiore, non un utile.")
