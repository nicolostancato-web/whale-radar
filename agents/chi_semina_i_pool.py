"""Come si riconosce un pool DIPLOMATO, prima di entrarci?

Al diploma il pool nasce gia' pieno (~4,2 ether in un colpo solo), seminato da
un contratto. Un lancio fresco parte quasi vuoto. Quindi il discriminante e'
CHI fa la prima aggiunta di liquidita' e QUANTO grande e'. Entrambe le cose si
sanno PRIMA di entrare, come richiede la regola.
"""
import json, urllib.request, collections, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"; GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
MODL="0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def s(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v

ult=int(rpc("eth_blockNumber",[]),16); FIN=30000
amm=set(); nato={}
for b in range(ult-FIN, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        d=L["data"][2:]
        if int(d[0:64],16)==10000 and "0x"+d[128+24:192]=="0x"+"0"*40:
            amm.add(L["topics"][1]); nato[L["topics"][1]]=int(L["blockNumber"],16)
print(f"pool 1% senza hook nati in ~{FIN*0.093/3600:.1f} ore: {len(amm)}")

prima={}
for b in range(ult-FIN, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[MODL],"fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        pid=L["topics"][1]
        if pid in amm and pid not in prima:
            prima[pid]=(L["transactionHash"], s(L["data"][2:][128:192]))
print(f"   di cui con una prima aggiunta vista: {len(prima)}")
mitt=collections.Counter(); liq=[]
for pid,(h,d) in list(prima.items())[:60]:
    t=rpc("eth_getTransactionByHash",[h])
    if not t: continue
    mitt[(t.get("to") or "?").lower()] += 1
    liq.append(d)
print("\n   contratto che riceve la prima aggiunta (il seminatore):")
for k,v in mitt.most_common(5): print(f"      {k}  {v}")
if liq:
    liq=[abs(x) for x in liq]
    print(f"\n   liquidita' della prima aggiunta: mediana {st.median(liq):.3e}")
    print(f"      minima {min(liq):.2e} | massima {max(liq):.2e}")
    print(f"      sopra la mediana: {sum(1 for x in liq if x>st.median(liq))}/{len(liq)}")
