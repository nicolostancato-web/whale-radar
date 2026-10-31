"""Se non c'e' NATIVO/USDG, si passa da WETH: WETH/USDG da' il prezzo in dollari,
NATIVO/WETH dice se il nativo e' ether avvolto (rapporto ~1) o un'altra cosa.
"""
import json, urllib.request, collections, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"; GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
USDG="0x5fc5360d0400a0fd4f2af552add042d716f1d168"; WETH="0x0bd7d308f8e1639fab988df18a8011f41eacad73"; NAT="0x"+"0"*40
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None
def s(h):
    v=int(h,16); return v-(1<<256) if v>>255 else v
ult=int(rpc("eth_blockNumber",[]),16)
coppia={}
for b in range(ult-60000, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],"fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        c0="0x"+L["topics"][2][-40:]; c1="0x"+L["topics"][3][-40:]
        coppia[L["topics"][1]]=(c0,c1)
dec={USDG:6, WETH:18, NAT:18}
gruppi=collections.defaultdict(list)
for b in range(ult-20000, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[SWAP],"fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        k=L["topics"][1]
        if k not in coppia: continue
        c0,c1=coppia[k]
        if c0 not in dec or c1 not in dec: continue
        d=L["data"][2:]; a0=s(d[0:64])/10**dec[c0]; a1=s(d[64:128])/10**dec[c1]
        if a0 and a1: gruppi[(c0,c1)].append(abs(a1/a0))
for (c0,c1),v in gruppi.items():
    n0 = "NATIVO" if c0==NAT else ("WETH" if c0==WETH else "USDG")
    n1 = "NATIVO" if c1==NAT else ("WETH" if c1==WETH else "USDG")
    print(f"   {n0}/{n1}: {len(v)} scambi, prezzo mediano {st.median(v):,.4f}")
