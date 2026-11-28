"""La storia delle liquidazioni da Blockscout: archivio completo, zero chiavi.

Sbloccato il 28/10: i nodi pubblici tengono solo gli ultimi giorni, ma
l'istanza pubblica di Blockscout serve tutto l'archivio, accetta finestre da
10.000 blocchi e restituisce anche gas, orario e posizione nel blocco dentro
il log stesso — tutto in una chiamata.

Si salva ogni finestra appena arriva, cosi' una caduta non perde il lavoro.
"""
import json, os, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
POOL={"aave_v3":"0x87870bCa3F3fD6335C3F4ce8392D69350B4fA4E2",
      "spark":"0xC13e21B648A5Ee794902342038FF3aDAB66BE987"}
B="https://eth.blockscout.com/api"
FUORI="data/liquidazioni/storia_blockscout.jsonl"
os.makedirs("data/liquidazioni", exist_ok=True)
def get(u, giri=4):
    for g in range(giri):
        try:
            r=urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"})
            return json.load(urllib.request.urlopen(r, timeout=60))
        except Exception:
            time.sleep(1.0*(g+1))
    return None
# blocco attuale
d=get("https://eth.blockscout.com/api/v2/blocks?type=block")
ult=d["items"][0]["height"] if d and d.get("items") else None
if not ult: print("   blocco attuale non letto"); sys.exit(1)
GIORNI=60; PASSO=10000
inizio=ult-GIORNI*7200
visti=set()
if os.path.exists(FUORI):
    for x in open(FUORI): visti.add(json.loads(x)["tx"]+str(json.loads(x)["logIndex"]))
# LEZIONE 28/10: il 91% delle finestre falliva e il giro dopo le rifaceva
# TUTTE, comprese quelle gia' riuscite. Si segnano le finestre completate e
# si riprovano solo le mancanti: cosi' ogni giro aggiunge copertura vera.
FATTE="data/liquidazioni/finestre_fatte.json"
fatte=set(tuple(x) for x in json.load(open(FATTE))) if os.path.exists(FATTE) else set()
print(f"   dal blocco {inizio} al {ult} ({GIORNI} giorni), passo {PASSO}")
nuovi=0; falliti=0; fin=0; t0=time.time()
for nome,ind in POOL.items():
    b=inizio
    while b<ult:
        f=min(b+PASSO-1, ult)
        if (nome,b) in fatte:
            b=f+1; continue
        d=get(f"{B}?module=logs&action=getLogs&fromBlock={b}&toBlock={f}"
              f"&address={ind}&topic0={LIQ}", giri=6)
        fin+=1
        res=d.get("result") if isinstance(d,dict) else None
        if not isinstance(res,list): falliti+=1
        else:
            fatte.add((nome,b))
            json.dump([list(x) for x in fatte], open(FATTE,"w"))
            with open(FUORI,"a") as g:
                for x in res:
                    k=x["transactionHash"]+str(x["logIndex"])
                    if k in visti: continue
                    visti.add(k); nuovi+=1
                    g.write(json.dumps({"prot":nome,"tx":x["transactionHash"],
                      "blocco":int(x["blockNumber"],16),"logIndex":x["logIndex"],
                      "gar":"0x"+x["topics"][1][-40:],"dati":x["data"],
                      "ora":int(x["timeStamp"],16),"gasUsed":x["gasUsed"],
                      "gasPrice":x["gasPrice"],"idx":x.get("transactionIndex")})+"\n")
        b=f+1; time.sleep(0.8)
    print(f"   {nome}: fatto ({time.time()-t0:.0f}s)")
print(f"   finestre completate in totale: {len(fatte)} su 88")
print(f"\n   finestre provate {fin}, fallite {falliti} ({falliti/max(fin,1)*100:.0f}%)")
print(f"   eventi nuovi: {nuovi} | totale in archivio: {len(visti)}")
