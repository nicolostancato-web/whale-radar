"""Quanti debitori sono davvero vicini alla soglia?

Controllarli tutti a ogni blocco e' impossibile (6 letture al secondo, e
sono migliaia). Ma serve sorvegliare solo chi e' VICINO: una scansione lenta
una volta al giorno trova la lista corta, poi si guarda solo quella.

Si misura su un campione: che frazione ha un debito aperto, e di questi
quanti stanno sotto una salute di 1,2.
"""
import json, time, urllib.request, random, sys, collections
sys.path.insert(0,"agents")
from keccak import firma
random.seed(7)
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
U="https://ethereum-rpc.publicnode.com"
def salute(a):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
                  "params":[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},"latest"]}).encode()
    for g in range(3):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=20))
            v=d.get("result")
            if v and len(v)>=2+64*6:
                x=v[2:]
                return int(x[64:128],16)/1e8, int(x[320:384],16)/1e18
        except Exception: pass
        time.sleep(0.3)
    return None
deb=json.load(open("data/liquidazioni/debitori.json"))
camp=random.sample(deb, min(220, len(deb)))
print(f"   {len(deb)} debitori raccolti finora | campione di {len(camp)}\n")
t0=time.time(); ok=0
condeb=[]; fasce=collections.Counter()
for a in camp:
    r=salute(a)
    if r is None: continue
    ok+=1
    d,h=r
    if d<=0: fasce["nessun debito"]+=1; continue
    condeb.append((a,d,h))
    if h<1.0: fasce["gia' liquidabile"]+=1
    elif h<1.05: fasce["sotto 1,05"]+=1
    elif h<1.20: fasce["sotto 1,20"]+=1
    elif h<2.0: fasce["1,20-2,0"]+=1
    else: fasce["oltre 2,0"]+=1
dt=time.time()-t0
print(f"   {ok} risposte in {dt:.0f}s ({ok/dt:.1f} al secondo)")
print(f"   con debito aperto: {len(condeb)}/{ok} ({len(condeb)/max(ok,1)*100:.0f}%)\n")
for k in ["gia' liquidabile","sotto 1,05","sotto 1,20","1,20-2,0","oltre 2,0","nessun debito"]:
    if fasce[k]: print(f"      {k:<20}{fasce[k]:>5}  ({fasce[k]/ok*100:>4.1f}%)")
vicini=fasce["gia' liquidabile"]+fasce["sotto 1,05"]+fasce["sotto 1,20"]
print(f"\n   vicini alla soglia (<1,20): {vicini}/{ok} = {vicini/max(ok,1)*100:.1f}%")
for tot in (10000, 20000):
    n=int(tot*vicini/max(ok,1))
    print(f"   su {tot:,} debitori sarebbero ~{n:,} da sorvegliare "
          f"= {n/72:.0f} blocchi per un giro completo ({n/72*12/60:.1f} minuti)")
