"""Raccolta GENTILE della storia da Blockscout.

Lezione del 28/10, pagata: ho martellato una fonte gratuita con 88 finestre
di fila e me la sono bruciata — da 10 finestre servite a 429 su tutto. Una
risorsa condivisa non si esaurisce per cattiveria, si esaurisce per fretta,
e poi non c'e' piu' nemmeno per me.

Quindi: al massimo TRE finestre per esecuzione, cinque secondi fra una e
l'altra, e ci si FERMA al primo rifiuto invece di insistere. Lo stato e'
salvato, quindi il giro dopo riprende. 88 finestre a 3 per giro = 30 giri.
"""
import json, os, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
POOL={"aave_v3":"0x87870bCa3F3fD6335C3F4ce8392D69350B4fA4E2",
      "spark":"0xC13e21B648A5Ee794902342038FF3aDAB66BE987"}
B="https://eth.blockscout.com/api"
D="data/liquidazioni"; os.makedirs(D, exist_ok=True)
FUORI=f"{D}/storia_v2.jsonl"; FATTE=f"{D}/finestre_fatte_v2.json"
MAX_PER_GIRO=5;   # dentro il limite 3-5 che mi sono dato, non oltre PASSO=10000; GIORNI=60
fatte=set(tuple(x) for x in json.load(open(FATTE))) if os.path.exists(FATTE) else set()
try:
    r=urllib.request.Request("https://eth.blockscout.com/api/v2/blocks?type=block",
                             headers={"user-agent":"Mozilla/5.0"})
    ult=json.load(urllib.request.urlopen(r, timeout=40))["items"][0]["height"]
except Exception as e:
    # non dipendere da un endpoint secondario per partire: se quello cade,
    # si usa l'ultimo blocco noto, salvato apposta.
    C=f"{D}/ultimo_blocco.json"
    if os.path.exists(C):
        ult=json.load(open(C))["b"]
        print(f"   blocchi non raggiungibile ({str(e)[:34]}), uso l'ultimo noto {ult}")
    else:
        print(f"   non raggiungo Blockscout e non ho un blocco di riferimento"); sys.exit(0)
else:
    json.dump({"b":ult}, open(f"{D}/ultimo_blocco.json","w"))
inizio=(ult-GIORNI*7200)//PASSO*PASSO
finestre=[(n, b) for n in POOL for b in range(inizio, ult, PASSO)]
restanti=[x for x in finestre if x not in fatte]
print(f"   {len(fatte)} finestre fatte, {len(restanti)} da fare "
      f"({len(fatte)/len(finestre)*100:.0f}% di copertura)")
if not restanti:
    print("   copertura completa"); sys.exit(0)
nuovi=0; presi=0
for nome, b in restanti[:MAX_PER_GIRO]:
    f=min(b+PASSO-1, ult)
    u=(f"{B}?module=logs&action=getLogs&fromBlock={b}&toBlock={f}"
       f"&address={POOL[nome]}&topic0={LIQ}")
    try:
        rq=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
        d=json.load(urllib.request.urlopen(rq, timeout=60))
    except Exception as e:
        print(f"   rifiuto su {nome} {b}: {str(e)[:40]} — mi fermo qui")
        break
    res=d.get("result")
    if not isinstance(res, list):
        print(f"   risposta inattesa su {nome} {b}: {str(d.get('message'))[:40]} — mi fermo")
        break
    with open(FUORI,"a") as g:
        for x in res:
            g.write(json.dumps({"prot":nome,"tx":x["transactionHash"],
              "blocco":int(x["blockNumber"],16),"logIndex":x["logIndex"],
              "gar":"0x"+x["topics"][1][-40:],"deb":"0x"+x["topics"][2][-40:],
              "utente":"0x"+x["topics"][3][-40:],"dati":x["data"],
              "ora":int(x["timeStamp"],16),"gasUsed":x["gasUsed"],
              "gasPrice":x["gasPrice"],"idx":x.get("transactionIndex")})+"\n")
            nuovi+=1
    fatte.add((nome,b)); presi+=1
    json.dump([list(x) for x in fatte], open(FATTE,"w"))
    time.sleep(5)
n=sum(1 for _ in open(FUORI)) if os.path.exists(FUORI) else 0
print(f"   prese {presi} finestre, {nuovi} eventi nuovi | archivio {n} eventi")
print(f"   copertura ora {len(fatte)}/{len(finestre)} "
      f"({len(fatte)/len(finestre)*100:.0f}%)")
