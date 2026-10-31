"""La lista dei debitori: il vero collo di bottiglia del tentativo.

Per sorvegliare le posizioni serve sapere CHI ha un debito. Aave non lo
espone: si ricostruisce dagli eventi Borrow. Chi ha preso in prestito almeno
una volta e' un candidato; poi si controlla la sua salute e si tengono solo
quelli vicini alla soglia.

Stessa disciplina della raccolta gentile: poche finestre per giro, pausa,
stop al primo rifiuto, stato salvato a ogni passo.
"""
import json, os, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bCa3F3fD6335C3F4ce8392D69350B4fA4E2"
BORROW=firma("Borrow(address,address,address,uint256,uint8,uint256,uint16)")
B="https://eth.blockscout.com/api"
D="data/liquidazioni"; os.makedirs(D, exist_ok=True)
FUORI=f"{D}/debitori.json"; FATTE=f"{D}/finestre_debitori.json"
MAX_PER_GIRO=5; PASSO=10000; GIORNI=120      # chi ha preso in prestito negli ultimi 4 mesi
deb=set(json.load(open(FUORI))) if os.path.exists(FUORI) else set()
fatte=set(json.load(open(FATTE))) if os.path.exists(FATTE) else set()
try:
    r=urllib.request.Request("https://eth.blockscout.com/api/v2/blocks?type=block",
                             headers={"user-agent":"Mozilla/5.0"})
    ult=json.load(urllib.request.urlopen(r, timeout=40))["items"][0]["height"]
except Exception as e:
    c=f"{D}/ultimo_blocco.json"
    if os.path.exists(c): ult=json.load(open(c))["b"]
    else: print(f"   non raggiungo la chain: {str(e)[:50]}"); sys.exit(0)
inizio=(ult-GIORNI*7200)//PASSO*PASSO
tutte=list(range(inizio, ult, PASSO))
restano=[b for b in tutte if b not in fatte]
print(f"   {len(fatte)}/{len(tutte)} finestre ({len(fatte)/len(tutte)*100:.0f}%) | "
      f"{len(deb)} debitori trovati")
if not restano:
    print("   lista completa"); sys.exit(0)
presi=0; nuovi=0
for b in restano[:MAX_PER_GIRO]:
    f=min(b+PASSO-1, ult)
    u=f"{B}?module=logs&action=getLogs&fromBlock={b}&toBlock={f}&address={POOL}&topic0={BORROW}"
    try:
        d=json.load(urllib.request.urlopen(
            urllib.request.Request(u, headers={"user-agent":"Mozilla/5.0"}), timeout=60))
    except Exception as e:
        print(f"   rifiuto su {b}: {str(e)[:36]} — mi fermo"); break
    res=d.get("result")
    if not isinstance(res, list):
        print(f"   risposta inattesa su {b}: {str(d.get('message'))[:36]} — mi fermo"); break
    for x in res:
        # topics: [sig, reserve, onBehalfOf, referral] -> il debitore e' topic 2
        if len(x.get("topics",[]))>2:
            a="0x"+x["topics"][2][-40:]
            if a not in deb: deb.add(a); nuovi+=1
    fatte.add(b); presi+=1
    json.dump(sorted(deb), open(FUORI,"w"))
    json.dump(sorted(fatte), open(FATTE,"w"))
    time.sleep(5)
print(f"   prese {presi} finestre, {nuovi} debitori nuovi | totale {len(deb)}")
print(f"   copertura {len(fatte)}/{len(tutte)} ({len(fatte)/len(tutte)*100:.0f}%)")
