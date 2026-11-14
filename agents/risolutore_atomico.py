"""Solo i riempimenti ATOMICI: ordine riempito e coperto nella STESSA transazione.

Perche' solo questi: se il risolutore si tiene il gettone, il suo guadagno
dipende da quanto varra' domani e il conto in dollari e' a meta'. Se invece
compra e rivende nello stesso blocco, non resta niente in magazzino e il netto
in USDG/WETH E' il guadagno. E' anche la sola versione che potremmo fare noi:
niente magazzino, niente monetina invendibile in mano.
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
ult=int(rpc("eth_blockNumber",[]),16); FIN=400000; PASSO=3000
fills=[]
for b in range(ult-FIN, ult, PASSO):
    for L in rpc("eth_getLogs",[{"topics":[FILL],"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}]) or []:
        if len(L["topics"])>2: fills.append((L["transactionHash"], "0x"+L["topics"][2][-40:]))
print(f"{len(fills)} riempimenti in ~{FIN*0.093/3600:.1f} ore | ne esamino 150")
at=[]; non_at=0; solvers=collections.Counter()
for h,solver in fills[:150]:
    r=rpc("eth_getTransactionReceipt",[h])
    if not r: continue
    gas=int(r["gasUsed"],16)*int(r.get("effectiveGasPrice","0x0"),16)/1e18*EUR[WETH]
    netto=collections.Counter(); hedge=False; altri=False
    for L in r["logs"]:
        if not L.get("topics"): continue
        if L["topics"][0]==SWAP: hedge=True
        if L["topics"][0]!=TRASF or len(L["topics"])<3: continue
        tok=L["address"].lower(); da="0x"+L["topics"][1][-40:]; a="0x"+L["topics"][2][-40:]
        try: v=int(L["data"],16)
        except Exception: continue
        if da==solver or a==solver:
            netto[tok] += v if a==solver else -v
    # non si scarta chi tocca altri gettoni: si tiene chi li AZZERA nella stessa
    # transazione. Residuo non nullo = merce in magazzino, e quel conto e' a meta'.
    resid=[t for t,v in netto.items() if t not in DEC and abs(v)>0]
    if not hedge or resid: non_at+=1; continue
    at.append(sum(v/10**DEC[t]*EUR[t] for t,v in netto.items() if t in DEC)-gas)
    solvers[solver]+=1
print(f"   atomici e puliti (coperti e solo USDG/WETH): {len(at)} | scartati: {non_at}")
if at:
    at.sort()
    print(f"\n   guadagno per riempimento, netto gas (EUR):")
    print(f"      mediana {st.median(at):+.4f} | media {st.mean(at):+.4f}")
    print(f"      peggiore {at[0]:+.3f} | migliore {at[-1]:+.3f} | positivi {sum(1 for x in at if x>0)}/{len(at)}")
    gg=st.mean(at)*len(fills)/ (FIN*0.093/3600) * 24
    print(f"\n   se prendessimo TUTTI i riempimenti della chain: {gg:+.0f} EUR/giorno")
    print(f"   realisticamente, con 20 risolutori in gara: ~{gg/20:+.0f} EUR/giorno")
