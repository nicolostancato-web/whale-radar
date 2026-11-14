# -*- coding: utf-8 -*-
"""CHI manda davvero gli aggiornamenti di prezzo, osservato e non dedotto.

DUE VOLTE mi sono sbagliato costruendo questa lista per deduzione:
  1. ho messo tre INDIRIZZI DI GETTONE (stETH, weETH, sUSDe) perche'
     RATIO_PROVIDER() dei proxy di Aave restituisce il token. In 27 minuti
     la sentinella ha «beccato» 5 approve e depositi su Lido: rumore.
  2. ho messo i contratti di PREZZO, ma le transazioni di aggiornamento non
     arrivano li': arrivano a dei TRASMETTITORI diversi (ETH/USD passa da
     0xe9dcbacc91, non da 0x7c7fdfca29). Sorvegliavo i posti sbagliati.

Qui la lista si costruisce GUARDANDO: si prendono gli eventi AnswerUpdated
veri di ogni prezzo, si risale alla transazione che li ha causati, e si
registra a CHI era indirizzata e con quale selettore. Quello e' il posto da
sorvegliare, per definizione, perche' e' il posto dove e' successo.
"""
import json, sys, time, urllib.request, itertools
from collections import Counter, defaultdict
sys.path.insert(0,"agents")
from keccak import firma
AU=firma("AnswerUpdated(int256,uint256,uint256)")
F=["https://gateway.tenderly.co/public/mainnet","https://rpc.mevblocker.io"]
_g=itertools.cycle([0,1])
def rpc(m,p):
    i=next(_g)
    for u in (F[i],F[1-i]):
        try:
            c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
            r=urllib.request.Request(u,data=c,headers={
                "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=45))
            if "result" in d: return d["result"]
        except Exception: pass
    return None
PREZZI=json.load(open("data/liquidazioni/da_sorvegliare.json"))
testa=int(rpc("eth_blockNumber",[]),16)
GIORNI=5
a=testa-GIORNI*7200
print(f"   osservo {GIORNI} giorni ({a}-{testa})\n")
mittenti=defaultdict(lambda: {"asset":set(),"selettori":Counter(),"volte":0})
for feed, chi in PREZZI.items():
    lg=rpc("eth_getLogs",[{"address":feed,"topics":[AU],
        "fromBlock":hex(a),"toBlock":hex(testa)}])
    if not lg:
        print(f"   {feed[:12]} {', '.join(chi):<22} nessun aggiornamento")
        continue
    # bastano gli ultimi 6: i trasmettitori sono stabili
    tx=[L["transactionHash"] for L in lg[-6:]]
    for h in tx:
        d=rpc("eth_getTransactionByHash",[h])
        if not d: continue
        to=(d.get("to") or "").lower()
        sel=(d.get("input") or "")[:10]
        m=mittenti[to]
        m["asset"].update(chi); m["selettori"][sel]+=1; m["volte"]+=1
        time.sleep(0.2)
    print(f"   {feed[:12]} {', '.join(chi):<22} {len(lg)} aggiornamenti in "
          f"{GIORNI} giorni")
fuori={}
print(f"\n   CHI SORVEGLIARE (osservato, non dedotto):")
for to,m in sorted(mittenti.items(), key=lambda x:-x[1]["volte"]):
    sel=list(m["selettori"].keys())
    fuori[to]={"asset":sorted(m["asset"]),"selettori":sel,"visto":m["volte"]}
    print(f"     {to}  {', '.join(sorted(m['asset'])):<22} "
          f"selettori {sel}  visto {m['volte']} volte")
json.dump(fuori, open("data/liquidazioni/trasmettitori.json","w"), indent=1)
print(f"\n   {len(fuori)} trasmettitori salvati in trasmettitori.json")
