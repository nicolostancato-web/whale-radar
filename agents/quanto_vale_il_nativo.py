"""Quanto vale il token nativo della chain? Senza questo, "13,4 di capitale
attivo" non e' un numero: puo' essere 40 mila euro o 40 centesimi, e cambia
tutto sulla fetta che compriamo con 52 euro.
Si ricava da un pool che accoppia il nativo con una moneta stabile nota.
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
GEST="0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception as e: return None
def call(to,dato):
    return rpc("eth_call",[{"to":to,"data":dato},"latest"])
def testo(h):
    if not h or len(h)<130: return "?"
    try:
        n=int(h[2+64:2+128],16); return bytes.fromhex(h[2+128:2+128+n*2]).decode(errors="replace")
    except Exception: return "?"

print("chainId:", int(rpc("eth_chainId",[]) or "0x0",16))
ult=int(rpc("eth_blockNumber",[]),16)
coppie={}
for b in range(ult-30000, ult, 100):
    for L in rpc("eth_getLogs",[{"address":GEST,"topics":[INIT],
          "fromBlock":hex(b),"toBlock":hex(min(b+99,ult))}]) or []:
        c0="0x"+L["topics"][2][-40:]; c1="0x"+L["topics"][3][-40:]
        coppie[L["topics"][1]]=(c0,c1)
cnt=collections.Counter()
for c0,c1 in coppie.values(): cnt[c0]+=1; cnt[c1]+=1
print(f"\n{len(coppie)} pool | monete piu' usate come CONTROVALORE:")
for a,n in cnt.most_common(5):
    nome = "NATIVO" if a=="0x"+"0"*40 else testo(call(a,"0x95d89b41"))  # symbol()
    dec  = "" if a=="0x"+"0"*40 else f" dec={int(call(a,'0x313ce567') or '0x12',16)}"
    print(f"   {a}  {n:>4} pool  {nome}{dec}")
