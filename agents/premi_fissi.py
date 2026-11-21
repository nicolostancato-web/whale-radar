"""Famiglia nuova: i PREMI FISSI a chi esegue un'azione.

Perche' questa e non un'altra: in tutto il progetto le cose reali pagavano
il CAPITALE (3-5% l'anno). Un premio fisso no — paga chi fa il lavoro, e
con i pacchetti Flashbots un tentativo sbagliato non costa nulla.

Si guarda quanto pagano davvero alcune funzioni pubbliche che chiunque puo'
chiamare, contando gli eventi reali sulla chain invece di leggere i
documenti dei protocolli.
"""
import json, time, urllib.request, sys, collections
sys.path.insert(0,"agents")
from keccak import firma
U="https://ethereum-rpc.publicnode.com"
def logs(ind, topic, da, a, giri=4):
    p=[{"fromBlock":hex(da),"toBlock":hex(a),"topics":[topic]}]
    if ind: p[0]["address"]=ind
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=35))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.5*(g+1))
    return None
def blocco():
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    r=urllib.request.Request(U,data=c,headers={
      "content-type":"application/json","user-agent":"Mozilla/5.0"})
    return int(json.load(urllib.request.urlopen(r,timeout=20))["result"],16)
ult=blocco()
# famiglie da sondare: eventi emessi quando qualcuno viene PAGATO per agire
# LEZIONE (di nuovo): senza indirizzo il nodo rifiuta e restituisce zeri
# silenziosi. Gli zeri della prima versione non significavano niente.
FAM=[
 ("Chainlink Automation (registro v2.1)", "0x6593c7de001fc8542bb1703532ee1e5aa0d458fd",
  firma("UpkeepPerformed(uint256,bool,uint96,uint256,uint256,bytes)")),
 ("Gelato Ops", "0xb3f5503f93d5ef84b06993a1975b9d21b962892f",
  firma("ExecSuccess(uint256,address,address,bytes32,bool)")),
 ("Aave — riscatto ricompense", "0x8164cc65827dcfe994ab23944cbc90e0aa80bfcb",
  firma("RewardsClaimed(address,address,address,address,uint256)")),
 ("MakerDAO clipper ETH-A (aste)", "0xc67963a226eddd77b91ad8c421630a1b0adff270",
  firma("Take(bytes32,uint256,uint256,uint256,uint256,uint256,address)")),
]
print(f"   blocco {ult} | finestra: ultime ~1.000 blocchi (3,3 ore)\n")
for nome, ind, sig in FAM:
    tot=0; falliti=0
    for b in range(ult-999, ult, 200):
        r=logs(ind, sig, b, min(b+199, ult))
        if r is None: falliti+=1
        else: tot+=len(r)
        time.sleep(0.15)
    print(f"   {nome:<46}{tot:>5} eventi"
          f"{'  (finestre fallite: '+str(falliti)+')' if falliti else ''}")
