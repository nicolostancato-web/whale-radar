"""UNDICESIMA STRADA: gli ordini UniswapX non presi dal risolutore esclusivo.

Forma migliore delle altre: un ordine olandese che scende sotto il prezzo del
pool e' qualcuno che PAGA per farsi eseguire lo scambio senza gas. Lo si
riempie e si ricompra dal pool nella stessa transazione: non si tiene nulla in
magazzino, quindi un test sui registri non puo' lasciarci una monetina morta.

Primo passo, prima di qualsiasi teoria: ESISTE? Il reattore emette
Fill(bytes32,address,address,uint256). Se quella firma non compare, la strada
e' chiusa in dieci minuti invece che in tre giorni.
"""
import json, urllib.request, collections
RPC="https://rpc.mainnet.chain.robinhood.com"
FILL="0x78ad7ec0e9f89e74012afa58738b6b661c024cb0fd185ee2f616c0a28924bd66"
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f:
            j=json.load(f)
            return j.get("result") if "result" in j else {"__err":j.get("error")}
    except Exception as e: return {"__err":str(e)}

ult=int(rpc("eth_blockNumber",[]),16); FIN=300000; PASSO=3000
print(f"cerco la firma Fill di UniswapX su ~{FIN*0.093/3600:.1f} ore\n")
reat=collections.Counter(); filler=collections.Counter(); tot=0
for b in range(ult-FIN, ult, PASSO):
    r=rpc("eth_getLogs",[{"topics":[FILL],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}])
    if isinstance(r,dict): continue
    for L in r or []:
        tot+=1; reat[L["address"].lower()]+=1
        if len(L["topics"])>2: filler["0x"+L["topics"][2][-40:]]+=1
print(f"riempimenti trovati: {tot}")
if not tot:
    print("   -> UniswapX non e' attivo su questa chain, o usa un'altra firma. STRADA CHIUSA.")
else:
    print("   reattori:")
    for a,n in reat.most_common(3): print(f"      {a}  {n}")
    print(f"   risolutori distinti: {len(filler)}")
    for a,n in filler.most_common(5): print(f"      {a}  {n}")
    q=sum(n for _,n in filler.most_common(1))/max(tot,1)
    print(f"\n   quota del primo risolutore: {q:.0%}")
    print("   -> " + ("UN SOLO risolutore: e' un giardino chiuso" if q>0.8 else
          "piu' risolutori: vale misurare quanto resta dopo l'esclusiva"))
