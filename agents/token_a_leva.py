"""DODICESIMA STRADA: i token a leva. CAPIENZA PRIMA DEL SEGNO (regola nuova).

Meccanica solida: un token a leva tripla si riequilibra ogni giorno, quindi
decade per costruzione quando il sottostante oscilla. Ma per guadagnarci
bisogna starci CORTI, e senza un mercato del prestito non si puo'.
L'alternativa vera e' l'arbitraggio sul valore: se il token scambia sopra o
sotto il suo valore teorico, si compra e si vende contro il sottostante.

Prima di studiare qualunque cosa: quanto VOLUME c'e'? Se la torta e' piccola
come UniswapX, si chiude in dieci minuti.
"""
import json, urllib.request, collections, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"; GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
USDG="0x5fc5360d0400a0fd4f2af552add042d716f1d168"; NAT="0x"+"0"*40
WETH="0x0bd7d308f8e1639fab988df18a8011f41eacad73"
VAL={USDG:(6,0.92), NAT:(18,3030.0), WETH:(18,3030.0)}
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def call(to,d): return rpc("eth_call",[{"to":to,"data":d},"latest"])
def testo(h):
    if not h or len(h)<130: return "?"
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v

ult=int(rpc("eth_blockNumber",[]),16); FIN=400000; PASSO=2000
pool={}
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        c0="0x"+L["topics"][2][-40:]; c1="0x"+L["topics"][3][-40:]
        if c0 in VAL or c1 in VAL: pool[L["topics"][1]]=(c0,c1,int(L["data"][2:][0:64],16))
sc=collections.Counter(); vol=collections.Counter()
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        k=L["topics"][1]
        if k in pool:
            c0,c1,_f = pool[k]; d=L["data"][2:]
            sc[k]+=1
            vol[k]+=abs(sg(d[0:64])) if c0 in VAL else abs(sg(d[64:128]))
ore=FIN*0.093/3600
righe=[]
for pid,(c0,c1,fee) in pool.items():
    if sc.get(pid,0)<50: continue
    base = c1 if c0 in VAL else c0
    sim = testo(call(base,"0x95d89b41"))
    if not any(k in sim.upper() for k in ("X3L","X3S","X2L","X2S","3L","3S","BULL","BEAR")): continue
    d,p = VAL[c0 if c0 in VAL else c1]
    righe.append((vol[pid]/10**d*p, sc[pid], sim, fee))
righe.sort(reverse=True)
print(f"finestra ~{ore:.1f} ore | pool a leva con >=50 scambi: {len(righe)}\n")
print("   simbolo        scambi    volume(EUR)    EUR/giorno    fee")
tot=0
for v,n,sim,fee in righe[:12]:
    et="dinamica" if fee==0x800000 else f"{fee/10000:.2f}%"
    tot+=v/ore*24
    print(f"   {sim:<14} {n:>6}  {v:>12,.0f}  {v/ore*24:>12,.0f}  {et:>8}")
print(f"\n   volume totale dei token a leva: ~{tot:,.0f} EUR al giorno")
print("   -> " + ("torta abbastanza grossa: vale studiare il meccanismo" if tot>50000 else
      "torta piccola: come UniswapX, non e' la macchina"))
