"""Quanto costa sorvegliare le posizioni? E' la domanda che decide se
possiamo accorgercene prima degli altri 29.

Aave espone getUserAccountData(address): fra i valori c'e' il FATTORE DI
SALUTE. Sotto 1 la posizione e' liquidabile. Un sorvegliante deve poterne
controllare molte, spesso.

Si misura: quante chiamate al secondo reggono i nodi pubblici, e quindi
quante posizioni si possono tenere d'occhio con che frequenza.
"""
import json, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
RPC=["https://ethereum-rpc.publicnode.com","https://eth.llamarpc.com",
     "https://eth.drpc.org","https://1rpc.io/eth","https://rpc.payload.de"]
def chiama(m,p,u):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    r=urllib.request.Request(u,data=c,headers={
      "content-type":"application/json","user-agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r,timeout=20)).get("result")
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
utenti=sorted({e["utente"] for e in ev if e.get("utente")})
print(f"   {len(utenti)} indirizzi da controllare (utenti gia' liquidati)\n")
# quale nodo risponde alle chiamate di lettura?
buono=None
for u in RPC:
    try:
        r=chiama("eth_call",[{"to":POOL,"data":"0x"+SEL+utenti[0][2:].zfill(64)},"latest"],u)
        if r and len(r)>100: buono=u; print(f"   nodo che risponde: {u}"); break
    except Exception as e: pass
if not buono: print("   nessun nodo risponde alle letture"); sys.exit(0)
t0=time.time(); ok=0; vivi=[]
for a in utenti[:60]:
    try:
        r=chiama("eth_call",[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},"latest"],buono)
    except Exception: continue
    # la risposta sono 6 parole da 64 caratteri + '0x' = 386, non 396:
    # il controllo sbagliato scartava TUTTE le risposte valide
    if not r or len(r) < 2+64*6: continue
    ok+=1
    d=r[2:]
    deb=int(d[64*1:64*2],16)/1e8
    hf=int(d[64*5:64*6],16)/1e18
    if deb>0: vivi.append((a, deb, hf))
    time.sleep(0.05)
dt=time.time()-t0
print(f"   {ok} risposte in {dt:.1f}s  ->  {ok/dt:.1f} al secondo")
print(f"   in un minuto si controllano ~{ok/dt*60:,.0f} posizioni")
print(f"   un blocco dura 12s: ~{ok/dt*12:,.0f} posizioni per blocco\n")
vivi.sort(key=lambda x:x[2])
print(f"   {len(vivi)} di questi indirizzi hanno ancora un debito aperto")
for a,deb,hf in vivi[:8]:
    print(f"      {a[:20]}  debito {deb:>10,.0f} USD  salute {hf:>8.3f}"
          f"{'  LIQUIDABILE' if hf<1 else ''}")
