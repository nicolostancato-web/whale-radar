"""Prezzo del nativo contro la stabile USDG (6 decimali), letto da uno Swap vero.
Attenzione ai DECIMALI diversi: 18 contro 6 vale un fattore mille miliardi, ed
e' il tipo di errore che fa sembrare un pool da 40 euro un pool da 40 milioni.
"""
import json, urllib.request, collections, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
USDG="0x5fc5360d0400a0fd4f2af552add042d716f1d168"; NAT="0x"+"0"*40
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def s(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v

ult=int(rpc("eth_blockNumber",[]),16)
cerco=set()
for b in range(ult-40000, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        c0="0x"+L["topics"][2][-40:]; c1="0x"+L["topics"][3][-40:]
        if {c0,c1} == {NAT,USDG}: cerco.add(L["topics"][1])
print(f"pool NATIVO/USDG trovati nella finestra: {len(cerco)}")
pr=[]
for b in range(ult-4000, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        if cerco and L["topics"][1] not in cerco: continue
        if not cerco: continue
        d=L["data"][2:]
        a0=s(d[0:64])/1e18; a1=s(d[64:128])/1e6
        if a0 and a1: pr.append(abs(a1/a0))
if pr:
    print(f"   {len(pr)} scambi letti | prezzo mediano: {st.median(pr):,.2f} USDG per nativo")
    p=st.median(pr)
    print(f"\n   allora il capitale attivo dei pool misurati vale:")
    for cap in (13.4, 11.8, 30.9, 81.9):
        print(f"      {cap:>5} nativi = {cap*p:>12,.0f} USD  (~{cap*p*0.92:,.0f} EUR)")
    print(f"\n   con 52 EUR compriamo una fetta di: {52/0.92/(13.4*p)*100:.3f}% del pool piu' piccolo")
else:
    print("   nessuno scambio NATIVO/USDG nella finestra breve: allargo altrove")
