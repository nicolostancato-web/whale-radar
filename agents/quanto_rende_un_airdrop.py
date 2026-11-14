"""Quanto prende davvero chi partecipa a un airdrop?

Ultima strada crypto povera di capitale e ricca di lavoro: i protocolli
pagano chi li usa. Il compenso non dipende da quanto metti ma da quanto
fai — l'opposto di tutto il resto misurato finora.

Si guardano i RISCATTI veri sulla chain (eventi Transfer dal contratto di
distribuzione verso i partecipanti), non le cifre dei comunicati.
Si contano i fallimenti: gli zeri silenziosi hanno gia' ingannato due volte.
"""
import json, time, urllib.request, sys, statistics as st, collections
sys.path.insert(0,"agents")
from keccak import firma
U="https://ethereum-rpc.publicnode.com"
TRASF=firma("Transfer(address,address,uint256)")
def rpc(m,p,giri=4):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=30))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.4*(g+1))
    return None
ult=int(rpc("eth_blockNumber",[]),16)
# gettoni distribuiti di recente: si guarda il flusso Transfer dal
# distributore. Si parte da quelli con mercato, cosi' il valore e' noto.
GETTONI={"ENA (Ethena)":"0x57e114b691db790c35207b2e685d4a43181e6061",
         "EIGEN (EigenLayer)":"0xec53bf9167f50cdeb3ae105f56099aaab9061f83",
         "ZRO (LayerZero)":"0x6985884c4392d348587b19cb9eaaf157f13271cd",
         "W (Wormhole)":"0xb0ffa8000886e57f86dd5264b9582b2ad87b2b91"}
print(f"   blocco {ult} | ultimi 1.500 blocchi (5 ore)\n")
for nome, g in GETTONI.items():
    tot=[]; fal=0
    for b in range(ult-1499, ult, 300):
        r=rpc("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(min(b+299,ult)),
                              "address":g,"topics":[TRASF]}])
        if r is None: fal+=1
        else: tot+=r
        time.sleep(0.12)
    mitt=collections.Counter("0x"+x["topics"][1][-40:] for x in tot if len(x.get("topics",[]))>1)
    print(f"   {nome:<22}{len(tot):>6} trasferimenti  "
          f"{len(mitt):>5} mittenti  (finestre fallite {fal})")
    if tot and fal==0:
        for a,n in mitt.most_common(2):
            print(f"        il piu' attivo: {a[:20]}..  {n} invii")
