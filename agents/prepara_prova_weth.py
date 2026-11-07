# -*- coding: utf-8 -*-
"""Prepara i dati per la prova su garanzia WETH, al blocco di ADESSO.

Perche': il 60% delle liquidazioni vere e' su garanzia WETH e il pescatore
non la ammette. Prima di ammetterla si prova, come si e' fatto per weETH.
Prezzi letti dall'oracolo ORA, non dal file: un prezzo di ore prima
sposterebbe la taglia e la prova direbbe un'altra cosa.
"""
import json, sys, time, urllib.request
sys.path.insert(0,"agents"); from keccak import firma
U="https://ethereum-rpc.publicnode.com"
ORAC="0x54586be62e3c3580375ae3723c145253060ca0c2"
CONTR="0xE30b58692FB7a1a417d3e0F1F5585a8Bc4D51212"
WETH="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
SEL=firma("getAssetPrice(address)")[2:10]
def rpc(m,p):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(3):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=20))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.3)
    return None
def prezzo(a):
    v=rpc("eth_call",[{"to":ORAC,"data":"0x"+SEL+a[2:].zfill(64)},"latest"])
    return int(v,16)/1e8 if v else None
UTENTE=sys.argv[1] if len(sys.argv)>1 else "0x26e449a3bfbdc9c4ff8b6c160702fc9cb9c881fd"
comp=json.load(open("data/liquidazioni/composizione.json"))
c=comp[[k for k in comp if k.lower()==UTENTE.lower()][0]]
deb=c["debito_principale"].lower(); gar=c["garanzia_principale"].lower()
assert gar==WETH, f"questa prova e' per WETH, non {gar}"
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
pw=prezzo(WETH); pd=prezzo(deb)
print(f"   WETH dall'oracolo ORA: ${pw:,.2f}   (nel file: ${PR[WETH]['prezzo_usd']:,.2f})")
print(f"   debito {deb[:10]} ${pd:,.4f}")
TETTI=json.load(open("data/liquidazioni/tetti.json"))
dus=c["debito_usd"]*0.5
if dus*1.07>TETTI[gar]: dus=TETTI[gar]/1.07
dd=PR[deb]["decimali"]
qd=int(dus/pd*10**dd)
qg=int(dus*1.07*0.90/pw*10**18)
print(f"   chiudo ${dus:,.0f} di debito -> premio atteso ${dus*0.07:,.0f}")
print(f"   vendo {qg/1e18:.4f} WETH")
q=(f"srcToken={WETH}&destToken={deb}&amount={qg}&srcDecimals=18"
   f"&destDecimals={dd}&side=SELL&network=1")
r=urllib.request.Request("https://api.paraswap.io/prices?"+q,
  headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
pr=json.load(urllib.request.urlopen(r,timeout=30))["priceRoute"]
rq=urllib.request.Request(
  "https://api.paraswap.io/transactions/1?ignoreChecks=true&ignoreGasEstimate=true",
  data=json.dumps({"srcToken":WETH,"destToken":deb,"srcAmount":str(qg),
    "priceRoute":pr,"userAddress":CONTR,"slippage":100}).encode(),
  headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
tx=json.load(urllib.request.urlopen(rq,timeout=30))
# la posizione dell'importo si CERCA: la costante 132 valeva su una rotta sola
sys.path.insert(0,"agents")
from pescatore import trova_posizione
pos,n=trova_posizione(tx["data"], pr["srcAmount"])
if pos is None:
    print(f"   l'importo appare {n} volte nella calldata: prova ABBANDONATA")
    sys.exit(1)
print(f"   posizione dell'importo nella calldata: {pos} (la vecchia costante era 132)")
import os
os.makedirs("liquidatore/dati",exist_ok=True)
for nome,val in (("utente_weth",UTENTE),("sede_weth",tx["to"]),
                 ("dati_weth",tx["data"]),("debito_weth",deb),
                 ("qdebito_weth",str(qd)),("posizione_weth",str(pos))):
    open(f"liquidatore/dati/{nome}.txt","w").write(val)
print(f"   sede: {tx['to']}  calldata {len(tx['data'])//2} byte")
print(f"   ricevo ~{int(pr['destAmount'])/10**dd:,.2f} del debito")
print("   dati scritti in liquidatore/dati/*_weth.txt")
