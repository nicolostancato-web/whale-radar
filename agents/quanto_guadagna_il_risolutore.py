"""Quanto guadagna chi riempie un ordine UniswapX?

Se venti risolutori si fanno concorrenza fino a zero, non c'e' spazio per un
ventunesimo e la strada si chiude stanotte. Si misura il NETTO del risolutore
dentro la singola transazione: tutti i Transfer di ERC20 da/verso di lui, piu'
il gas pagato. Niente teoria: solo quello che e' entrato e uscito.
"""
import json, urllib.request, collections, statistics as st
RPC="https://rpc.mainnet.chain.robinhood.com"
FILL="0x78ad7ec0e9f89e74012afa58738b6b661c024cb0fd185ee2f616c0a28924bd66"
TRASF="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
USDG="0x5fc5360d0400a0fd4f2af552add042d716f1d168"; WETH="0x0bd7d308f8e1639fab988df18a8011f41eacad73"
DEC={USDG:6, WETH:18}; EUR={USDG:0.92, WETH:3030.0}
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=60) as f: return json.load(f).get("result")
    except Exception: return None

ult=int(rpc("eth_blockNumber",[]),16); FIN=300000; PASSO=3000
fills=[]
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"topics":[FILL],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        fills.append((L["transactionHash"], "0x"+L["topics"][2][-40:] if len(L["topics"])>2 else None))
print(f"{len(fills)} riempimenti | ne esamino 60\n")
guad=[]; con_hedge=0; letti=0; monete=collections.Counter()
for h,solver in fills[:60]:
    if not solver: continue
    r=rpc("eth_getTransactionReceipt",[h])
    if not r: continue
    letti+=1
    gas=int(r["gasUsed"],16)*int(r.get("effectiveGasPrice","0x0"),16)/1e18*EUR[WETH]
    netto=collections.Counter(); hedge=False
    for L in r["logs"]:
        if not L.get("topics"): continue
        if L["topics"][0]==SWAP: hedge=True
        if L["topics"][0]!=TRASF or len(L["topics"])<3: continue
        tok=L["address"].lower()
        da="0x"+L["topics"][1][-40:]; a="0x"+L["topics"][2][-40:]
        try: v=int(L["data"],16)
        except Exception: continue
        if da==solver: netto[tok]-=v
        if a==solver:  netto[tok]+=v
        monete[tok]+=1
    if hedge: con_hedge+=1
    eur=sum(v/10**DEC[t]*EUR[t] for t,v in netto.items() if t in DEC)
    guad.append(eur-gas)
if guad:
    guad.sort()
    print(f"   transazioni lette: {letti} | con una copertura sul pool nella stessa: {con_hedge}")
    print(f"   guadagno del risolutore, al netto del gas (EUR):")
    print(f"      mediana {st.median(guad):+.3f} | media {st.mean(guad):+.3f}")
    print(f"      peggiore {guad[0]:+.2f} | migliore {guad[-1]:+.2f} | positivi {sum(1 for x in guad if x>0)}/{len(guad)}")
    print(f"\n   monete piu' mosse: {[(t[:10],n) for t,n in monete.most_common(3)]}")
    print("   NB: contate solo USDG e WETH; altri gettoni non valutati, quindi e' un MINIMO")
