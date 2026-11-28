# -*- coding: utf-8 -*-
"""La copertura VERA: su quante cadute si e' posata la nostra sorveglianza.

Per ogni liquidazione avvenuta DOPO la prima istantanea, si prende
l'istantanea piu' recente che la precede e si guarda se la vittima era
armata e pronta IN QUEL MOMENTO. E' l'unico modo di misurarlo senza bias:
confrontare la lista di oggi con le cadute di ieri da' un numero storto
(dava 20,6% ed era strutturalmente sbagliato).

Si accumula: oggi dira' «0 cadute da misurare», e fra qualche giorno dira'
un numero vero. Serve pazienza, non un'altra formula.
"""
import json, os, sys, time, urllib.request, itertools
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SIG=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
F=["https://gateway.tenderly.co/public/mainnet","https://rpc.mevblocker.io"]
_g=itertools.cycle([0,1])
D="data/liquidazioni"; DOVE=f"{D}/istantanee"
PR=json.load(open(f"{D}/prezzi_oracolo.json"))
def rpc(m,p):
    i=next(_g)
    for u in (F[i],F[1-i]):
        try:
            c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
            r=urllib.request.Request(u,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=45))
            if "result" in d and d["result"] is not None: return d["result"]
        except Exception: pass
    return None
ist=sorted(os.listdir(DOVE)) if os.path.exists(DOVE) else []
if not ist:
    print("   nessuna istantanea: non c'e' niente da misurare"); sys.exit(0)
prime=json.load(open(f"{DOVE}/{ist[0]}"))
da=prime.get("blocco")
testa=int(rpc("eth_blockNumber",[]) or "0x0",16)
if not da or testa<=da:
    print("   la prima istantanea e' troppo recente"); sys.exit(0)
print(f"   dalla prima istantanea (blocco {da}) a ora ({testa}): "
      f"{testa-da} blocchi = {(testa-da)*12/3600:.1f} ore")
# le liquidazioni in quella finestra
ev=[]
a=da
while a<testa:
    b=min(testa, a+50_000)
    lg=rpc("eth_getLogs",[{"address":POOL,"topics":[SIG],
        "fromBlock":hex(a),"toBlock":hex(b)}])
    if lg is None: break
    ev+=lg; a=b+1
    time.sleep(0.4)
print(f"   {len(ev)} liquidazioni avvenute nella finestra")
if not ev: 
    print("   ancora nessuna caduta da misurare: si riprova piu' tardi"); sys.exit(0)
# le istantanee, in ordine di blocco
snap=[]
for f in ist:
    try:
        d=json.load(open(f"{DOVE}/{f}"))
        if d.get("blocco"): snap.append(d)
    except Exception: pass
snap.sort(key=lambda d:d["blocco"])
tot=arm=prn=0
dettagli=[]
for L in ev:
    blk=int(L["blockNumber"],16)
    u=("0x"+L["topics"][3][-40:]).lower()
    a_=L["topics"][2]; p=PR.get(("0x"+a_[-40:]).lower())
    premio=None
    if p:
        premio=int(L["data"][2:66],16)/10**p["decimali"]*p["prezzo_usd"]*0.07
    if premio is not None and premio<5: continue
    prec=[s for s in snap if s["blocco"]<=blk]
    if not prec: continue
    s=prec[-1]
    tot+=1
    ea = u in s["armate"]; ep = u in s["pronte"]
    arm+=ea; prn+=ep
    dettagli.append({"blocco":blk,"utente":u,"premio":round(premio or 0),
                     "era_armata":ea,"era_pronta":ep})
if not tot:
    print("   nessuna caduta sopra EUR 5 nella finestra"); sys.exit(0)
print()
print(f"   COPERTURA VERA, misurata in avanti su {tot} cadute:")
print(f"     era ARMATA : {arm}/{tot} = {100*arm/tot:.0f}%")
print(f"     era PRONTA : {prn}/{tot} = {100*prn/tot:.0f}%")
json.dump({"quando":int(time.time()),"cadute":tot,"armate":arm,"pronte":prn,
           "dettagli":dettagli[-50:]}, open(f"{D}/copertura_vera.json","w"), indent=1)
for d in dettagli[-8:]:
    print(f"     blocco {d['blocco']}  EUR {d['premio']:>8,}  "
          f"armata {'si' if d['era_armata'] else 'NO'}  "
          f"pronta {'si' if d['era_pronta'] else 'NO'}")
