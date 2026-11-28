# -*- coding: utf-8 -*-
"""Da che salute cadono, le posizioni che vengono liquidate?

E' la misura che dice dove mettere il confine della nostra sorveglianza.
Oggi prepariamo le vendite fino a salute 1,12 e copriamo il 20,6% delle
liquidazioni reali. Se le vittime erano a 1,05 un'ora prima, il confine non
e' il problema; se erano a 1,40, allargarlo e' tutta la risposta.

Si legge la salute della vittima a vari momenti PRIMA della liquidazione,
con l'archivio. Non e' una stima: e' il suo stato di allora.
"""
import json, sys, time, urllib.request, itertools
sys.path.insert(0,"agents")
from keccak import firma
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
F=["https://gateway.tenderly.co/public/mainnet","https://rpc.mevblocker.io"]
_g=itertools.cycle([0,1])
D="data/liquidazioni"
PR=json.load(open(f"{D}/prezzi_oracolo.json"))
S=json.load(open(f"{D}/novanta_giorni.json"))
def rpc(m,p):
    i=next(_g)
    for u in (F[i],F[1-i]):
        try:
            c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
            r=urllib.request.Request(u,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=35))
            if "result" in d and d["result"] is not None: return d["result"]
        except Exception: pass
    return None
def salute(a, blk):
    v=rpc("eth_call",[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},blk])
    if isinstance(v,str) and len(v)>=2+64*6:
        x=v[2:]
        h=int(x[320:384],16)/1e18
        return h if 0<h<100 else None
    return None
liq=[]
for e in S["eventi"].values():
    p=PR.get(e["debito"].lower())
    if not p: continue
    x=e["dati"][2:]
    if len(x)<64*3: continue
    pr=int(x[0:64],16)/10**p["decimali"]*p["prezzo_usd"]*0.07
    if pr>=200: liq.append((pr, e["blocco"], e["utente"]))
liq.sort(key=lambda z:-z[1])
QUANTE=int(sys.argv[1]) if len(sys.argv)>1 else 40
liq=liq[:QUANTE]
print(f"   {len(liq)} liquidazioni sopra EUR 200, le piu' recenti\n")
# un'ora = 300 blocchi, un giorno = 7200
TEMPI=[("1 ora prima",300),("6 ore prima",1800),("1 giorno prima",7200)]
out=[]
for pr, blocco, u in liq:
    riga={"premio":round(pr),"blocco":blocco,"utente":u}
    for et,indietro in TEMPI:
        h=salute(u, hex(blocco-indietro))
        riga[et]=round(h,4) if h else None
        time.sleep(0.12)
    out.append(riga)
    print(f"   EUR {pr:>9,.0f}  " + "  ".join(
        f"{et}: {riga[et] if riga[et] else '?':>7}" for et,_ in TEMPI))
json.dump(out, open(f"{D}/da_che_salute.json","w"), indent=1)
print()
for et,_ in TEMPI:
    v=sorted(x[et] for x in out if x[et])
    if not v: continue
    sotto=lambda s: 100*sum(1 for y in v if y<s)/len(v)
    print(f"   {et}: n={len(v)}  mediana {v[len(v)//2]:.3f}  "
          f"sotto 1,12: {sotto(1.12):.0f}%  sotto 1,20: {sotto(1.20):.0f}%  "
          f"sotto 1,40: {sotto(1.40):.0f}%")
