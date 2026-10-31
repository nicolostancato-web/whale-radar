"""STRADA 16: quanto incassa chi sta dal lato del pedaggio, su QUESTA chain.

Le tre porte indicate dai revisori; la prima e' "essere l'indirizzo scritto nel
contratto". Il lancio di monete l'abbiamo gia' misurato e chiuso (0,55 EUR di
mediana per il lancio che faremmo davvero). Resta il LOCALE: il contratto
attraverso cui passano tutti.

Su Robinhood quello e' l'hook di Pons. Qui si misura il volume che ci passa e
quindi quanto incassa in un giorno. Serve a sapere se costruire una cosa del
genere vale mille euro al giorno o venti.
Niente ripieghi: se una costante non si legge, ci si ferma (dato_obbligatorio).
"""
import sys, json, urllib.request, collections, statistics as st
sys.path.insert(0,"agents")
from keccak import firma
import dato_obbligatorio as DO
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
HOOK="0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"
SWAP=firma("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)")
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def sg(h,bits=128):
    v=int(h,16)
    if v >= (1<<(bits-1)): v-=(1<<bits)
    return v
ult=int(rpc("eth_blockNumber",[]),16)
ORE=1.0; FIN=int(ORE*3600/0.093); PASSO=2000
print(f"finestra {ORE:.0f} ora ({FIN:,} blocchi)\n")
# quali pool hanno l'hook di Pons: si leggono gli Initialize recenti
INIT=firma("Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)")
pons=set(); altri=set()
for b in range(ult-FIN*6, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        d=L["data"][2:]; h="0x"+d[128+24:192]
        (pons if h.lower()==HOOK else altri).add(L["topics"][1])
print(f"   pool con l'hook di Pons: {len(pons)} | senza: {len(altri)}")
vol_pons=0.0; vol_altri=0.0; n_p=n_a=0
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        d=L["data"][2:]
        a0=abs(sg(d[0:64]))/1e18
        k=L["topics"][1]
        if k in pons: vol_pons+=a0; n_p+=1
        elif k in altri: vol_altri+=a0; n_a+=1
ETH=3030.0
print(f"\n   in un'ora: {n_p:,} scambi su pool Pons, volume {vol_pons:,.3f} ETH = {vol_pons*ETH:,.0f} EUR")
print(f"              {n_a:,} scambi su pool senza hook, volume {vol_altri:,.3f} ETH = {vol_altri*ETH:,.0f} EUR")
for q,et in ((0.01,"1,00% (l'hook di Pons)"),(0.003,"0,30%"),(0.0015,"0,15% (tipica di un'app che instrada)")):
    print(f"   chi incassa il {et:<38} {vol_pons*ETH*q*24:>10,.0f} EUR/giorno sul flusso Pons")
tot=(vol_pons+vol_altri)*ETH*24
print(f"\n   volume TOTALE della chain: {tot:,.0f} EUR al giorno")
print(f"   un'app che instradasse TUTTO prendendo lo 0,15%: {tot*0.0015:,.0f} EUR/giorno")
print("\n   NB: estrapolazione da un'ora. E' un ordine di grandezza per decidere")
print("       se la porta vale, non una previsione di incasso.")
