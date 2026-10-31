"""Perche' una posizione a salute 1,000 con 25k di debito resta intoccata?

Tre spiegazioni possibili, tutte verificabili:
  1) la salute non e' davvero sotto 1 (l'1,000 era arrotondato);
  2) la garanzia e' in qualcosa che non si rivende, quindi il premio del 5%
     non copre il costo di uscirne;
  3) la parte liquidabile e' piccola (il protocollo limita quanto si puo'
     chiudere in una volta).

La spiegazione che viene per prima in mente va sospettata: si verificano
tutte e tre con un numero.
"""
import json, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
DATI="0x7b4a4e5a"   # placeholder, non usato
U="https://ethereum-rpc.publicnode.com"
def call(to, dato):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
                  "params":[{"to":to,"data":dato},"latest"]}).encode()
    for g in range(4):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=25))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.5*(g+1))
    return None
SEL=firma("getUserAccountData(address)")[2:10]
casi=["0x7a0575018b57cb6443","0x40e93a52f6af9fcd3b","0x26e449a3bfbdc9c4ff"]
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
tutti=sorted({e["utente"] for e in ev if e.get("utente")})
scelti=[a for a in tutti if any(a.startswith(c) for c in casi)]
print(f"   {len(scelti)} posizioni da esaminare\n")
for a in scelti:
    r=call(POOL, "0x"+SEL+a[2:].zfill(64))
    if not r or len(r)<2+64*6: print(f"   {a}: nessuna risposta"); continue
    d=r[2:]
    gar=int(d[0:64],16)/1e8
    deb=int(d[64:128],16)/1e8
    disp=int(d[128:192],16)/1e8
    soglia=int(d[192:256],16)/100
    ltv=int(d[256:320],16)/100
    hf=int(d[320:384],16)/1e18
    print(f"   {a}")
    print(f"      garanzia {gar:>16,.2f} USD   debito {deb:>16,.2f} USD")
    print(f"      soglia di liquidazione {soglia:.2f}%   LTV massimo {ltv:.2f}%")
    print(f"      SALUTE con tutti i decimali: {hf:.9f}")
    print(f"      -> {'SOTTO 1: liquidabile' if hf<1 else 'sopra 1: NON liquidabile'}")
    if hf>=1:
        quanto = (1-1/hf)*100 if hf>0 else 0
        print(f"      quanto deve scendere la garanzia perche' lo diventi: {quanto:.3f}%")
    print()
