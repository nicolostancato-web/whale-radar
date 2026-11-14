"""Dentro AAPLx3L/USDG: chi c'e' dall'altra parte, e quanto costa un giro.

A commissione zero l'arbitraggio costa solo gas, ma prima servono due cose:
  1. la RIGA DI TARATURA: comprare e rivendere subito deve costare (impatto).
     Se guadagna, la tabella e' illeggibile e si ferma tutto.
  2. chi scambia: se un indirizzo fa il 90%, e' il suo pool e noi saremmo
     l'avversario di un professionista, non un partecipante.
"""
import json, urllib.request, collections, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"; GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
USDG="0x5fc5360d0400a0fd4f2af552add042d716f1d168"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def call(to,d): return rpc("eth_call",[{"to":to,"data":d},"latest"])
def testo(h):
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace").strip()
    except Exception: return "?"
def sg(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(rpc("eth_blockNumber",[]),16); PASSO=2000
# ritrovo il pool a leva piu' scambiato
pid=None
for b in range(ult-700000, ult, 4000):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+3999,ult))}]) or []:
        c0="0x"+L["topics"][2][-40:]; c1="0x"+L["topics"][3][-40:]
        if USDG in (c0,c1):
            altro = c1 if c0==USDG else c0
            if "X3L" in testo(call(altro,"0x95d89b41")).upper():
                pid=L["topics"][1]; base=altro; primo=(c0==USDG)
if not pid: print("pool non ritrovato"); raise SystemExit
print(f"pool {pid[:18]}… | USDG e' currency{'0' if primo else '1'}")
sw=[]; tx={}
for b in range(ult-60000, ult, PASSO):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP,pid],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        d=L["data"][2:]
        a_usdg = sg(d[0:64])/1e6 if primo else sg(d[64:128])/1e6
        a_tok  = sg(d[64:128])/1e18 if primo else sg(d[0:64])/1e18
        if a_tok==0: continue
        sw.append((int(L["blockNumber"],16), abs(a_usdg/a_tok), a_usdg, L["transactionHash"]))
print(f"   {len(sw)} scambi in ~{60000*0.093/3600:.1f} ore")
chi=collections.Counter()
for _b,_p,_a,h in sw[:120]:
    t=rpc("eth_getTransactionByHash",[h])
    if t: chi[t["from"].lower()]+=1
print(f"   indirizzi distinti (su {sum(chi.values())} letti): {len(chi)}")
for a,n in chi.most_common(4): print(f"      {a[:24]}…  {n}")
q=chi.most_common(1)[0][1]/max(sum(chi.values()),1) if chi else 0
print(f"   quota del primo: {q:.0%}  -> {'un professionista solo: siamo l-avversario' if q>0.6 else 'molti partecipanti'}")
# riga di taratura: compro (USDG esce) e rivendo subito (USDG entra)
giri=[]
for i in range(len(sw)-1):
    b0,p0,a0,_ = sw[i]
    for j in range(i+1, min(i+8, len(sw))):
        b1,p1,a1,_ = sw[j]
        if b1-b0 > 3: break
        if (a0<0) != (a1<0):
            giri.append((p1/p0-1) * (1 if a0<0 else -1)); break
if giri:
    print(f"\n   RIGA DI TARATURA ({len(giri)} giri entro 3 blocchi):")
    print(f"      mediana {st.median(giri)*100:+.4f}%  media {st.mean(giri)*100:+.4f}%")
    print("      -> " + ("negativa come deve: la tabella si legge" if st.median(giri)<0 else
          "POSITIVA: illeggibile, fermarsi qui"))
