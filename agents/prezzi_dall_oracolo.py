"""I prezzi dall'oracolo di Aave, non dalle mie assunzioni.

Errore del 28/10: avevo prezzato wstETH, rETH, cbETH come ETH e sDAI come un
dollaro. Valgono 1,2 / 1,12 / 1,08 / 1,1 volte tanto: sottostimando la
garanzia, decine di liquidazioni risultavano IN PERDITA e la somma dei premi
veniva negativa (-37.903 EUR) mentre le positive facevano +201.456.

Famiglia «importo senza moneta»: avevo ASSUNTO un cambio invece di leggerlo.
La soluzione giusta non e' una tabella corretta a mano ma chiedere il prezzo
ad Aave, che e' anche quello con cui il protocollo decide le liquidazioni.
Si salva in un file, cosi' si chiede una volta sola per asset.
"""
import json, os, time, urllib.request, sys
sys.path.insert(0,"agents")
from keccak import firma
ORACOLO="0x54586be62e3c3580375ae3723c145253060ca0c2"
U="https://ethereum-rpc.publicnode.com"
SEL=firma("getAssetPrice(address)")[2:10]
FUORI="data/liquidazioni/prezzi_oracolo.json"
def call(dato, giri=5):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
                  "params":[{"to":ORACOLO,"data":dato},"latest"]}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=25))
            if "result" in d and d["result"] not in (None,"0x"): return d["result"]
        except Exception: pass
        time.sleep(0.4*(g+1))
    return None
DEC=firma("decimals()")[2:10]
def decimali(a):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call",
                  "params":[{"to":a,"data":"0x"+DEC},"latest"]}).encode()
    for g in range(4):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=20))
            if "result" in d and d["result"] not in (None,"0x"):
                return int(d["result"],16)
        except Exception: pass
        time.sleep(0.3*(g+1))
    return None
ev=[json.loads(x) for x in open("data/liquidazioni/storia_v2.jsonl")]
asset=sorted({e[k] for e in ev for k in ("gar","deb") if e.get(k)})
vecchi=json.load(open(FUORI)) if os.path.exists(FUORI) else {}
print(f"   {len(asset)} asset distinti, {len(vecchi)} gia' noti")
n=0
for a in asset:
    if a in vecchi: continue
    p=call("0x"+SEL+a[2:].zfill(64))
    if not p: print(f"   {a[:12]}: prezzo non letto"); continue
    d=decimali(a)
    if d is None: print(f"   {a[:12]}: decimali non letti — SCARTATO"); continue
    vecchi[a]={"prezzo_usd": int(p,16)/1e8, "decimali": d}
    n+=1
    json.dump(vecchi, open(FUORI,"w"))
    time.sleep(0.2)
print(f"   letti {n} nuovi | totale {len(vecchi)}\n")
for a,v in sorted(vecchi.items(), key=lambda x:-x[1]["prezzo_usd"])[:12]:
    print(f"      {a[:14]}...  {v['prezzo_usd']:>12,.2f} USD   {v['decimali']} decimali")
